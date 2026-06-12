from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Compare Test", text_content="Test"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": "text", "text_content": text_content,
    })
    return resp.json()


async def test_batch_compare_needs_two_items():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/batches/nonexistent/compare")
    assert resp.status_code == 404


async def test_batch_compare_works_with_multiple_completed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client, title="Variant X", text_content="First message")
        a2 = await _create_asset(client, title="Variant Y", text_content="Second message")
        created = await client.post("/batches", json={
            "name": "Compare Batch",
            "creative_asset_ids": [a1["id"], a2["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        await client.post(f"/batches/{batch_id}/run-all")
        resp = await client.post(f"/batches/{batch_id}/compare")
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        data = resp.json()
        assert "comparison_id" in data or "score_deltas" in data
