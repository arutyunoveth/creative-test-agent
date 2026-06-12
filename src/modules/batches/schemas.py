from datetime import datetime

from pydantic import BaseModel


class CreateBatchRequest(BaseModel):
    project_id: str | None = None
    name: str
    description: str | None = None
    creative_asset_ids: list[str] = []
    audience_profile_ids: list[str] = []
    brand_profile_id: str | None = None
    test_rubric_id: str | None = None
    input_context: dict = {}


class BatchRunResponse(BaseModel):
    id: str
    project_id: str | None = None
    name: str
    description: str | None = None
    status: str = "draft"
    creative_asset_ids: list[str] = []
    audience_profile_ids: list[str] = []
    brand_profile_id: str | None = None
    test_rubric_id: str | None = None
    input_context: dict = {}
    result_summary: dict = {}
    created_by_user_id: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime | None = None


class BatchRunItemResponse(BaseModel):
    id: str
    batch_run_id: str
    creative_asset_id: str
    audience_profile_id: str | None = None
    test_run_id: str | None = None
    report_id: str | None = None
    job_id: str | None = None
    status: str = "pending"
    score_summary: dict = {}
    error_message: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
