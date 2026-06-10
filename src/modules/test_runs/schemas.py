from datetime import datetime

from pydantic import BaseModel


class CreateTestRunRequest(BaseModel):
    creative_asset_id: str
    brand_profile_id: str | None = None
    audience_profile_ids: list[str] = []
    rubric_id: str | None = None
    input_context: dict = {}


class FindingItem(BaseModel):
    criterion: str
    score: float
    explanation: str


class TestRunResponse(BaseModel):
    id: str
    creative_asset_id: str
    brand_profile_id: str | None = None
    audience_profile_ids: list[str]
    rubric_id: str | None = None
    status: str
    input_context: dict
    findings: list[FindingItem]
    created_at: datetime
    completed_at: datetime | None = None
