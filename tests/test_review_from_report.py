from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client):
    resp = await client.post("/creative-assets", json={
        "title": "Report Review Test", "asset_type": "text", "text_content": "Test",
    })
    return resp.json()


async def _create_completed_test_run(client, asset_id):
    resp = await client.post("/test-runs", json={
        "creative_asset_id": asset_id,
        "brand_profile_id": None,
        "audience_profile_ids": [],
    })
    run_id = resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_create_review_from_report():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset = await _create_asset(client)
        run_id = await _create_completed_test_run(client, asset["id"])
        report_resp = await client.get(f"/reports/{run_id}?format=json&mode=internal")
        assert report_resp.status_code == 200
        report_id = report_resp.json()["id"]

        resp = await client.post(f"/reviews/from-report/{report_id}")
    assert resp.status_code == 201
    data = resp.json()
    assert data["creative_asset_id"] == asset["id"]
    assert data["report_id"] == report_id


async def test_create_review_from_nonexistent_report():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/reviews/from-report/nonexistent")
    assert resp.status_code == 404
