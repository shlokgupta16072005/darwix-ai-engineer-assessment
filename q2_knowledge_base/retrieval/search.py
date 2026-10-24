from pathlib import Path
from typing import List, Dict
import re
import sys

import numpy as np

# ============================================================
# PROJECT PATH AND IMPORTS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.document_loader import load_all_documents
from ingestion.cleaner import clean_documents
from ingestion.pii_detector import process_documents
from ingestion.chunker import chunk_documents

from retrieval.vector_store import build_vector_store, load_vector_store


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(query_vector, document_matrix):
    """Calculate cosine similarity between a query and document vectors."""
    query_array = query_vector.toarray()[0]
    document_array = document_matrix.toarray()

    query_norm = np.linalg.norm(query_array)
    document_norms = np.linalg.norm(document_array, axis=1)

    if query_norm == 0:
        return np.zeros(len(document_array))

    denominator = document_norms * query_norm
    denominator = np.where(denominator == 0, 1e-10, denominator)

    return (document_array @ query_array) / denominator


# ============================================================
# QUERY CATEGORIES AND INTENT
# ============================================================

def detect_query_categories(query: str) -> List[str]:
    """Detect knowledge-base categories relevant to the query."""
    q = query.lower()
    categories = []

    term_groups = {
        "eligibility": (
            "eligible", "eligibility", "qualify", "qualification",
            "business vintage", "business age", "operated",
            "months old", "years old", "minimum age", "how old",
        ),
        "application_process": (
            "document", "documents", "paperwork", "proof",
            "identity proof", "bank statement", "pan",
            "tax identification", "application", "apply",
        ),
        "product": (
            "loan amount", "minimum loan", "maximum loan", "borrow",
            "loan range", "loan limit", "tenure", "loan product",
        ),
        "objection_handling": (
            "too high", "too expensive", "don't want to share",
            "do not want to share", "don't trust", "do not trust",
            "objection", "what should i say", "how should i respond",
            "customer thinks", "customer says",
        ),
        "faq": (
            "faq", "what is", "how much", "how long",
            "do you have", "how old", "business vintage",
        ),
    }

    for category, terms in term_groups.items():
        if any(term in q for term in terms):
            categories.append(category)

    return categories


def detect_query_intent(query: str) -> str:
    """Identify a specific intent before applying ranking boosts."""
    q = query.lower()

    explicit_vintage_terms = (
        "business vintage", "business-vintage", "business age",
        "how old", "months old", "years old",
        "minimum business age", "how long has my business",
        "business operating", "operated for only one year",
        "one year qualify",
    )

    # Conservative recovery for a malformed ASR transcript.
    # Do not classify ordinary minimum-loan-amount questions as vintage.
    has_asr_vintage_cues = (
        "business" in q
        and "minimum" in q
        and any(term in q for term in ("loan", "required", "requirement"))
        and not any(term in q for term in (
            "loan amount", "minimum loan amount",
            "minimum and maximum loan amount",
        ))
    )

    if (
        any(term in q for term in explicit_vintage_terms)
        or has_asr_vintage_cues
    ):
        return "business_vintage"

    if any(term in q for term in (
        "required document", "documents required", "paperwork",
        "what documents", "which documents", "identity proof",
        "bank statement", "what do i need to apply",
        "documents are needed",
    )):
        return "documents"

    if any(term in q for term in (
        "minimum and maximum loan", "minimum loan",
        "minimum amount", "smallest loan", "least amount",
    )):
        return "minimum_loan_amount"

    if any(term in q for term in (
        "maximum loan", "maximum amount", "largest amount",
        "highest amount", "loan limit",
    )):
        return "maximum_loan_amount"

    if any(term in q for term in (
        "loan amount", "loan range", "how much can i borrow",
        "how much can we borrow",
    )):
        return "loan_amount"

    if any(term in q for term in (
        "tenure", "repayment period", "repayment term",
        "how long to repay", "loan duration",
    )):
        return "loan_tenure"

    if any(term in q for term in (
        "interest rate", "pricing", "too expensive", "too high",
    )):
        return "interest_rate"

    if any(term in q for term in (
        "what should i say", "how should i respond",
        "customer thinks", "customer says", "objection",
    )):
        return "objection_handling"

    return "general"


# ============================================================
# CATEGORY BOOST
# ============================================================

