import os
from datetime import datetime, timezone

from src.shared.db.repository import db_session, json_dumps, json_loads

from .models import ExportJob
from .schemas import ExportJobResponse


def create_stub_export(entity_type: str, entity_id: str, export_type: str,
                       stub_message: str, metadata: dict | None = None) -> ExportJobResponse:
    settings = _get_settings()
    exports_dir = settings.exports_root
    os.makedirs(exports_dir, exist_ok=True)

    file_name = f"{export_type}_{entity_id}.txt"
    file_path = os.path.join(exports_dir, file_name)
    with open(file_path, "w") as f:
        f.write(stub_message)

    with db_session() as db:
        job = ExportJob(
            entity_type=entity_type,
            entity_id=entity_id,
            export_type=export_type,
            status="completed",
            file_path=file_path,
            metadata_json=json_dumps(metadata),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(job)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def create_export_job(entity_type: str, entity_id: str, export_type: str) -> ExportJobResponse:
    with db_session() as db:
        job = ExportJob(
            entity_type=entity_type,
            entity_id=entity_id,
            export_type=export_type,
            status="created",
        )
        db.add(job)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def complete_export_job(job_id: str, file_path: str, metadata: dict | None = None) -> ExportJobResponse:
    with db_session() as db:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if job is None:
            raise ValueError(f"export_job_not_found: {job_id}")
        job.status = "completed"
        job.file_path = file_path
        job.completed_at = datetime.now(timezone.utc)
        if metadata:
            job.metadata_json = json_dumps(metadata)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def fail_export_job(job_id: str, error_message: str) -> ExportJobResponse:
    with db_session() as db:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if job is None:
            raise ValueError(f"export_job_not_found: {job_id}")
        job.status = "failed"
        job.error_message = error_message
        job.completed_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(job)
        return _to_response(job)


def list_export_jobs(entity_type: str | None = None) -> list[ExportJobResponse]:
    with db_session() as db:
        q = db.query(ExportJob)
        if entity_type:
            q = q.filter(ExportJob.entity_type == entity_type)
        jobs = q.order_by(ExportJob.created_at.desc()).all()
        return [_to_response(j) for j in jobs]


def get_export_job(job_id: str) -> ExportJobResponse | None:
    with db_session() as db:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        return _to_response(job) if job else None


def _to_response(job: ExportJob) -> ExportJobResponse:
    return ExportJobResponse(
        id=job.id,
        entity_type=job.entity_type,
        entity_id=job.entity_id,
        export_type=job.export_type,
        status=job.status,
        file_path=job.file_path,
        error_message=job.error_message,
        metadata=json_loads(job.metadata_json),
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


def _get_settings():
    from src.shared.config.settings import get_settings
    return get_settings()
