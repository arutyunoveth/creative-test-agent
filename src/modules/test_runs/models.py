from datetime import datetime, timezone


class TestRun:
    def __init__(
        self,
        run_id: str,
        creative_asset_id: str,
        brand_profile_id: str | None = None,
        audience_profile_ids: list[str] | None = None,
        rubric_id: str | None = None,
        input_context: dict | None = None,
    ):
        self.id = run_id
        self.creative_asset_id = creative_asset_id
        self.brand_profile_id = brand_profile_id
        self.audience_profile_ids = audience_profile_ids or []
        self.rubric_id = rubric_id
        self.status = "created"
        self.input_context = input_context or {}
        self.findings: list[dict] = []
        self.summary: str = ""
        self.overall_score: float = 0.0
        self.scorecard: list[dict] = []
        self.risks: list[dict] = []
        self.audience_reactions: list[dict] = []
        self.final_recommendation: str = ""
        self.created_at = datetime.now(timezone.utc)
        self.completed_at: datetime | None = None
