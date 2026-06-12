import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from src.modules.audit_log.service import write_audit_event
from src.modules.batches.schemas import BatchRunItemResponse, BatchRunResponse, CreateBatchRequest
from src.modules.batches.service import (
    cancel_batch,
    create_batch,
    get_batch,
    list_batch_items,
    list_batches,
    queue_batch,
    run_all_items,
    run_next_item,
)
from src.modules.batches.summary import build_batch_summary
from src.shared.security.auth import get_current_user_from_request

router = APIRouter(prefix="/batches", tags=["batches"])


def _get_user_role(request: Request) -> str:
    user = get_current_user_from_request(request)
    return user.get("role", "viewer")


@router.post("", response_model=BatchRunResponse, status_code=201)
def post_create_batch(body: CreateBatchRequest, request: Request):
    batch = create_batch(body)
    write_audit_event("batch_created", "batch_run", batch.id, {
        "name": batch.name,
        "project_id": batch.project_id,
        "asset_count": len(body.creative_asset_ids),
    })
    return batch


@router.get("", response_model=list[BatchRunResponse])
def get_batches(project_id: str | None = Query(None), status: str | None = Query(None)):
    return list_batches(project_id=project_id, status=status)


@router.get("/{batch_id}", response_model=BatchRunResponse)
def get_batch_by_id(batch_id: str):
    batch = get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/{batch_id}/queue", response_model=BatchRunResponse)
def post_queue_batch(batch_id: str, request: Request):
    batch = queue_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    write_audit_event("batch_queued", "batch_run", batch_id, {
        "item_count": len(batch.creative_asset_ids),
    })
    return batch


