from httpx import ASGITransport, AsyncClient
from src.main import app


async def _setup_completed_run(client, text_content="Test creative content"):
    create_resp = await client.post(
        "/creative-assets",
        json={"title": "Report Test", "asset_type": "text", "text_content": text_content},
    )
    asset_id = create_resp.json()["id"]
    run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_markdown_has_all_required_sections():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    md = report_resp.json()["report_markdown"]
    required_sections = [
        "Executive Summary",
        "Creative Overview",
        "Main Message",
        "Audience Reactions",
        "Scorecard",
        "Brand Safety and Risks",
        "Recommendations",
        "Final Recommendation",
        "Appendix: Test Context",
    ]
    for section in required_sections:
        assert f"## {section}" in md, f"Missing section: {section}"


async def test_html_report_returns_html_content():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?format=html")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert data["report_format"] == "html"
    assert data["report_html"] is not None
    assert "<!DOCTYPE html>" in data["report_html"]
    assert "<h1>" in data["report_html"]
    assert "Scorecard" in data["report_html"]
    assert "Final Recommendation" in data["report_html"]


async def test_mode_internal_works():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?mode=internal")
    assert report_resp.status_code == 200
    assert report_resp.json()["report_mode"] == "internal"


async def test_mode_client_facing_works():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?mode=client_facing")
    assert report_resp.status_code == 200
    assert report_resp.json()["report_mode"] == "client_facing"


async def test_client_facing_mode_no_internal_phrases():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)

        internal_resp = await client.get(f"/reports/{run_id}?mode=internal&format=markdown")
        client_resp = await client.get(f"/reports/{run_id}?mode=client_facing&format=markdown")
    assert internal_resp.status_code == 200
    assert client_resp.status_code == 200
    internal_md = internal_resp.json()["report_markdown"]
    client_md = client_resp.json()["report_markdown"]
    assert "Top Strengths" in internal_md or "Key Improvement Areas" in internal_md
    assert "Input context keys" in internal_md
    assert "Input context keys" not in client_md


async def test_html_with_client_facing_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?format=html&mode=client_facing")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert data["report_mode"] == "client_facing"
    assert data["report_format"] == "html"
    assert "Client-Facing" in data["report_html"] or "client-facing" in data["report_html"].lower()
