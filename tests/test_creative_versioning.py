from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Test Asset", asset_type="text", text_content="Hello"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": asset_type, "text_content": text_content,
    })
    return resp.json()


async def test_create_version():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        resp = await client.post(f"/creative-assets/{asset['id']}/create-version", json={
            "version_label": "v2",
            "revision_summary": "Updated copy",
            "revision_source": "manual_revision",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["parent_asset_id"] == asset["id"]
    assert data["version_number"] == 1
    assert data["version_label"] == "v2"
    assert data["revision_summary"] == "Updated copy"
    assert data["revision_source"] == "manual_revision"


async def test_create_version_uses_parent_title():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client, title="Original Ad")
        resp = await client.post(f"/creative-assets/{asset['id']}/create-version", json={})
    data = resp.json()
    assert data["title"] == "Original Ad"


async def test_create_version_with_custom_title():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        resp = await client.post(f"/creative-assets/{asset['id']}/create-version", json={
            "title": "Revised Ad Copy",
            "revision_source": "manual_revision",
        })
    data = resp.json()
    assert data["title"] == "Revised Ad Copy"


async def test_get_versions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        await client.post(f"/creative-assets/{asset['id']}/create-version", json={
            "revision_source": "manual_revision",
        })
        resp = await client.get(f"/creative-assets/{asset['id']}/versions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


async def test_get_version_chain():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        v1 = await client.post(f"/creative-assets/{asset['id']}/create-version", json={
            "revision_source": "manual_revision",
        })
        v1_data = v1.json()
        resp = await client.get(f"/creative-assets/{asset['id']}/version-chain")
    assert resp.status_code == 200
    data = resp.json()
    assert data["root"]["id"] == asset["id"]
    assert len(data["versions"]) == 2


async def test_create_version_nonexistent_asset():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/creative-assets/nonexistent/create-version", json={
            "revision_source": "manual_revision",
        })
    assert resp.status_code == 404
