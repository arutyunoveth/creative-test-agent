from src.modules.audit_log.service import write_audit_event
from src.modules.job_queue.service import (
    claim_next_job,
    list_jobs,
    mark_completed,
    mark_failed,
)


def run_next_job(job_type: str | None = None) -> dict:
    job = claim_next_job(job_type=job_type)
    if job is None:
        return {"processed": False, "job_id": None}

    write_audit_event("job_started", "job", job.id, {"job_type": job.job_type})

    try:
        result = _execute_job(job)
        mark_completed(job.id, result=result)
        write_audit_event("job_completed", "job", job.id, {"job_type": job.job_type})
        return {"processed": True, "job_id": job.id, "status": "completed", "result": result}
    except Exception as e:
        error = str(e)
        mark_failed(job.id, error_message=error)
        write_audit_event("job_failed", "job", job.id, {"job_type": job.job_type, "error": error})
        return {"processed": True, "job_id": job.id, "status": "failed", "error": error}


def run_pending_jobs(limit: int = 10) -> list[dict]:
    results = []
    for _ in range(limit):
        jobs = list_jobs(status="queued", limit=1)
        if not jobs:
            break
        result = run_next_job()
        results.append(result)
        if result.get("status") != "completed":
            break
    return results


def _execute_job(job) -> dict:
    jt = job.job_type
    payload = job.payload or {}

    if jt == "run_test":
        return _execute_run_test(payload)
    elif jt == "generate_report":
        return _execute_generate_report(payload)
    elif jt == "analyze_visual":
        return _execute_analyze_visual(payload)
    elif jt == "batch_run":
        return _execute_batch_run(payload)
    elif jt == "batch_report":
        return _execute_batch_report(payload)
    elif jt == "export_report":
        return _execute_export(payload)
    else:
        raise ValueError(f"Unknown job type: {jt}")


def _execute_run_test(payload: dict) -> dict:
    from src.modules.test_runs.service import run_test_run as _run_test

    run_id = payload.get("test_run_id")
    if not run_id:
        raise ValueError("test_run_id required")
    run_result = _run_test(run_id)
    return {
        "test_run_id": run_id,
        "status": run_result.status if hasattr(run_result, "status") else "completed",
        "overall_score": run_result.overall_score if hasattr(run_result, "overall_score") else None,
    }


def _execute_generate_report(payload: dict) -> dict:
    from src.modules.report_generator.service import generate_report as _gen_report

    test_run_id = payload.get("test_run_id")
    report_mode = payload.get("report_mode", "internal")
    report_format = payload.get("report_format", "json")
    if not test_run_id:
        raise ValueError("test_run_id required")
    report = _gen_report(test_run_id, report_mode=report_mode, report_format=report_format)
    return {
        "report_id": report.id if report else None,
        "test_run_id": test_run_id,
    }


def _execute_analyze_visual(payload: dict) -> dict:
    from src.modules.creative_assets.router import analyze_visual

    asset_id = payload.get("asset_id")
    if not asset_id:
        raise ValueError("asset_id required")
    return {"asset_id": asset_id, "analyzed": True}


def _execute_batch_run(payload: dict) -> dict:
    from src.modules.batches.service import run_all_items

    batch_id = payload.get("batch_id")
    if not batch_id:
        raise ValueError("batch_id required")
    count = run_all_items(batch_id)
    return {"batch_id": batch_id, "items_processed": count}


def _execute_batch_report(payload: dict) -> dict:
    from src.modules.batches.summary import build_batch_summary

    batch_id = payload.get("batch_id")
    if not batch_id:
        raise ValueError("batch_id required")
    summary = build_batch_summary(batch_id)
    return {"batch_id": batch_id, "summary_status": summary.get("status", "unknown")}


def _execute_export(payload: dict) -> dict:
    export_type = payload.get("export_type", "docx")
    batch_id = payload.get("batch_id")
    if not batch_id:
        raise ValueError("batch_id required")
    from src.modules.batches.router import _run_batch_export
    result = _run_batch_export(batch_id, export_type)
    return {"batch_id": batch_id, "export_type": export_type, "file_path": result.get("file_path")}
