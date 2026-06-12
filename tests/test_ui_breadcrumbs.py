from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_dashboard_link_present():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert "Dashboard" in resp.text


async def test_clients_page_has_breadcrumbs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/clients")
    assert resp.status_code == 200
