"""
Local demo client for the Q1 voice agent.

This client provides deterministic offline responses so that the
conversation-agent workflow can be tested without consuming
OpenAI API credits.

The real OpenAI integration remains available through
OpenAIClient in openai_client.py.
"""


class DemoClient:
    """Simple offline text-generation client for demonstration/testing."""

    def __init__(self) -> None:
        self.model = "local-demo"

    def generate_response(
        self,
        user_message: str,
        conversation_context: str | None = None,
    ) -> str:
        """
        Generate a deterministic local response.

        This method follows the same interface used by ConversationAgent,
        allowing the agent to operate without an external API call.
        """

        message = user_message.strip()

        if not message:
            raise ValueError("user_message cannot be empty.")

        lowered = message.lower()

        if any(word in lowered for word in ["hello", "hi", "hey"]):
            return (
                "Hello! I am the Darwix Voice Assistant demo. "
                "How can I help you today?"
            )

        if "loan" in lowered:
            return (
                "I can help with general loan-related questions. "
                "For this local demo, responses are generated without "
                "calling an external AI API."
            )

        if any(word in lowered for word in ["bye", "goodbye"]):
            return "Goodbye! Thank you for using the Darwix Voice Assistant demo."

        if "name" in lowered:
            return "I am the Darwix Voice Assistant demo."

        return (
            "I understood your message: "
            f'"{message}". This is a local demonstration response, '
            "so no paid API call was made."
        )