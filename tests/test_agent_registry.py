from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_get_agents_returns_default_roles():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    names = [a["name"] for a in data]
    assert "creative_intake_agent" in names
    assert "audience_simulation_agent" in names
    assert "brand_safety_agent" in names
    assert "rubric_scoring_agent" in names
    assert "report_agent" in names


async def test_register_agent():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/agents/register", json={"name": "test_agent", "description": "test desc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "test_agent"
    assert data["description"] == "test desc"
