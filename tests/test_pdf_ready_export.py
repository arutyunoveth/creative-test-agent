"""Tests for PDF-ready HTML export."""

import os

from httpx import ASGITransport, AsyncClient
from src.main import app

from src.modules.export_jobs.renderers.pdf_report import build_pdf_ready_html
from src.modules.report_generator.service import generate_report
from src.modules.creative_assets.service import create_asset as create_creative_asset
from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
from src.modules.test_runs.schemas import CreateTestRunRequest
from src.modules.test_runs.service import create_test_run, run_test_run
from src.shared.config.settings import get_settings


def test_pdf_ready_renderer_creates_file():
    settings = get_settings()
    output_path = os.path.join(settings.exports_root, "test_pdf_ready.html")
    os.makedirs(settings.exports_root, exist_ok=True)

    result = build_pdf_ready_html(
        markdown_content="# Test\n\nHello world.",
        html_content="<h1>Test</h1><p>Hello world.</p>",
        title="Test Report",
        output_path=output_path,
    )
    assert os.path.isfile(result)
    assert os.path.getsize(result) > 0

    with open(result) as f:
        content = f.read()
    assert "<html" in content
    assert "print" in content
    assert "Test Report" in content
    os.remove(result)


def test_pdf_ready_endpoint_creates_job():
    transport = ASGITransport(app=app)
    import anyio

    async def test():
        asset = create_creative_asset(CreateCreativeAssetRequest(
            title="PDF Ready Asset", asset_type="text", text_content="PDF export test."
        ))
        run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
        run = run_test_run(run.id)
        report = generate_report(run.id, report_mode="internal", report_format="html")
        assert report is not None

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(f"/exports/report/{report.id}/pdf")
        assert resp.status_code == 201
        data = resp.json()
        assert data["export_type"] == "html"
        assert data["status"] == "completed"
        assert data["file_path"] is not None

    anyio.run(test)


def test_pdf_ready_file_print_css():
    settings = get_settings()
    output_path = os.path.join(settings.exports_root, "test_print_css.html")
    os.makedirs(settings.exports_root, exist_ok=True)

    build_pdf_ready_html(
        markdown_content="# Hello",
        html_content=None,
        title="Report",
        output_path=output_path,
    )
    with open(output_path) as f:
        content = f.read()
    assert "@media print" in content
    assert "page-break" in content
    os.remove(output_path)


def test_pdf_ready_md_conversion():
    settings = get_settings()
    output_path = os.path.join(settings.exports_root, "test_md_conv.html")
    os.makedirs(settings.exports_root, exist_ok=True)

    build_pdf_ready_html(
        markdown_content="## Section Title\n\nSome paragraph content.",
        html_content=None,
        title="MD Test",
        output_path=output_path,
    )
    with open(output_path) as f:
        content = f.read()
    assert "Section Title" in content
    assert "Some paragraph" in content
    os.remove(output_path)


def test_pdf_ready_file_nonzero():
    transport = ASGITransport(app=app)
    import anyio

    async def test():
        asset = create_creative_asset(CreateCreativeAssetRequest(
            title="PDF Zero Test", asset_type="text", text_content="Check file size."
        ))
        run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
        run = run_test_run(run.id)
        report = generate_report(run.id, report_mode="internal", report_format="html")
        assert report is not None

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(f"/exports/report/{report.id}/pdf")
        assert resp.status_code == 201
        data = resp.json()
        assert os.path.isfile(data["file_path"])
        assert os.path.getsize(data["file_path"]) > 50

    anyio.run(test)
