from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_unsupported_report_format_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/reports/nonexistent?format=xml")
    assert resp.status_code == 400
    detail = resp.json()
    assert "unsupported_report_format" in str(detail).lower() or "Unsupported format" in str(detail)


async def test_unsupported_report_mode_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/reports/nonexistent?mode=secret")
    assert resp.status_code == 400
    detail = resp.json()
    assert "unsupported_report_mode" in str(detail).lower() or "Unsupported mode" in str(detail)


async def test_nonexistent_run_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/reports/nonexistent-run-id")
    assert resp.status_code == 404


async def test_created_run_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "No Run", "asset_type": "text", "text_content": "Hello"},
        )
        asset_id = create_resp.json()["id"]
        run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = run_resp.json()["id"]
        resp = await client.get(f"/reports/{run_id}")
    assert resp.status_code == 404
