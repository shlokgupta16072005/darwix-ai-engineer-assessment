import numpy as np

from retrieval.search import (
    detect_query_categories,
    apply_category_boost,
    apply_content_boost,
    cosine_similarity,
    search,
)


def test_detect_query_categories_for_eligibility():
    categories = detect_query_categories(
        "Can a business that operated for one year qualify?"
    )
    assert "eligibility" in categories


def test_detect_query_categories_for_objection():
    categories = detect_query_categories(
        "What should I say if the customer thinks the interest rate is too high?"
    )
    assert "objection_handling" in categories


def test_category_boost_increases_matching_category():
    chunks = [
        {"category": "eligibility"},
        {"category": "product"},
    ]
    original = np.array([0.2, 0.2])

    adjusted = apply_category_boost(
        "Can this business qualify?",
        original,
        chunks,
    )

    assert adjusted[0] > original[0]
    assert adjusted[1] == original[1]


def test_content_boost_increases_relevant_chunk():
    chunks = [
        {"text": "The minimum loan amount is 2 lakh and maximum is 25 lakh."},
        {"text": "The business must operate continuously for 24 months."},
    ]
    original = np.array([0.2, 0.2])

    adjusted = apply_content_boost(
        "What is the minimum and maximum loan amount?",
        original,
        chunks,
    )

    assert adjusted[0] > original[0]
    assert adjusted[1] == original[1]


def test_cosine_similarity_returns_zero_for_zero_query():
    from scipy.sparse import csr_matrix

    query = csr_matrix([[0.0, 0.0]])
    documents = csr_matrix([[1.0, 0.0], [0.0, 1.0]])

    scores = cosine_similarity(query, documents)

    assert np.allclose(scores, [0.0, 0.0])


def test_search_returns_empty_for_blank_query():
    assert search("   ") == []

def test_business_vintage_query_ranks_relevant_faq_first():
    results = search("What is the minimum business vintage?", top_k=3)

    assert results, "Search should return results"

    top_result = results[0]
    top_text = top_result["text"].lower()

    assert "24 months" in top_text
    assert (
        "business" in top_text
        and (
            "operation" in top_text
            or "old must my business be" in top_text
            or "business vintage" in top_text
        )
    )
