import pytest

try:
    from q2_knowledge_base.retrieval import rag_answer
except ModuleNotFoundError:
    from retrieval import rag_answer


def test_generated_answer_cannot_confuse_business_vintage_with_loan_tenure(
    monkeypatch,
):
    results = [
        {
            "source": "eligibility_rules.pdf",
            "category": "eligibility",
            "score": 0.9,
            "text": (
                "The business must have operated continuously "
                "for at least 24 months."
            ),
        },
        {
            "source": "loan_products.pdf",
            "category": "loan_product",
            "score": 0.8,
            "text": (
                "The available loan repayment tenure is "
                "12 to 60 months."
            ),
        },
    ]

    monkeypatch.setattr(
        rag_answer,
        "search",
        lambda question, top_k=3: results,
    )

    monkeypatch.setattr(
        rag_answer,
        "generate_openai_answer",
        lambda question, results: (
            "The minimum business vintage is 60 months."
        ),
    )

    response = rag_answer.answer_question(
        "What is the minimum business vintage?"
    )

    assert "24 months" in response["answer"].lower()
    assert "60 months" not in response["answer"].lower()
