"""Tests for project-scoped entity creation forms."""
from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_creative_asset_form_has_project_id_field():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/creative-assets/new")
    assert resp.status_code == 200
    assert "project_id" in resp.text


async def test_creative_asset_form_shows_preset_project_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/creative-assets/new?project_id=test-proj-123")
    assert resp.status_code == 200
    assert 'value="test-proj-123"' in resp.text


async def test_test_run_form_has_project_id_field():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/test-runs/new")
    assert resp.status_code == 200
    assert "project_id" in resp.text


async def test_test_run_form_shows_preset_project_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/test-runs/new?project_id=test-proj-456")
    assert resp.status_code == 200
    assert 'value="test-proj-456"' in resp.text


async def test_brandbook_form_has_project_id_field():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/brandbooks/new")
    assert resp.status_code == 200
    assert "Project ID" in resp.text


async def test_create_creative_asset_with_project_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await client.post("/ui/clients", data={"name": "Scoped Client"}, follow_redirects=False)
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Scoped Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]

        resp = await client.post(
            "/ui/creative-assets",
            data={"title": "Scoped Asset", "asset_type": "text", "text_content": "Scoped", "project_id": p_id},
            follow_redirects=True,
        )
    assert resp.status_code == 200
    assert "Scoped Asset" in resp.text


async def test_dashboard_shows_project_counts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await client.post("/ui/clients", data={"name": "Dash Client"}, follow_redirects=False)
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Dash Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]

        await client.post(
            "/ui/creative-assets",
            data={"title": "Dash Asset", "asset_type": "text", "text_content": "Dash", "project_id": p_id},
        )

        dash_resp = await client.get(f"/ui/projects/{p_id}")
    assert dash_resp.status_code == 200
    assert "Dash Asset" in dash_resp.text or "Creative Assets" in dash_resp.text


async def test_project_empty_state():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await client.post("/ui/clients", data={"name": "Empty State Client"}, follow_redirects=False)
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Empty State Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]

        dash_resp = await client.get(f"/ui/projects/{p_id}")
    assert dash_resp.status_code == 200
    assert "Empty State Project" in dash_resp.text
    assert "No activity yet" in dash_resp.text