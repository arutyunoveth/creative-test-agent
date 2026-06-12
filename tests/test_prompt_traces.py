"""Prompt trace service tests."""

import pytest
from src.modules.prompt_traces.models import PromptTrace
from src.modules.prompt_traces.service import (
    create_trace,
    get_trace,
    list_traces,
    get_trace_count,
)
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


def test_create_and_get_trace():
    t = create_trace(
        stage_name="creative_summary",
        provider="stub",
        model="stub",
        prompt_hash="abc123",
        parsed_success=True,
    )
    assert t.id
    assert t.stage_name == "creative_summary"
    assert t.provider == "stub"
    assert t.parsed_success is True


def test_get_missing_trace():
    assert get_trace("nonexistent") is None


def test_list_traces_returns_list():
    assert isinstance(list_traces(), list)


def test_list_traces_with_data():
    create_trace(stage_name="test_stage", provider="stub", model="stub", prompt_hash="h1")
    traces = list_traces()
    assert len(traces) >= 1


def test_trace_with_repair_info():
    t = create_trace(
        stage_name="brand_safety_review",
        provider="ollama",
        model="qwen2.5:7b",
        prompt_hash="def456",
        parsed_success=True,
        repaired=True,
        repair_steps=["removed_markdown_fence", "trimmed_outer_text"],
        validation_warnings=["missing optional field"],
        validation_errors=[],
    )
    assert t.repaired is True
    assert len(t.repair_steps) == 2
    assert len(t.validation_warnings) == 1


def test_trace_preview_truncation():
    long_text = "x" * 5000
    t = create_trace(
        stage_name="test_stage",
        provider="stub",
        model="stub",
        prompt_hash="h2",
        prompt_text=long_text,
        raw_response=long_text,
        parsed_success=True,
    )
    assert t.prompt_preview is not None
    # Preview should be shorter than full text (not stored full by default)
    assert len(t.prompt_preview) <= 2100  # preview chars + possible ellipsis


def test_trace_with_errors():
    t = create_trace(
        stage_name="rubric_scoring",
        provider="stub",
        model="stub",
        prompt_hash="h3",
        parsed_success=False,
        repaired=False,
        validation_errors=["Missing required field: scorecard"],
    )
    assert t.parsed_success is False
    assert len(t.validation_errors) == 1


def test_trace_count():
    create_trace(stage_name="s1", provider="stub", model="stub", prompt_hash="h4")
    create_trace(stage_name="s2", provider="stub", model="stub", prompt_hash="h5")
    count = get_trace_count()
    assert count["trace_count"] >= 2


def test_trace_model_fields():
    assert hasattr(PromptTrace, "stage_name")
    assert hasattr(PromptTrace, "provider")
    assert hasattr(PromptTrace, "model")
    assert hasattr(PromptTrace, "prompt_hash")
    assert hasattr(PromptTrace, "parsed_success")
    assert hasattr(PromptTrace, "repaired")
    assert hasattr(PromptTrace, "latency_ms")


def test_trace_with_latency():
    t = create_trace(
        stage_name="test",
        provider="stub",
        model="stub",
        prompt_hash="h6",
        parsed_success=True,
        latency_ms=123.45,
        token_estimate_input=100,
        token_estimate_output=50,
    )
    assert t.latency_ms == 123.45
    assert t.token_estimate_input == 100
    assert t.token_estimate_output == 50
