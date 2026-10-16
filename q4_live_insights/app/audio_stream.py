
"""Represent incoming audio chunks for the live-insights prototype.

This module provides an in-memory chunk abstraction. It does not capture
microphone audio or perform speech recognition.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import Iterator


@dataclass(frozen=True)
class AudioChunk:
    """One piece of audio data received by the application."""

    sequence: int
    data: bytes
    received_at: float


class AudioStreamBuffer:
    """Store and iterate over audio chunks in arrival order."""

    def __init__(self) -> None:
        self._chunks: list[AudioChunk] = []
        self._next_sequence = 1

    def add_chunk(self, data: bytes) -> AudioChunk:
        """Add a non-empty byte chunk and return its metadata."""
        if not isinstance(data, bytes):
            raise TypeError("Audio chunk data must be bytes")

        if not data:
            raise ValueError("Audio chunk data cannot be empty")

        chunk = AudioChunk(
            sequence=self._next_sequence,
            data=data,
            received_at=perf_counter(),
        )
        self._chunks.append(chunk)
        self._next_sequence += 1
        return chunk

    def __len__(self) -> int:
        return len(self._chunks)

    def __iter__(self) -> Iterator[AudioChunk]:
        return iter(self._chunks)

    def clear(self) -> None:
        """Remove buffered chunks while preserving sequence numbering."""
        self._chunks.clear()
