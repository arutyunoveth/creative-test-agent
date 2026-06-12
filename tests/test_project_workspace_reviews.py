from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_reviews_filtered_by_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "Project Review", "asset_type": "text", "text_content": "Test",
            "project_id": "proj-test-123",
        })).json()
        await client.post("/reviews", json={
            "creative_asset_id": asset["id"],
            "reviewer": "tester",
            "project_id": "proj-test-123",
        })
        resp = await client.get("/reviews?project_id=proj-test-123")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert all(r["project_id"] == "proj-test-123" for r in data)


async def test_reviews_by_asset_and_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "Multi Filter", "asset_type": "text", "text_content": "Test",
            "project_id": "proj-multi",
        })).json()
        await client.post("/reviews", json={
            "creative_asset_id": asset["id"],
            "reviewer": "tester",
            "project_id": "proj-multi",
        })
        resp = await client.get(f"/reviews?creative_asset_id={asset['id']}&project_id=proj-multi")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["creative_asset_id"] == asset["id"] and r["project_id"] == "proj-multi" for r in data)
