
from pathlib import Path
import sys

# Resolve the Q4 project root and make its app package importable.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.signal_detector import detect_signals
from app.nudge_engine import NudgeEngine


# Each scenario includes a transcript and the expected signal.
# Cross-sell wording expresses actual purchase intent rather than
# merely mentioning a second vehicle.
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
        "The customer is interested in a second vehicle.",
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


def run_scenarios():
    """Run all scenarios, save their results, and return a summary."""
    lines = []
    passed_count = 0
    failed_scenarios = []

    # Keep the existing deterministic timestamps and cooldown behaviour.
    engine = NudgeEngine(cooldown_seconds=30)

    for index, (name, transcript, expected) in enumerate(scenarios):
        signals = detect_signals(transcript)

        # Space timestamps sufficiently apart so the cooldown from one
        # scenario does not suppress another scenario's signal.
        timestamp = 1000 + index * 100
        nudges = engine.generate(signals, now=timestamp)

        detected = [signal["signal"] for signal in signals]
        generated = [nudge["signal"] for nudge in nudges]

        # A scenario passes only when the expected signal is detected
        # and produces a nudge. Normal conversation should produce neither.
        if expected is None:
            passed = not detected and not generated
        else:
            passed = expected in detected and expected in generated

        if passed:
            passed_count += 1
            verdict = "PASS"
        else:
            verdict = "FAIL"
            failed_scenarios.append(name)

        lines.extend(
            [
                f"Scenario: {name}",
                f"Transcript: {transcript}",
                f"Expected signal: {expected or 'No signal'}",
                f"Detected signals: {detected}",
                f"Generated nudges: {nudges}",
                f"Verdict: {verdict}",
                "",
            ]
        )

    total = len(scenarios)
    lines.extend(
        [
            "=" * 50,
            f"Scenario summary: {passed_count}/{total} passed",
            f"Failed scenarios: {failed_scenarios or 'None'}",
            "",
        ]
    )

    report = "\n".join(lines)

    # Ensure the evidence directory exists before writing the report.
    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    output = evidence_dir / "scenario_results.txt"
    output.write_text(report, encoding="utf-8")

    print(report)
    print(f"Report saved to: {output}")

    # Return a non-zero process exit code if any scenario fails.
    return 0 if passed_count == total else 1


if __name__ == "__main__":
    raise SystemExit(run_scenarios())
