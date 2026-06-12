from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_ui_asset_detail_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = (await client.post("/creative-assets", json={
            "title": "UI Test", "asset_type": "text", "text_content": "Test",
        })).json()
        resp = await client.get(f"/ui/creative-assets/{asset['id']}")
    assert resp.status_code == 200
    assert "Creative Asset:" in resp.text


async def test_ui_asset_list_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/creative-assets")
    assert resp.status_code == 200
    assert "Creative Assets" in resp.text
