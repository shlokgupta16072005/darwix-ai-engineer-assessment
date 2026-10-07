"""
Tests for the Q1 OpenAI client configuration.

These tests intentionally avoid making paid API requests.
They verify that the client module can be imported and that
configuration values are loaded correctly.
"""

from q1_voice_agent.config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TRANSCRIPTION_MODEL,
    OPENAI_TTS_MODEL,
    OPENAI_TTS_VOICE,
)


def test_api_key_is_configured():
    """Verify that an API key exists without exposing its value."""
    assert OPENAI_API_KEY
    assert len(OPENAI_API_KEY) > 20


def test_text_model_is_configured():
    """Verify that a text-generation model is configured."""
    assert OPENAI_MODEL
    assert OPENAI_MODEL != "your_text_model_here"


def test_transcription_model_is_configured():
    """Verify that a transcription model is configured."""
    assert OPENAI_TRANSCRIPTION_MODEL


def test_tts_model_is_configured():
    """Verify that a text-to-speech model is configured."""
    assert OPENAI_TTS_MODEL


def test_tts_voice_is_configured():
    """Verify that a TTS voice is configured."""
    assert OPENAI_TTS_VOICE


def test_openai_client_module_imports():
    """Verify that the OpenAI client wrapper imports successfully."""
    from q1_voice_agent.app.openai_client import OpenAIClient

    assert OpenAIClient is not None