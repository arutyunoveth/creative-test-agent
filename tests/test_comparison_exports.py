"""Tests for comparison DOCX/PPTX exports."""

import os

from httpx import ASGITransport, AsyncClient
from src.main import app

from src.modules.creative_assets.service import create_asset as create_creative_asset
from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
from src.modules.test_runs.schemas import CreateTestRunRequest
from src.modules.test_runs.service import create_test_run, run_test_run
from src.modules.report_generator.service import generate_report
from src.shared.config.settings import get_settings


def _run_async(coro):
    import anyio
    return anyio.run(coro)


def _create_completed_run(title: str = "Comparison Asset"):
    asset = create_creative_asset(CreateCreativeAssetRequest(
        title=title, asset_type="text", text_content="Test content for comparison."
    ))
    run = create_test_run(CreateTestRunRequest(creative_asset_id=asset.id))
    run = run_test_run(run.id)
    report = generate_report(run.id, report_mode="internal", report_format="json")
    return run, report


def _create_two_runs():
    run1, rep1 = _create_completed_run("Comparison A")
    run2, rep2 = _create_completed_run("Comparison B")
    return run1, run2


def test_comparison_docx_endpoint():
    transport = ASGITransport(app=app)
    run1, run2 = _create_two_runs()

    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/exports/comparison/docx",
                params={"test_run_ids": [run1.id, run2.id], "report_mode": "internal"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["export_type"] == "docx"
        assert data["status"] == "completed"

    _run_async(test)


def test_comparison_pptx_endpoint():
    transport = ASGITransport(app=app)
    run1, run2 = _create_two_runs()

    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/exports/comparison/pptx",
                params={"test_run_ids": [run1.id, run2.id], "report_mode": "internal"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["export_type"] == "pptx"
        assert data["status"] == "completed"

    _run_async(test)


def test_comparison_docx_file_exists():
    run1, run2 = _create_two_runs()
    transport = ASGITransport(app=app)

    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/exports/comparison/docx",
                params={"test_run_ids": [run1.id, run2.id], "report_mode": "internal"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert os.path.isfile(data["file_path"])
        assert os.path.getsize(data["file_path"]) > 100

    _run_async(test)


def test_comparison_pptx_file_exists():
    run1, run2 = _create_two_runs()
    transport = ASGITransport(app=app)

    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/exports/comparison/pptx",
                params={"test_run_ids": [run1.id, run2.id], "report_mode": "internal"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert os.path.isfile(data["file_path"])
        assert os.path.getsize(data["file_path"]) > 100

    _run_async(test)