def apply_category_boost(
    query: str,
    similarities: np.ndarray,
    chunks: List[Dict],
) -> np.ndarray:
    """Apply modest boosts to matching document categories."""
    adjusted_scores = similarities.copy()
    categories = detect_query_categories(query)

    boost_values = {
        "eligibility": 0.10,
        "application_process": 0.08,
        "product": 0.08,
        "objection_handling": 0.10,
        "faq": 0.03,
    }

    for index, chunk in enumerate(chunks):
        category = chunk.get("category", "")
        if category in categories:
            adjusted_scores[index] += boost_values.get(category, 0.0)

    return adjusted_scores


# ============================================================
# CONTENT-BASED BOOST
# ============================================================

def apply_content_boost(
    query: str,
    similarities: np.ndarray,
    chunks: List[Dict],
) -> np.ndarray:
    """Boost chunks containing content relevant to the query."""
    adjusted_scores = similarities.copy()
    q = query.lower()

    keyword_groups = {
        "documents": (
            "identity proof", "pan", "tax identification",
            "business proof", "business registration",
            "bank statements", "financial records",
            "required documents",
        ),
        "eligibility": (
            "24 months", "business-vintage", "business vintage",
            "minimum eligibility", "continuous operation",
            "business should have", "business has operated",
        ),
        "loan_amount": (
            "₹2,00,000", "₹25,00,000", "2 lakh", "25 lakh",
            "loan amount", "maximum loan", "minimum loan",
        ),
        "interest_rate": (
            "interest rate", "pricing", "customer-specific",
            "live rate", "live pricing",
        ),
    }

    active_groups = []

    if any(term in q for term in (
        "document", "documents", "paperwork", "proof", "pan",
        "bank statement", "apply", "application",
    )):
        active_groups.append("documents")

    if any(term in q for term in (
        "eligible", "eligibility", "qualify", "business vintage",
        "business age", "operated", "months old", "years old",
        "how old",
    )):
        active_groups.append("eligibility")

    if any(term in q for term in (
        "loan amount", "minimum loan", "maximum loan",
        "borrow", "loan range",
    )):
        active_groups.append("loan_amount")

    if any(term in q for term in (
        "interest rate", "pricing", "too high", "too expensive",
    )):
        active_groups.append("interest_rate")

    for index, chunk in enumerate(chunks):
        text = chunk.get("text", "").lower()

        for group in active_groups:
            matches = sum(
                keyword.lower() in text
                for keyword in keyword_groups[group]
            )

            if matches:
                adjusted_scores[index] += min(matches * 0.025, 0.10)

    return adjusted_scores


# ============================================================
# FAQ QUESTION MATCHING
# ============================================================

