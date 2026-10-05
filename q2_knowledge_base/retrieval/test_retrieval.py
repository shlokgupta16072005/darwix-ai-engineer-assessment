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

    combined_text = " ".join(
        result["text"].lower()
        for result in results
    )

    source_found = any(
        test_case["expected_source"].lower() in result["source"].lower()
        for result in results
    )

    keyword_found = test_case["expected_keyword"].lower() in combined_text

    passed = source_found and keyword_found

    return {
        "query": test_case["query"],
        "expected_source": test_case["expected_source"],
        "expected_keyword": test_case["expected_keyword"],
        "top_result": results[0]["source"],
        "top_score": round(results[0]["score"], 4),
        "source_found_in_top_3": source_found,
        "keyword_found_in_top_3": keyword_found,
        "result": "PASS" if passed else "REVIEW",
    }


def main():
    print("=" * 80)
    print("Q2 KNOWLEDGE BASE - RETRIEVAL EVALUATION")
    print("=" * 80)

    evaluation_results = []

    for index, test_case in enumerate(TEST_CASES, start=1):
        print(f"\nTest {index}/{len(TEST_CASES)}")
        print(f"Query: {test_case['query']}")

        result = evaluate_test(test_case)
        evaluation_results.append(result)

        print(f"Expected source: {result['expected_source']}")
        print(f"Top result:      {result['top_result']}")
        print(f"Top score:       {result['top_score']}")
        print(f"Source in top 3: {result['source_found_in_top_3']}")
        print(f"Keyword in top 3:{result['keyword_found_in_top_3']}")
        print(f"Result:          {result['result']}")

    passed = sum(
        result["result"] == "PASS"
        for result in evaluation_results
    )

    total = len(evaluation_results)

    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    print(f"Tests passed: {passed}/{total}")

    print("\n" + "-" * 80)
    print(f"{'Query':<50} {'Top Source':<25} {'Result'}")
    print("-" * 80)

    for result in evaluation_results:
        query = result["query"]

        if len(query) > 47:
            query = query[:44] + "..."

        source = result["top_result"]

        if len(source) > 22:
            source = source[:19] + "..."

        print(
            f"{query:<50} "
            f"{source:<25} "
            f"{result['result']}"
        )

    print("-" * 80)

    output_path = PROJECT_ROOT / "retrieval" / "retrieval_test_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "total_tests": total,
                "passed_tests": passed,
                "results": evaluation_results,
            },
            file,
            indent=4,
        )

    print(f"\nResults saved to:")
    print(output_path)

    print("\nRETRIEVAL EVALUATION COMPLETE")


if __name__ == "__main__":
    main()