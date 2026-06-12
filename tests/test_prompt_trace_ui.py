"""Prompt trace UI page tests."""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_traces_list_page(client):
    resp = client.get("/ui/prompt-traces", follow_redirects=True)
    assert resp.status_code == 200
    assert "Prompt Traces" in resp.text


def test_traces_detail_page_not_found(client):
    resp = client.get("/ui/prompt-traces/nonexistent", follow_redirects=True)
    assert resp.status_code == 200
    assert "not found" in resp.text.lower() or "Trace" in resp.text


def test_traces_list_page_has_nav(client):
    resp = client.get("/ui/prompt-traces", follow_redirects=True)
    assert resp.status_code == 200
    # Should contain some common page elements
    assert "Creative Test Agent" in resp.text or "Prompt Traces" in resp.text


def test_traces_detail_with_real_trace(client):
    from src.modules.prompt_traces.service import create_trace
    t = create_trace(
        stage_name="ui_test_stage",
        provider="ollama",
        model="qwen2.5:7b",
        prompt_hash="uihash",
        parsed_success=True,
        repaired=True,
        repair_steps=["removed_markdown_fence"],
        validation_warnings=["test warning"],
        latency_ms=150.0,
    )
    resp = client.get(f"/ui/prompt-traces/{t.id}", follow_redirects=True)
    assert resp.status_code == 200
    assert "ui_test_stage" in resp.text
    assert "ollama" in resp.text


def test_test_run_prompt_traces_ui(client):
    resp = client.get("/ui/test-runs/nonexistent/prompt-traces", follow_redirects=True)
    assert resp.status_code == 200
    assert "Prompt Traces" in resp.text


def test_trace_detail_shows_validation_errors(client):
    from src.modules.prompt_traces.service import create_trace
    t = create_trace(
        stage_name="error_stage",
        provider="stub",
        model="stub",
        prompt_hash="errhash",
        parsed_success=False,
        validation_errors=["Missing field", "Wrong type"],
    )
    resp = client.get(f"/ui/prompt-traces/{t.id}", follow_redirects=True)
    assert resp.status_code == 200
    assert "Missing field" in resp.text
