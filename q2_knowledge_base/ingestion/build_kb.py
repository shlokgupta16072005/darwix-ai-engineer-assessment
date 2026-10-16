"""Build the Q2 knowledge base and searchable TF-IDF index."""

from pathlib import Path
import sys

# Ensure imports work when this file is executed directly.
Q2_ROOT = Path(__file__).resolve().parent.parent
if str(Q2_ROOT) not in sys.path:
    sys.path.insert(0, str(Q2_ROOT))

from ingestion.document_loader import load_all_documents
from ingestion.cleaner import clean_documents
from ingestion.pii_detector import process_documents
from ingestion.chunker import chunk_documents
from retrieval.vector_store import build_vector_store


def main():
    print("=" * 60)
    print("Q2 KNOWLEDGE BASE BUILD")
    print("=" * 60)

    documents = load_all_documents()
    print(f"Loaded {len(documents)} documents")

    cleaned_documents = clean_documents(documents)
    processed_documents = process_documents(cleaned_documents)
    chunks = chunk_documents(processed_documents)

    print(f"Created {len(chunks)} chunks")
    build_vector_store(chunks)

    print("Knowledge base build complete.")


if __name__ == "__main__":
    main()
