"""
OpenAI client wrapper for the Q1 voice agent.

This module keeps OpenAI API interaction in one place so that the
rest of the application does not need to manage API-client details.
"""

from typing import Optional

from openai import OpenAI

from q1_voice_agent.config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    SYSTEM_PROMPT,
    validate_configuration,
)


class OpenAIClient:
    """Wrapper around the official OpenAI Python client."""

    def __init__(self) -> None:
        validate_configuration()

        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        self.model = OPENAI_MODEL
        self.system_prompt = SYSTEM_PROMPT

    def generate_response(
        self,
        user_message: str,
        conversation_context: Optional[str] = None,
    ) -> str:
        """
        Generate a text response from the OpenAI Responses API.

        Parameters
        ----------
        user_message:
            The latest user message.

        conversation_context:
            Optional previous conversation context.

        Returns
        -------
        str
            The generated assistant response.
        """

        user_message = user_message.strip()

        if not user_message:
            raise ValueError("user_message cannot be empty.")

        if conversation_context:
            input_text = (
                f"Previous conversation:\n"
                f"{conversation_context.strip()}\n\n"
                f"Current user message:\n"
                f"{user_message}"
            )
        else:
            input_text = user_message

        response = self.client.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=input_text,
        )

        return response.output_text.strip()