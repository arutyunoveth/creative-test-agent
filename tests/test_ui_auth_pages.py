"""Tests for UI auth pages."""

from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_ui_login_page_loads():
    """GET /ui/login loads without error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/login")
    assert resp.status_code == 200


async def test_ui_users_page_loads():
    """GET /ui/users loads without error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/users")
    assert resp.status_code == 200


async def test_ui_users_new_page_loads():
    """GET /ui/users/new loads without error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/users/new")
    assert resp.status_code == 200


async def test_dashboard_shows_user_info():
    """Dashboard shows user context."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "System" in resp.text or "User" in resp.text


async def test_dashboard_shows_auth_status():
    """Dashboard shows auth status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "Auth" in resp.text or "auth" in resp.text
