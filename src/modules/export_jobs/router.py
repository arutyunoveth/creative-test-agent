import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from src.modules.audit_log.service import write_audit_event
from src.shared.config.settings import get_settings

from .schemas import ExportJobResponse
from .service import (
    complete_export_job,
    create_export_job,
    create_stub_export,
    fail_export_job,
    get_export_job,
    list_export_jobs,
)

router = APIRouter(tags=["exports"])

ALLOWED_EXPORT_TYPES = {"docx", "pptx", "html", "json", "markdown", "pdf_stub", "docx_stub", "pptx_stub"}


def _get_exports_dir():
    settings = get_settings()
    path = settings.exports_root
    os.makedirs(path, exist_ok=True)
    return path


def _get_report(report_id: str):
    from src.modules.report_generator.service import get_report_by_id
    report = get_report_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def _get_test_run(run_id: str):
    from src.modules.test_runs.service import get_test_run
    run = get_test_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    if run.status != "completed":
        raise HTTPException(status_code=400, detail="Test run not completed")
    return run


@router.get("", response_model=list[ExportJobResponse])
def get_exports(entity_type: str | None = Query(None)):
    return list_export_jobs(entity_type=entity_type)


@router.get("/{job_id}", response_model=ExportJobResponse)
def get_export_by_id(job_id: str):
    job = get_export_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Export job not found")
    return job


@router.get("/{job_id}/download")
def download_export(job_id: str):
    job = get_export_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Export job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400 if job.status == "failed" else 409,
                            detail=f"Export job status: {job.status}")
    if not job.file_path or not os.path.isfile(job.file_path):
        raise HTTPException(status_code=404, detail="Export file not found")
    resolved = os.path.normpath(os.path.abspath(job.file_path))
    exports_dir = os.path.normpath(os.path.abspath(_get_exports_dir()))
    if not resolved.startswith(exports_dir):
        raise HTTPException(status_code=403, detail="Path traversal denied")
    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "html": "text/html",
        "json": "application/json",
        "markdown": "text/markdown",
        "pdf_stub": "text/plain",
        "docx_stub": "text/plain",
        "pptx_stub": "text/plain",
    }
    mt = media_types.get(job.export_type, "application/octet-stream")
    filename = os.path.basename(job.file_path)
    return FileResponse(resolved, media_type=mt, filename=filename)


@router.post("/report/{report_id}/docx", response_model=ExportJobResponse, status_code=201)
def post_docx_export(report_id: str):
    from src.modules.export_jobs.renderers.docx_report import build_docx_report
    report = _get_report(report_id)
    export_job = create_export_job(entity_type="report", entity_id=report_id, export_type="docx")
    try:
        exports_dir = _get_exports_dir()
        filename = f"report_{report_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(exports_dir, filename)
        build_docx_report(report, report.report_mode or "internal", output_path)
        result = complete_export_job(export_job.id, output_path, {
            "report_id": report_id, "mode": report.report_mode, "filename": filename,
        })
        write_audit_event("export_created", "export_job", result.id,
                          {"entity_type": "report", "export_type": "docx"})
        return result
    except Exception as e:
        fail_export_job(export_job.id, str(e))
        raise HTTPException(status_code=500, detail=f"DOCX export failed: {e}")


@router.post("/report/{report_id}/pptx", response_model=ExportJobResponse, status_code=201)
def post_pptx_export(report_id: str):
    from src.modules.export_jobs.renderers.pptx_report import build_pptx_report
    report = _get_report(report_id)
    export_job = create_export_job(entity_type="report", entity_id=report_id, export_type="pptx")
    try:
        exports_dir = _get_exports_dir()
        filename = f"report_{report_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pptx"
        output_path = os.path.join(exports_dir, filename)
        build_pptx_report(report, report.report_mode or "internal", output_path)
        result = complete_export_job(export_job.id, output_path, {
            "report_id": report_id, "mode": report.report_mode, "filename": filename,
        })
        write_audit_event("export_created", "export_job", result.id,
                          {"entity_type": "report", "export_type": "pptx"})
        return result
    except Exception as e:
        fail_export_job(export_job.id, str(e))
        raise HTTPException(status_code=500, detail=f"PPTX export failed: {e}")


