
"""Chunked WAV replay with incremental ASR and Q4 dashboard publishing.

Prototype limitations:
- Re-transcribes overlapping audio windows; this is not native streaming ASR.
- Processes prerecorded WAV audio, not live microphone or telephony audio.
- Local timing measurements do not establish production end-to-end latency.
"""

import argparse
import json
import re
import sys
import time
import wave
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
Q4_DIR = HERE.parent
PROJECT_ROOT = Q4_DIR.parent
Q1_APP = PROJECT_ROOT / "q1_voice_agent" / "app"

sys.path.insert(0, str(Q1_APP))
sys.path.insert(0, str(HERE))

from local_stt import LocalSTT
from signal_detector import detect_signals
from nudge_engine import NudgeEngine
from live_replay import publish_to_dashboard


def percentile(values: list[float], p: float) -> float:
    """Return a linearly interpolated percentile."""
    if not 0 <= p <= 1:
        raise ValueError("Percentile must be between 0 and 1")

    if not values:
        return 0.0

    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower

    return ordered[lower] + fraction * (
        ordered[upper] - ordered[lower]
    )


def latency_summary(values: list[float]) -> dict[str, float | None]:
    """Summarize successful measurements; use None when none exist."""
    if not values:
        return {"median": None, "p50": None, "p95": None}

    return {
        "median": round(median(values), 3),
        "p50": round(percentile(values, 0.50), 3),
        "p95": round(percentile(values, 0.95), 3),
    }


def clean_asr_text(text: str) -> str:
    """Normalize ASR text and reject empty or punctuation-only output."""
    text = " ".join(text.split()).strip()

    if not text or not any(char.isalnum() for char in text):
        return ""

    # Keep only tokens containing at least one letter or digit.
    # Punctuation attached to a word, such as "hello!", is preserved.
    tokens = [
        token for token in text.split()
        if any(char.isalnum() for char in token)
    ]

    return " ".join(tokens)


