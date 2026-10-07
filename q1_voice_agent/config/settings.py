"""
Q1 Voice Agent Configuration

Central configuration for the Darwix AI voice-agent prototype.
Secrets are loaded from environment variables and are never hard-coded.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------------

Q1_ROOT = Path(__file__).resolve().parents[1]

APP_DIR = Q1_ROOT / "app"
CONFIG_DIR = Q1_ROOT / "config"
TESTS_DIR = Q1_ROOT / "tests"
TRANSCRIPTS_DIR = Q1_ROOT / "transcripts"


# ---------------------------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------------------------

# Load the root/project environment file if present.
load_dotenv()

# Also support a Q1-specific .env file if one is created later.
load_dotenv(Q1_ROOT / ".env")


# ---------------------------------------------------------------------------
# OPENAI CONFIGURATION
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "",
).strip()

OPENAI_TRANSCRIPTION_MODEL = os.getenv(
    "OPENAI_TRANSCRIPTION_MODEL",
    "gpt-4o-mini-transcribe",
).strip()

OPENAI_TTS_MODEL = os.getenv(
    "OPENAI_TTS_MODEL",
    "gpt-4o-mini-tts",
).strip()

OPENAI_TTS_VOICE = os.getenv(
    "OPENAI_TTS_VOICE",
    "alloy",
).strip()


# ---------------------------------------------------------------------------
# VOICE AGENT BEHAVIOUR
# ---------------------------------------------------------------------------

AGENT_NAME = os.getenv(
    "AGENT_NAME",
    "Darwix Voice Assistant",
).strip()

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    (
        "You are a helpful voice assistant for the Darwix AI assessment. "
        "Answer clearly, naturally, and concisely. "
        "Do not invent facts. "
        "If you do not know something, say so."
    ),
).strip()


# ---------------------------------------------------------------------------
# AUDIO CONFIGURATION
# ---------------------------------------------------------------------------

AUDIO_SAMPLE_RATE = int(
    os.getenv("AUDIO_SAMPLE_RATE", "16000")
)

AUDIO_CHANNELS = int(
    os.getenv("AUDIO_CHANNELS", "1")
)

AUDIO_CHUNK_SECONDS = float(
    os.getenv("AUDIO_CHUNK_SECONDS", "3")
)


# ---------------------------------------------------------------------------
# CONVERSATION CONFIGURATION
# ---------------------------------------------------------------------------

MAX_CONVERSATION_TURNS = int(
    os.getenv("MAX_CONVERSATION_TURNS", "20")
)

MAX_RESPONSE_TOKENS = int(
    os.getenv("MAX_RESPONSE_TOKENS", "500")
)


# ---------------------------------------------------------------------------
# FILE CONFIGURATION
# ---------------------------------------------------------------------------

TRANSCRIPT_FILE = TRANSCRIPTS_DIR / "conversation.txt"

AUDIO_OUTPUT_FILE = TRANSCRIPTS_DIR / "latest_response.mp3"


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

def validate_configuration() -> None:
    """
    Validate the minimum configuration required to run the voice agent.

    The API key is intentionally not printed or exposed in error messages.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. "
            "Create a .env file and add your API key."
        )

    if not OPENAI_MODEL:
        raise RuntimeError("OPENAI_MODEL cannot be empty.")

    if not OPENAI_TRANSCRIPTION_MODEL:
        raise RuntimeError(
            "OPENAI_TRANSCRIPTION_MODEL cannot be empty."
        )

    if not OPENAI_TTS_MODEL:
        raise RuntimeError(
            "OPENAI_TTS_MODEL cannot be empty."
        )

    if not OPENAI_TTS_VOICE:
        raise RuntimeError(
            "OPENAI_TTS_VOICE cannot be empty."
        )

    if AUDIO_SAMPLE_RATE <= 0:
        raise ValueError("AUDIO_SAMPLE_RATE must be greater than zero.")

    if AUDIO_CHANNELS <= 0:
        raise ValueError("AUDIO_CHANNELS must be greater than zero.")

    if AUDIO_CHUNK_SECONDS <= 0:
        raise ValueError("AUDIO_CHUNK_SECONDS must be greater than zero.")

    if MAX_CONVERSATION_TURNS <= 0:
        raise ValueError(
            "MAX_CONVERSATION_TURNS must be greater than zero."
        )

    if MAX_RESPONSE_TOKENS <= 0:
        raise ValueError(
            "MAX_RESPONSE_TOKENS must be greater than zero."
        )


# ---------------------------------------------------------------------------
# DIRECTORY INITIALIZATION
# ---------------------------------------------------------------------------

def ensure_directories() -> None:
    """Create runtime directories required by the Q1 application."""

    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)