"""Model profiles UI page tests."""

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


def test_model_profiles_list_page(client):
    resp = client.get("/ui/model-profiles", follow_redirects=True)
    assert resp.status_code == 200
    assert "Model Profiles" in resp.text


def test_model_profiles_new_page(client):
    resp = client.get("/ui/model-profiles/new", follow_redirects=True)
    assert resp.status_code == 200
    assert "New Model Profile" in resp.text


def test_model_profiles_create(client):
    resp = client.post("/ui/model-profiles", data={
        "profile_name": "ui-test-profile",
        "provider": "stub",
        "model": "stub",
        "timeout_seconds": 60,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert "ui-test-profile" in resp.text


def test_model_profiles_create_forbidden_provider(client):
    resp = client.post("/ui/model-profiles", data={
        "profile_name": "bad-profile",
        "provider": "openai",
        "model": "gpt-4",
        "timeout_seconds": 60,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert "not allowed" in resp.text.lower() or "bad-profile" not in resp.text


def test_model_profiles_detail(client):
    create_resp = client.post("/ui/model-profiles", data={
        "profile_name": "detail-test",
        "provider": "stub",
        "model": "stub",
        "timeout_seconds": 60,
    }, follow_redirects=True)
    assert "detail-test" in create_resp.text
    detail_url = create_resp.url
    resp = client.get(detail_url, follow_redirects=True)
    assert resp.status_code == 200


def test_model_profiles_health(client):
    create_resp = client.post("/ui/model-profiles", data={
        "profile_name": "health-ui-test",
        "provider": "stub",
        "model": "stub",
        "timeout_seconds": 60,
    }, follow_redirects=True)
    assert create_resp.status_code == 200
    detail_url = create_resp.url
    health_resp = client.post(f"{detail_url}/health", follow_redirects=True)
    assert health_resp.status_code == 200
    assert "reachable" in health_resp.text.lower() or "Health" in health_resp.text


def test_model_profiles_load_config(client):
    resp = client.post("/ui/model-profiles/load-from-config", follow_redirects=True)
    assert resp.status_code == 200
