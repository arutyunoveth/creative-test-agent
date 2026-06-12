from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    priority: int = 0
    entity_type: str | None = None
    entity_id: str | None = None
    project_id: str | None = None
    payload: dict = {}
    result: dict = {}
    error_message: str | None = None
    attempts: int = 0
    max_attempts: int = 3
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
