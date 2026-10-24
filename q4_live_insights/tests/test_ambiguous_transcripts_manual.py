import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.signal_detector import detect_signals
from app.nudge_engine import NudgeEngine

scenarios = {
    "clear_payment_difficulty": {
        "transcript": "I cannot afford my payment this month.",
        "expected": ["payment_difficulty"],
    },
    "ambiguous_fragment": {
        "transcript": "I... uh... payment... maybe...",
        "expected": [],
    },
    "normal_payment_question": {
        "transcript": "I have a question about my payment statement.",
        "expected": [],
    },
    "clear_callback_request": {
        "transcript": "Please let me speak to a human representative.",
        "expected": ["callback_needed"],
    },
    "uncertain_callback_fragment": {
        "transcript": "human... representative... maybe...",
        "expected": [],
    },
}

results = []

for name, case in scenarios.items():
    detected = detect_signals(case["transcript"])
    nudges = NudgeEngine().generate(detected)
    actual = sorted(n["signal"] for n in nudges)
    expected = sorted(case["expected"])

    result = {
        "scenario": name,
        "transcript": case["transcript"],
        "expected_nudges": expected,
        "actual_nudges": actual,
        "status": "PASS" if actual == expected else "FAIL",
    }
    results.append(result)
    print(
        f"{result['status']} | {name} | "
        f"expected={expected} actual={actual}"
    )

output = Path("evidence/ambiguous_transcript_results.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(results, indent=2), encoding="utf-8")

passed = sum(r["status"] == "PASS" for r in results)
print(f"\nSummary: {passed}/{len(results)} passed")
print(f"Evidence saved: {output.resolve()}")

if passed != len(results):
    raise SystemExit(1)
