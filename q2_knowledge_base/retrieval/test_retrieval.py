
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
        "expected_chunk_id": "faq.txt::chunk_4",
        "expected_topic_terms": ["business", "operation"],
    },
    {
        "query": "What documents are required for the loan application?",
        "expected_source": "eligibility_rules.pdf",
        "acceptable_sources": [
            "faq.txt",
            "eligibility_rules.pdf",
            "application_process.txt",
        ],
        "expected_keyword": "documents",
    },
    {
        "query": "What is the minimum and maximum loan amount?",
        "expected_source": "faq.txt",
        "expected_keywords": ["2,00,000", "25,00,000"],
        "require_all_keywords_in_top3": True,
    },
    {
        "query": (
            "What should I say if the customer thinks "
            "the interest rate is too high?"
        ),
        "expected_source": "objection_handling.txt",
        "expected_keyword": "interest",
    },
    {
        "query": (
            "Can a business that has operated for only one year qualify?"
        ),
        "expected_source": "eligibility_rules.pdf",
        "expected_keyword": "24 months",
    },
]


def evaluate_test(test_case):
    results = search(test_case["query"], top_k=3)

    acceptable_sources = [
        Path(source).name.lower()
        for source in test_case.get(
            "acceptable_sources",
            [test_case["expected_source"]],
        )
    ]

    expected_keywords = [
        keyword.lower()
        for keyword in test_case.get(
            "expected_keywords",
            [test_case["expected_keyword"]]
            if "expected_keyword" in test_case
            else [],
        )
    ]

    expected_chunk_id = test_case.get("expected_chunk_id")
    expected_topic_terms = test_case.get("expected_topic_terms", [])

    retrieved = []

    for result in results:
        source = str(result.get("source", "unknown"))
        text = str(result.get("text", ""))
        chunk_id = result.get("chunk_id")
        normalized_text = text.lower()

        source_match = (
            Path(source.replace("\\", "/")).name.lower()
            in acceptable_sources
        )

        matched_keywords = [
            keyword
            for keyword in expected_keywords
            if keyword in normalized_text
        ]

        retrieved.append({
            "rank": result.get("rank"),
            "chunk_id": chunk_id,
            "source": source,
            "category": result.get("category"),
            "adjusted_score": round(float(result["score"]), 4),
            "raw_tfidf_score": round(float(result["raw_score"]), 4),
            "text": text,
            "expected_source_match": source_match,
            "matched_keywords": matched_keywords,
            "expected_keyword_in_chunk": bool(matched_keywords),
            "expected_chunk_match": (
                chunk_id == expected_chunk_id
                if expected_chunk_id
                else None
            ),
        })

    source_found = any(
        item["expected_source_match"] for item in retrieved
    )

    covered_keywords = [
        keyword
        for keyword in expected_keywords
        if any(
            keyword in item["text"].lower()
            for item in retrieved
        )
    ]

    all_keywords_found = (
        set(covered_keywords) == set(expected_keywords)
    )

    keyword_found = bool(covered_keywords)
    top_result = retrieved[0] if retrieved else None

    top1_source_match = bool(
        top_result and top_result["expected_source_match"]
    )

    top1_keyword_match = bool(
        top_result
        and all(
            keyword in top_result["text"].lower()
            for keyword in expected_keywords
        )
    )

    top1_chunk_match = bool(
        top_result
        and expected_chunk_id
        and top_result["chunk_id"] == expected_chunk_id
    )

    top_text = (
        str(top_result["text"]).lower()
        if top_result
        else ""
    )

    top1_topic_match = bool(
        top_result
        and expected_topic_terms
        and all(
            term.lower() in top_text
            for term in expected_topic_terms
        )
    )

    expected_source_rank = next(
        (
            item["rank"]
            for item in retrieved
            if item["expected_source_match"]
        ),
        None,
    )

    strict_top1_required = bool(expected_chunk_id)
    require_all_keywords = test_case.get(
        "require_all_keywords_in_top3", False
    )

    if require_all_keywords:
        if source_found and all_keywords_found:
            verdict = "PASS"
            explanation = (
                "All required loan-amount facts appear in the top three. "
                "The response must combine evidence from multiple chunks "
                "if no single chunk contains both amounts."
            )
        elif source_found or keyword_found:
            verdict = "REVIEW"
            explanation = (
                "Some expected evidence was retrieved, but the expected "
                "source or complete keyword coverage is missing."
            )
        else:
            verdict = "FAIL"
            explanation = (
                "The expected source and required loan-amount facts "
                "were not retrieved."
            )

    elif strict_top1_required:
        strict_pass = (
            top1_chunk_match
            and top1_topic_match
            and top1_keyword_match
        )

        if strict_pass:
            verdict = "PASS"
            explanation = (
                "The expected chunk ranks first and contains the required "
                "topic terms and keyword."
            )
        else:
            verdict = "REVIEW"
            explanation = (
                "Strict top-1 relevance criteria were not all satisfied. "
                "Inspect the top-ranked chunk and supporting evidence."
            )

    elif top1_source_match and top1_keyword_match:
        verdict = "PASS"
        explanation = (
            "The top result matches an acceptable source and contains "
            "all expected keywords. This is a rule-based check, not "
            "a human relevance judgment."
        )

    elif source_found and keyword_found:
        verdict = "REVIEW"
        explanation = (
            "An acceptable source and expected keyword were found in "
            "the top three, but the top result did not satisfy both checks."
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
            "Neither an acceptable source nor an expected keyword "
            "was found in the top three."
        )

    return {
        "query": test_case["query"],
        "expected_source": test_case["expected_source"],
        "acceptable_sources": acceptable_sources,
        "expected_keywords": expected_keywords,
        "expected_chunk_id": expected_chunk_id,
        "expected_topic_terms": expected_topic_terms,
        "require_all_keywords_in_top3": require_all_keywords,
        "top_result": top_result["source"] if top_result else None,
        "top_chunk_id": top_result["chunk_id"] if top_result else None,
        "top_score": (
            top_result["adjusted_score"] if top_result else None
        ),
        "top1_source_match": top1_source_match,
        "top1_keyword_match": top1_keyword_match,
        "top1_chunk_match": (
            top1_chunk_match if expected_chunk_id else None
        ),
        "top1_topic_match": (
            top1_topic_match if expected_topic_terms else None
        ),
        "expected_source_rank_in_top_3": expected_source_rank,
        "source_found_in_top_3": source_found,
        "covered_keywords_in_top3": covered_keywords,
        "all_expected_keywords_found": all_keywords_found,
        "keyword_found_in_top3": keyword_found,
        "retrieved_evidence": retrieved,
        "relevance_explanation": explanation,
        "verdict_basis": (
            "strict_top1_chunk_and_topic_check"
            if strict_top1_required
            else (
                "top3_required_keyword_coverage"
                if require_all_keywords
                else "top1_acceptable_source_and_keyword_smoke_test"
            )
        ),
        "result": verdict,
    }


