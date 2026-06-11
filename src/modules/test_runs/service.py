from datetime import datetime, timezone
from uuid import uuid4

from src.modules.test_runs.models import TestRun
from src.modules.test_runs.pipeline import run_pipeline
from src.modules.test_runs.schemas import (
    AudienceReaction,
    CreateTestRunRequest,
    FindingItem,
    RiskEntry,
    ScorecardEntry,
    TestRunResponse,
)
from src.shared.llm.factory import get_llm_provider
from src.shared.llm.policy import validate_llm_provider

_store: dict[str, TestRun] = {}


def _to_response(run: TestRun) -> TestRunResponse:
    return TestRunResponse(
        id=run.id,
        creative_asset_id=run.creative_asset_id,
        brand_profile_id=run.brand_profile_id,
        audience_profile_ids=run.audience_profile_ids,
        rubric_id=run.rubric_id,
        status=run.status,
        input_context=run.input_context,
        findings=[FindingItem(**f) if isinstance(f, dict) else f for f in run.findings],
        summary=run.summary,
        overall_score=run.overall_score,
        scorecard=[ScorecardEntry(**s) if isinstance(s, dict) else s for s in run.scorecard],
        risks=[RiskEntry(**r) if isinstance(r, dict) else r for r in run.risks],
        audience_reactions=[AudienceReaction(**a) if isinstance(a, dict) else a for a in run.audience_reactions],
        final_recommendation=run.final_recommendation,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


def create_test_run(req: CreateTestRunRequest) -> TestRunResponse:
    run = TestRun(
        run_id=str(uuid4()),
        creative_asset_id=req.creative_asset_id,
        brand_profile_id=req.brand_profile_id,
        audience_profile_ids=req.audience_profile_ids,
        rubric_id=req.rubric_id,
        input_context=req.input_context,
    )
    _store[run.id] = run
    return _to_response(run)


def list_test_runs() -> list[TestRunResponse]:
    sorted_runs = sorted(
        _store.values(),
        key=lambda r: r.created_at,
        reverse=True,
    )
    return [_to_response(r) for r in sorted_runs]


def get_test_run(run_id: str) -> TestRunResponse | None:
    run = _store.get(run_id)
    if run is None:
        return None
    return _to_response(run)


def run_test_run(run_id: str, audit_writer=None) -> TestRunResponse:
    run = _store.get(run_id)
    if run is None:
        raise ValueError(f"Test run {run_id} not found")

    validate_llm_provider()

    if audit_writer:
        audit_writer("test_run_started", "test_run", run_id, {})

    provider = get_llm_provider()

    run.status = "running"

    try:
        result = run_pipeline(
            creative_asset_id=run.creative_asset_id,
            brand_profile_id=run.brand_profile_id,
            audience_profile_ids=run.audience_profile_ids,
            rubric_id=run.rubric_id,
            provider=provider,
        )

        run.findings = result["findings"]
        run.summary = result["summary"]
        run.overall_score = result.get("overall_score", 0.0)
        run.scorecard = result["scorecard"]
        run.risks = result["risks"]
        run.audience_reactions = result["audience_reactions"]
        run.final_recommendation = result["final_recommendation"]
        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)

        if audit_writer:
            audit_writer("test_run_completed", "test_run", run_id, {
                "findings_count": len(result["findings"]),
                "final_recommendation": result["final_recommendation"],
            })

    except Exception:
        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        raise

    return _to_response(run)
