from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_empty_state_clients():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/clients")
    assert resp.status_code == 200
    assert "Clients" in resp.text
    assert "empty-state" in resp.text or "btn-primary" in resp.text


async def test_empty_state_projects():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/projects")
    assert resp.status_code == 200
    assert "Projects" in resp.text
    assert "empty-state" in resp.text or "btn-primary" in resp.text


async def test_empty_state_batches():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/batches")
    assert resp.status_code == 200
    assert "Campaign Batches" in resp.text or "Batches" in resp.text


async def test_empty_state_reviews():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/reviews")
    assert resp.status_code == 200
    assert "Reviews" in resp.text
