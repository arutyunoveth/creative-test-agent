from datetime import datetime, timezone
from uuid import uuid4

from src.modules.test_runs.models import TestRun
from src.modules.test_runs.schemas import CreateTestRunRequest, FindingItem, TestRunResponse
from src.shared.llm.factory import get_llm_provider
from src.shared.llm.policy import validate_llm_provider

_store: dict[str, TestRun] = {}

_DEFAULT_FINDINGS = [
    FindingItem(criterion="message_clarity", score=7.5, explanation="The core message is reasonably clear."),
    FindingItem(criterion="memorability", score=6.0, explanation="Moderate memorability; could use a stronger hook."),
    FindingItem(criterion="audience_fit", score=8.0, explanation="Good alignment with target audience."),
    FindingItem(criterion="call_to_action", score=7.0, explanation="CTA is present but could be more compelling."),
    FindingItem(criterion="trust", score=8.5, explanation="High trust signals."),
    FindingItem(criterion="brand_fit", score=9.0, explanation="Strong brand alignment."),
    FindingItem(criterion="negativity_risk", score=3.0, explanation="Low risk of negative perception."),
    FindingItem(criterion="distinctiveness", score=6.5, explanation="Moderately distinct from competitors."),
]


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
    result = provider.generate(
        prompt=f"Score creative {run.creative_asset_id} against rubric {run.rubric_id or 'default'}",
        metadata={"test_run_id": run_id},
    )

    run.status = "running"

    findings_data = [f.model_dump() for f in _DEFAULT_FINDINGS]
    run.findings = findings_data
    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)

    if audit_writer:
        audit_writer("test_run_completed", "test_run", run_id, {"findings_count": len(findings_data)})

    return _to_response(run)
