"""Tests for project history endpoint."""

from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_project_history_returns_timeline():
    """GET /projects/{id}/history returns a timeline array."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await client.post("/clients", json={"name": "History Test Client"})
        c_id = c_resp.json()["id"]
        p_resp = await client.post("/projects", json={"client_id": c_id, "name": "History Test Project"})
        p_id = p_resp.json()["id"]

        resp = await client.get(f"/projects/{p_id}/history")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


async def test_project_history_with_asset():
    """Project history should include creative assets linked to project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await client.post("/clients", json={"name": "Asset History Client"})
        c_id = c_resp.json()["id"]
        p_resp = await client.post("/projects", json={"client_id": c_id, "name": "Asset History Project"})
        p_id = p_resp.json()["id"]

        await client.post("/creative-assets", json={
            "title": "History Asset",
            "asset_type": "text",
            "text_content": "test",
            "project_id": p_id,
        })

        resp = await client.get(f"/projects/{p_id}/history")
    assert resp.status_code == 200
    data = resp.json()
    types = [e["entity_type"] for e in data]
    assert "creative_asset" in types


async def test_project_history_unknown_project():
    """Unknown project returns empty timeline, not 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/projects/nonexistent_id/history")
    assert resp.status_code == 200
    assert resp.json() == []
