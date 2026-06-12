"""Tests that auth disabled mode works exactly as before."""

import os

from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_auth_me_returns_system_user():
    """GET /auth/me returns system user when auth disabled."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "system"
    assert data["role"] == "admin"
    assert data["auth_enabled"] is False


async def test_users_me_returns_system_user():
    """GET /users/me returns system user info when auth disabled."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "system"


async def test_write_endpoints_work_without_auth():
    """POST endpoints work without auth when auth disabled."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/creative-assets", json={
            "title": "Auth Disabled Asset",
            "asset_type": "text",
            "text_content": "test",
        })
    assert resp.status_code == 201


async def test_login_returns_auth_disabled_message():
    """POST /auth/login returns auth disabled message."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/auth/login", json={
            "email": "test@test.com",
            "password": "test",
        })
    assert resp.status_code == 200
    assert resp.json()["auth_enabled"] is False


async def test_ui_login_page_shows_auth_disabled():
    """GET /ui/login shows auth disabled message."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/login")
    assert resp.status_code == 200
    assert "Auth disabled" in resp.text or "auth" in resp.text.lower()
