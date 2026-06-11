from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_existing_report_endpoint_still_works():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Backward Compat", "asset_type": "text", "text_content": "Hello"},
        )
    asset_id = create_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(f"/test-runs/{run_id}/run")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        report_resp = await client.get(f"/reports/{run_id}")
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert report_data["test_run_id"] == run_id
    assert report_data["summary"] != ""
    assert len(report_data["scorecard"]) > 0
    assert report_data["final_recommendation"] in ("show_to_client", "revise", "reject")
    assert "# Creative Pre-Test Report" in report_data["report_markdown"]
    assert report_data.get("id", "") != ""
    assert report_data.get("version", 0) >= 1
    assert report_data.get("report_mode") == "internal"
    assert report_data.get("report_format") == "json"


async def test_report_with_format_markdown():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Markdown Report", "asset_type": "text", "text_content": "Test content"},
        )
    asset_id = create_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(f"/test-runs/{run_id}/run")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert data["report_format"] == "markdown"
    assert "## Executive Summary" in data["report_markdown"]
    assert "## Creative Overview" in data["report_markdown"]
    assert "## Scorecard" in data["report_markdown"]