@router.post("/report/{report_id}/pdf", response_model=ExportJobResponse, status_code=201)
def post_pdf_export(report_id: str):
    from src.modules.export_jobs.renderers.pdf_report import build_pdf_ready_html
    report = _get_report(report_id)
    export_job = create_export_job(entity_type="report", entity_id=report_id, export_type="html")
    try:
        exports_dir = _get_exports_dir()
        filename = f"report_{report_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_print_ready.html"
        output_path = os.path.join(exports_dir, filename)
        build_pdf_ready_html(
            markdown_content=report.report_markdown or "",
            html_content=report.report_html,
            title=report.title or "Report",
            output_path=output_path,
        )
        result = complete_export_job(export_job.id, output_path, {
            "report_id": report_id, "mode": report.report_mode,
            "pdf_generation_mode": "html_print_ready",
        })
        write_audit_event("export_created", "export_job", result.id,
                          {"entity_type": "report", "export_type": "pdf_ready_html"})
        return result
    except Exception as e:
        fail_export_job(export_job.id, str(e))
        raise HTTPException(status_code=500, detail=f"PDF-ready export failed: {e}")


@router.post("/comparison/docx", response_model=ExportJobResponse, status_code=201)
def post_comparison_docx(
    test_run_ids: list[str] = Query(...),
    report_mode: str = Query("internal"),
):
    from src.modules.export_jobs.renderers.docx_report import build_docx_report
    from src.modules.report_generator.comparison import compare_test_runs
    from src.modules.report_generator.service import generate_report

    try:
        comparison = compare_test_runs(test_run_ids, report_mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    run_id = test_run_ids[0]
    report = generate_report(run_id, report_mode=report_mode, report_format="json")
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    comparison_id = comparison.comparison_id
    export_job = create_export_job(entity_type="comparison", entity_id=comparison_id, export_type="docx")
    try:
        exports_dir = _get_exports_dir()
        filename = f"comparison_{comparison_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(exports_dir, filename)
        build_docx_report(report, report_mode, output_path)
        result = complete_export_job(export_job.id, output_path, {
            "comparison_id": comparison_id, "mode": report_mode,
            "winner": comparison.winner,
        })
        write_audit_event("export_created", "export_job", result.id,
                          {"entity_type": "comparison", "export_type": "docx"})
        return result
    except Exception as e:
        fail_export_job(export_job.id, str(e))
        raise HTTPException(status_code=500, detail=f"Comparison DOCX export failed: {e}")


@router.post("/comparison/pptx", response_model=ExportJobResponse, status_code=201)
def post_comparison_pptx(
    test_run_ids: list[str] = Query(...),
    report_mode: str = Query("internal"),
):
    from src.modules.export_jobs.renderers.pptx_report import build_pptx_report
    from src.modules.report_generator.comparison import compare_test_runs
    from src.modules.report_generator.service import generate_report

    try:
        comparison = compare_test_runs(test_run_ids, report_mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    run_id = test_run_ids[0]
    report = generate_report(run_id, report_mode=report_mode, report_format="json")
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    comparison_id = comparison.comparison_id
    export_job = create_export_job(entity_type="comparison", entity_id=comparison_id, export_type="pptx")
    try:
        exports_dir = _get_exports_dir()
        filename = f"comparison_{comparison_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pptx"
        output_path = os.path.join(exports_dir, filename)
        build_pptx_report(report, report_mode, output_path)
        result = complete_export_job(export_job.id, output_path, {
            "comparison_id": comparison_id, "mode": report_mode,
            "winner": comparison.winner,
        })
        write_audit_event("export_created", "export_job", result.id,
                          {"entity_type": "comparison", "export_type": "pptx"})
        return result
    except Exception as e:
        fail_export_job(export_job.id, str(e))
        raise HTTPException(status_code=500, detail=f"Comparison PPTX export failed: {e}")


# Backward-compatible stub endpoints
@router.post("/report/{report_id}/docx_stub", response_model=ExportJobResponse, status_code=201)
def post_docx_stub(report_id: str):
    job = create_stub_export(
        entity_type="report", entity_id=report_id, export_type="docx_stub",
        stub_message=f"DOCX export stub for report {report_id}. Legacy stub endpoint.",
        metadata={"report_id": report_id},
    )
    write_audit_event("export_created", "export_job", job.id,
                      {"entity_type": "report", "export_type": "docx_stub"})
    return job


@router.post("/report/{report_id}/pptx_stub", response_model=ExportJobResponse, status_code=201)
def post_pptx_stub(report_id: str):
    job = create_stub_export(
        entity_type="report", entity_id=report_id, export_type="pptx_stub",
        stub_message=f"PPTX export stub for report {report_id}. Legacy stub endpoint.",
        metadata={"report_id": report_id},
    )
    write_audit_event("export_created", "export_job", job.id,
                      {"entity_type": "report", "export_type": "pptx_stub"})
    return job
