"""Tests for export jobs UI pages."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_ui_exports_list():
    resp = client.get("/ui/exports")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500


def test_ui_reports_has_export_buttons():
    from src.modules.creative_assets.service import create_asset as create_creative_asset
    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
    from src.modules.test_runs.schemas import CreateTestRunRequest
    from src.modules.test_runs.service import create_test_run, run_test_run
    from src.modules.report_generator.service import generate_report

    asset = create_creative_asset(CreateCreativeAssetRequest(
        title="UI Export Buttons", asset_type="text", text_content="Test."
    ))
    run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
    run = run_test_run(run.id)
    report = generate_report(run.id, report_mode="internal", report_format="json")
    assert report is not None

    resp = client.get(f"/ui/reports/{run.id}")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500


def test_ui_export_docx_redirect():
    from src.modules.creative_assets.service import create_asset as create_creative_asset
    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
    from src.modules.test_runs.schemas import CreateTestRunRequest
    from src.modules.test_runs.service import create_test_run, run_test_run
    from src.modules.report_generator.service import generate_report

    asset = create_creative_asset(CreateCreativeAssetRequest(
        title="UI DOCX Export", asset_type="text", text_content="Test."
    ))
    run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
    run = run_test_run(run.id)
    report = generate_report(run.id, report_mode="internal", report_format="json")
    assert report is not None

    resp = client.post(f"/ui/exports/report/{report.id}/docx")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500


def test_ui_export_pptx_redirect():
    from src.modules.creative_assets.service import create_asset as create_creative_asset
    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
    from src.modules.test_runs.schemas import CreateTestRunRequest
    from src.modules.test_runs.service import create_test_run, run_test_run
    from src.modules.report_generator.service import generate_report

    asset = create_creative_asset(CreateCreativeAssetRequest(
        title="UI PPTX Export", asset_type="text", text_content="Test."
    ))
    run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
    run = run_test_run(run.id)
    report = generate_report(run.id, report_mode="internal", report_format="json")
    assert report is not None

    resp = client.post(f"/ui/exports/report/{report.id}/pptx")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500


def test_ui_export_pdf_redirect():
    from src.modules.creative_assets.service import create_asset as create_creative_asset
    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
    from src.modules.test_runs.schemas import CreateTestRunRequest
    from src.modules.test_runs.service import create_test_run, run_test_run
    from src.modules.report_generator.service import generate_report

    asset = create_creative_asset(CreateCreativeAssetRequest(
        title="UI PDF Export", asset_type="text", text_content="Test."
    ))
    run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
    run = run_test_run(run.id)
    report = generate_report(run.id, report_mode="internal", report_format="html")
    assert report is not None

    resp = client.post(f"/ui/exports/report/{report.id}/pdf")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500


def test_ui_exports_detail():
    from src.modules.export_jobs.service import create_stub_export
    job = create_stub_export("report", "ui_detail_test", "markdown", "test")
    resp = client.get(f"/ui/exports/{job.id}")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500
