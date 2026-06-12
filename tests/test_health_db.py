from httpx import ASGITransport, AsyncClient

from src.main import app


async def test_health_db_returns_200():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/db")
    assert resp.status_code == 200


async def test_health_db_contains_status_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/db")
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


async def test_health_db_url_is_masked():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/db")
    data = resp.json()
    assert "database_url" in data
    # Should not contain raw password
    assert ":****@" in data["database_url"] or "@" not in data["database_url"]


async def test_health_db_shows_sqlite_scheme():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/db")
    data = resp.json()
    # With in-memory test DB, URL will contain :memory:
    assert ":memory:" in data["database_url"] or "sqlite" in data["database_url"]
