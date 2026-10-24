
try:
    from q2_knowledge_base.retrieval.rag_answer import (
        format_answer_with_citations,
    )
except ModuleNotFoundError:
    from retrieval.rag_answer import (
        format_answer_with_citations,
    )


def test_citations_include_source_and_chunk():
    answer = "The minimum business vintage is 24 months."
    sources = [
        {
            "source": "eligibility_rules.pdf",
            "chunk_id": "eligibility_rules.pdf::chunk_0",
        }
    ]

    result = format_answer_with_citations(answer, sources)

    assert answer in result
    assert "eligibility_rules.pdf" in result
    assert "eligibility_rules.pdf::chunk_0" in result


def test_duplicate_citations_are_removed():
    sources = [
        {
            "source": "faq.txt",
            "chunk_id": "faq.txt::chunk_1",
        },
        {
            "source": "faq.txt",
            "chunk_id": "faq.txt::chunk_1",
        },
    ]

    result = format_answer_with_citations("Test answer.", sources)

    assert result.count("faq.txt::chunk_1") == 1


def test_missing_sources_leave_answer_unchanged():
    answer = "I could not verify that information."

    assert format_answer_with_citations(answer, []) == answer


def test_missing_chunk_id_uses_filename():
    result = format_answer_with_citations(
        "Test answer.",
        [{"source": "faq.txt"}],
    )

    assert "faq.txt" in result


def test_missing_source_metadata_does_not_add_empty_citation():
    answer = "Test answer."

    result = format_answer_with_citations(
        answer,
        [{"category": "faq", "text": "Example content"}],
    )

    assert result == answer
