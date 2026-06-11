from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_creative_assets_list_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/creative-assets")
    assert resp.status_code == 200
    assert "Creative Assets" in resp.text


async def test_new_creative_asset_form_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/creative-assets/new")
    assert resp.status_code == 200
    assert "New Creative Asset" in resp.text


async def test_text_creative_can_be_created_through_ui():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/ui/creative-assets",
            data={"title": "UI Test Asset", "asset_type": "text", "text_content": "Hello from UI test"},
            follow_redirects=False,
        )
    assert resp.status_code == 303
    assert "/ui/creative-assets/" in resp.headers.get("location", "")


async def test_creative_asset_detail_shows_after_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/ui/creative-assets",
            data={"title": "Detail Test", "asset_type": "text", "text_content": "Detail content"},
            follow_redirects=True,
        )
    assert create_resp.status_code == 200
    assert "Detail Test" in create_resp.text
