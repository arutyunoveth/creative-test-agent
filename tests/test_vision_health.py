from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_vision_health_with_stub():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/vision/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "stub"
    assert data["available"] is True
    assert data["local_ocr_enabled"] is False
    assert data["local_vlm_enabled"] is False


async def test_vision_health_returns_expected_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/vision/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "provider" in data
    assert "local_ocr_enabled" in data
    assert "local_vlm_enabled" in data
    assert "available" in data
    assert "warnings" in data
