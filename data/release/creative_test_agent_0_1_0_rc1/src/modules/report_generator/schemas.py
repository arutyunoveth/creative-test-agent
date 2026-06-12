from datetime import datetime

from pydantic import BaseModel


class ScorecardItem(BaseModel):
    criterion: str
    score: float
    weight: float = 1.0


class RiskItem(BaseModel):
    risk: str
    severity: str


class RecommendationItem(BaseModel):
    recommendation: str
    priority: str


class ReportAudienceReaction(BaseModel):
    audience_profile_id: str = ""
    segment_name: str = ""
    reaction: str = ""
    positive_triggers: list[str] = []
    objections: list[str] = []
    engagement_probability: float = 0.0


class ReportMetadata(BaseModel):
    model_config = {"extra": "allow"}
    generated_at: str = ""
    version_info: str = ""
    note: str = ""


class ReportResponse(BaseModel):
    id: str
    test_run_id: str
    report_mode: str = "internal"
    report_format: str = "json"
    version: int = 1
    title: str = ""
    summary: str = ""
    main_message: str = ""
    audience_reactions: list[ReportAudienceReaction] = []
    scorecard: list[ScorecardItem] = []
    risks: list[RiskItem] = []
    recommendations: list[RecommendationItem] = []
    final_recommendation: str = ""
    report_markdown: str = ""
    report_html: str | None = None
    visual_notes: str = ""
    file_path: str | None = None
    created_at: datetime | None = None
    metadata: ReportMetadata = ReportMetadata()


class ReportVersionInfo(BaseModel):
    test_run_id: str
    report_mode: str
    report_format: str
    version: int
    created_at: datetime


class CompareRequest(BaseModel):
    test_run_ids: list[str]
    report_mode: str = "internal"


class ScoreDelta(BaseModel):
    criterion: str
    scores: dict[str, float]
    difference_summary: str


class VariantSummary(BaseModel):
    test_run_id: str
    summary: str
    strengths: list[str]
    weaknesses: list[str]


class CompareResponse(BaseModel):
    comparison_id: str
    test_run_ids: list[str]
    report_mode: str
    winner: str
    rationale: str
    score_deltas: list[ScoreDelta]
    variant_summaries: list[VariantSummary]
    recommendation: str
