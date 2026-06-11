from httpx import ASGITransport, AsyncClient
from src.main import app


async def _setup_completed_run(client, text="UI Report test"):
    create_resp = await client.post(
        "/creative-assets",
        json={"title": "UI Report", "asset_type": "text", "text_content": text},
    )
    asset_id = create_resp.json()["id"]
    run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_report_page_loads_for_completed_run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        resp = await client.get(f"/ui/reports/{run_id}")
    assert resp.status_code == 200
    assert "Report" in resp.text


async def test_compare_page_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _setup_completed_run(client, "A")
        await _setup_completed_run(client, "B")
        resp = await client.get("/ui/compare")
    assert resp.status_code == 200
    assert "Comparison" in resp.text or "Compare" in resp.text


async def test_compare_handles_fewer_than_two_runs_gracefully():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _setup_completed_run(client, "Only one")
        resp = await client.get("/ui/compare")
    assert resp.status_code == 200
    assert "at least 2" in resp.text.lower() or "required" in resp.text.lower()
