
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from q2_knowledge_base.retrieval.rag_answer import answer_question


CASES = [
    {
        "question": "What is the minimum business vintage?",
        "expected": ["24 months"],
    },
    {
        "question": "What documents are required to apply?",
        "expected": ["documents"],
    },
    {
        "question": "What is the maximum loan amount?",
        "expected": ["25,00,000"],
    },
    {
        "question": "What is the current interest rate?",
        "expected": [
            "current interest rate",
	    "customer-specific",
            "human follow-up",
        ],
    },
    {
        "question": "Can a business operating for 12 months qualify?",
        "expected": ["one year", "24 months"],
    },
]


def evaluate_case(case):
    """Run a question and check expected phrases and source availability."""
    question = case["question"]
    expected_phrases = case["expected"]

    try:
        result = answer_question(question)
        if not isinstance(result, dict):
            raise TypeError(
                f"answer_question returned {type(result).__name__}, "
                "expected a dictionary"
            )
    except Exception as exc:
        return {
            "question": question,
            "expected": expected_phrases,
            "error": f"{type(exc).__name__}: {exc}",
            "answer": "",
            "sources": [],
            "mode": "error",
            "expected_found": [],
            "phrase_pass": False,
            "sources_present": False,
        }

    answer = str(result.get("answer", ""))
    sources = result.get("sources", [])
    if not isinstance(sources, list):
        sources = []

    answer_lower = answer.casefold()
    expected_found = [
        phrase
        for phrase in expected_phrases
        if phrase.casefold() in answer_lower
    ]

    return {
        "question": question,
        "expected": expected_phrases,
        "answer": answer,
        "sources": sources,
        "mode": result.get("mode", "unknown"),
        "expected_found": expected_found,
        "phrase_pass": len(expected_found) == len(expected_phrases),
        "sources_present": len(sources) > 0,
        "error": None,
    }


def build_report(results):
    """Build a readable report containing answers and retrieved evidence."""
    output = [
        "DARWIX AI — Q2 SOURCE-GROUNDING VERIFICATION",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "=" * 75,
    ]

    for index, result in enumerate(results, start=1):
        output.append(f"\nCASE {index}: {result['question']}")
        output.append("-" * 75)
        output.append(f"Mode: {result['mode']}")

        if result["error"]:
            output.append(f"ERROR: {result['error']}")
            output.append("Phrase check: NOT RUN")
            output.append("Source check: NOT RUN")
            continue

        output.append(f"Answer:\n{result['answer'] or '[EMPTY ANSWER]'}")
        sources = result["sources"]
        output.append(f"\nNumber of sources: {len(sources)}")
        output.append("Source details:")

        if not sources:
            output.append("  NO SOURCES RETURNED")
        else:
            for source_index, source in enumerate(sources, start=1):
                output.append(
                    f"  Source {source_index}:\n"
                    + json.dumps(
                        source,
                        indent=4,
                        ensure_ascii=False,
                        default=str,
                    )
                )

        expected = result["expected"]
        found = result["expected_found"]
        output.append(
            f"Expected-answer phrase check: "
            f"{len(found)}/{len(expected)} phrases found"
        )
        output.append(
            "Expected phrases found: "
            + (", ".join(found) if found else "None")
        )
        missing = [phrase for phrase in expected if phrase not in found]
        output.append(
            "Expected phrases missing: "
            + (", ".join(missing) if missing else "None")
        )
        output.append(
            f"Sources returned: {'YES' if result['sources_present'] else 'NO'}"
        )
        output.append(
            "Grounding verdict: MANUAL REVIEW REQUIRED — "
            "verify that each factual claim is supported by the cited source text."
        )

    successful_runs = [r for r in results if not r["error"]]
    phrase_passes = sum(r["phrase_pass"] for r in successful_runs)
    source_present = sum(r["sources_present"] for r in successful_runs)
    errors = sum(bool(r["error"]) for r in results)

    output.extend([
        "\n" + "=" * 75,
        "SUMMARY",
        f"Total cases: {len(results)}",
        f"Cases executed: {len(successful_runs)}",
        f"Cases with execution errors: {errors}",
        f"Cases passing expected-phrase checks: "
        f"{phrase_passes}/{len(successful_runs)}",
        f"Cases returning sources: {source_present}/{len(successful_runs)}",
        "",
        "IMPORTANT LIMITATIONS:",
        "- Phrase matching is a basic string check, not a factuality evaluation.",
        "- Returning sources does not prove the answer is supported by them.",
        "- Manually compare every answer claim with its retrieved source text.",
        "- A fallback response is not evidence that OpenAI generation succeeded.",
    ])

    return "\n".join(output)


def main():
    results = [evaluate_case(case) for case in CASES]
    report = build_report(results)

    report_path = PROJECT_ROOT / "q2_knowledge_base" / "source_grounding_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nReport saved to: {report_path.resolve()}")


if __name__ == "__main__":
    main()
