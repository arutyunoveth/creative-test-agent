"""Tests for export download endpoint security."""

import os

from httpx import ASGITransport, AsyncClient
from src.main import app
from src.modules.export_jobs.service import create_export_job, complete_export_job, fail_export_job, create_stub_export
from src.shared.config.settings import get_settings


def _run_async(coro):
    import anyio
    return anyio.run(coro)


def test_download_completed_job():
    transport = ASGITransport(app=app)

    async def test():
        job = create_stub_export("report", "test_dl", "markdown", "test content")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/exports/{job.id}/download")
        assert resp.status_code == 200
        assert resp.headers.get("content-type") is not None

    _run_async(test)


def test_download_incomplete_job_rejected():
    transport = ASGITransport(app=app)

    async def test():
        job = create_export_job("report", "test_incomplete", "docx")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/exports/{job.id}/download")
        assert resp.status_code in (400, 409)

    _run_async(test)


def test_download_failed_job_rejected():
    transport = ASGITransport(app=app)

    async def test():
        job = create_export_job("report", "test_fail", "docx")
        fail_export_job(job.id, "Test failure")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/exports/{job.id}/download")
        assert resp.status_code in (400, 409)

    _run_async(test)


def test_download_nonexistent_job():
    transport = ASGITransport(app=app)

    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/exports/nonexistent-id/download")
        assert resp.status_code == 404

    _run_async(test)


def test_download_normal_file_works():
    settings = get_settings()
    exports_dir = settings.exports_root
    os.makedirs(exports_dir, exist_ok=True)
    test_path = os.path.join(exports_dir, "test_normal.txt")
    with open(test_path, "w") as f:
        f.write("test content")

    job = create_stub_export("report", "normal_test", "txt", "test")

    transport = ASGITransport(app=app)
    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/exports/{job.id}/download")
        assert resp.status_code == 200

    _run_async(test)
    os.remove(test_path)


def test_download_sets_filename():
    transport = ASGITransport(app=app)

    async def test():
        job = create_stub_export("report", "filename_test", "markdown", "content")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/exports/{job.id}/download")
        assert resp.status_code == 200
        assert "filename" in resp.headers.get("content-disposition", "")

    _run_async(test)
