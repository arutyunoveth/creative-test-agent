from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_create_and_run_test_run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={
                "title": "Test Ad",
                "asset_type": "text",
                "text_content": "Buy now!",
            },
        )
    assert create_resp.status_code == 201
    asset_id = create_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_resp = await client.post(
            "/test-runs",
            json={"creative_asset_id": asset_id},
        )
    assert run_resp.status_code == 201
    run_data = run_resp.json()
    assert run_data["status"] == "created"
    run_id = run_data["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        exec_resp = await client.post(f"/test-runs/{run_id}/run")
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["status"] == "completed"
    assert len(exec_data["findings"]) > 0
    assert exec_data["completed_at"] is not None
    assert exec_data["summary"] != ""
    assert len(exec_data["scorecard"]) > 0
    assert exec_data["final_recommendation"] in ("show_to_client", "revise", "reject")


async def test_test_run_with_brand_and_rubric():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        asset_resp = await client.post("/creative-assets", json={"title": "Brand Test", "asset_type": "text", "text_content": "Buy now!"})
    asset_id = asset_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        brand_resp = await client.post("/brand-profiles", json={"name": "TestBrand", "tone_of_voice": "professional"})
    brand_id = brand_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        rubric_resp = await client.post("/test-rubrics", json={"name": "TestRubric"})
    rubric_id = rubric_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_resp = await client.post("/test-runs", json={
            "creative_asset_id": asset_id,
            "brand_profile_id": brand_id,
            "rubric_id": rubric_id,
        })
    run_id = run_resp.json()["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        exec_resp = await client.post(f"/test-runs/{run_id}/run")
    assert exec_resp.status_code == 200
    data = exec_resp.json()
    assert data["status"] == "completed"
    assert data["final_recommendation"] in ("show_to_client", "revise", "reject")
    assert len(data["scorecard"]) > 0
    assert data["summary"] != ""


async def test_report_endpoint_returns_structured_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Report Test", "asset_type": "text", "text_content": "Hello"},
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
