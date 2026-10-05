from pathlib import Path
from typing import List, Dict

import sys
import numpy as np


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from ingestion.document_loader import load_all_documents
from ingestion.cleaner import clean_documents
from ingestion.pii_detector import process_documents
from ingestion.chunker import chunk_documents

from retrieval.vector_store import (
    build_vector_store,
    load_vector_store,
)


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    query_vector,
    document_matrix
):
    """
    Calculate cosine similarity between a query vector
    and all document vectors.
    """

    query_array = query_vector.toarray()[0]

    document_array = document_matrix.toarray()

    query_norm = np.linalg.norm(
        query_array
    )

    document_norms = np.linalg.norm(
        document_array,
        axis=1
    )

    if query_norm == 0:
        return np.zeros(
            len(document_array)
        )

    denominator = (
        document_norms * query_norm
    )

    denominator = np.where(
        denominator == 0,
        1e-10,
        denominator
    )

    return (
        document_array @ query_array
    ) / denominator


# ============================================================
# QUERY CATEGORY DETECTION
# ============================================================

def detect_query_categories(
    query: str
) -> List[str]:
    """
    Detect the likely knowledge-base category
    required to answer the query.

    This is not a replacement for TF-IDF.
    It is a small rule-based relevance adjustment
    used for this prototype.
    """

    query_lower = query.lower()

    categories = []

    # --------------------------------------------------------
    # Eligibility
    # --------------------------------------------------------

    eligibility_terms = [
        "eligible",
        "eligibility",
        "qualify",
        "qualification",
        "business vintage",
        "business age",
        "operated",
        "months old",
        "years old",
        "minimum age",
        "how old",
    ]

    if any(
        term in query_lower
        for term in eligibility_terms
    ):
        categories.append("eligibility")

    # --------------------------------------------------------
    # Documents / application process
    # --------------------------------------------------------

    document_terms = [
        "document",
        "documents",
        "required documents",
        "paperwork",
        "proof",
        "identity proof",
        "bank statement",
        "pan",
        "tax identification",
        "application",
        "apply",
    ]

    if any(
        term in query_lower
        for term in document_terms
    ):
        categories.append("application_process")

    # --------------------------------------------------------
    # Product / loan amount
    # --------------------------------------------------------

    product_terms = [
        "loan amount",
        "minimum loan",
        "maximum loan",
        "borrow",
        "loan range",
        "loan limit",
        "tenure",
        "loan product",
    ]

    if any(
        term in query_lower
        for term in product_terms
    ):
        categories.append("product")

    # --------------------------------------------------------
    # Objection handling
    # --------------------------------------------------------

    objection_terms = [
        "too high",
        "too expensive",
        "don't want to share",
        "do not want to share",
        "don't trust",
        "do not trust",
        "objection",
        "what should i say",
        "how should i respond",
        "customer thinks",
        "customer says",
    ]

    if any(
        term in query_lower
        for term in objection_terms
    ):
        categories.append("objection_handling")

    # --------------------------------------------------------
    # FAQ
    # --------------------------------------------------------

    faq_terms = [
        "faq",
        "what is",
        "how much",
        "how long",
        "do you have",
    ]

    if any(
        term in query_lower
        for term in faq_terms
    ):
        categories.append("faq")

    return categories


# ============================================================
# CATEGORY BOOST
# ============================================================

def apply_category_boost(
    query: str,
    similarities: np.ndarray,
    chunks: List[Dict]
) -> np.ndarray:
    """
    Apply small relevance boosts based on the detected
    type of query.

    TF-IDF remains the primary retrieval mechanism.

    The boosts are deliberately small so that a completely
    irrelevant chunk does not become relevant only because
    of its category.
    """

    adjusted_scores = similarities.copy()

    categories = detect_query_categories(
        query
    )

    # --------------------------------------------------------
    # Boost values
    # --------------------------------------------------------

    boost_values = {
        "eligibility": 0.10,
        "application_process": 0.08,
        "product": 0.08,
        "objection_handling": 0.10,
        "faq": 0.03,
    }

    # --------------------------------------------------------
    # Apply category boosts
    # --------------------------------------------------------

    for index, chunk in enumerate(chunks):

        category = chunk.get(
            "category",
            ""
        )

        if category in categories:

            adjusted_scores[index] += (
                boost_values.get(
                    category,
                    0.0
                )
            )

    return adjusted_scores


