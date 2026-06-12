from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_list_reviews_by_asset():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "Perm Test", "asset_type": "text", "text_content": "Test",
        })).json()
        await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        resp = await client.get(f"/reviews?creative_asset_id={asset['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["creative_asset_id"] == asset["id"] for r in data)


async def test_filter_reviews_by_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "Status Filter", "asset_type": "text", "text_content": "Test",
        })).json()
        await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        resp = await client.get("/reviews?status=draft")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["status"] == "draft" for r in data)


async def test_update_review_decision_and_rating():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "Decision Test", "asset_type": "text", "text_content": "Test",
        })).json()
        created = (await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })).json()
        resp = await client.patch(f"/reviews/{created['id']}", json={
            "decision": "approve", "rating": 5,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "approve"
    assert data["rating"] == 5
