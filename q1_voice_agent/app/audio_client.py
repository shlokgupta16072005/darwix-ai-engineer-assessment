"""
Audio client for the Q1 voice agent.

This module handles:
1. Speech-to-text transcription
2. Text-to-speech generation

All OpenAI audio API interaction is kept here so that the
rest of the application does not need to manage API details.
"""

from pathlib import Path

from openai import OpenAI

from q1_voice_agent.config.settings import (
    AUDIO_OUTPUT_FILE,
    OPENAI_API_KEY,
    OPENAI_TRANSCRIPTION_MODEL,
    OPENAI_TTS_MODEL,
    OPENAI_TTS_VOICE,
    validate_configuration,
)


class AudioClient:
    """Wrapper around OpenAI audio APIs."""

    def __init__(self) -> None:
        validate_configuration()

        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        self.transcription_model = OPENAI_TRANSCRIPTION_MODEL
        self.tts_model = OPENAI_TTS_MODEL
        self.tts_voice = OPENAI_TTS_VOICE

    def transcribe_audio(self, audio_file: str | Path) -> str:
        """
        Convert an audio file into text.

        Parameters
        ----------
        audio_file:
            Path to the audio file.

        Returns
        -------
        str
            Transcribed text.
        """

        audio_path = Path(audio_file)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if not audio_path.is_file():
            raise ValueError(
                f"Audio path is not a file: {audio_path}"
            )

        with audio_path.open("rb") as file:
            transcription = self.client.audio.transcriptions.create(
                model=self.transcription_model,
                file=file,
            )

        text = getattr(transcription, "text", "")

        if not text:
            raise RuntimeError(
                "The transcription API returned an empty response."
            )

        return text.strip()

    def text_to_speech(
        self,
        text: str,
        output_file: str | Path | None = None,
    ) -> Path:
        """
        Convert text into speech and save it as an MP3 file.

        Parameters
        ----------
        text:
            Text that should be spoken.

        output_file:
            Optional destination path.

        Returns
        -------
        Path
            Path to the generated audio file.
        """

        text = text.strip()

        if not text:
            raise ValueError("text cannot be empty.")

        if output_file is None:
            output_path = AUDIO_OUTPUT_FILE
        else:
            output_path = Path(output_file)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        response = self.client.audio.speech.create(
            model=self.tts_model,
            voice=self.tts_voice,
            input=text,
        )

        response.stream_to_file(output_path)

        if not output_path.exists():
            raise RuntimeError(
                "Text-to-speech completed but no output file was created."
            )

        return output_path