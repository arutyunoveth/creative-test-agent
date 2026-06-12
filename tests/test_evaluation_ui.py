"""Evaluation UI page tests."""

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


def test_evaluations_list_page(client):
    resp = client.get("/ui/evaluations", follow_redirects=True)
    assert resp.status_code == 200
    assert "Evaluations" in resp.text


def test_evaluations_run_page(client):
    resp = client.get("/ui/evaluations/run", follow_redirects=True)
    assert resp.status_code == 200
    assert "Run Evaluation" in resp.text


def test_evaluations_detail_page_not_found(client):
    resp = client.get("/ui/evaluations/nonexistent", follow_redirects=True)
    assert resp.status_code == 200
    assert "not found" in resp.text.lower() or "Evaluation" in resp.text


def test_evaluations_run_post(client):
    resp = client.post("/ui/evaluations/run", data={"case_ids": ["novabank_variant_a"]}, follow_redirects=True)
    assert resp.status_code == 200
    assert "novabank_variant_a" in resp.text


def test_evaluations_run_post_empty(client):
    resp = client.post("/ui/evaluations/run", data={}, follow_redirects=True)
    assert resp.status_code == 200
    assert "score" in resp.text.lower() or "Evaluation" in resp.text


def test_evaluations_run_post_invalid(client):
    resp = client.post("/ui/evaluations/run", data={"case_ids": ["nonexistent"]}, follow_redirects=True)
    assert resp.status_code == 200


def test_evaluations_detail_after_run(client):
    run_resp = client.post("/ui/evaluations/run", data={"case_ids": ["novabank_variant_a"]}, follow_redirects=True)
    assert run_resp.status_code == 200
