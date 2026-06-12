from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_version_returns_rc1():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/version")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "0.1.0-rc1"


async def test_version_stage_is_pilot():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/version")
    assert resp.status_code == 200
    assert resp.json()["stage"] == "pilot"


async def test_ui_shows_rc_version():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "0.1.0-rc1" in resp.text or "rc1" in resp.text
