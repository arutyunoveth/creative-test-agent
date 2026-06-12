"""Prompt trace API tests."""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.modules.prompt_traces.service import create_trace
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seeded_trace():
    return create_trace(
        stage_name="api_test_stage",
        provider="stub",
        model="stub",
        prompt_hash="apihash123",
        parsed_success=True,
    )


def test_list_traces_api(client):
    resp = client.get("/prompt-traces")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_trace_api(client, seeded_trace):
    resp = client.get(f"/prompt-traces/{seeded_trace.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage_name"] == "api_test_stage"
    assert data["provider"] == "stub"


def test_get_missing_trace_api(client):
    resp = client.get("/prompt-traces/nonexistent")
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()


def test_list_traces_with_limit(client):
    create_trace(stage_name="s1", provider="stub", model="stub", prompt_hash="h1")
    create_trace(stage_name="s2", provider="stub", model="stub", prompt_hash="h2")
    resp = client.get("/prompt-traces?limit=1")
    data = resp.json()
    assert len(data) <= 1


def test_list_traces_with_offset(client):
    create_trace(stage_name="offset_test", provider="stub", model="stub", prompt_hash="h3")
    resp = client.get("/prompt-traces?offset=0&limit=100")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_test_run_prompt_traces_api(client):
    from src.modules.test_runs.router import router
    resp = client.get("/test-runs/nonexistent/prompt-traces")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_evaluation_prompt_traces_api(client):
    resp = client.get("/evaluations/nonexistent/prompt-traces")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
