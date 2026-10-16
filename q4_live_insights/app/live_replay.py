
"""Real-time-speed transcript replay for the Q4 live-insights prototype.

This simulates incremental transcript delivery. It does not perform ASR
or capture microphone audio. Processing latency is measured locally.
"""

import math
import json
import time
from statistics import median
from typing import Any
import urllib.error
import urllib.request

from signal_detector import detect_signals
from nudge_engine import NudgeEngine


def publish_to_dashboard(
    dashboard_url: str,
    transcript: str,
    events: list[dict[str, Any]],
) -> bool:
    """Publish the latest replay state; never fail the replay if offline."""
    payload = json.dumps({
        "transcript": transcript,
        "events": events[-100:],
    }).encode("utf-8")
    request = urllib.request.Request(
        dashboard_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=0.5) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return False


def replay_transcript(
    transcript: str,
    chunk_size: int = 35,
    interval_seconds: float = 0.5,
    dashboard_url: str | None = "http://127.0.0.1:8765/api/events",
) -> dict[str, Any]:
    """Process transcript chunks incrementally and report processing latency."""
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("Transcript cannot be empty")
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    if interval_seconds < 0:
        raise ValueError("interval_seconds cannot be negative")

    engine = NudgeEngine(min_confidence=0.70, cooldown_seconds=30)
    partial_transcript = ""
    chunk_latencies_ms = []
    events = []
    emitted_signals = set()

    words = transcript.split()
    chunks = [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

    print("Starting incremental transcript replay...")
    print(f"Chunks: {len(chunks)} | Interval: {interval_seconds:.2f}s")

    for index, chunk in enumerate(chunks, start=1):
        if index > 1 and interval_seconds:
            time.sleep(interval_seconds)

        received_at = time.perf_counter()
        partial_transcript = f"{partial_transcript} {chunk}".strip()

        detected = detect_signals(partial_transcript)
        new_signals = [
            signal for signal in detected
            if signal["signal"] not in emitted_signals
        ]

        # Use wall-clock timestamps for emitted nudges.
        processing_started = time.perf_counter()
        nudges = engine.generate(new_signals)
        processing_ms = (time.perf_counter() - processing_started) * 1000
        chunk_latency_ms = (time.perf_counter() - received_at) * 1000
        chunk_latencies_ms.append(chunk_latency_ms)

        for signal in new_signals:
            emitted_signals.add(signal["signal"])

        event = {
            "chunk": index,
            "partial_transcript": partial_transcript,
            "detected_signals": [s["signal"] for s in new_signals],
            "nudges": nudges,
            "processing_ms": round(processing_ms, 3),
            "chunk_latency_ms": round(chunk_latency_ms, 3),
        }
        events.append(event)

        # Dashboard delivery is separate from the local processing metric.
        if dashboard_url:
            published = publish_to_dashboard(
                dashboard_url, partial_transcript, events
            )
            if not published and index == 1:
                print(
                    "Dashboard unavailable; continuing replay without live display."
                )

        print(f"\nChunk {index}/{len(chunks)}: {chunk}")
        print(f"Detected: {event['detected_signals']}")
        print(f"Nudges: {json.dumps(nudges, ensure_ascii=False)}")
        print(f"Local processing latency: {chunk_latency_ms:.3f} ms")

    sorted_latencies = sorted(chunk_latencies_ms)


    def percentile(values: list[float], p: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        rank = max(1, math.ceil(p * len(ordered)))
        return ordered[min(len(ordered) - 1, rank - 1)]


    results = {
        "mode": "real_time_speed_text_replay",
        "asr_used": False,
        "chunks_processed": len(chunks),
        "signals_emitted": sorted(emitted_signals),
        "latency_ms": {
            "median": round(median(chunk_latencies_ms), 3),
            "p50": round(percentile(sorted_latencies, 0.50), 3),
            "p95": round(percentile(sorted_latencies, 0.95), 3),
            "measurement_scope": (
                "local transcript processing only; excludes ASR, audio transport, "
                "network and dashboard delivery"
            ),
        },
        "events": events,
    }


    print("\n--- Replay summary ---")
    print(f"Chunks processed: {len(chunks)}")
    print(f"Signals emitted: {sorted(emitted_signals)}")
    print(f"Median local processing latency: {results['latency_ms']['median']} ms")
    print(f"P95 local processing latency: {results['latency_ms']['p95']} ms")
    return results



if __name__ == "__main__":
    scenarios = {
        "Payment difficulty, frustration and callback": (
            "Hello, I am calling about my payment. "
            "I cannot afford the payment this month. "
            "This is frustrating and you are not listening. "
            "Please call me back so I can speak to a human."
        ),
        "Compliance gap": (
            "The agent guaranteed approval without telling the customer "
            "about the required disclosure."
        ),
        "Missed cross-sell": (
            "The customer mentioned a second vehicle and another vehicle "
            "on the policy."
        ),
        "Normal conversation": (
            "Hello, thank you for calling. How can I help you today?"
        ),
    }

    all_results = {}

    for scenario_name, transcript in scenarios.items():
        print(f"\n{'=' * 60}")
        print(f"SCENARIO: {scenario_name}")
        print("=" * 60)
        all_results[scenario_name] = replay_transcript(
            transcript,
            chunk_size=7,
            interval_seconds=0.1,
        )

    output_path = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "evidence"
        / "live_replay_results.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nAll {len(all_results)} scenarios saved to: {output_path}")