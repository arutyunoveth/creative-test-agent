from httpx import ASGITransport, AsyncClient
from src.main import app


async def _setup_completed_run(client, text_content="Test creative content"):
    create_resp = await client.post(
        "/creative-assets",
        json={"title": "Comparison Test", "asset_type": "text", "text_content": text_content},
    )
    asset_id = create_resp.json()["id"]
    run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_comparison_returns_score_deltas():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_a = await _setup_completed_run(client, "Variant A: Buy now!")
        run_b = await _setup_completed_run(client, "Variant B: Limited offer!")
        resp = await client.post(
            "/reports/compare",
            json={"test_run_ids": [run_a, run_b], "report_mode": "internal"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["comparison_id"] != ""
    assert len(data["test_run_ids"]) == 2
    assert len(data["score_deltas"]) > 0
    assert len(data["variant_summaries"]) == 2
    for delta in data["score_deltas"]:
        assert "criterion" in delta
        assert "scores" in delta
        assert run_a in delta["scores"]
        assert run_b in delta["scores"]
        assert "difference_summary" in delta


async def test_comparison_returns_winner_or_no_clear_winner():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_a = await _setup_completed_run(client, "Variant A: Buy now!")
        run_b = await _setup_completed_run(client, "Variant B: Limited offer!")
        resp = await client.post(
            "/reports/compare",
            json={"test_run_ids": [run_a, run_b], "report_mode": "internal"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["winner"] in (run_a, run_b, "no_clear_winner")
    assert data["recommendation"] != ""


async def test_comparison_requires_minimum_two_runs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/reports/compare",
            json={"test_run_ids": ["single-run"], "report_mode": "internal"},
        )
    assert resp.status_code == 400


async def test_comparison_rejects_not_completed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Not Run", "asset_type": "text", "text_content": "Hello"},
        )
        asset_id = create_resp.json()["id"]
        run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = run_resp.json()["id"]
        resp = await client.post(
            "/reports/compare",
            json={"test_run_ids": [run_id, "other"], "report_mode": "internal"},
        )
    assert resp.status_code in (404, 422, 400)


async def test_comparison_rejects_missing_findings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/reports/compare",
            json={"test_run_ids": ["nonexistent-a", "nonexistent-b"], "report_mode": "internal"},
        )
    assert resp.status_code == 404


async def test_comparison_writes_audit_events():
    from src.modules.audit_log.service import list_audit_events

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_a = await _setup_completed_run(client, "Audit A")
        run_b = await _setup_completed_run(client, "Audit B")
        await client.post(
            "/reports/compare",
            json={"test_run_ids": [run_a, run_b], "report_mode": "internal"},
        )
    events = list_audit_events()
    event_types = [e.event_type for e in events]
    assert "comparison_report_requested" in event_types
    assert "comparison_report_generated" in event_types


async def test_comparison_rejects_unsupported_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_a = await _setup_completed_run(client, "A")
        run_b = await _setup_completed_run(client, "B")
        resp = await client.post(
            "/reports/compare",
            json={"test_run_ids": [run_a, run_b], "report_mode": "secret"},
        )
    assert resp.status_code == 400
