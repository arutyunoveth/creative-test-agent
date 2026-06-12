from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_ui_batches_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/batches")
    assert resp.status_code == 200
    assert "Batches" in resp.text or "batches" in resp.text


async def test_ui_batches_new():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/batches/new")
    assert resp.status_code == 200
    assert "New" in resp.text


async def test_ui_batches_detail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = (await client.post("/creative-assets", json={
            "title": "UI Batch", "asset_type": "text", "text_content": "Test",
        })).json()
        created = await client.post("/batches", json={
            "name": "UI Detail Batch",
            "creative_asset_ids": [a1["id"]],
        })
        batch_id = created.json()["id"]
        resp = await client.get(f"/ui/batches/{batch_id}")
    assert resp.status_code == 200
    assert "UI Detail Batch" in resp.text


async def test_ui_batches_create():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = (await client.post("/creative-assets", json={
            "title": "UI Create", "asset_type": "text", "text_content": "Test",
        })).json()
        resp = await client.post("/ui/batches", data={
            "name": "UI Created Batch",
            "creative_asset_ids": a1["id"],
        })
    assert resp.status_code in (200, 303)
