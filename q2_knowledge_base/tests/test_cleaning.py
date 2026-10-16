from ingestion.cleaner import normalize_whitespace, normalize_text


def test_normalize_whitespace_converts_windows_line_endings():
    assert normalize_whitespace("First\r\nSecond") == "First\nSecond"


def test_normalize_whitespace_trims_lines():
    assert normalize_whitespace("  First  \n  Second  ") == "First\nSecond"


def test_normalize_whitespace_collapses_repeated_blank_lines():
    result = normalize_whitespace("First\n\n\nSecond")
    assert result == "First\n\nSecond"


def test_normalize_whitespace_handles_blank_input():
    assert normalize_whitespace("") == ""
    assert normalize_whitespace("   \r\n  ") == ""


def test_normalize_text_normalizes_visible_dash_artifacts():
    result = normalize_text("A - B and C - D")
    assert result == "A - B and C - D"
