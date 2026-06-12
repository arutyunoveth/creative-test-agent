"""JSON repair tests."""

from src.shared.llm.structured_output.json_repair import repair_json


def test_clean_json_no_repair():
    result = repair_json('{"key": "value"}')
    assert result["repaired"] is False
    assert result["data"] == {"key": "value"}


def test_empty_input():
    result = repair_json("")
    assert result["repaired"] is False
    assert result["error"] == "empty_input"


def test_none_input():
    result = repair_json(None)
    assert result["repaired"] is False


def test_markdown_fence_removal():
    text = "```json\n{\"key\": \"value\"}\n```"
    result = repair_json(text)
    assert result["repaired"] is True
    assert "removed_markdown_fence" in result["repair_steps"]
    assert result["data"] == {"key": "value"}


def test_markdown_fence_no_lang():
    text = "```\n{\"key\": \"value\"}\n```"
    result = repair_json(text)
    assert result["repaired"] is True
    assert result["data"] == {"key": "value"}


def test_trim_outer_text():
    text = "Some prefix text {\"key\": \"value\"} some suffix"
    result = repair_json(text)
    assert result["repaired"] is True
    assert "trimmed_outer_text" in result["repair_steps"]
    assert result["data"] == {"key": "value"}


def test_trailing_comma_in_object():
    text = '{"key": "value",}'
    result = repair_json(text)
    assert result["repaired"] is True
    assert result["data"] == {"key": "value"}


def test_trailing_comma_in_array():
    text = '{"items": [1, 2, 3,]}'
    result = repair_json(text)
    assert result["repaired"] is True
    assert result["data"] == {"items": [1, 2, 3]}


def test_multiple_repair_steps():
    text = "Some text\n```json\n{\"key\": \"value\",}\n```\nMore text"
    result = repair_json(text)
    assert result["repaired"] is True
    assert len(result["repair_steps"]) >= 1
    assert result["data"] == {"key": "value"}


def test_invalid_json_unrepairable():
    text = "this is definitely not json or even close"
    result = repair_json(text)
    assert result["repaired"] is False
    assert result["error"] == "json_parse_failed"
    assert result["data"] is None


def test_partial_json_unrepairable():
    text = '{"key": "value" "another": "thing"}'
    result = repair_json(text)
    assert result["repaired"] is False


def test_nested_trailing_commas():
    text = '{"outer": {"inner": "val",},}'
    result = repair_json(text)
    assert result["repaired"] is True
    assert result["data"] == {"outer": {"inner": "val"}}


def test_plain_array():
    result = repair_json("[1, 2, 3]")
    assert result["repaired"] is False
    assert result["data"] == [1, 2, 3]


def test_array_with_trailing_comma():
    text = "[1, 2, 3,]"
    result = repair_json(text)
    assert result["repaired"] is True
    assert result["data"] == [1, 2, 3]
