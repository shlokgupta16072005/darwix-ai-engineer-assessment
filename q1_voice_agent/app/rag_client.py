"""
Adapter between the Q1 conversation agent and the Q2 RAG system.

This module keeps the existing Q1 conversation interface unchanged
while using the grounded Q2 knowledge-base answer layer.
"""

from typing import Optional

from q2_knowledge_base.retrieval.rag_answer import answer_question


class RAGClient:
    """Client-compatible adapter that uses the Q2 RAG pipeline."""

    def __init__(self, top_k: int = 3) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self.top_k = top_k

    def generate_response(
        self,
        user_message: str,
        conversation_context: Optional[str] = None,
    ) -> str:
        """
        Generate a grounded response using the Q2 knowledge base.

        Conversation context is accepted for compatibility with the
        existing ConversationAgent interface.
        """

        user_message = user_message.strip()

        if not user_message:
            raise ValueError("user_message cannot be empty.")

        result = answer_question(
            question=user_message,
            top_k=self.top_k,
        )

        answer = result.get("answer", "").strip()

        if not answer:
            raise RuntimeError(
                "The RAG system returned an empty answer."
            )

        return answer