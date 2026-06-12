"""Tests for export jobs foundation module."""

from src.modules.export_jobs.models import ExportType, ExportStatus
from src.modules.export_jobs.service import create_stub_export, list_export_jobs, get_export_job
from httpx import ASGITransport, AsyncClient
from src.main import app


def test_export_type_enum():
    """ExportType enum has expected values."""
    assert ExportType.html == "html"
    assert ExportType.pdf_stub == "pdf_stub"
    assert ExportType.docx_stub == "docx_stub"
    assert ExportType.pptx_stub == "pptx_stub"
    assert ExportType.json == "json"
    assert ExportType.markdown == "markdown"


def test_export_status_enum():
    """ExportStatus enum has expected values."""
    assert ExportStatus.created == "created"
    assert ExportStatus.running == "running"
    assert ExportStatus.completed == "completed"
    assert ExportStatus.failed == "failed"


def test_create_stub_export():
    """create_stub_export returns a completed export job."""
    job = create_stub_export(
        entity_type="report",
        entity_id="report_001",
        export_type="docx_stub",
        stub_message="DOCX stub for report_001",
    )
    assert job.status == "completed"
    assert job.entity_type == "report"
    assert job.entity_id == "report_001"
    assert job.export_type == "docx_stub"
    assert job.file_path is not None
    assert job.completed_at is not None


def test_list_export_jobs():
    """list_export_jobs returns a list."""
    jobs = list_export_jobs()
    assert isinstance(jobs, list)


def test_get_export_job():
    """Created export job can be retrieved by ID."""
    job = create_stub_export(
        entity_type="report", entity_id="r2",
        export_type="pptx_stub", stub_message="PPTX stub",
    )
    retrieved = get_export_job(job.id)
    assert retrieved is not None
    assert retrieved.id == job.id
    assert retrieved.export_type == "pptx_stub"


def test_docx_stub_endpoint():
    """POST /exports/report/{id}/docx_stub returns a completed job."""
    transport = ASGITransport(app=app)
    import anyio
    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/exports/report/test_report_id/docx_stub")
        assert resp.status_code == 201
        data = resp.json()
        assert data["export_type"] == "docx_stub"
        assert data["status"] == "completed"
    anyio.run(test)


def test_pptx_stub_endpoint():
    """POST /exports/report/{id}/pptx_stub returns a completed job."""
    transport = ASGITransport(app=app)
    import anyio
    async def test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/exports/report/test_report_id/pptx_stub")
        assert resp.status_code == 201
        data = resp.json()
        assert data["export_type"] == "pptx_stub"
        assert data["status"] == "completed"
    anyio.run(test)