def replay_audio(
    audio_path: Path,
    model_size: str = "base.en",
    chunk_seconds: float = 2.0,
    overlap_seconds: float = 0.5,
    playback_speed: float = 1.0,
    dashboard_url: str | None = "http://127.0.0.1:8765/api/events",
) -> dict[str, Any]:
    """Replay prerecorded audio, detect signals, and record delivery outcomes."""
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if chunk_seconds <= 0 or overlap_seconds < 0:
        raise ValueError(
            "Chunk duration must be positive and overlap non-negative"
        )

    if overlap_seconds >= chunk_seconds:
        raise ValueError("Overlap must be shorter than chunk duration")

    if playback_speed <= 0:
        raise ValueError("Playback speed must be positive")

    with wave.open(str(audio_path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frame_count = wav.getnframes()
        pcm = wav.readframes(frame_count)

    if sample_width != 2:
        raise ValueError("This prototype expects 16-bit PCM WAV audio")

    if sample_rate != 16000:
        raise ValueError("This prototype currently expects 16 kHz audio")

    if channels < 1:
        raise ValueError("Audio must contain at least one channel")

    samples = np.frombuffer(pcm, dtype=np.int16)

    if channels > 1:
        samples = (
            samples.reshape(-1, channels)
            .mean(axis=1)
            .astype(np.int16)
        )

    duration = len(samples) / sample_rate
    chunk_frames = max(1, int(chunk_seconds * sample_rate))
    overlap_frames = int(overlap_seconds * sample_rate)
    step_frames = chunk_frames - overlap_frames

    print(f"Audio: {audio_path}")
    print(f"Duration: {duration:.2f}s | chunk: {chunk_seconds:.2f}s")
    print("Loading Faster-Whisper model...")

    stt = LocalSTT(
        model_size=model_size,
        device="cpu",
        compute_type="int8",
    )

    engine = NudgeEngine(
        min_confidence=0.70,
        cooldown_seconds=30,
    )

    partial_transcript = ""
    events: list[dict[str, Any]] = []
    emitted_signals: set[str] = set()

    asr_latencies_ms: list[float] = []
    signal_latencies_ms: list[float] = []
    delivery_latencies_ms: list[float] = []

    delivery_attempts = 0
    delivery_successes = 0
    delivery_failures = 0

    previous_text = ""

    starts = list(range(0, len(samples), step_frames))
    replay_started = time.perf_counter()

    for index, start in enumerate(starts, start=1):
        end = min(len(samples), start + chunk_frames)
        chunk = samples[start:end]

        if len(chunk) == 0:
            continue

        # Approximate the arrival time of each subsequent audio window.
        if start > 0:
            time.sleep(
                min(
                    step_frames / sample_rate / playback_speed,
                    3.0,
                )
            )

        chunk_duration = len(chunk) / sample_rate
        audio_float = chunk.astype(np.float32) / 32768.0

        # Measure ASR processing time independently.
        asr_start = time.perf_counter()

        segments, _ = stt.model.transcribe(
            audio_float,
            beam_size=1,
            language="en",
            vad_filter=False,
            condition_on_previous_text=False,
        )

        # Materialize segments once so text and quality metrics use
        # the same transcription output.
        segment_list = list(segments)

        raw_chunk_text = " ".join(
            segment.text.strip()
            for segment in segment_list
            if segment.text.strip()
        ).strip()

        quality_segments = [
            segment for segment in segment_list
            if segment.text.strip()
        ]

        avg_logprobs = [
            float(segment.avg_logprob)
            for segment in quality_segments
            if getattr(segment, "avg_logprob", None) is not None
        ]
        no_speech_probs = [
            float(segment.no_speech_prob)
            for segment in quality_segments
            if getattr(segment, "no_speech_prob", None) is not None
        ]
        compression_ratios = [
            float(segment.compression_ratio)
            for segment in quality_segments
            if getattr(segment, "compression_ratio", None) is not None
        ]

        asr_quality = {
            "segment_count": len(quality_segments),
            "avg_logprob": (
                round(sum(avg_logprobs) / len(avg_logprobs), 4)
                if avg_logprobs else None
            ),
            "max_no_speech_prob": (
                round(max(no_speech_probs), 4)
                if no_speech_probs else None
            ),
            "max_compression_ratio": (
                round(max(compression_ratios), 4)
                if compression_ratios else None
            ),
            # Diagnostics only: do not suppress signals based on these
            # values until thresholds have been validated on more audio.
            "quality_suspect": False,
            "quality_reasons": [],
        }

        chunk_text = clean_asr_text(raw_chunk_text)

        asr_ms = (time.perf_counter() - asr_start) * 1000
        asr_latencies_ms.append(asr_ms)

        # Deduplicate overlapping windows using a simple prefix heuristic.
        # This does not guarantee word-level alignment.
        new_text = chunk_text

        if previous_text and chunk_text.startswith(previous_text):
            new_text = chunk_text[len(previous_text):].strip()
        elif previous_text and chunk_text == previous_text:
            new_text = ""

        if new_text:
            partial_transcript = (
                f"{partial_transcript} {new_text}"
            ).strip()

        # Do not let an empty final chunk erase useful preceding context.
        if chunk_text:
            previous_text = chunk_text

        # Measure signal detection and nudge generation.
        signal_start = time.perf_counter()

        detected = (
            detect_signals(partial_transcript)
            if partial_transcript
            else []
        )

        new_signals = [
            signal for signal in detected
            if signal["signal"] not in emitted_signals
        ]

        nudges = engine.generate(new_signals)

        for signal in new_signals:
            emitted_signals.add(signal["signal"])

        signal_ms = (time.perf_counter() - signal_start) * 1000
        signal_latencies_ms.append(signal_ms)

        event: dict[str, Any] = {
            "chunk": index,
            "audio_start_seconds": round(start / sample_rate, 3),
            "audio_end_seconds": round(end / sample_rate, 3),
            "partial_transcript": partial_transcript,
            "chunk_transcript": chunk_text,
            "asr_quality": asr_quality,
            "detected_signals": [
                signal["signal"] for signal in new_signals
            ],
            "nudges": nudges,
            "asr_latency_ms": round(asr_ms, 3),
            "signal_latency_ms": round(signal_ms, 3),
            "chunk_latency_ms": round(asr_ms + signal_ms, 3),
            "audio_chunk_duration_seconds": round(chunk_duration, 3),
            "dashboard_delivery_success": None,
            "dashboard_delivery_attempt_latency_ms": None,
            "dashboard_delivery_latency_ms": None,
        }

        events.append(event)

        # Record attempts separately from successful delivery timings.
        published: bool | None = None

        if dashboard_url:
            delivery_attempts += 1
            delivery_start = time.perf_counter()

            published = publish_to_dashboard(
                dashboard_url,
                partial_transcript,
                events,
            )

            attempt_ms = (
                time.perf_counter() - delivery_start
            ) * 1000

            event["dashboard_delivery_attempt_latency_ms"] = round(
                attempt_ms, 3
            )
            event["dashboard_delivery_success"] = published

            if published:
                delivery_successes += 1
                delivery_latencies_ms.append(attempt_ms)
                event["dashboard_delivery_latency_ms"] = round(
                    attempt_ms, 3
                )
            else:
                delivery_failures += 1

        print(
            f"Chunk {index}/{len(starts)} "
            f"[{start / sample_rate:.2f}-"
            f"{end / sample_rate:.2f}s]"
        )
        print(f"  ASR: {chunk_text!r}")
        print(f"  Signals: {event['detected_signals']}")
        print(f"  ASR latency: {asr_ms:.1f} ms")

        if dashboard_url and not published:
            print("  Dashboard unavailable; replay continues.")

    elapsed_seconds = time.perf_counter() - replay_started

    if not dashboard_url:
        delivery_status = "disabled"
    elif delivery_attempts == 0:
        delivery_status = "no_attempts"
    elif delivery_failures == 0:
        delivery_status = "success"
    elif delivery_successes > 0:
        delivery_status = "partial"
    else:
        delivery_status = "failed"

    results: dict[str, Any] = {
        "mode": "chunked_prerecorded_audio_replay",
        "asr_used": True,
        "asr_provider": "Faster-Whisper",
        "asr_model": model_size,
        "device": "cpu",
        "audio_file": str(audio_path),
        "audio_duration_seconds": round(duration, 3),
        "playback_speed": playback_speed,
        "chunk_seconds": chunk_seconds,
        "overlap_seconds": overlap_seconds,
        "chunks_processed": len(events),
        "signals_emitted": sorted(emitted_signals),
        "elapsed_wall_seconds": round(elapsed_seconds, 3),
        "asr_latency_ms": latency_summary(asr_latencies_ms),
        "signal_latency_ms": latency_summary(signal_latencies_ms),
        "dashboard_delivery": {
            "enabled": dashboard_url is not None,
            "attempts": delivery_attempts,
            "successes": delivery_successes,
            "failures": delivery_failures,
            "status": delivery_status,
        },
        "dashboard_delivery_latency_ms": latency_summary(
            delivery_latencies_ms
        ),
        "latency_scope": (
            "ASR and local signal processing are measured separately. "
            "Dashboard attempt latency is recorded for every attempt; "
            "dashboard_delivery_latency_ms summarizes successful deliveries "
            "only. Failed attempts are excluded from successful-delivery "
            "latency statistics. These measurements are not validated "
            "live-telephony end-to-end latency."
        ),
        "events": events,
    }

    evidence_dir = Q4_DIR / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    output_path = evidence_dir / "audio_replay_results.json"
    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n--- Audio replay summary ---")
    print(f"Chunks processed: {len(events)}")
    print(f"Transcript: {partial_transcript}")
    print(f"Signals: {sorted(emitted_signals)}")
    print(f"Elapsed wall time: {elapsed_seconds:.2f}s")
    print(
        "Dashboard delivery: "
        f"{delivery_status} "
        f"(attempts={delivery_attempts}, "
        f"successes={delivery_successes}, "
        f"failures={delivery_failures})"
    )
    print(f"Evidence: {output_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Replay prerecorded WAV audio for Q4 live insights."
    )

    parser.add_argument(
        "--audio",
        default=str(
            PROJECT_ROOT
            / "q1_voice_agent"
            / "transcripts"
            / "temp_audio.wav"
        ),
    )
    parser.add_argument("--model", default="base.en")
    parser.add_argument("--chunk-seconds", type=float, default=2.0)
    parser.add_argument("--overlap-seconds", type=float, default=0.5)
    parser.add_argument("--playback-speed", type=float, default=1.0)
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Run without publishing to the dashboard",
    )

    args = parser.parse_args()

    replay_audio(
        audio_path=Path(args.audio).resolve(),
        model_size=args.model,
        chunk_seconds=args.chunk_seconds,
        overlap_seconds=args.overlap_seconds,
        playback_speed=args.playback_speed,
        dashboard_url=(
            None
            if args.no_dashboard
            else "http://127.0.0.1:8765/api/events"
        ),
    )
