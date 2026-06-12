from datetime import datetime

from pydantic import BaseModel


class EvaluationCaseResultResponse(BaseModel):
    id: str
    evaluation_run_id: str
    case_id: str
    status: str
    score: int
    passed: int
    total_checks: int
    failures: list[str] = []
    warnings: list[str] = []
    output_summary: dict = {}
    created_at: datetime


class EvaluationRunResponse(BaseModel):
    id: str
    profile_id: str | None = None
    provider: str
    model: str
    status: str
    summary: dict = {}
    metadata: dict = {}
    started_at: datetime | None = None
    completed_at: datetime | None = None
    results: list[EvaluationCaseResultResponse] = []


class RunEvaluationRequest(BaseModel):
    profile_id: str | None = None
    case_ids: list[str] | None = None
    mode: str = "stub"
