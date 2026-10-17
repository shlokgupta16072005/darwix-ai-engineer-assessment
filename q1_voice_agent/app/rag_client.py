"""
Adapter between the Q1 conversation agent and the Q2 RAG system.
"""

from typing import Any, Dict, Optional

from q2_knowledge_base.retrieval.rag_answer import answer_question


class RAGClient:
    """Client-compatible adapter using the Q2 RAG pipeline."""

    HUMAN_REQUEST_PHRASES = (
        "speak to a human",
        "talk to a human",
        "speak to a person",
        "talk to a person",
        "human representative",
        "real person",
        "human assistance",
        "human agent",
        "request a callback",
        "arrange a callback",
        "call me back",
        "call back",
        "callback",
    )

    def __init__(self, top_k: int = 3) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self.top_k = top_k
        self.last_result: Dict[str, Any] = {}

    @classmethod
    def _is_explicit_human_request(cls, message: str) -> bool:
        """Detect explicit human or callback requests."""
        normalized = " ".join(message.lower().split())
        return any(
            phrase in normalized
            for phrase in cls.HUMAN_REQUEST_PHRASES
        )

    def generate_response(
        self,
        user_message: str,
        conversation_context: Optional[str] = None,
    ) -> str:
        """Return a grounded answer and retain its evidence metadata."""

        user_message = user_message.strip()

        if not user_message:
            raise ValueError("user_message cannot be empty.")

        if self._is_explicit_human_request(user_message):
            answer = (
                "I can flag your request for human follow-up. "
                "This prototype does not automatically place a "
                "callback or connect you to a representative."
            )
            self.last_result = {
                "answer": answer,
                "mode": "human_escalation_requested",
                "sources": [],
                "escalation_requested": True,
                "escalation_reason": "explicit_customer_request",
                "handoff_completed": False,
            }
            return answer

        result = answer_question(
            question=user_message,
            top_k=self.top_k,
        )

        answer = result.get("answer", "").strip()

        if not answer:
            raise RuntimeError(
                "The RAG system returned an empty answer."
            )

        self.last_result = result
        return answer
