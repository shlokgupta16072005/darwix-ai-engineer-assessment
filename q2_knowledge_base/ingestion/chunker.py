from typing import Dict, List
import re


DEFAULT_CHUNK_SIZE = 80
DEFAULT_CHUNK_OVERLAP = 20


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentence-like units while preserving useful context.
    """

    text = text.strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def count_words(text: str) -> int:
    """
    Count words in a text block.
    """

    return len(text.split())


def create_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Create sentence-aware overlapping chunks.

    The chunker tries to keep related sentences together instead
    of cutting the document at arbitrary word positions.
    """

    if not text.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []

    current_sentences = []
    current_word_count = 0

    for sentence in sentences:

        sentence_word_count = count_words(sentence)

        # If adding this sentence would exceed the target size,
        # save the current chunk first.
        if (
            current_sentences
            and current_word_count + sentence_word_count
            > chunk_size
        ):

            chunk = " ".join(
                current_sentences
            ).strip()

            if chunk:
                chunks.append(chunk)

            # Keep a small overlap from the end of the
            # previous chunk.
            overlap_sentences = []
            overlap_words = 0

            for previous_sentence in reversed(
                current_sentences
            ):

                previous_words = count_words(
                    previous_sentence
                )

                if (
                    overlap_words + previous_words
                    > chunk_overlap
                ):
                    break

                overlap_sentences.insert(
                    0,
                    previous_sentence
                )

                overlap_words += previous_words

            current_sentences = overlap_sentences
            current_word_count = overlap_words

        current_sentences.append(sentence)
        current_word_count += sentence_word_count

    # Add final chunk.
    if current_sentences:

        chunk = " ".join(
            current_sentences
        ).strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def chunk_document(
    document: Dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """
    Convert one cleaned document into retrieval chunks.

    Each chunk preserves the original document metadata.
    """

    chunks = create_chunks(
        document["text"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunk_records = []

    for index, chunk in enumerate(chunks):

        chunk_records.append(
            {
                "chunk_id": (
                    f"{document['source']}"
                    f"::chunk_{index}"
                ),
                "source": document["source"],
                "file_type": document["file_type"],
                "category": document["category"],
                "pii_detected": document.get(
                    "pii_detected",
                    False
                ),
                "pii_types": document.get(
                    "pii_types",
                    []
                ),
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
    """
    Chunk all documents.

    Returns a flat list of chunk records.
    """

    all_chunks = []

    for document in documents:

        document_chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        all_chunks.extend(
            document_chunks
        )

        print(
            f"[CHUNKED] {document['source']} "
            f"-> {len(document_chunks)} chunks"
        )

    return all_chunks


if __name__ == "__main__":

    from document_loader import load_all_documents
    from cleaner import clean_documents
    from pii_detector import process_documents

    print("=" * 60)
    print("Q2 KNOWLEDGE BASE - CHUNKER")
    print("=" * 60)

    # Step 1: Load documents
    print("\nLoading documents...\n")

    documents = load_all_documents()

    # Step 2: Clean documents
    print("\nCleaning documents...\n")

    cleaned_documents = clean_documents(
        documents
    )

    # Step 3: Detect/mask PII
    print("\nChecking for PII...\n")

    processed_documents = process_documents(
        cleaned_documents
    )

    # Step 4: Create chunks
    print("\nCreating chunks...\n")

    chunks = chunk_documents(
        processed_documents
    )

    print("\n" + "=" * 60)

    print(
        f"TOTAL CHUNKS CREATED: {len(chunks)}"
    )

    print("=" * 60)

    # Display examples
    for chunk in chunks[:5]:

        print("\n" + "-" * 60)

        print(
            f"Chunk ID: {chunk['chunk_id']}"
        )

        print(
            f"Source: {chunk['source']}"
        )

        print(
            f"Category: {chunk['category']}"
        )

        print(
            f"Chunk index: "
            f"{chunk['chunk_index']}"
        )

        print(
            f"Text:\n{chunk['text'][:700]}"
        )