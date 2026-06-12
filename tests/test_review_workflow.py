from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client):
    resp = await client.post("/creative-assets", json={
        "title": "Review Test", "asset_type": "text", "text_content": "Test content",
    })
    return resp.json()


async def test_create_review():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        resp = await client.post("/reviews", json={
            "creative_asset_id": asset["id"],
            "reviewer": "tester",
            "summary": "Looks good",
            "strengths": "Clear messaging",
            "concerns": "None",
            "rating": 4,
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["creative_asset_id"] == asset["id"]
    assert data["reviewer"] == "tester"
    assert data["summary"] == "Looks good"
    assert data["status"] == "draft"


async def test_list_reviews():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        resp = await client.get("/reviews")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


async def test_get_review():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        created = await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        review_id = created.json()["id"]
        resp = await client.get(f"/reviews/{review_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == review_id


async def test_update_review_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        created = await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        review_id = created.json()["id"]
        resp = await client.patch(f"/reviews/{review_id}", json={"status": "in_review"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "in_review"


async def test_review_status_transitions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        created = await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        review_id = created.json()["id"]
        await client.patch(f"/reviews/{review_id}", json={"status": "in_review"})
        resp = await client.patch(f"/reviews/{review_id}", json={"status": "approved"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"


async def test_review_invalid_transition():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        created = await client.post("/reviews", json={
            "creative_asset_id": asset["id"], "reviewer": "tester",
        })
        review_id = created.json()["id"]
        resp = await client.patch(f"/reviews/{review_id}", json={"status": "approved"})
        assert resp.status_code == 404
        assert "Cannot transition" in resp.json()["detail"]
