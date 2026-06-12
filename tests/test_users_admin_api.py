"""Tests for users admin API (auth disabled mode)."""

from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_list_users():
    """GET /users returns a list (system context when auth disabled)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/users")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_create_user():
    """POST /users creates a user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/users", json={
            "email": "unittest@test.local",
            "display_name": "Unit Test",
            "role": "analyst",
            "password": "test-password-for-unit",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "unittest@test.local"
    assert data["role"] == "analyst"
    assert data["is_active"] is True


async def test_create_user_duplicate_email():
    """POST /users with existing email returns 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/users", json={
            "email": "duplicate@test.local",
            "display_name": "First",
            "role": "viewer",
            "password": "test-password-here",
        })
        resp = await client.post("/users", json={
            "email": "duplicate@test.local",
            "display_name": "Second",
            "role": "viewer",
            "password": "test-password-here",
        })
    assert resp.status_code == 400


async def test_get_user():
    """GET /users/{id} returns user detail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/users", json={
            "email": "getuser@test.local",
            "display_name": "Get User",
            "role": "manager",
            "password": "test-password-here",
        })
        uid = create_resp.json()["id"]
        resp = await client.get(f"/users/{uid}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "getuser@test.local"


async def test_update_user():
    """PATCH /users/{id} updates user fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/users", json={
            "email": "updateuser@test.local",
            "display_name": "Before",
            "role": "viewer",
            "password": "test-password-here",
        })
        uid = create_resp.json()["id"]
        resp = await client.patch(f"/users/{uid}", json={"display_name": "After", "role": "analyst"})
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "After"
    assert resp.json()["role"] == "analyst"


async def test_deactivate_user():
    """POST /users/{id}/deactivate deactivates user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/users", json={
            "email": "deactivate@test.local",
            "display_name": "To Deactivate",
            "role": "viewer",
            "password": "test-password-here",
        })
        uid = create_resp.json()["id"]
        resp = await client.post(f"/users/{uid}/deactivate")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_get_user_not_found():
    """GET /users/{id} returns 404 for unknown user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/users/nonexistent")
    assert resp.status_code == 404
