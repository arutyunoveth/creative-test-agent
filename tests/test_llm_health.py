from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_llm_health_with_stub():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/llm/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "stub"
    assert data["available"] is True
    assert data["local_only_mode"] is True


async def test_llm_health_returns_expected_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/llm/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "provider" in data
    assert "model" in data
    assert "base_url" in data
    assert "available" in data
    assert "local_only_mode" in data