# ============================================================
# CONTENT-BASED BOOST
# ============================================================

def apply_content_boost(
    query: str,
    similarities: np.ndarray,
    chunks: List[Dict]
) -> np.ndarray:
    """
    Apply very small keyword-based boosts when the retrieved
    chunk actually contains important terms from the query.

    This helps cases where the correct answer exists inside
    a chunk but TF-IDF ranks another related chunk higher.
    """

    adjusted_scores = similarities.copy()

    query_lower = query.lower()

    # --------------------------------------------------------
    # Keyword groups
    # --------------------------------------------------------

    keyword_groups = {

        "documents": [
            "identity proof",
            "pan",
            "tax identification",
            "business proof",
            "business registration",
            "bank statements",
            "financial records",
            "required documents",
        ],

        "eligibility": [
            "24 months",
            "business-vintage",
            "business vintage",
            "minimum eligibility",
            "continuous operation",
        ],

        "loan_amount": [
            "₹2 lakh",
            "₹25 lakh",
            "2 lakh",
            "25 lakh",
            "loan amount",
            "maximum loan",
            "minimum loan",
        ],

        "interest_rate": [
            "interest rate",
            "pricing",
            "customer-specific",
            "live rate",
            "live pricing",
        ],
    }

    # --------------------------------------------------------
    # Determine relevant keyword group
    # --------------------------------------------------------

    active_groups = []

    if any(
        term in query_lower
        for term in [
            "document",
            "documents",
            "paperwork",
            "proof",
            "pan",
            "bank statement",
            "apply",
            "application",
        ]
    ):
        active_groups.append(
            "documents"
        )

    if any(
        term in query_lower
        for term in [
            "eligible",
            "eligibility",
            "qualify",
            "business vintage",
            "business age",
            "operated",
            "months old",
            "years old",
        ]
    ):
        active_groups.append(
            "eligibility"
        )

    if any(
        term in query_lower
        for term in [
            "loan amount",
            "minimum loan",
            "maximum loan",
            "borrow",
            "loan range",
        ]
    ):
        active_groups.append(
            "loan_amount"
        )

    if any(
        term in query_lower
        for term in [
            "interest rate",
            "pricing",
            "too high",
            "too expensive",
        ]
    ):
        active_groups.append(
            "interest_rate"
        )

    # --------------------------------------------------------
    # Apply content boost
    # --------------------------------------------------------

    for index, chunk in enumerate(chunks):

        text = chunk.get(
            "text",
            ""
        ).lower()

        for group in active_groups:

            keywords = keyword_groups[
                group
            ]

            matches = sum(
                1
                for keyword in keywords
                if keyword in text
            )

            if matches > 0:

                # Small boost per matched keyword.
                # Maximum content boost is capped.
                boost = min(
                    matches * 0.025,
                    0.10
                )

                adjusted_scores[index] += boost

    return adjusted_scores


# ============================================================
# SEARCH
# ============================================================

