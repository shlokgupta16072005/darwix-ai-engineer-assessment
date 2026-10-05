from pathlib import Path
from typing import Dict, List

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

VECTORIZER_PATH = VECTOR_STORE_DIR / "tfidf_vectorizer.joblib"
CHUNKS_PATH = VECTOR_STORE_DIR / "chunks.joblib"


def build_vector_store(chunks: List[Dict]) -> None:
    """
    Build a local TF-IDF vector store from knowledge-base chunks.

    Application/customer data is excluded from the searchable
    knowledge base.
    """

    knowledge_chunks = [
        chunk
        for chunk in chunks
        if chunk["category"] != "application_data"
    ]

    if not knowledge_chunks:
        raise ValueError(
            "No knowledge-base chunks available."
        )

    texts = [
        chunk["text"]
        for chunk in knowledge_chunks
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=5000,
    )

    matrix = vectorizer.fit_transform(texts)

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH
    )

    joblib.dump(
        {
            "chunks": knowledge_chunks,
            "matrix": matrix,
        },
        CHUNKS_PATH
    )

    print(
        f"[VECTOR STORE] "
        f"{len(knowledge_chunks)} chunks indexed"
    )

    print(
        f"[VECTOR STORE] "
        f"Vocabulary size: {len(vectorizer.vocabulary_)}"
    )

    print(
        f"[VECTOR STORE] Saved to: "
        f"{VECTOR_STORE_DIR}"
    )


def load_vector_store():
    """
    Load the saved vectorizer and chunk matrix.
    """

    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            "TF-IDF vectorizer not found. "
            "Build the vector store first."
        )

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            "Chunk index not found. "
            "Build the vector store first."
        )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    store = joblib.load(
        CHUNKS_PATH
    )

    return vectorizer, store


if __name__ == "__main__":

    from ingestion.document_loader import load_all_documents
    from ingestion.cleaner import clean_documents
    from ingestion.pii_detector import process_documents
    from ingestion.chunker import chunk_documents

    print("=" * 60)
    print("Q2 KNOWLEDGE BASE - VECTOR STORE")
    print("=" * 60)

    print("\nLoading documents...\n")

    documents = load_all_documents()

    print("\nCleaning documents...\n")

    cleaned_documents = clean_documents(
        documents
    )

    print("\nChecking for PII...\n")

    processed_documents = process_documents(
        cleaned_documents
    )

    print("\nCreating chunks...\n")

    chunks = chunk_documents(
        processed_documents
    )

    print("\nBuilding vector store...\n")

    build_vector_store(chunks)

    print("\n" + "=" * 60)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 60)