from ingestion.chunker import (
    split_into_sentences,
    count_words,
    create_chunks,
    chunk_document,
    chunk_documents,
)


def test_split_into_sentences_handles_empty_text():
    assert split_into_sentences("") == []
    assert split_into_sentences("   ") == []


def test_split_into_sentences_splits_and_trims():
    result = split_into_sentences(
        " First sentence. Second sentence! Third sentence?"
    )
    assert result == [
        "First sentence.",
        "Second sentence!",
        "Third sentence?",
    ]


def test_count_words():
    assert count_words("business loan eligibility") == 3
    assert count_words("") == 0


def test_create_chunks_returns_empty_for_blank_text():
    assert create_chunks("") == []
    assert create_chunks("   ") == []


def test_create_chunks_rejects_invalid_overlap():
    try:
        create_chunks("One sentence.", chunk_size=10, chunk_overlap=10)
    except ValueError as exc:
        assert "smaller than chunk_size" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid overlap")


def test_chunk_document_preserves_metadata():
    document = {
        "source": "faq.txt",
        "file_type": ".txt",
        "category": "faq",
        "pii_detected": True,
        "pii_types": ["phone"],
        "text": "The business must operate for 24 months. The applicant must provide bank statements.",
    }

    chunks = chunk_document(document, chunk_size=8, chunk_overlap=2)

    assert chunks
    for index, chunk in enumerate(chunks):
        assert chunk["source"] == "faq.txt"
        assert chunk["file_type"] == ".txt"
        assert chunk["category"] == "faq"
        assert chunk["pii_detected"] is True
        assert chunk["pii_types"] == ["phone"]
        assert chunk["chunk_index"] == index
        assert chunk["chunk_id"] == f"faq.txt::chunk_{index}"
        assert chunk["text"].strip()


def test_chunk_documents_flattens_multiple_documents():
    documents = [
        {
            "source": "a.txt",
            "file_type": ".txt",
            "category": "faq",
            "text": "First document has useful information.",
        },
        {
            "source": "b.txt",
            "file_type": ".txt",
            "category": "eligibility",
            "text": "Second document has other useful information.",
        },
    ]

    chunks = chunk_documents(documents, chunk_size=80, chunk_overlap=20)

    assert len(chunks) == 2
    assert {chunk["source"] for chunk in chunks} == {"a.txt", "b.txt"}
