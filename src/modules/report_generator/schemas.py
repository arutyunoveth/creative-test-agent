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


class ReportResponse(BaseModel):
    test_run_id: str
    summary: str
    scorecard: list[ScorecardItem]
    risks: list[RiskItem]
    recommendations: list[RecommendationItem]
    final_recommendation: str
    report_markdown: str