def apply_faq_question_boost(
    query: str,
    similarities: np.ndarray,
    chunks: List[Dict],
) -> np.ndarray:
    """Boost FAQ question matches without overwhelming source relevance."""
    adjusted_scores = similarities.copy()
    intent = detect_query_intent(query)
    query_lower = query.lower()

    stop_words = {
        "a", "an", "and", "are", "can", "do", "does", "for",
        "how", "i", "if", "in", "is", "it", "my", "of", "on",
        "the", "to", "what", "when", "where", "which", "who",
        "why", "will", "with", "would", "you", "your",
    }

    query_terms = (
        set(re.findall(r"\b[a-z0-9]+\b", query_lower)) - stop_words
    )

    intent_question_phrases = {
        "business_vintage": (
            "how old must my business be",
            "how old is my business",
            "business vintage",
            "business age",
        ),
        "documents": (
            "what documents are required",
            "which documents are required",
            "what documents do i need",
            "required documents",
        ),
        "minimum_loan_amount": (
            "what is the minimum loan amount",
            "minimum loan amount",
        ),
        "maximum_loan_amount": (
            "what is the maximum loan amount",
            "maximum loan amount",
        ),
        "loan_tenure": (
            "what is the loan tenure",
            "how long is the loan tenure",
            "repayment period",
        ),
        "interest_rate": (
            "what is the interest rate",
            "how is the interest rate",
            "interest rate",
        ),
    }

    for index, chunk in enumerate(chunks):
        if chunk.get("category") != "faq":
            continue

        text = chunk.get("text", "")
        match = re.match(
            r"^\s*Q\d+\.\s*(.*?)(?:\n|$)",
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        question_text = match.group(1).lower()
        # Avoid ranking unrelated FAQ topics for business-vintage queries.
        if intent == "business_vintage" and any(
            term in question_text
            for term in (
                "loan amount",
                "minimum loan",
                "maximum loan",
                "loan tenure",
                "interest rate",
                "documents",
            )
        ):
            adjusted_scores[index] -= 0.20
        question_terms = (
            set(re.findall(r"\b[a-z0-9]+\b", question_text)) - stop_words
        )

        if query_terms and question_terms:
            overlap = len(query_terms & question_terms)
            coverage = overlap / len(query_terms)

            if overlap:
                adjusted_scores[index] += min(0.04, coverage * 0.04)

        phrases = intent_question_phrases.get(intent, ())
        if phrases and any(phrase in question_text for phrase in phrases):
            # Keep FAQ matching useful without overwhelming specific sources.
            adjusted_scores[index] += 0.20

    return adjusted_scores


# ============================================================
# SOURCE-INTENT BOOST
# ============================================================

def apply_source_intent_boost(
    query: str,
    similarities: np.ndarray,
    chunks: List[Dict],
) -> np.ndarray:
    """
    Prefer dedicated sources for objection-handling and specific
    eligibility-decision queries. Document questions rely on lexical,
    category, content, and FAQ-question matching instead of a blanket
    eligibility-source boost.

    These are heuristic ranking boosts, not relevance guarantees.
    """
    adjusted_scores = similarities.copy()
    q = query.lower()
    intent = detect_query_intent(query)

    objection_intent = intent == "objection_handling" or any(
        phrase in q
        for phrase in (
            "what should i say",
            "how should i respond",
            "customer thinks",
            "customer says",
            "objection",
            "too high",
            "too expensive",
        )
    )

    # Apply this only to explicit eligibility decisions, not general
    # questions asking for the minimum business vintage.
    eligibility_decision_intent = (
        intent == "business_vintage"
        and any(
            phrase in q
            for phrase in (
                "qualify",
                "eligible",
                "eligibility",
                "only one year",
                "one year",
                "12 months",
            )
        )
    )

    for index, chunk in enumerate(chunks):
        category = chunk.get("category", "")
        source = Path(
            str(chunk.get("source", "")).replace("\\", "/")
        ).name.lower()

        if objection_intent and (
            category == "objection_handling"
            or source == "objection_handling.txt"
        ):
            adjusted_scores[index] += 0.35

        if eligibility_decision_intent and (
            category == "eligibility"
            or source == "eligibility_rules.pdf"
        ):
            adjusted_scores[index] += 0.25

    return adjusted_scores


# ============================================================
# SEARCH
# ============================================================

def search(query: str, top_k: int = 3) -> List[Dict]:
    """
    Retrieve and rank knowledge-base chunks.

    Pipeline:
        Query -> TF-IDF -> cosine similarity
        -> category boost -> content boost
        -> FAQ question boost -> source-intent boost
        -> ranked results
    """
    if not query or not query.strip():
        return []

    if top_k <= 0:
        return []

    vectorizer, store = load_vector_store()
    chunks = store["chunks"]
    matrix = store["matrix"]

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, matrix)

    adjusted_scores = apply_category_boost(
        query, similarities, chunks
    )

    adjusted_scores = apply_content_boost(
        query, adjusted_scores, chunks
    )

    adjusted_scores = apply_faq_question_boost(
        query, adjusted_scores, chunks
    )

    adjusted_scores = apply_source_intent_boost(
        query, adjusted_scores, chunks
    )

    ranked_indices = np.argsort(adjusted_scores)[::-1]
    results = []

    for index in ranked_indices[:top_k]:
        chunk = chunks[index]

        results.append({
            "rank": len(results) + 1,
            "score": float(adjusted_scores[index]),
            "raw_score": float(similarities[index]),
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "category": chunk["category"],
            "text": chunk["text"],
        })

    return results


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(query: str, results: List[Dict]) -> None:
    """Print retrieval results in a readable format."""
    print("\n" + "=" * 70)
    print("QUERY")
    print("=" * 70)
    print(query)

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    if not results:
        print("\nNo results found.")
        return

    for result in results:
        print(f"\nRank: {result['rank']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Raw TF-IDF Score: {result['raw_score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Category: {result['category']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"\nText:\n{result['text']}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Q2 KNOWLEDGE BASE - RETRIEVAL TEST")
    print("=" * 70)

    try:
        load_vector_store()
        print("\n[OK] Existing vector store found.")

    except FileNotFoundError:
        print("\n[INFO] Vector store not found.")
        print("[INFO] Building vector store...")

        documents = load_all_documents()
        cleaned_documents = clean_documents(documents)
        processed_documents = process_documents(cleaned_documents)
        chunks = chunk_documents(processed_documents)

        build_vector_store(chunks)

    test_queries = [
        "What is the minimum business vintage?",
        "What documents are required for the loan application?",
        "What is the minimum and maximum loan amount?",
        "What should I say if the customer thinks the interest rate is too high?",
        "Can a business that has operated for only one year qualify?",
    ]

    for query in test_queries:
        results = search(query, top_k=3)
        print_results(query, results)
