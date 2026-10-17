import pytest

try:
    from q2_knowledge_base.retrieval.rag_answer import fallback_answer
except ModuleNotFoundError:
    from retrieval.rag_answer import fallback_answer

@pytest.fixture
def results():
    return [
        {
            "source": "objection_handling.txt",
            "category": "objection_handling",
            "score": 0.8,
            "text": (
                "I don't have all my documents. That's okay for the "
                "initial conversation. Let me identify which information "
                "you already have and which items may still be required. "
                "Additional documents can be requested during assessment. "
                "Recent financial records may be requested as part of "
                "the assessment."
            ),
        },
        {
            "source": "faq.txt",
            "category": "faq",
            "score": 0.7,
            "text": (
                "Final approval is subject to verification and internal "
                "assessment. The prototype knowledge base does not contain "
                "a live rate table. Pricing is customer-specific."
            ),
        },
    ]


@pytest.mark.parametrize(
    "question",
    [
        "I don't have all my documents.",
        "I am missing some paperwork.",
        "I don't have my bank statement right now.",
    ],
)
def test_incomplete_documents_get_reassuring_guidance(question, results):
    answer = fallback_answer(question, results).lower()

    assert "additional documents" in answer or "information" in answer
    assert "reject" not in answer


def test_bank_statement_objection_is_acknowledged(results):
    answer = fallback_answer(
        "I don't want to share my bank statement.",
        results,
    ).lower()

    assert "understand" in answer
    assert "financial records" in answer or "documentation" in answer
    assert "human assistance" in answer or "human" in answer


def test_live_interest_rate_is_not_invented(results):
    answer = fallback_answer(
        "What is today's live interest rate?",
        results,
    ).lower()

    assert "does not provide a live" in answer
    assert "human follow-up" in answer


def test_guaranteed_approval_is_not_promised(results):
    answer = fallback_answer(
        "Can you guarantee approval?",
        results,
    ).lower()

    assert "verification" in answer
    assert "should not be promised" in answer


def test_low_confidence_retrieval_uses_safe_fallback():
    answer = fallback_answer(
        "Is my home-based business eligible?",
        [{"score": 0.01, "text": "Unrelated content."}],
    ).lower()

    assert "could not find this information" in answer
    assert "human" in answer


def test_empty_retrieval_uses_safe_fallback():
    answer = fallback_answer("How do I apply?", [])

    assert "could not find relevant information" in answer
    assert "human representative" in answer
