import pytest

from q1_voice_agent.app import rag_client
from q1_voice_agent.app.rag_client import RAGClient


@pytest.mark.parametrize(
    "message",
    [
        "Can I speak to a human representative?",
        "I want to talk to a person.",
        "Please call me back.",
        "I need human assistance.",
    ],
)
def test_explicit_human_request_records_escalation(message, monkeypatch):
    def unexpected_rag_call(**kwargs):
        pytest.fail("Human requests should be handled before RAG.")

    monkeypatch.setattr(
        rag_client,
        "answer_question",
        unexpected_rag_call,
    )

    client = RAGClient()
    response = client.generate_response(message)

    assert "human follow-up" in response.lower()
    assert client.last_result["mode"] == "human_escalation_requested"
    assert client.last_result["escalation_requested"] is True
    assert client.last_result["handoff_completed"] is False
    assert client.last_result["escalation_reason"] == (
        "explicit_customer_request"
    )


def test_regular_question_uses_rag_and_preserves_sources(monkeypatch):
    expected = {
        "answer": "The stated minimum business vintage is 24 months.",
        "mode": "local_fallback",
        "sources": [{"source": "eligibility_rules.pdf", "score": 0.8}],
    }
    calls = []

    def fake_answer_question(question, top_k):
        calls.append((question, top_k))
        return expected

    monkeypatch.setattr(
        rag_client,
        "answer_question",
        fake_answer_question,
    )

    client = RAGClient(top_k=2)
    response = client.generate_response(
        "How old must my business be?"
    )

    assert response == expected["answer"]
    assert calls == [("How old must my business be?", 2)]
    assert client.last_result == expected


def test_empty_message_is_rejected():
    client = RAGClient()

    with pytest.raises(ValueError, match="cannot be empty"):
        client.generate_response("   ")


def test_empty_rag_answer_is_rejected(monkeypatch):
    monkeypatch.setattr(
        rag_client,
        "answer_question",
        lambda **kwargs: {"answer": "   ", "sources": []},
    )

    client = RAGClient()

    with pytest.raises(RuntimeError, match="empty answer"):
        client.generate_response("How do I apply?")
import pytest

from q1_voice_agent.app import rag_client
from q1_voice_agent.app.rag_client import RAGClient


@pytest.mark.parametrize(
    "message",
    [
        "I don't have all my documents.",
        "I am missing some paperwork.",
        "I don't have my bank statement right now.",
    ],
)
def test_incomplete_documents_are_sent_to_grounded_rag(
    message,
    monkeypatch,
):
    expected = {
        "answer": (
            "That's okay for the initial conversation. "
            "Let me identify which information you already have "
            "and which items may still be required. "
            "Additional documents can be requested during assessment."
        ),
        "mode": "local_fallback",
        "sources": [{"source": "objection_handling.txt", "score": 0.8}],
    }
    calls = []

    def fake_answer_question(question, top_k):
        calls.append(question)
        return expected

    monkeypatch.setattr(
        rag_client,
        "answer_question",
        fake_answer_question,
    )

    client = RAGClient()
    response = client.generate_response(message)

    assert calls == [message]
    assert "additional documents" in response.lower()
    assert client.last_result["sources"] == expected["sources"]
    assert client.last_result["mode"] == "local_fallback"


def test_human_request_does_not_claim_callback_was_placed():
    client = RAGClient()
    response = client.generate_response(
        "Can I speak to a human representative?"
    )

    assert client.last_result["escalation_requested"] is True
    assert client.last_result["handoff_completed"] is False
    assert "does not automatically place a callback" in response.lower()
