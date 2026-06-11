from httpx import ASGITransport, AsyncClient
from src.main import app
from src.modules.audit_log.service import _store as audit_store


async def _setup_completed_run(client, text="Audit event test"):
    create_resp = await client.post(
        "/creative-assets",
        json={"title": "Audit", "asset_type": "text", "text_content": text},
    )
    asset_id = create_resp.json()["id"]
    run_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
    run_id = run_resp.json()["id"]
    await client.post(f"/test-runs/{run_id}/run")
    return run_id


async def test_report_generated_audit_event():
    audit_store.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        await client.get(f"/reports/{run_id}")
    event_types = [e.event_type for e in audit_store]
    assert "report_requested" in event_types
    assert "report_generated" in event_types


async def test_version_created_triggers_audit():
    audit_store.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run_id = await _setup_completed_run(client)
        await client.get(f"/reports/{run_id}")
    generated_events = [e for e in audit_store if e.event_type == "report_generated"]
    assert len(generated_events) >= 1
    assert generated_events[0].payload.get("version") is not None


async def test_comparison_failed_audit_event():
    audit_store.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/reports/compare",
            json={"test_run_ids": ["bad-a", "bad-b"], "report_mode": "internal"},
        )
    event_types = [e.event_type for e in audit_store]
    assert "comparison_report_requested" in event_types
    assert "comparison_report_failed" in event_types
