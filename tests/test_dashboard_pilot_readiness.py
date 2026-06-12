from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_dashboard_shows_pilot_readiness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "Pilot Readiness" in resp.text


async def test_dashboard_has_quick_actions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "Quick Actions" in resp.text
