from pathlib import Path
from typing import Optional
import wave

from faster_whisper import WhisperModel


class LocalSTT:
    """Local speech-to-text using Faster-Whisper."""

    def __init__(
        self,
        model_size: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
        model_dir: Optional[str] = None,
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        download_root = None
        if model_dir:
            download_root = str(Path(model_dir).resolve())

        print(f"Loading local Whisper model: {model_size}")
        print("This may download the model the first time.")

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            download_root=download_root,
        )

        print("Local Whisper model ready.")

    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe an existing WAV/audio file."""

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        segments, _ = self.model.transcribe(
            str(path),
            beam_size=5,
            vad_filter=True,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        return text

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        output_path: str = "q1_voice_agent/transcripts/temp_audio.wav",
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> str:
        """Convert raw PCM microphone bytes to WAV and transcribe them."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)

        return self.transcribe_file(str(path))