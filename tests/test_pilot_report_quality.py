"""Report quality assertions for pilot acceptance."""

from httpx import ASGITransport, AsyncClient
from src.main import app


MARKDOWN_SECTIONS = [
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

HTML_REQUIRED = ["<html", "Creative Pre-Test Report", "Final Recommendation", "Scorecard"]

CLIENT_FACING_FORBIDDEN = ["traceback", "raw finding", "debug", "LLM output"]


async def _completed_run(client, text="Test creative content for report quality checks."):
    create_resp = await client.post(
        "/creative-assets",
        json={"title": "QA Test", "asset_type": "text", "text_content": text},
    )
    asset_id = create_resp.json()["id"]
    run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_markdown_has_all_required_sections():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    md = report_resp.json()["report_markdown"]
    for section in MARKDOWN_SECTIONS:
        assert f"## {section}" in md, f"Missing section: {section}"


async def test_html_has_required_content():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?format=html")
    assert report_resp.status_code == 200
    html = report_resp.json()["report_html"]
    for item in HTML_REQUIRED:
        assert item in html, f"Missing HTML content: {item}"


async def test_client_facing_no_forbidden_phrases():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?mode=client_facing&format=markdown")
    assert report_resp.status_code == 200
    md = report_resp.json()["report_markdown"]
    for phrase in CLIENT_FACING_FORBIDDEN:
        assert phrase not in md.lower(), f"Client-facing report contains forbidden phrase: {phrase}"


async def test_internal_report_has_technical_details():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?mode=internal&format=markdown")
    assert report_resp.status_code == 200
    md = report_resp.json()["report_markdown"]
    assert "## Top Strengths" in md
    assert "## Key Improvement Areas" in md


async def test_client_facing_omits_internal_sections():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _completed_run(client)
        report_resp = await client.get(f"/reports/{run_id}?mode=client_facing&format=markdown")
    assert report_resp.status_code == 200
    md = report_resp.json()["report_markdown"]
    assert "Input context keys" not in md
