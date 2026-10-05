import re
from typing import Dict, List, Tuple


# Basic PII patterns for the prototype.
PII_PATTERNS = {
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "phone": re.compile(
        r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
    ),

    "pan": re.compile(
        r"\b[A-Z]{5}\d{4}[A-Z]\b"
    ),

    "aadhaar": re.compile(
        r"(?<!\d)\d{4}[-\s]?\d{4}[-\s]?\d{4}(?!\d)"
    ),
}


def detect_pii(text: str) -> List[str]:
    """
    Detect PII types present in a piece of text.

    Returns a list such as:
    ['email', 'phone']
    """

    detected = []

    for pii_type, pattern in PII_PATTERNS.items():

        if pattern.search(text):
            detected.append(pii_type)

    return detected


def mask_pii(text: str) -> Tuple[str, List[str]]:
    """
    Detect and mask PII in text.

    Returns:
        masked_text
        detected_pii_types
    """

    detected = []

    masked_text = text

    for pii_type, pattern in PII_PATTERNS.items():

        if pattern.search(masked_text):
            detected.append(pii_type)

            replacement = f"[{pii_type.upper()}_REDACTED]"

            masked_text = pattern.sub(
                replacement,
                masked_text
            )

    return masked_text, detected


def process_document(document: Dict) -> Dict:
    """
    Detect and mask PII in one document.
    """

    original_text = document["text"]

    masked_text, detected_pii = mask_pii(
        original_text
    )

    processed_document = document.copy()

    processed_document["text"] = masked_text
    processed_document["pii_detected"] = bool(
        detected_pii
    )
    processed_document["pii_types"] = detected_pii

    return processed_document


def process_documents(
    documents: List[Dict],
) -> List[Dict]:
    """
    Process all documents for PII.
    """

    processed_documents = []

    for document in documents:

        processed = process_document(
            document
        )

        processed_documents.append(processed)

        if processed["pii_detected"]:

            print(
                f"[PII DETECTED] "
                f"{document['source']}: "
                f"{', '.join(processed['pii_types'])}"
            )

        else:

            print(
                f"[NO PII] "
                f"{document['source']}"
            )

    return processed_documents


if __name__ == "__main__":

    from document_loader import load_all_documents
    from cleaner import clean_documents

    print("=" * 60)
    print("Q2 KNOWLEDGE BASE - PII DETECTOR")
    print("=" * 60)

    documents = load_all_documents()

    print("\nCleaning documents...\n")

    cleaned_documents = clean_documents(
        documents
    )

    print("\nChecking for PII...\n")

    processed_documents = process_documents(
        cleaned_documents
    )

    total_with_pii = sum(
        1
        for document in processed_documents
        if document["pii_detected"]
    )

    print("\n" + "=" * 60)
    print(
        f"DOCUMENTS CONTAINING PII: "
        f"{total_with_pii}"
    )
    print("=" * 60)