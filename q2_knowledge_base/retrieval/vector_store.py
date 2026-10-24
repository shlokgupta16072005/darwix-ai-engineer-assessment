
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Dict, List
import json
import sys

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

VECTORIZER_PATH = VECTOR_STORE_DIR / "tfidf_vectorizer.joblib"
CHUNKS_PATH = VECTOR_STORE_DIR / "chunks.joblib"

VECTOR_STORE_SCHEMA_VERSION = "1.0"

VECTORIZER_CONFIG = {
    "type": "TfidfVectorizer",
    "lowercase": True,
    "ngram_range": [1, 2],
    "max_features": 5000,
}


def _get_source_name(chunk: Dict) -> str:
    """Extract a source filename from common chunk metadata fields."""

    for key in ("source", "source_file", "filename", "document_name"):
        value = chunk.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    metadata = chunk.get("metadata")

    if isinstance(metadata, dict):
        for key in ("source", "source_file", "filename", "document_name"):
            value = metadata.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

    return "unknown"


def create_build_metadata(chunks: List[Dict]) -> Dict:
    """
    Create reproducibility and audit metadata for indexed chunks.

    The hash covers the ordered source names and chunk text.
    It is a content fingerprint, not a security signature.
    """

    fingerprint_records = [
        {
            "source": _get_source_name(chunk),
            "text": chunk.get("text", ""),
        }
        for chunk in chunks
    ]

    canonical_content = json.dumps(
        fingerprint_records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    content_hash = sha256(
        canonical_content.encode("utf-8")
    ).hexdigest()

    source_documents = sorted(
        {
            _get_source_name(chunk)
            for chunk in chunks
        }
    )

    return {
        "schema_version": VECTOR_STORE_SCHEMA_VERSION,
        "build_timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "content_hash_sha256": content_hash,
        "indexed_chunk_count": len(chunks),
        "source_documents": source_documents,
        "embedding_method": "TF-IDF",
        "vectorizer_config": VECTORIZER_CONFIG.copy(),
    }


def build_vector_store(chunks: List[Dict]) -> None:
    """
    Build a local TF-IDF vector store from knowledge-base chunks.

    Application/customer data is excluded from the searchable
    knowledge base.
    """

    knowledge_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("category") != "application_data"
    ]

    if not knowledge_chunks:
        raise ValueError(
            "No knowledge-base chunks available."
        )

    for index, chunk in enumerate(knowledge_chunks):
        if not isinstance(chunk.get("text"), str):
            raise ValueError(
                f"Chunk at index {index} has missing or invalid text."
            )

        if not chunk["text"].strip():
            raise ValueError(
                f"Chunk at index {index} has empty text."
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

    metadata = create_build_metadata(knowledge_chunks)

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH,
    )

    joblib.dump(
        {
            "chunks": knowledge_chunks,
            "matrix": matrix,
            "metadata": metadata,
        },
        CHUNKS_PATH,
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
        f"[VECTOR STORE] "
        f"Source documents: {len(metadata['source_documents'])}"
    )

    print(
        f"[VECTOR STORE] "
        f"Content SHA-256: {metadata['content_hash_sha256']}"
    )

    print(
        f"[VECTOR STORE] "
        f"Build timestamp (UTC): {metadata['build_timestamp_utc']}"
    )

    print(
        f"[VECTOR STORE] Saved to: "
        f"{VECTOR_STORE_DIR}"
    )


def load_vector_store():
    """
    Load the saved vectorizer and chunk matrix.

    Older stores without metadata remain loadable. Their metadata
    is reported as unavailable rather than fabricated.
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

    vectorizer = joblib.load(VECTORIZER_PATH)
    store = joblib.load(CHUNKS_PATH)

    if not isinstance(store, dict):
        raise ValueError(
            "Invalid vector store format: expected a dictionary."
        )

    if "chunks" not in store or "matrix" not in store:
        raise ValueError(
            "Invalid vector store: 'chunks' or 'matrix' is missing."
        )

    # Backward compatibility for stores built before metadata existed.
    store.setdefault("metadata", None)

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
    cleaned_documents = clean_documents(documents)

    print("\nChecking for PII...\n")
    processed_documents = process_documents(cleaned_documents)

    print("\nCreating chunks...\n")
    chunks = chunk_documents(processed_documents)

    print("\nBuilding vector store...\n")
    build_vector_store(chunks)

    print("\n" + "=" * 60)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 60)
