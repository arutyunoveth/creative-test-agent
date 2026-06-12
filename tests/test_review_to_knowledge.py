from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_save_review_to_knowledge():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset_resp = await client.post("/creative-assets", json={
            "title": "Knowledge Test", "asset_type": "text", "text_content": "Test",
        })
        asset = asset_resp.json()

        review_resp = await client.post("/reviews", json={
            "creative_asset_id": asset["id"],
            "reviewer": "tester",
            "summary": "Good work",
            "strengths": "Clear and concise",
            "concerns": "Minor typos",
        })
        review = review_resp.json()

        resp = await client.post(f"/reviews/{review['id']}/save-to-knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert data["saved"] is True
    assert "knowledge_item_id" in data


async def test_save_empty_review_does_not_create_knowledge():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset_resp = await client.post("/creative-assets", json={
            "title": "Empty Test", "asset_type": "text", "text_content": "Test",
        })
        asset = asset_resp.json()

        review_resp = await client.post("/reviews", json={
            "creative_asset_id": asset["id"],
            "reviewer": "tester",
        })
        review = review_resp.json()

        resp = await client.post(f"/reviews/{review['id']}/save-to-knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert data["saved"] is False
    assert "no substantive content" in data["reason"]
