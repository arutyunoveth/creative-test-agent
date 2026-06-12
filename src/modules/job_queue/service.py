from datetime import datetime, timezone

from src.modules.job_queue.models import Job
from src.modules.job_queue.schemas import JobResponse
from src.shared.db.repository import db_session, json_dumps, json_loads


def _to_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        entity_type=job.entity_type,
        entity_id=job.entity_id,
        project_id=job.project_id,
        payload=json_loads(job.payload_json) if job.payload_json else {},
        result=json_loads(job.result_json) if job.result_json else {},
        error_message=job.error_message,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        scheduled_at=job.scheduled_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def enqueue_job(
    job_type: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    project_id: str | None = None,
    payload: dict | None = None,
    priority: int = 0,
    max_attempts: int = 3,
) -> JobResponse:
    with db_session() as db:
        job = Job(
            job_type=job_type,
            status="queued",
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            project_id=project_id,
            payload_json=json_dumps(payload or {}),
            max_attempts=max_attempts,
        )
        db.add(job)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def get_job(job_id: str) -> JobResponse | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        return _to_response(job)


def list_jobs(
    job_type: str | None = None,
    status: str | None = None,
    project_id: str | None = None,
    limit: int = 100,
) -> list[JobResponse]:
    with db_session() as db:
        q = db.query(Job)
        if job_type:
            q = q.filter(Job.job_type == job_type)
        if status:
            q = q.filter(Job.status == status)
        if project_id:
            q = q.filter(Job.project_id == project_id)
        jobs = q.order_by(Job.priority.desc(), Job.created_at.asc()).limit(limit).all()
        return [_to_response(j) for j in jobs]


def claim_next_job(job_type: str | None = None) -> JobResponse | None:
    with db_session() as db:
        q = db.query(Job).filter(Job.status == "queued")
        if job_type:
            q = q.filter(Job.job_type == job_type)
        job = q.order_by(Job.priority.desc(), Job.created_at.asc()).first()
        if job is None:
            return None
        job.status = "running"
        job.attempts = Job.attempts + 1
        job.started_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def mark_running(job_id: str) -> JobResponse | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def mark_completed(job_id: str, result: dict | None = None) -> JobResponse | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        if result is not None:
            job.result_json = json_dumps(result)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def mark_failed(job_id: str, error_message: str) -> JobResponse | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        job.status = "failed"
        job.error_message = error_message
        job.completed_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def cancel_job(job_id: str) -> JobResponse | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        if job.status in ("completed", "failed"):
            return _to_response(job)
        job.status = "cancelled"
        job.completed_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def retry_job(job_id: str) -> JobResponse | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        if job.status != "failed":
            return _to_response(job)
        if job.attempts >= job.max_attempts:
            return _to_response(job)
        job.status = "queued"
        job.error_message = None
        job.started_at = None
        job.completed_at = None
        db.flush()
        db.refresh(job)
        return _to_response(job)


def get_job_model(job_id: str) -> Job | None:
    with db_session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return None
        db.expunge(job)
        return job
