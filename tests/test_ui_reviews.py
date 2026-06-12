from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_ui_reviews_list_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/reviews")
    assert resp.status_code == 200
    assert "Reviews" in resp.text


async def test_ui_reviews_new_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/reviews/new")
    assert resp.status_code == 200
    assert "New Review" in resp.text


async def test_ui_reviews_detail_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "UI Review Test", "asset_type": "text", "text_content": "Test",
        })).json()
        review = (await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })).json()
        resp = await client.get(f"/ui/reviews/{review['id']}")
    assert resp.status_code == 200
    assert "Review" in resp.text
