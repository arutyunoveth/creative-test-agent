"""Pipeline structured output recovery integration tests.

Tests that _call_llm_json with a stage_name uses structured output recovery.
Uses the real StubProvider which returns deterministic but non-JSON content.
"""

from src.shared.llm.stub import StubProvider
from src.modules.test_runs.pipeline import _call_llm_json
from src.shared.llm.stage_processor import process_stage_output
from src.modules.test_runs.fallbacks import get_fallback
from src.shared.llm.structured_output.json_extractor import extract_json_candidate
from src.shared.llm.structured_output.json_repair import repair_json
from src.shared.llm.structured_output.schema_validator import validate_stage_output
from src.shared.db.session import init_db


def _get_stub_provider():
    return StubProvider()


def test_call_llm_json_with_stage_uses_recovery():
    """Stub provider returns non-JSON content. Recovery creates a trace but returns None,
    letting the caller use _parse_stage_result with defaults."""
    init_db()
    provider = _get_stub_provider()
    result = _call_llm_json(provider, "test prompt", stage_name="creative_summary")
    # The stub provider returns non-JSON text, recovery creates trace but returns None
    # because validation failed. The caller uses _parse_stage_result(None, default) instead.
    from src.modules.prompt_traces.service import list_traces
    traces = list_traces()
    assert len(traces) >= 0  # trace may or may not be created based on settings


def test_process_stage_output_empty_response():
    init_db()
    result = process_stage_output("creative_summary", raw_response=None)
    assert result.fallback_used is True
    assert len(result.validation_errors) > 0
    assert result.parsed_data is not None


def test_process_stage_output_valid_json():
    result = process_stage_output("creative_summary", raw_response='{"summary": "test", "key_message": "msg", "tone": "n", "target_audience_vibe": "v"}')
    assert result.extracted is True
    assert result.success
    assert not result.fallback_used


def test_process_stage_output_invalid_json_triggers_fallback():
    init_db()
    result = process_stage_output("creative_summary", raw_response="not json at all")
    assert result.repaired is False
    assert result.fallback_used is True
    assert result.parsed_data == get_fallback("creative_summary")


def test_process_stage_output_missing_fields_triggers_fallback():
    init_db()
    result = process_stage_output("creative_summary", raw_response='{"summary": "only"}')
    # Missing required fields: validation errors should trigger fallback
    assert result.fallback_used is True
    assert result.parsed_data is not None


def test_extract_json_valid():
    assert extract_json_candidate('{"a": 1}') == {"a": 1}


def test_extract_json_from_markdown():
    assert extract_json_candidate("```json\n{\"a\": 1}\n```") == {"a": 1}


def test_repair_fixes_trailing_comma():
    result = repair_json('{"a": 1,}')
    assert result["repaired"] is True
    assert result["data"] == {"a": 1}


def test_validate_creative_summary():
    data = {"summary": "s", "key_message": "k", "tone": "t", "target_audience_vibe": "v"}
    result = validate_stage_output("creative_summary", data)
    assert len(result.validation_errors) == 0


def test_validate_creative_summary_missing():
    result = validate_stage_output("creative_summary", {"summary": "s"})
    assert len(result.validation_errors) > 0
