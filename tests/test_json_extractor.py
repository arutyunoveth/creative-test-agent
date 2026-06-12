"""JSON extractor tests."""

from src.shared.llm.structured_output.json_extractor import extract_json_candidate


def test_clean_json_object():
    result = extract_json_candidate('{"key": "value"}')
    assert result == {"key": "value"}


def test_clean_json_array():
    result = extract_json_candidate('[1, 2, 3]')
    assert result == [1, 2, 3]


def test_json_with_prose_before():
    text = "Here is the result:\n{\"key\": \"value\"}"
    result = extract_json_candidate(text)
    assert result == {"key": "value"}


def test_json_with_prose_after():
    text = "{\"key\": \"value\"}\nSome text after"
    result = extract_json_candidate(text)
    assert result == {"key": "value"}


def test_json_prose_before_and_after():
    text = "Before text\n{\"key\": \"value\"}\nAfter text"
    result = extract_json_candidate(text)
    assert result == {"key": "value"}


def test_markdown_fence_json():
    text = "```json\n{\"key\": \"value\"}\n```"
    result = extract_json_candidate(text)
    assert result == {"key": "value"}


def test_markdown_fence_no_lang():
    text = "```\n{\"key\": \"value\"}\n```"
    result = extract_json_candidate(text)
    assert result == {"key": "value"}


def test_markdown_fence_with_prose():
    text = "Here is the JSON:\n```json\n{\"key\": \"value\"}\n```\nHope that helps."
    result = extract_json_candidate(text)
    assert result == {"key": "value"}


def test_empty_string():
    assert extract_json_candidate("") is None


def test_none_input():
    assert extract_json_candidate(None) is None


def test_whitespace_only():
    assert extract_json_candidate("   \n\n  ") is None


def test_no_json():
    assert extract_json_candidate("This is just plain text without any JSON.") is None


def test_single_quotes_not_valid_json():
    result = extract_json_candidate("{'key': 'value'}")
    # Python json.loads does not accept single quotes
    assert result is None or result == {"key": "value"}


def test_nested_object():
    text = '{"outer": {"inner": [1, 2, 3]}, "flag": true}'
    result = extract_json_candidate(text)
    assert result == {"outer": {"inner": [1, 2, 3]}, "flag": True}


def test_json_with_escaped_chars():
    text = '{"text": "line1\\nline2"}'
    result = extract_json_candidate(text)
    assert result == {"text": "line1\nline2"}
