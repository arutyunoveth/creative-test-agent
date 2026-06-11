from httpx import ASGITransport, AsyncClient
from src.main import app


async def _setup_completed_run(client, text="Test content"):
    create_resp = await client.post(
        "/creative-assets",
        json={"title": "Version Test", "asset_type": "text", "text_content": text},
    )
    asset_id = create_resp.json()["id"]
    run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_report_version_increments():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report1 = await client.get(f"/reports/{run_id}")
        report2 = await client.get(f"/reports/{run_id}")
    assert report1.status_code == 200
    assert report2.status_code == 200
    v1 = report1.json()["version"]
    v2 = report2.json()["version"]
    assert v2 == v1 + 1


async def test_different_modes_have_separate_versions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        int1 = await client.get(f"/reports/{run_id}?mode=internal")
        int2 = await client.get(f"/reports/{run_id}?mode=internal")
        cli1 = await client.get(f"/reports/{run_id}?mode=client_facing")
        cli2 = await client.get(f"/reports/{run_id}?mode=client_facing")
    assert int1.json()["version"] == 1
    assert int2.json()["version"] == 2
    assert cli1.json()["version"] == 1
    assert cli2.json()["version"] == 2


async def test_different_formats_have_separate_versions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        j1 = await client.get(f"/reports/{run_id}?format=json")
        j2 = await client.get(f"/reports/{run_id}?format=json")
        m1 = await client.get(f"/reports/{run_id}?format=markdown")
    assert j1.json()["version"] == 1
    assert j2.json()["version"] == 2
    assert m1.json()["version"] == 1


async def test_pdf_stub_generates_report():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?format=pdf_stub")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert data["report_format"] == "pdf_stub"
    assert data["report_markdown"] != ""
    assert data["report_html"] is not None
