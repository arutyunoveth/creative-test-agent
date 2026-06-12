from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Summary Test", text_content="Test content"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": "text", "text_content": text_content,
    })
    return resp.json()


async def test_batch_summary_returns_structure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Summary Test",
            "creative_asset_ids": [a1["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        await client.post(f"/batches/{batch_id}/run-all")
        resp = await client.get(f"/batches/{batch_id}/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "batch_id" in data
    assert "total_items" in data
    assert "completed_items" in data
    assert "score_summary" in data
    assert "risk_summary" in data
    assert "brandbook_compliance_summary" in data


async def test_batch_summary_includes_completed_count():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        a2 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Count Test",
            "creative_asset_ids": [a1["id"], a2["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        await client.post(f"/batches/{batch_id}/run-all")
        resp = await client.get(f"/batches/{batch_id}/summary")
    data = resp.json()
    assert data["completed_items"] >= 1


async def test_batch_summary_identifies_best_creative():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Best Creative Test",
            "creative_asset_ids": [a1["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        await client.post(f"/batches/{batch_id}/run-all")
        resp = await client.get(f"/batches/{batch_id}/summary")
    data = resp.json()
    if data["completed_items"] > 0:
        assert data.get("best_creative_asset_id") is not None