def search(
    query: str,
    top_k: int = 3
) -> List[Dict]:
    """
    Search the knowledge base.

    Retrieval pipeline:

        Query
          ↓
        TF-IDF vector
          ↓
        Cosine similarity
          ↓
        Category relevance boost
          ↓
        Content keyword boost
          ↓
        Ranked results

    TF-IDF remains the primary retrieval mechanism.
    """

    if not query.strip():
        return []

    # --------------------------------------------------------
    # Load vector store
    # --------------------------------------------------------

    vectorizer, store = load_vector_store()

    chunks = store["chunks"]

    matrix = store["matrix"]

    # --------------------------------------------------------
    # Convert query to TF-IDF
    # --------------------------------------------------------

    query_vector = vectorizer.transform(
        [query]
    )

    # --------------------------------------------------------
    # Calculate similarity
    # --------------------------------------------------------

    similarities = cosine_similarity(
        query_vector,
        matrix
    )

    # --------------------------------------------------------
    # Category-aware boost
    # --------------------------------------------------------

    adjusted_scores = apply_category_boost(
        query,
        similarities,
        chunks
    )

    # --------------------------------------------------------
    # Content-aware boost
    # --------------------------------------------------------

    adjusted_scores = apply_content_boost(
        query,
        adjusted_scores,
        chunks
    )

    # --------------------------------------------------------
    # Rank results
    # --------------------------------------------------------

    ranked_indices = np.argsort(
        adjusted_scores
    )[::-1]

    # --------------------------------------------------------
    # Build results
    # --------------------------------------------------------

    results = []

    for index in ranked_indices[:top_k]:

        chunk = chunks[index]

        results.append(
            {
                "rank": len(results) + 1,
                "score": float(
                    adjusted_scores[index]
                ),
                "raw_score": float(
                    similarities[index]
                ),
                "chunk_id": chunk[
                    "chunk_id"
                ],
                "source": chunk[
                    "source"
                ],
                "category": chunk[
                    "category"
                ],
                "text": chunk[
                    "text"
                ],
            }
        )

    return results


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    query: str,
    results: List[Dict]
) -> None:
    """
    Print retrieval results in a readable format.
    """

    print(
        "\n" + "=" * 70
    )

    print(
        "QUERY"
    )

    print(
        "=" * 70
    )

    print(
        query
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "RETRIEVAL RESULTS"
    )

    print(
        "=" * 70
    )

    if not results:

        print(
            "\nNo results found."
        )

        return

    for result in results:

        print(
            f"\nRank: {result['rank']}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Raw TF-IDF Score: "
            f"{result['raw_score']:.4f}"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Category: {result['category']}"
        )

        print(
            f"Chunk ID: {result['chunk_id']}"
        )

        print(
            f"\nText:\n{result['text']}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 70
    )

    print(
        "Q2 KNOWLEDGE BASE - RETRIEVAL TEST"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Check vector store
    # --------------------------------------------------------

    try:

        load_vector_store()

        print(
            "\n[OK] Existing vector store found."
        )

    except FileNotFoundError:

        print(
            "\n[INFO] Vector store not found."
        )

        print(
            "[INFO] Building vector store..."
        )

        # ----------------------------------------------------
        # Load documents
        # ----------------------------------------------------

        documents = load_all_documents()

        # ----------------------------------------------------
        # Clean documents
        # ----------------------------------------------------

        cleaned_documents = clean_documents(
            documents
        )

        # ----------------------------------------------------
        # PII processing
        # ----------------------------------------------------

        processed_documents = process_documents(
            cleaned_documents
        )

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        chunks = chunk_documents(
            processed_documents
        )

        # ----------------------------------------------------
        # Build vector store
        # ----------------------------------------------------

        build_vector_store(
            chunks
        )

    # --------------------------------------------------------
    # Required Q2 retrieval tests
    # --------------------------------------------------------

    test_queries = [

        "What is the minimum business vintage?",

        "What documents are required for the loan application?",

        "What is the minimum and maximum loan amount?",

        "What should I say if the customer thinks the interest rate is too high?",

        "Can a business that has operated for only one year qualify?",
    ]

    # --------------------------------------------------------
    # Run tests
    # --------------------------------------------------------

    for query in test_queries:

        results = search(
            query,
            top_k=3
        )

        print_results(
            query,
            results
        )