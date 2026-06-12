"""Tests for clients and projects API."""

from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_client(client) -> dict:
    resp = await client.post("/clients", json={
        "name": "Test Client",
        "industry": "Tech",
        "description": "A test client",
    })
    return resp.json()


async def _create_project(client, client_id: str) -> dict:
    resp = await client.post("/projects", json={
        "client_id": client_id,
        "name": "Test Project",
        "description": "A test project",
    })
    return resp.json()


async def test_create_client():
    """POST /clients creates and returns a client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/clients", json={
            "name": "Create Client Test",
            "industry": "Finance",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Create Client Test"
    assert data["industry"] == "Finance"
    assert "id" in data


async def test_list_clients():
    """GET /clients returns a list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/clients")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_client():
    """GET /clients/{id} returns the client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await _create_client(client)
        resp = await client.get(f"/clients/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_client_not_found():
    """GET /clients/{id} returns 404 for unknown client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/clients/nonexistent")
    assert resp.status_code == 404


async def test_create_project():
    """POST /projects creates and returns a project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c = await _create_client(client)
        resp = await client.post("/projects", json={
            "client_id": c["id"],
            "name": "Project Alpha",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Project Alpha"
    assert data["client_id"] == c["id"]
    assert "id" in data


async def test_list_projects():
    """GET /projects returns a list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/projects")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_client_projects():
    """GET /clients/{id}/projects returns projects for that client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c = await _create_client(client)
        await _create_project(client, c["id"])
        await _create_project(client, c["id"])
        resp = await client.get(f"/clients/{c['id']}/projects")
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) >= 2
    for p in projects:
        assert p["client_id"] == c["id"]
