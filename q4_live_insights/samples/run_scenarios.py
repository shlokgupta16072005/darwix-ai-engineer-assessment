
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.signal_detector import detect_signals
from app.nudge_engine import NudgeEngine

scenarios = [
    (
        "Payment difficulty",
        "The customer cannot afford the payment.",
        "payment_difficulty",
    ),
    (
        "Rising frustration",
        "This is frustrating. You are not listening.",
        "rising_frustration",
    ),
    (
        "Compliance gap",
        "The agent guaranteed approval.",
        "compliance_gap",
    ),
    (
        "Missed cross-sell",
        "The customer mentioned a second vehicle.",
        "missed_cross_sell",
    ),
    (
        "Callback needed",
        "Please call me back and let me speak to a human.",
        "callback_needed",
    ),
    (
        "Normal conversation",
        "Hello, how can I help you today?",
        None,
    ),
]

lines = []
engine = NudgeEngine(cooldown_seconds=30)

for name, transcript, expected in scenarios:
    signals = detect_signals(transcript)
    nudges = engine.generate(signals, now=1000 + len(lines) * 100)

    detected = [s["signal"] for s in signals]
    passed = (
        expected in detected if expected else not detected
    )

    lines.extend([
        f"Scenario: {name}",
        f"Transcript: {transcript}",
        f"Detected: {detected}",
        f"Nudges: {nudges}",
        f"Verdict: {'PASS' if passed else 'FAIL'}",
        "",
    ])

output = ROOT / "evidence" / "scenario_results.txt"
output.write_text("\n".join(lines), encoding="utf-8")
print(output.read_text(encoding="utf-8"))
