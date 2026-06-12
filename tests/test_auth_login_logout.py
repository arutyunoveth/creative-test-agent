"""Tests for login/logout flow with auth enabled."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_with_auth(monkeypatch):
    monkeypatch.setenv("CTA_ENABLE_AUTH", "true")
    monkeypatch.setenv("CTA_SECRET_KEY", "test-secret-key-for-tests")
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_EMAIL", "admin@test.local")
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_PASSWORD", "test-password-here")
    from src.shared.config.settings import get_settings
    get_settings.cache_clear()
    from src.main import app
    return app


@pytest.fixture
def admin_user(app_with_auth):
    from src.modules.users.models import UserRole
    from src.modules.users.schemas import CreateUserRequest
    from src.modules.users.service import create_user, get_user_by_email
    existing_model = get_user_by_email("admin@test.local")
    if existing_model:
        return True
    create_user(CreateUserRequest(
        email="admin@test.local",
        display_name="Test Admin",
        role=UserRole.admin,
        is_active=True,
        password="test-password-here",
    ))
    return True


async def test_login_with_valid_credentials(app_with_auth, admin_user):
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/auth/login", json={
            "email": "admin@test.local",
            "password": "test-password-here",
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] is not None
    assert data["role"] == "admin"
    assert data["token"] is not None


async def test_login_with_wrong_password(app_with_auth, admin_user):
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/auth/login", json={
            "email": "admin@test.local",
            "password": "wrong-password",
        })
    assert resp.status_code == 401


async def test_logout_clears_session(app_with_auth):
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Logged out"


async def test_auth_me_after_login(app_with_auth, admin_user):
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/auth/login", json={
            "email": "admin@test.local",
            "password": "test-password-here",
        })
        token = login_resp.json()["token"]
        client.cookies.set("cta_session", token)
        me_resp = await client.get("/auth/me")
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["role"] == "admin"
    assert data["auth_enabled"] is True


async def test_inactive_user_cannot_login(app_with_auth, admin_user):
    from src.modules.users.models import UserRole
    from src.modules.users.schemas import CreateUserRequest
    from src.modules.users.service import create_user
    try:
        create_user(CreateUserRequest(
            email="inactive-login@test.local",
            display_name="Inactive",
            role=UserRole.viewer,
            is_active=False,
            password="test-password-here",
        ))
    except ValueError:
        pass
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/auth/login", json={
            "email": "inactive-login@test.local",
            "password": "test-password-here",
        })
    assert resp.status_code == 401