def main():
    evaluation_results = [
        evaluate_test(test_case)
        for test_case in TEST_CASES
    ]

    total = len(evaluation_results)
    passed = sum(
        result["result"] == "PASS"
        for result in evaluation_results
    )
    reviewed = sum(
        result["result"] == "REVIEW"
        for result in evaluation_results
    )
    failed = sum(
        result["result"] == "FAIL"
        for result in evaluation_results
    )

    top1_source_matches = sum(
        result["top1_source_match"]
        for result in evaluation_results
    )

    strict_cases = [
        result for result in evaluation_results
        if result["expected_chunk_id"]
    ]

    strict_passes = sum(
        result["result"] == "PASS"
        for result in strict_cases
    )

    summary = {
        "evaluation_type": "small_prototype_retrieval_smoke_test",
        "total_tests": total,
        "passed_tests": passed,
        "review_tests": reviewed,
        "failed_tests": failed,
        "top1_expected_source_matches": top1_source_matches,
        "top1_source_match_rate": (
            round(top1_source_matches / total, 4)
            if total else 0
        ),
        "strict_top1_tests": len(strict_cases),
        "strict_top1_passed": strict_passes,
        "strict_top1_pass_rate": (
            round(strict_passes / len(strict_cases), 4)
            if strict_cases else None
        ),
        "note": (
            "Rule-based prototype evaluation, not a human relevance "
            "judgment or production retrieval-accuracy benchmark. "
            "The business-vintage case uses strict top-1 chunk checks. "
            "The combined loan-amount case checks that both required "
            "amounts appear in the top three. Other cases use top-1 "
            "source and keyword checks."
        ),
        "results": evaluation_results,
    }

    output_path = (
        PROJECT_ROOT / "retrieval" / "retrieval_test_results.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    for index, result in enumerate(evaluation_results, start=1):
        print(
            f"Test {index}: {result['result']} | "
            f"top={result['top_result']} | "
            f"chunk={result['top_chunk_id']} | "
            f"expected source rank="
            f"{result['expected_source_rank_in_top_3']}"
        )

        if result["expected_keywords"]:
            print(
                "  Keyword coverage: "
                f"{result['covered_keywords_in_top3']} / "
                f"{result['expected_keywords']}"
            )

        for evidence in result["retrieved_evidence"]:
            print(
                f"  Rank {evidence['rank']} | "
                f"chunk_id={evidence['chunk_id']} | "
                f"source={evidence['source']} | "
                f"score={evidence['adjusted_score']}"
            )

    print(
        f"\nTests: {total}; PASS: {passed}; "
        f"REVIEW: {reviewed}; FAIL: {failed}"
    )
    print(
        f"Top-1 acceptable-source matches: "
        f"{top1_source_matches}/{total}"
    )
    print(
        f"Strict top-1 tests passed: "
        f"{strict_passes}/{len(strict_cases)}"
    )
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
