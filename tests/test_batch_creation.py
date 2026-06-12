from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Batch Test", text_content="Test"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": "text", "text_content": text_content,
    })
    return resp.json()


async def test_create_batch():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        a2 = await _create_asset(client)
        resp = await client.post("/batches", json={
            "name": "Test Campaign",
            "creative_asset_ids": [a1["id"], a2["id"]],
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Campaign"
    assert data["status"] == "draft"
    assert len(data["creative_asset_ids"]) == 2


async def test_get_batch():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Get Test", "creative_asset_ids": [a1["id"]],
        })
        batch_id = created.json()["id"]
        resp = await client.get(f"/batches/{batch_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == batch_id


async def test_list_batches():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/batches")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_batch_with_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        resp = await client.post("/batches", json={
            "name": "Project Batch",
            "project_id": "proj-test-456",
            "creative_asset_ids": [a1["id"]],
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["project_id"] == "proj-test-456"


async def test_batch_creates_items_on_queue():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        a2 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Queue Test",
            "creative_asset_ids": [a1["id"], a2["id"]],
        })
        batch_id = created.json()["id"]
        resp = await client.post(f"/batches/{batch_id}/queue")
        assert resp.status_code == 200
        items_resp = await client.get(f"/batches/{batch_id}/items")
        items = items_resp.json()
    assert len(items) == 2
