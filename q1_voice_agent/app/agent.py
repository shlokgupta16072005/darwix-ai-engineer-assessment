"""
Conversation agent for the Q1 voice assistant.

This module manages conversation state and connects the
text-generation client with the voice-agent workflow.

The agent is deliberately kept independent of microphone
and speaker hardware so it can be tested without API calls
or audio devices.
"""

from dataclasses import dataclass, field
from typing import List, Tuple

from q1_voice_agent.app.openai_client import OpenAIClient


@dataclass
class ConversationAgent:
    """
    Manage a conversation with the voice assistant.

    Parameters
    ----------
    client:
        OpenAIClient instance used for response generation.

    max_turns:
        Maximum number of user/assistant exchanges retained
        in memory.
    """

    client: OpenAIClient
    max_turns: int = 20
    history: List[Tuple[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.max_turns <= 0:
            raise ValueError("max_turns must be greater than zero.")

    def _build_context(self) -> str:
        """Build a plain-text representation of conversation history."""

        if not self.history:
            return ""

        lines = []

        for user_message, assistant_message in self.history:
            lines.append(f"User: {user_message}")
            lines.append(f"Assistant: {assistant_message}")

        return "\n".join(lines)

    def respond(self, user_message: str) -> str:
        """
        Generate an assistant response and update conversation history.

        Parameters
        ----------
        user_message:
            Latest user message.

        Returns
        -------
        str
            Assistant response.
        """

        user_message = user_message.strip()

        if not user_message:
            raise ValueError("user_message cannot be empty.")

        context = self._build_context()

        response = self.client.generate_response(
            user_message=user_message,
            conversation_context=context,
        )

        response = response.strip()

        if not response:
            raise RuntimeError(
                "The assistant returned an empty response."
            )

        self.history.append(
            (user_message, response)
        )

        # Keep only the most recent exchanges.
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]

        return response

    def reset(self) -> None:
        """Clear the current conversation history."""

        self.history.clear()

    def get_history(self) -> List[Tuple[str, str]]:
        """
        Return a copy of the conversation history.

        Returns
        -------
        list
            List containing (user_message, assistant_response) tuples.
        """

        return list(self.history)

    def turn_count(self) -> int:
        """Return the number of stored conversation exchanges."""

        return len(self.history)