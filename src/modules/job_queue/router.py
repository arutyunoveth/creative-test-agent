from fastapi import APIRouter, HTTPException

from src.modules.audit_log.service import write_audit_event
from src.modules.job_queue.schemas import JobResponse
from src.modules.job_queue.service import (
    cancel_job,
    claim_next_job,
    enqueue_job,
    get_job,
    list_jobs,
    mark_completed,
    mark_failed,
    retry_job,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=201)
def post_enqueue_job(body: dict):
    job_type = body.get("job_type")
    if not job_type:
        raise HTTPException(status_code=400, detail="job_type is required")
    job = enqueue_job(
        job_type=job_type,
        entity_type=body.get("entity_type"),
        entity_id=body.get("entity_id"),
        project_id=body.get("project_id"),
        payload=body.get("payload"),
        priority=body.get("priority", 0),
        max_attempts=body.get("max_attempts", 3),
    )
    write_audit_event("job_enqueued", "job", job.id, {"job_type": job_type})
    return job


@router.get("", response_model=list[JobResponse])
def get_jobs(
    job_type: str | None = None,
    status: str | None = None,
    project_id: str | None = None,
    limit: int = 100,
):
    return list_jobs(job_type=job_type, status=status, project_id=project_id, limit=limit)


@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/claim-next", response_model=JobResponse)
def post_claim_next(job_type: str | None = None):
    job = claim_next_job(job_type=job_type)
    if job is None:
        raise HTTPException(status_code=404, detail="No queued jobs available")
    write_audit_event("job_started", "job", job.id, {"job_type": job.job_type})
    return job


@router.post("/{job_id}/complete", response_model=JobResponse)
def post_complete_job(job_id: str, body: dict = {}):
    result = body.get("result")
    job = mark_completed(job_id, result=result)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    write_audit_event("job_completed", "job", job_id, {"job_type": job.job_type})
    return job


@router.post("/{job_id}/fail", response_model=JobResponse)
def post_fail_job(job_id: str, body: dict):
    error = body.get("error_message", "Unknown error")
    job = mark_failed(job_id, error_message=error)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    write_audit_event("job_failed", "job", job_id, {"error": error})
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
def post_cancel_job(job_id: str):
    job = cancel_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    write_audit_event("job_cancelled", "job", job_id, {})
    return job


@router.post("/{job_id}/retry", response_model=JobResponse)
def post_retry_job(job_id: str):
    job = retry_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
