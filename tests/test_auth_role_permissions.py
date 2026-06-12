"""Tests for role-based permissions when auth is enabled."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_with_auth(monkeypatch):
    monkeypatch.setenv("CTA_ENABLE_AUTH", "true")
    monkeypatch.setenv("CTA_SECRET_KEY", "test-secret-key-for-permissions")
    from src.shared.config.settings import get_settings
    get_settings.cache_clear()
    from src.main import app
    yield app
    get_settings.cache_clear()


def _make_user(email, role_str, pw="test-password-here"):
    from src.modules.users.models import UserRole
    from src.modules.users.schemas import CreateUserRequest
    from src.modules.users.service import create_user, get_user_by_email, get_user
    role = getattr(UserRole, role_str, UserRole.viewer)
    existing_model = get_user_by_email(email)
    if existing_model:
        uid = existing_model.id
        return get_user(uid)
    return create_user(CreateUserRequest(
        email=email, display_name=role_str, role=role,
        is_active=True, password=pw,
    ))


async def _login(client, email, pw="test-password-here"):
    resp = await client.post("/auth/login", json={"email": email, "password": pw})
    assert resp.status_code == 200
    token = resp.json()["token"]
    client.cookies.set("cta_session", token)


async def test_viewer_cannot_write(app_with_auth):
    _make_user("viewer@test.local", "viewer")
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _login(client, "viewer@test.local")
        resp = await client.post("/creative-assets", json={
            "title": "Viewer Asset", "asset_type": "text", "text_content": "test",
        })
    assert resp.status_code == 403


async def test_analyst_can_write(app_with_auth):
    _make_user("analyst@test.local", "analyst")
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _login(client, "analyst@test.local")
        resp = await client.post("/creative-assets", json={
            "title": "Analyst Asset", "asset_type": "text", "text_content": "test",
        })
    assert resp.status_code == 201


async def test_manager_can_create_project(app_with_auth):
    _make_user("manager@test.local", "manager")
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _login(client, "manager@test.local")
        c_resp = await client.post("/clients", json={"name": "Manager Client"})
        c_id = c_resp.json()["id"]
        p_resp = await client.post("/projects", json={"client_id": c_id, "name": "Manager Project"})
    assert p_resp.status_code == 201


async def test_admin_can_create_user(app_with_auth):
    _make_user("superadmin@test.local", "admin")
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _login(client, "superadmin@test.local")
        resp = await client.post("/users", json={
            "email": "newuser@test.local",
            "display_name": "New User",
            "role": "viewer",
            "password": "new-user-password",
        })
    assert resp.status_code == 201


async def test_non_admin_cannot_create_user(app_with_auth):
    _make_user("nonadmin@test.local", "manager")
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _login(client, "nonadmin@test.local")
        resp = await client.post("/users", json={
            "email": "shouldfail@test.local",
            "display_name": "Should Fail",
            "role": "viewer",
        })
    assert resp.status_code == 403


async def test_anonymous_request_rejected(app_with_auth):
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/creative-assets", json={
            "title": "No Auth", "asset_type": "text", "text_content": "test",
        })
    assert resp.status_code == 401
