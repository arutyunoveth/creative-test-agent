from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_test_runs_list_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/test-runs")
    assert resp.status_code == 200
    assert "Test Runs" in resp.text


async def test_new_test_run_form_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/test-runs/new")
    assert resp.status_code == 200
    assert "New Test Run" in resp.text


async def _setup_text_asset(client):
    resp = await client.post(
        "/creative-assets",
        json={"title": "UI Run Asset", "asset_type": "text", "text_content": "Buy now!"},
    )
    return resp.json()["id"]


async def test_test_run_can_be_created_through_ui():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset_id = await _setup_text_asset(client)
        resp = await client.post(
            "/ui/test-runs",
            data={"creative_asset_id": asset_id},
            follow_redirects=True,
        )
    assert resp.status_code == 200
    assert "Test Run" in resp.text


async def test_test_run_can_be_launched_through_ui_in_stub_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset_id = await _setup_text_asset(client)
        run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        launch_resp = await client.post(
            f"/ui/test-runs/{run_id}/run",
            follow_redirects=True,
        )
    assert launch_resp.status_code == 200
    assert "completed" in launch_resp.text or "Failed" not in launch_resp.text
