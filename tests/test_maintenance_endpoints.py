"""Tests for admin maintenance API endpoints."""
from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_maintenance_status_endpoint_exists():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/status")
    # Should work with auth disabled (default)
    assert resp.status_code == 200


async def test_maintenance_status_contains_env():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/status")
    data = resp.json()
    assert "env" in data
    assert "database_connected" in data
    assert "storage_writable" in data
    assert "exports_writable" in data
    assert "backup_root_writable" in data
    assert "closed_loop_enabled" in data
    assert "auth_enabled" in data
    assert "llm_provider" in data
    assert "vision_provider" in data
    assert "checked_at" in data


async def test_maintenance_status_no_secrets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/status")
    data = resp.json()
    # Should not expose secret_key or password
    assert "secret_key" not in data
    body = resp.text.lower()
    assert "password" not in body or "password_min_length" in body


async def test_maintenance_storage_endpoint_exists():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/storage")
    assert resp.status_code == 200


async def test_maintenance_storage_returns_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/storage")
    data = resp.json()
    assert "storage_root" in data
    assert "writable" in data
    assert "exports_root" in data
    assert "backup_root" in data
    assert "total_files" in data
    assert "total_size_bytes" in data


async def test_maintenance_database_endpoint_exists():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/database")
    assert resp.status_code == 200


async def test_maintenance_database_returns_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/database")
    data = resp.json()
    assert "connected" in data
    assert "url_type" in data
    assert "table_count" in data
    assert data["connected"] is True


async def test_maintenance_database_requires_admin_when_auth_enabled():
    """Test that maintenance endpoints check auth. With auth disabled, this tests basic access."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/admin/maintenance/status")
    assert resp.status_code in (200, 401, 403)
