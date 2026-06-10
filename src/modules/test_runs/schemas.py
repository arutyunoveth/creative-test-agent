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


class ScorecardEntry(BaseModel):
    criterion: str
    score: float
    rationale: str = ""
    recommendation: str = ""


class RiskEntry(BaseModel):
    risk_type: str = ""
    level: str = ""
    description: str = ""
    mitigation: str = ""


class AudienceReaction(BaseModel):
    audience_profile_id: str = ""
    segment_name: str = ""
    reaction: str = ""
    positive_triggers: list[str] = []
    objections: list[str] = []
    engagement_probability: float = 0.0


class TestRunResponse(BaseModel):
    id: str
    creative_asset_id: str
    brand_profile_id: str | None = None
    audience_profile_ids: list[str]
    rubric_id: str | None = None
    status: str
    input_context: dict
    findings: list[FindingItem]
    summary: str = ""
    overall_score: float = 0.0
    scorecard: list[ScorecardEntry] = []
    risks: list[RiskEntry] = []
    audience_reactions: list[AudienceReaction] = []
    final_recommendation: str = ""
    created_at: datetime
    completed_at: datetime | None = None
