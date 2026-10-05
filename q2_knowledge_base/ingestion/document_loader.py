from pathlib import Path
from typing import List, Dict
import csv

from pypdf import PdfReader


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF file.
    """
    reader = PdfReader(str(file_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def load_text(file_path: Path) -> str:
    """
    Read a plain-text file using UTF-8 encoding.
    """
    return file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def load_csv(file_path: Path) -> str:
    """
    Read a CSV file and convert each row into a readable text representation.

    Note:
    The application CSV is currently treated as test/application data.
    Later, build_kb.py will decide whether it should enter the reusable
    knowledge base.
    """
    rows = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            row_text = " | ".join(
                f"{key}: {value}"
                for key, value in row.items()
                if value is not None
            )

            rows.append(row_text)

    return "\n".join(rows)


def load_document(file_path: Path) -> str:
    """
    Load a single document based on its file extension.
    """
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension == ".txt":
        return load_text(file_path)

    if extension == ".csv":
        return load_csv(file_path)

    raise ValueError(
        f"Unsupported file type: {file_path.suffix}"
    )


def get_category(file_name: str) -> str:
    """
    Assign a simple category based on the source filename.
    """
    name = file_name.lower()

    if "eligibility" in name:
        return "eligibility"

    if "loan_product" in name:
        return "product"

    if "faq" in name:
        return "faq"

    if "objection" in name:
        return "objection_handling"

    if "application_process" in name:
        return "application_process"

    if "sample_application" in name:
        return "application_data"

    return "general"


def load_all_documents() -> List[Dict]:
    """
    Load all supported documents from the data directory.

    Returns:
        A list of dictionaries containing:
        - source
        - file_type
        - category
        - text
    """

    documents = []

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Data directory not found: {DATA_DIR}"
        )

    supported_extensions = {".pdf", ".txt", ".csv"}

    for file_path in sorted(DATA_DIR.iterdir()):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in supported_extensions:
            continue

        try:
            text = load_document(file_path)

            documents.append(
                {
                    "source": file_path.name,
                    "file_type": file_path.suffix.lower(),
                    "category": get_category(file_path.name),
                    "text": text,
                }
            )

            print(
                f"[LOADED] {file_path.name} "
                f"({len(text):,} characters)"
            )

        except Exception as error:
            print(
                f"[ERROR] Could not load "
                f"{file_path.name}: {error}"
            )

    return documents


if __name__ == "__main__":

    print("=" * 60)
    print("Q2 KNOWLEDGE BASE - DOCUMENT LOADER")
    print("=" * 60)

    documents = load_all_documents()

    print("\n" + "=" * 60)
    print(f"TOTAL DOCUMENTS LOADED: {len(documents)}")
    print("=" * 60)

    for document in documents:

        print("\nSource:", document["source"])
        print("Type:", document["file_type"])
        print("Category:", document["category"])

        preview = document["text"][:300]
        preview = preview.replace("\n", " ")

        print("Preview:", preview)