"""
Local text-to-speech support for the Q1 voice agent.

Uses the operating system's local speech engine so the
voice-agent demo can run without external API credits.
"""

import pyttsx3


class LocalTTS:
    """Offline text-to-speech engine."""

    def __init__(self, rate: int = 170, volume: float = 1.0) -> None:
        if not 0 <= volume <= 1:
            raise ValueError("volume must be between 0 and 1.")

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)

    def speak(self, text: str) -> None:
        """Speak the supplied text through the local speaker."""

        text = text.strip()

        if not text:
            raise ValueError("text cannot be empty.")

        self.engine.say(text)
        self.engine.runAndWait()

    def save(self, text: str, output_file: str) -> None:
        """Save speech to an audio file."""

        text = text.strip()

        if not text:
            raise ValueError("text cannot be empty.")

        self.engine.save_to_file(text, output_file)
        self.engine.runAndWait()