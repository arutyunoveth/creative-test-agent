from fastapi import APIRouter, HTTPException, Query

from src.modules.audit_log.service import write_audit_event
from src.modules.report_generator.comparison import compare_test_runs
from src.modules.report_generator.schemas import (
    CompareRequest,
    CompareResponse,
    ReportResponse,
)
from src.modules.report_generator.service import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])

_VALID_MODES = {"internal", "client_facing"}
_VALID_FORMATS = {"json", "markdown", "html", "pdf_stub"}


@router.get("/{test_run_id}", response_model=ReportResponse)
def get_report(
    test_run_id: str,
    format: str = Query("json", alias="format"),
    mode: str = Query("internal", alias="mode"),
):
    if format not in _VALID_FORMATS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "unsupported_report_format",
                    "message": f"Unsupported format '{format}'. Valid: {', '.join(sorted(_VALID_FORMATS))}",
                }
            },
        )
    if mode not in _VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "unsupported_report_mode",
                    "message": f"Unsupported mode '{mode}'. Valid: {', '.join(sorted(_VALID_MODES))}",
                }
            },
        )

    write_audit_event("report_requested", "report", test_run_id, {"format": format, "mode": mode})
    report = generate_report(test_run_id, report_mode=mode, report_format=format)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not available")
    write_audit_event("report_generated", "report", report.id, {
        "test_run_id": test_run_id,
        "format": format,
        "mode": mode,
        "version": report.version,
    })
    return report


@router.post("/{test_run_id}/save-findings-to-knowledge")
def save_report_findings(test_run_id: str):
    from src.modules.test_runs.service import get_test_run
    from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
    from src.modules.knowledge_base.service import create_knowledge_item

    run = get_test_run(test_run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    if run.status != "completed":
        raise HTTPException(status_code=400, detail="Test run not completed")

    count = 0
    for f in run.findings or []:
        item = create_knowledge_item(CreateKnowledgeItemRequest(
            source_type="report_finding",
            source_id=test_run_id,
            title=f"Finding: {f.criterion} ({f.score}/10)",
            content=f.explanation,
            tags=[f.criterion, f"score_{int(f.score)}", "auto_saved"],
        ))
        if item:
            count += 1

    for v in (run.brandbook_compliance.violations if run.brandbook_compliance else []):
        item = create_knowledge_item(CreateKnowledgeItemRequest(
            source_type="report_finding",
            source_id=test_run_id,
            title=f"Compliance: {v.rule}",
            content=v.details,
            tags=["compliance", v.severity, "auto_saved"],
        ))
        if item:
            count += 1

    write_audit_event("report_findings_saved", "knowledge", test_run_id, {"items_created": count})
    return {"status": "ok", "items_created": count, "test_run_id": test_run_id}


@router.post("/compare", response_model=CompareResponse)
def compare_reports(req: CompareRequest):
    if req.report_mode not in _VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "unsupported_report_mode",
                    "message": f"Unsupported mode '{req.report_mode}'. Valid: {', '.join(sorted(_VALID_MODES))}",
                }
            },
        )

    write_audit_event("comparison_report_requested", "comparison", str(req.test_run_ids), {
        "test_run_ids": req.test_run_ids,
        "report_mode": req.report_mode,
    })

    try:
        result = compare_test_runs(req.test_run_ids, req.report_mode)
    except ValueError as e:
        error_code = str(e)
        status_code = 400
        if "not_found" in error_code:
            status_code = 404
        elif "not_completed" in error_code or "findings_missing" in error_code:
            status_code = 422

        write_audit_event("comparison_report_failed", "comparison", str(req.test_run_ids), {
            "error": error_code,
            "test_run_ids": req.test_run_ids,
        })

        raise HTTPException(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code.split(":")[0],
                    "message": error_code,
                }
            },
        )

    write_audit_event("comparison_report_generated", "comparison", result.comparison_id, {
        "test_run_ids": req.test_run_ids,
        "winner": result.winner,
        "recommendation": result.recommendation,
    })
    return result
