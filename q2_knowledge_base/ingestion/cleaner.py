import re
from typing import Dict, List


def normalize_whitespace(text: str) -> str:
    """
    Normalize spaces and blank lines without changing the meaning
    of the document.
    """

    # Replace Windows-style line endings
    text = text.replace("\r\n", "\n")

    # Remove spaces at the beginning/end of lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove excessive blank lines
    cleaned_lines = []
    previous_blank = False

    for line in lines:
        if line == "":
            if not previous_blank:
                cleaned_lines.append(line)
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


def normalize_text(text: str) -> str:
    """
    Apply basic text normalization suitable for retrieval.
    """

    text = normalize_whitespace(text)

    # Normalize common dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Normalize quotation marks
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    text = text.replace("‘", "'")
    text = text.replace("’", "'")

    # Remove repeated spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def remove_repeated_lines(text: str) -> str:
    """
    Remove repeated lines such as duplicated PDF headers/footers.
    """

    lines = text.split("\n")

    line_counts = {}

    for line in lines:
        normalized_line = line.strip().lower()

        if normalized_line:
            line_counts[normalized_line] = (
                line_counts.get(normalized_line, 0) + 1
            )

    cleaned_lines = []

    for line in lines:
        normalized_line = line.strip().lower()

        # Remove a non-empty line if it appears repeatedly.
        # Keep normal content that occurs only once.
        if (
            normalized_line
            and line_counts.get(normalized_line, 0) > 1
        ):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def clean_document(document: Dict) -> Dict:
    """
    Clean one loaded document while preserving its metadata.
    """

    original_text = document["text"]

    cleaned_text = normalize_text(original_text)
    cleaned_text = remove_repeated_lines(cleaned_text)
    cleaned_text = normalize_text(cleaned_text)

    cleaned_document = document.copy()

    cleaned_document["text"] = cleaned_text
    cleaned_document["original_length"] = len(original_text)
    cleaned_document["cleaned_length"] = len(cleaned_text)

    return cleaned_document


def clean_documents(documents: List[Dict]) -> List[Dict]:
    """
    Clean a list of loaded documents.
    """

    cleaned_documents = []

    for document in documents:
        cleaned_document = clean_document(document)

        cleaned_documents.append(cleaned_document)

        print(
        f"[CLEANED] {document['source']} "
        f"{cleaned_document['original_length']:,} -> "
        f"{cleaned_document['cleaned_length']:,} characters"
    )

    return cleaned_documents


if __name__ == "__main__":
    from document_loader import load_all_documents

    print("=" * 60)
    print("Q2 KNOWLEDGE BASE - DOCUMENT CLEANER")
    print("=" * 60)

    documents = load_all_documents()

    print("\nCleaning documents...\n")

    cleaned_documents = clean_documents(documents)

    print("\n" + "=" * 60)
    print(f"DOCUMENTS CLEANED: {len(cleaned_documents)}")
    print("=" * 60)

    for document in cleaned_documents:
        print(
            f"\n{document['source']}"
            f"\nCategory: {document['category']}"
            f"\nOriginal: {document['original_length']:,} characters"
            f"\nCleaned:  {document['cleaned_length']:,} characters"
        )