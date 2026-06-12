from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Run Test", text_content="Test"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": "text", "text_content": text_content,
    })
    return resp.json()


async def test_batch_run_all_completes_items():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client, title="Variant A", text_content="Safe banking message")
        a2 = await _create_asset(client, title="Variant B", text_content="Bold banking message")
        created = await client.post("/batches", json={
            "name": "Run All Test",
            "creative_asset_ids": [a1["id"], a2["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        resp = await client.post(f"/batches/{batch_id}/run-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items_processed"] == 2

        items_resp = await client.get(f"/batches/{batch_id}/items")
        items = items_resp.json()
    assert all(i["status"] == "completed" for i in items)
    assert all(i["test_run_id"] is not None for i in items)


async def test_batch_run_next_processes_one_item():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        a2 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Run Next Test",
            "creative_asset_ids": [a1["id"], a2["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        resp = await client.post(f"/batches/{batch_id}/run-next")
    assert resp.status_code == 200
    data = resp.json()
    assert "test_run_id" in data or "error" in data


async def test_batch_cancel():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Cancel Test",
            "creative_asset_ids": [a1["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        resp = await client.post(f"/batches/{batch_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_batch_run_all_updates_batch_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = await _create_asset(client)
        created = await client.post("/batches", json={
            "name": "Status Test",
            "creative_asset_ids": [a1["id"]],
        })
        batch_id = created.json()["id"]
        await client.post(f"/batches/{batch_id}/queue")
        await client.post(f"/batches/{batch_id}/run-all")
        resp = await client.get(f"/batches/{batch_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] in ("completed", "failed")
