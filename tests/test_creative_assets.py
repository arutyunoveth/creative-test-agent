from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_create_creative_asset():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/creative-assets",
            json={
                "title": "Test Ad",
                "asset_type": "text",
                "text_content": "Buy now!",
                "metadata": {"campaign": "test"},
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Ad"
    assert data["asset_type"] == "text"
    assert data["text_content"] == "Buy now!"
    assert "id" in data


async def test_list_creative_assets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/creative-assets")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
