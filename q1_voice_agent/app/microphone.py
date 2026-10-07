"""
Local microphone input for the Q1 voice agent.

Uses PyAudioWPatch directly so the project works with
Python 3.14 on Windows without requiring the standard
PyAudio package.
"""

from dataclasses import dataclass

import pyaudiowpatch as pyaudio


@dataclass
class RecordedAudio:
    """Container for recorded microphone audio."""

    audio_bytes: bytes
    sample_rate: int
    channels: int
    sample_width: int


class MicrophoneInput:
    """Capture raw PCM audio from the computer microphone."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        recording_seconds: int = 5,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be greater than zero.")

        if channels <= 0:
            raise ValueError("channels must be greater than zero.")

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if recording_seconds <= 0:
            raise ValueError(
                "recording_seconds must be greater than zero."
            )

        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.recording_seconds = recording_seconds

    def list_microphones(self) -> list[str]:
        """Return names of available audio input devices."""

        audio = pyaudio.PyAudio()

        try:
            devices = []

            for index in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(index)

                if info.get("maxInputChannels", 0) > 0:
                    devices.append(
                        f"{index}: {info.get('name', 'Unknown device')}"
                    )

            return devices

        finally:
            audio.terminate()

    def get_default_microphone(self) -> dict:
        """Return information about the default input device."""

        audio = pyaudio.PyAudio()

        try:
            return audio.get_default_input_device_info()

        finally:
            audio.terminate()

    def record_once(self) -> RecordedAudio:
        """
        Record audio from the default microphone.

        Returns:
            RecordedAudio containing raw PCM microphone data.
        """

        audio = pyaudio.PyAudio()

        stream = None

        try:
            sample_format = pyaudio.paInt16

            stream = audio.open(
                format=sample_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            print("Listening... Speak now.")

            frames = []

            total_chunks = int(
                self.sample_rate
                / self.chunk_size
                * self.recording_seconds
            )

            for _ in range(total_chunks):
                data = stream.read(
                    self.chunk_size,
                    exception_on_overflow=False,
                )
                frames.append(data)

            print("Recording complete.")

            sample_width = audio.get_sample_size(sample_format)

            return RecordedAudio(
                audio_bytes=b"".join(frames),
                sample_rate=self.sample_rate,
                channels=self.channels,
                sample_width=sample_width,
            )

        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()

            audio.terminate()