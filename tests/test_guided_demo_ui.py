from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_guided_demo_ui_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/demo")
    assert resp.status_code == 200


async def test_guided_demo_status_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/demo/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "next_recommended_action" in data


async def test_demo_steps_listed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/demo/steps")
    assert resp.status_code == 200
    steps = resp.json()
    assert isinstance(steps, list)
    assert len(steps) >= 5