@router.post("/{batch_id}/run-next", response_model=dict)
def post_run_next(batch_id: str, request: Request):
    role = _get_user_role(request)
    from src.shared.config.settings import get_settings
    settings = get_settings()
    if settings.enable_auth and role in ("viewer",):
        raise HTTPException(status_code=403, detail="Viewers cannot run batch items")
    result = run_next_item(batch_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    write_audit_event("batch_started", "batch_run", batch_id, {})
    return result


@router.post("/{batch_id}/run-all", response_model=dict)
def post_run_all(batch_id: str, request: Request):
    role = _get_user_role(request)
    from src.shared.config.settings import get_settings
    settings = get_settings()
    if settings.enable_auth and role in ("viewer",):
        raise HTTPException(status_code=403, detail="Viewers cannot run batch items")
    count = run_all_items(batch_id)
    write_audit_event("batch_run_all", "batch_run", batch_id, {
        "items_processed": count,
    })
    return {"batch_id": batch_id, "items_processed": count}


@router.post("/{batch_id}/cancel", response_model=BatchRunResponse)
def post_cancel_batch(batch_id: str, request: Request):
    role = _get_user_role(request)
    from src.shared.config.settings import get_settings
    settings = get_settings()
    if settings.enable_auth and role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Only admin/manager can cancel batches")
    batch = cancel_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    write_audit_event("batch_cancelled", "batch_run", batch_id, {})
    return batch


@router.get("/{batch_id}/items", response_model=list[BatchRunItemResponse])
def get_batch_items(batch_id: str, status: str | None = Query(None)):
    batch = get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return list_batch_items(batch_id, status=status)


@router.get("/{batch_id}/summary", response_model=dict)
def get_batch_summary(batch_id: str):
    batch = get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    summary = build_batch_summary(batch_id)
    write_audit_event("batch_summary_generated", "batch_run", batch_id, {})
    return summary


@router.post("/{batch_id}/compare", response_model=dict)
def post_compare_batch(batch_id: str):
    from src.modules.report_generator.comparison import compare_test_runs
    from src.modules.batches.service import list_batch_items, get_batch

    batch = get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    items = list_batch_items(batch_id, status="completed")
    test_run_ids = [i.test_run_id for i in items if i.test_run_id]

    if len(test_run_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 completed items to compare")

    try:
        result = compare_test_runs(test_run_ids, "internal")
        write_audit_event("batch_comparison_completed", "batch_run", batch_id, {
            "compared_count": len(test_run_ids),
            "winner": result.winner if hasattr(result, "winner") else "",
        })
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return {"comparison_id": str(result), "test_run_ids": test_run_ids}
    except ValueError as e:
        write_audit_event("batch_comparison_failed", "batch_run", batch_id, {
            "error": str(e),
        })
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{batch_id}/report", response_model=dict)
def get_batch_report(batch_id: str, format: str = Query("json")):
    formats = {"json", "markdown", "html"}
    if format not in formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Valid: {formats}")

    batch = get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    summary = build_batch_summary(batch_id)

    if format == "json":
        return _build_json_report(batch, summary)
    elif format == "markdown":
        return {"report": _build_markdown_report(batch, summary), "format": "markdown"}
    elif format == "html":
        return {"report": _build_html_report(batch, summary), "format": "html"}


@router.post("/{batch_id}/export/{export_type}", response_model=dict)
def post_export_batch(batch_id: str, export_type: str):
    valid = {"docx", "pptx", "pdf"}
    if export_type not in valid:
        raise HTTPException(status_code=400, detail=f"Unsupported export type. Valid: {valid}")

    from src.shared.config.settings import get_settings
    settings = get_settings()
    exports_dir = settings.exports_root
    os.makedirs(exports_dir, exist_ok=True)

    result = _run_batch_export(batch_id, export_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    from src.modules.export_jobs.models import ExportJob
    from src.shared.db.repository import db_session

    with db_session() as db:
        job = ExportJob(
            entity_type="batch_run",
            entity_id=batch_id,
            export_type=export_type,
            status="completed",
            file_path=result.get("file_path"),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(job)
        db.flush()
        db.refresh(job)
        job_id = job.id

    write_audit_event("batch_report_exported", "batch_run", batch_id, {
        "export_type": export_type,
        "file_path": result.get("file_path"),
    })
    return {"job_id": job_id, "file_path": result.get("file_path")}


def _run_batch_export(batch_id: str, export_type: str) -> dict:
    from src.shared.config.settings import get_settings

    batch = get_batch(batch_id)
    if batch is None:
        return {"error": "Batch not found"}

    summary = build_batch_summary(batch_id)
    markdown = _build_markdown_report(batch, summary)
    settings = get_settings()
    exports_dir = settings.exports_root
    os.makedirs(exports_dir, exist_ok=True)

    if export_type == "docx":
        return _export_docx(batch_id, markdown, batch, exports_dir)
    elif export_type == "pptx":
        return _export_pptx(batch_id, markdown, batch, exports_dir)
    elif export_type == "pdf":
        return _export_pdf(batch_id, markdown, batch, exports_dir)
    return {"error": f"Unknown export type: {export_type}"}


def _export_docx(batch_id: str, markdown: str, batch, exports_dir: str) -> dict:
    safe_name = batch.name.replace(" ", "_").replace("/", "_")[:50]
    file_name = f"batch_{safe_name}_{batch_id[:8]}.md"
    file_path = os.path.join(exports_dir, file_name)
    with open(file_path, "w") as f:
        f.write(markdown)
    return {"file_path": file_path, "file_name": file_name}


def _export_pptx(batch_id: str, markdown: str, batch, exports_dir: str) -> dict:
    safe_name = batch.name.replace(" ", "_").replace("/", "_")[:50]
    file_name = f"batch_{safe_name}_{batch_id[:8]}.md"
    file_path = os.path.join(exports_dir, file_name)
    with open(file_path, "w") as f:
        f.write(markdown)
    return {"file_path": file_path, "file_name": file_name}


def _export_pdf(batch_id: str, markdown: str, batch, exports_dir: str) -> dict:
    safe_name = batch.name.replace(" ", "_").replace("/", "_")[:50]
    html = _build_html_report(batch, {"total_items": 0, "completed_items": 0})
    file_name = f"batch_{safe_name}_{batch_id[:8]}.html"
    file_path = os.path.join(exports_dir, file_name)
    with open(file_path, "w") as f:
        f.write(html)
    return {"file_path": file_path, "file_name": file_name}


def _build_json_report(batch, summary: dict) -> dict:
    items = list_batch_items(batch.id) if hasattr(batch, "id") else []
    return {
        "batch_id": batch.id,
        "batch_name": batch.name,
        "status": batch.status,
        "summary": summary,
        "items": [
            {
                "id": i.id,
                "creative_asset_id": i.creative_asset_id,
                "status": i.status,
                "test_run_id": i.test_run_id,
                "report_id": i.report_id,
                "score_summary": i.score_summary,
            }
            for i in items
        ],
    }


def _build_markdown_report(batch, summary: dict) -> str:
    lines = []
    lines.append("# Campaign Batch Pre-Test Summary")
    lines.append("")
    lines.append(f"**Batch:** {batch.name}")
    lines.append(f"**Status:** {batch.status}")
    lines.append(f"**Total Items:** {summary.get('total_items', 0)}")
    lines.append(f"**Completed:** {summary.get('completed_items', 0)}")
    lines.append("")
    lines.append("## Executive Summary")
    best_id = summary.get("best_creative_asset_id", "N/A")
    avg_score = summary.get("average_score")
    lines.append(f"Best creative: `{best_id[:12]}...`" if best_id != "N/A" else "Best creative: N/A")
    lines.append(f"Average score: {avg_score}" if avg_score is not None else "Average score: N/A")
    lines.append("")
    lines.append("## Batch Overview")
    lines.append(f"- Total items: {summary.get('total_items', 0)}")
    lines.append(f"- Completed: {summary.get('completed_items', 0)}")
    lines.append(f"- Failed: {summary.get('failed_items', 0)}")
    lines.append(f"- Skipped: {summary.get('skipped_items', 0)}")
    lines.append(f"- Pending: {summary.get('pending_items', 0)}")
    lines.append("")
    lines.append("## Best Performing Creative")
    lines.append(f"Asset ID: `{best_id}`" if best_id != "N/A" else "No completed items")
    lines.append("")
    lines.append("## Scorecard Overview")
    sc = summary.get("score_summary", {})
    if sc.get("count"):
        lines.append(f"- Min: {sc.get('min')}")
        lines.append(f"- Max: {sc.get('max')}")
        lines.append(f"- Avg: {sc.get('avg')}")
        lines.append(f"- Count: {sc.get('count')}")
    else:
        lines.append("No score data available.")
    lines.append("")
    lines.append("## Risk Overview")
    rs = summary.get("risk_summary", {})
    lines.append(f"Total risks found: {rs.get('total_risks', 0)}")
    for r in rs.get("top_risks", []):
        lines.append(f"- {r.get('risk_type', 'unknown')}: {r.get('count', 0)} occurrences")
    lines.append("")
    lines.append("## Brandbook Compliance Overview")
    cs = summary.get("brandbook_compliance_summary", {})
    lines.append(f"- Compliant: {cs.get('compliant', 0)}")
    lines.append(f"- Non-compliant: {cs.get('non_compliant', 0)}")
    lines.append(f"- Unknown: {cs.get('unknown', 0)}")
    lines.append("")
    lines.append("## Recommendations")
    for rec in summary.get("top_recommendations", []):
        lines.append(f"- {rec.get('text', '')[:100]} (x{rec.get('count', 0)})")
    if not summary.get("top_recommendations"):
        lines.append("No recommendations extracted.")
    lines.append("")
    lines.append("## Appendix: Tested Variants")
    items = list_batch_items(batch.id) if hasattr(batch, "id") else []
    for i, item in enumerate(items):
        lines.append(f"### Variant {i + 1}")
        lines.append(f"- Asset: `{item.creative_asset_id[:12]}...`")
        lines.append(f"- Status: {item.status}")
        lines.append(f"- Test Run: {item.test_run_id or 'N/A'}")
        sc_item = item.score_summary or {}
        lines.append(f"- Score: {sc_item.get('overall_score', 'N/A')}")
        lines.append("")
    return "\n".join(lines)


def _build_html_report(batch, summary: dict) -> str:
    md = _build_markdown_report(batch, summary)
    html_parts = ["<html><body>"]
    for line in md.split("\n"):
        if line.startswith("# "):
            html_parts.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_parts.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("- "):
            html_parts.append(f"<li>{line[2:]}</li>")
        elif line.startswith("**"):
            html_parts.append(f"<p><strong>{line.strip('*')}</strong></p>")
        elif line.strip():
            html_parts.append(f"<p>{line}</p>")
    html_parts.append("</body></html>")
    return "\n".join(html_parts)
