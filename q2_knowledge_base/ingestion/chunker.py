
from typing import Dict, List
import re


DEFAULT_CHUNK_SIZE = 80
DEFAULT_CHUNK_OVERLAP = 20


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentence-like units while preserving context."""
    text = text.strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def count_words(text: str) -> int:
    """Count words in a text block."""
    return len(text.split())


def create_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """Create sentence-aware overlapping chunks for general documents."""
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = count_words(sentence)

        if (
            current_sentences
            and current_word_count + sentence_word_count > chunk_size
        ):
            chunk = " ".join(current_sentences).strip()

            if chunk:
                chunks.append(chunk)

            # Preserve a small overlap from the previous chunk.
            overlap_sentences = []
            overlap_words = 0

            for previous_sentence in reversed(current_sentences):
                previous_words = count_words(previous_sentence)

                if overlap_words + previous_words > chunk_overlap:
                    break

                overlap_sentences.insert(0, previous_sentence)
                overlap_words += previous_words

            current_sentences = overlap_sentences
            current_word_count = overlap_words

        current_sentences.append(sentence)
        current_word_count += sentence_word_count

    if current_sentences:
        chunk = " ".join(current_sentences).strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def create_faq_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Keep each FAQ question and its answer in a separate chunk.

    The question-answer entry is treated as an indivisible unit.
    An entry may exceed chunk_size to preserve its complete answer.
    Any preamble before the first numbered question is retained.
    """
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    # Split immediately before numbered FAQ questions.
    parts = re.split(
        r"(?=^\s*Q\d+\.\s)",
        text.strip(),
        flags=re.IGNORECASE | re.MULTILINE,
    )

    chunks = []
    preamble = []

    for part in parts:
        part = part.strip()

        if not part:
            continue

        if re.match(r"^\s*Q\d+\.\s", part, flags=re.IGNORECASE):
            # Preserve any preamble as a separate chunk.
            if preamble:
                chunks.append("\n\n".join(preamble))
                preamble = []

            # Keep this entire question and its answer together.
            chunks.append(part)

        elif chunks:
            # Attach intervening text to the preceding FAQ entry.
            chunks[-1] += "\n" + part

        else:
            preamble.append(part)

    if preamble:
        chunks.insert(0, "\n\n".join(preamble))

    return chunks


def chunk_document(
    document: Dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """Chunk one document while preserving its metadata."""
    if document.get("category") == "faq":
        chunks = create_faq_chunks(
            document["text"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        chunks = create_chunks(
            document["text"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    chunk_records = []

    for index, chunk in enumerate(chunks):
        chunk_records.append(
            {
                "chunk_id": f"{document['source']}::chunk_{index}",
                "source": document["source"],
                "file_type": document["file_type"],
                "category": document["category"],
                "pii_detected": document.get("pii_detected", False),
                "pii_types": document.get("pii_types", []),
                "chunk_index": index,
                "text": chunk,
            }
        )

    return chunk_records


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """Chunk all documents and return a flat list of chunk records."""
    all_chunks = []

    for document in documents:
        document_chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        all_chunks.extend(document_chunks)

        print(
            f"[CHUNKED] {document['source']} "
            f"-> {len(document_chunks)} chunks"
        )

    return all_chunks


if __name__ == "__main__":
    # Support both direct script execution and package execution.
    try:
        from ingestion.document_loader import load_all_documents
        from ingestion.cleaner import clean_documents
        from ingestion.pii_detector import process_documents
    except ImportError:
        from document_loader import load_all_documents
        from cleaner import clean_documents
        from pii_detector import process_documents

    print("=" * 60)
    print("Q2 KNOWLEDGE BASE - CHUNKER")
    print("=" * 60)

    print("\nLoading documents...\n")
    documents = load_all_documents()

    print("\nCleaning documents...\n")
    cleaned_documents = clean_documents(documents)

    print("\nChecking for PII...\n")
    processed_documents = process_documents(cleaned_documents)

    print("\nCreating chunks...\n")
    chunks = chunk_documents(processed_documents)

    print("\n" + "=" * 60)
    print(f"TOTAL CHUNKS CREATED: {len(chunks)}")
    print("=" * 60)

    for chunk in chunks[:5]:
        print("\n" + "-" * 60)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['source']}")
        print(f"Category: {chunk['category']}")
        print(f"Chunk index: {chunk['chunk_index']}")
        print(f"Text:\n{chunk['text'][:700]}")
