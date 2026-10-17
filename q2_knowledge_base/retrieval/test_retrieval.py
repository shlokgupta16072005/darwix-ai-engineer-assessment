from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from retrieval.search import search


TEST_CASES = [
    {
        "query": "What is the minimum business vintage?",
        "expected_source": "faq.txt",
        "expected_keyword": "24 months",
    },
    {
        "query": "What documents are required for the loan application?",
        "expected_source": "eligibility_rules.pdf",
        "expected_keyword": "documents",
    },
    {
        "query": "What is the minimum and maximum loan amount?",
        "expected_source": "faq.txt",
        "expected_keyword": "25,00,000",
    },
    {
        "query": "What should I say if the customer thinks the interest rate is too high?",
        "expected_source": "objection_handling.txt",
        "expected_keyword": "interest",
    },
    {
        "query": "Can a business that has operated for only one year qualify?",
        "expected_source": "eligibility_rules.pdf",
        "expected_keyword": "24 months",
    },
]


def evaluate_test(test_case):
    results = search(test_case["query"], top_k=3)

    expected_source = Path(
        test_case["expected_source"]
    ).name.lower()
    expected_keyword = test_case["expected_keyword"].lower()

    retrieved = []

    for result in results:
        source = str(result.get("source", "unknown"))
        text = str(result.get("text", ""))
        source_match = (
            Path(source.replace("\\", "/")).name.lower()
            == expected_source
        )
        keyword_match = expected_keyword in text.lower()

        retrieved.append({
            "rank": result.get("rank"),
            "chunk_id": result.get("chunk_id"),
            "source": source,
            "category": result.get("category"),
            "adjusted_score": round(float(result["score"]), 4),
            "raw_tfidf_score": round(float(result["raw_score"]), 4),
            "text": text,
            "expected_source_match": source_match,
            "expected_keyword_in_chunk": keyword_match,
        })

    source_found = any(
        item["expected_source_match"] for item in retrieved
    )
    keyword_found = any(
        item["expected_keyword_in_chunk"] for item in retrieved
    )
    top1_source_match = bool(
        retrieved and retrieved[0]["expected_source_match"]
    )

    expected_source_rank = next(
        (
            item["rank"]
            for item in retrieved
            if item["expected_source_match"]
        ),
        None,
    )

    if source_found and keyword_found:
        verdict = "PASS"
        explanation = (
            "The expected source and keyword appear in the top three. "
            "This is a rule-based match; semantic relevance still requires review."
        )
    elif source_found or keyword_found:
        verdict = "REVIEW"
        explanation = (
            "Only one of the expected-source and keyword checks passed. "
            "Inspect the retrieved evidence."
        )
    else:
        verdict = "FAIL"
        explanation = (
            "Neither the expected source nor the expected keyword was found "
            "in the top three."
        )

    return {
        "query": test_case["query"],
        "expected_source": test_case["expected_source"],
        "expected_keyword": test_case["expected_keyword"],
        "top_result": retrieved[0]["source"] if retrieved else None,
        "top_score": retrieved[0]["adjusted_score"] if retrieved else None,
        "top1_source_match": top1_source_match,
        "expected_source_rank_in_top_3": expected_source_rank,
        "source_found_in_top_3": source_found,
        "keyword_found_in_top_3": keyword_found,
        "retrieved_evidence": retrieved,
        "relevance_explanation": explanation,
        "verdict_basis": "rule_based_smoke_test_not_human_judgment",
        "result": verdict,
    }


def main():
    evaluation_results = [
        evaluate_test(test_case) for test_case in TEST_CASES
    ]

    total = len(evaluation_results)
    passed = sum(r["result"] == "PASS" for r in evaluation_results)
    reviewed = sum(r["result"] == "REVIEW" for r in evaluation_results)
    failed = sum(r["result"] == "FAIL" for r in evaluation_results)
    top1_matches = sum(r["top1_source_match"] for r in evaluation_results)

    summary = {
        "evaluation_type": "small_prototype_retrieval_smoke_test",
        "total_tests": total,
        "passed_tests": passed,
        "review_tests": reviewed,
        "failed_tests": failed,
        "top1_expected_source_matches": top1_matches,
        "top1_source_match_rate": round(top1_matches / total, 4) if total else 0,
        "note": (
            "Rule-based checks are not human relevance judgments or a "
            "production retrieval-accuracy benchmark."
        ),
        "results": evaluation_results,
    }

    output_path = PROJECT_ROOT / "retrieval" / "retrieval_test_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    for index, result in enumerate(evaluation_results, start=1):
        print(
            f"Test {index}: {result['result']} | "
            f"top={result['top_result']} | "
            f"expected source rank={result['expected_source_rank_in_top_3']}"
        )
        for evidence in result["retrieved_evidence"]:
            print(
                f"  Rank {evidence['rank']} | "
                f"chunk_id={evidence['chunk_id']} | "
                f"source={evidence['source']} | "
                f"score={evidence['adjusted_score']}"
            )

    print(f"\nTests: {total}; PASS: {passed}; REVIEW: {reviewed}; FAIL: {failed}")
    print(f"Top-1 expected-source matches: {top1_matches}/{total}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
