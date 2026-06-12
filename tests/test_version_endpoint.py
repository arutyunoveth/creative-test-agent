from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_version_returns_app_metadata():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/version")
    assert resp.status_code == 200
    data = resp.json()
    assert "app_name" in data
    assert "version" in data
    assert "stage" in data
    assert data["stage"] == "pilot"


async def test_version_has_pilot_stage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/version")
    assert resp.status_code == 200
    assert resp.json()["stage"] == "pilot"


async def test_ui_shows_version():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "0.1.0-pilot" in resp.text or "pilot" in resp.text
