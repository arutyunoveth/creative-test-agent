"""Evaluation API tests."""

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


def test_post_run_evaluation(client):
    resp = client.post("/evaluations/run", json={"case_ids": ["novabank_variant_a"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "evaluation_run_id" in data
    assert data["status"] == "completed"


def test_post_run_all_cases(client):
    resp = client.post("/evaluations/run", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_score"] >= 50


def test_get_evaluations_empty(client):
    resp = client.get("/evaluations")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_evaluations_after_run(client):
    client.post("/evaluations/run", json={"case_ids": ["novabank_variant_a"]})
    resp = client.get("/evaluations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


def test_get_evaluation_detail(client):
    run = client.post("/evaluations/run", json={"case_ids": ["novabank_variant_a"]}).json()
    eval_id = run["evaluation_run_id"]
    resp = client.get(f"/evaluations/{eval_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == eval_id
    assert len(data["results"]) == 1


def test_get_evaluation_results(client):
    run = client.post("/evaluations/run", json={"case_ids": ["novabank_variant_a"]}).json()
    eval_id = run["evaluation_run_id"]
    resp = client.get(f"/evaluations/{eval_id}/results")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["case_id"] == "novabank_variant_a"


def test_get_missing_evaluation(client):
    resp = client.get("/evaluations/nonexistent")
    assert resp.status_code == 404


def test_get_missing_results(client):
    resp = client.get("/evaluations/nonexistent/results")
    assert resp.status_code == 404


def test_post_run_invalid_case(client):
    resp = client.post("/evaluations/run", json={"case_ids": ["nonexistent_case"]})
    assert resp.status_code == 200  # handles gracefully


def test_post_run_with_profile(client):
    from src.modules.model_profiles.schemas import CreateModelProfileRequest
    from src.modules.model_profiles.service import create_profile
    p = create_profile(CreateModelProfileRequest(profile_name="api-test", provider="stub", model="stub"))
    resp = client.post("/evaluations/run", json={"profile_id": p.id, "case_ids": ["novabank_variant_a"]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_score"] == 100
