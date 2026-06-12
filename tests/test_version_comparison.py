from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client):
    resp = await client.post("/creative-assets", json={
        "title": "Compare Test", "asset_type": "text", "text_content": "Test",
    })
    return resp.json()


async def test_compare_versions_needs_two_assets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/creative-assets/compare-versions", json={"asset_ids": ["one"]})
    assert resp.status_code == 400
    assert "two" in resp.json()["detail"].lower()


async def test_compare_versions_nonexistent_asset():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/creative-assets/compare-versions", json={
            "asset_ids": ["nonexistent1", "nonexistent2"],
        })
    assert resp.status_code == 404


async def test_compare_versions_returns_structure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        a2 = await _create_asset(client)
        resp = await client.post("/creative-assets/compare-versions", json={
            "asset_ids": [a1["id"], a2["id"]],
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "assets" in data
    assert len(data["assets"]) == 2
    for entry in data["assets"]:
        assert "asset_id" in entry
        assert "title" in entry
        assert "has_report" in entry
