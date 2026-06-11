from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_dashboard_returns_200():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")


async def test_dashboard_shows_app_name():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui")
    assert resp.status_code == 200
    assert "Creative Test Agent" in resp.text


async def test_dashboard_shows_closed_loop_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "Closed-loop mode" in resp.text
    assert "Cloud LLMs" in resp.text
    assert "Provider" in resp.text
