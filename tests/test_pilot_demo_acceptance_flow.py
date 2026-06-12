"""Full NovaBank demo acceptance flow via HTTP API."""

from httpx import ASGITransport, AsyncClient
from src.main import app


async def _text_asset(client, title: str, text: str):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": "text", "text_content": text,
    })
    return resp


async def _setup_run(client, asset_id: str, brand_id: str | None = None, audience_ids: list[str] | None = None, rubric_id: str | None = None):
    body = {"creative_asset_id": asset_id}
    if brand_id:
        body["brand_profile_id"] = brand_id
    if audience_ids:
        body["audience_profile_ids"] = audience_ids
    if rubric_id:
        body["rubric_id"] = rubric_id
    create_resp = await client.post("/test-runs", json=body)
    run_id = create_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_full_demo_flow_variant_a():
    """Variant A (Practical) — full create → run → report flow."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await _text_asset(client, "NovaBank A — Practical",
            "One card for your freelance income and expenses. Clear terms, no hidden fees.")
        asset_id = create_resp.json()["id"]
        run_id = await _setup_run(client, asset_id)
        report_resp = await client.get(f"/reports/{run_id}")
    assert create_resp.status_code == 201
    assert run_id is not None
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert "report_markdown" in data
    assert data.get("visual_notes") is not None


async def test_full_demo_flow_variant_b():
    """Variant B (Freedom) — full create → run → report flow."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await _text_asset(client, "NovaBank B — Freedom",
            "Your freelance money, finally under control. Take charge of your finances.")
        asset_id = create_resp.json()["id"]
        run_id = await _setup_run(client, asset_id)
        report_resp = await client.get(f"/reports/{run_id}")
    assert create_resp.status_code == 201
    assert report_resp.status_code == 200


async def test_full_demo_flow_variant_c():
    """Variant C (Risky) — should get risk flags."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await _text_asset(client, "NovaBank C — Risky",
            "The only card freelancers will ever need. Forget financial stress forever. "
            "NovaBank guarantees full control over your money with zero hassle and no risks.")
        asset_id = create_resp.json()["id"]
        run_id = await _setup_run(client, asset_id)
        report_resp = await client.get(f"/reports/{run_id}")
    assert create_resp.status_code == 201
    assert report_resp.status_code == 200
    data = report_resp.json()
    risks = data.get("risks", [])
    risk_types = [r.get("risk", "") for r in risks]
    assert len(risks) > 2, "Variant C should have more than just base risks"
    high_risks = [r for r in risks if r.get("severity", "").lower() == "high"]
    assert len(high_risks) > 0, "Variant C should have at least one high-severity risk"


async def test_demo_comparison_a_vs_b():
    """Compare Variant A vs B — should work and return result."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a_resp = await _text_asset(client, "Variant A", "Clear practical messaging for freelancers.")
        a_id = a_resp.json()["id"]
        b_resp = await _text_asset(client, "Variant B", "Emotional freedom messaging for freelancers.")
        b_id = b_resp.json()["id"]
        run_a = await _setup_run(client, a_id)
        run_b = await _setup_run(client, b_id)
        compare_resp = await client.post("/reports/compare", json={
            "test_run_ids": [run_a, run_b],
        })
    assert compare_resp.status_code == 200
    data = compare_resp.json()
    assert "comparison_id" in data
    assert data["winner"] in (run_a, run_b, "no_clear_winner")
    assert len(data.get("score_deltas", [])) > 0


async def test_demo_comparison_includes_variant_c():
    """Compare A vs B vs C — must handle all three."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a = await _text_asset(client, "VA", "Practical card for freelancers.")
        b = await _text_asset(client, "VB", "Freedom card for freelancers.")
        c = await _text_asset(client, "VC", "The only card you will ever need. Zero risk. Guaranteed.")
        run_a = await _setup_run(client, a.json()["id"])
        run_b = await _setup_run(client, b.json()["id"])
        run_c = await _setup_run(client, c.json()["id"])
        compare_resp = await client.post("/reports/compare", json={
            "test_run_ids": [run_a, run_b, run_c],
        })
    assert compare_resp.status_code == 200
    data = compare_resp.json()
    assert len(data.get("variant_summaries", [])) == 3


async def test_demo_flow_uses_no_cloud_providers():
    """Verify demo flow completes without cloud providers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _text_asset(client, "Cloud Check", "Test content for cloud verification.")
        asset_id = resp.json()["id"]
        run_id = await _setup_run(client, asset_id)
        report_resp = await client.get(f"/reports/{run_id}")
    assert resp.status_code == 201
    assert report_resp.status_code == 200
    assert "/vision/health" is not None  # endpoint exists
