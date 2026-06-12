from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Test Asset", asset_type="text", text_content="Hello"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": asset_type, "text_content": text_content,
    })
    return resp.json()


async def test_asset_response_has_version_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        resp = await client.get(f"/creative-assets/{asset['id']}")
    data = resp.json()
    assert "parent_asset_id" in data
    assert "version_label" in data
    assert "version_number" in data
    assert "revision_summary" in data
    assert "revision_source" in data


async def test_asset_response_version_fields_are_null_for_original():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        resp = await client.get(f"/creative-assets/{asset['id']}")
    data = resp.json()
    assert data["parent_asset_id"] is None
    assert data["version_label"] is None
    assert data["version_number"] is None
    assert data["revision_summary"] is None
    assert data["revision_source"] is None


async def test_version_chain_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        await client.post(f"/creative-assets/{asset['id']}/create-version", json={
            "revision_source": "manual_revision",
        })
        chain = await client.get(f"/creative-assets/{asset['id']}/version-chain")
    data = chain.json()
    assert "root" in data
    assert "versions" in data
    assert data["root"]["id"] == asset["id"]


async def test_create_version_with_text_content():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client, text_content="Original text")
        resp = await client.post(f"/creative-assets/{asset['id']}/create-version", json={
            "text_content": "Revised text",
            "revision_source": "manual_revision",
        })
    data = resp.json()
    assert data["text_content"] == "Revised text"
