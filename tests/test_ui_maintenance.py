"""Tests for maintenance UI page."""
from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_maintenance_ui_page_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert resp.status_code == 200


async def test_maintenance_ui_shows_server_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert resp.status_code == 200
    assert "Server Maintenance" in resp.text


async def test_maintenance_ui_shows_db_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert "Database" in resp.text or "DB" in resp.text


async def test_maintenance_ui_shows_storage_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert "Storage" in resp.text or "Writable" in resp.text


async def test_maintenance_ui_shows_closed_loop_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert "Closed-loop" in resp.text


async def test_maintenance_ui_shows_useful_commands():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert "Useful Commands" in resp.text or "Commands" in resp.text


async def test_maintenance_ui_has_back_link():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/admin/maintenance")
    assert "/ui" in resp.text


async def test_maintenance_ui_nav_link_exists():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui")
    assert "/ui/admin/maintenance" in resp.text
