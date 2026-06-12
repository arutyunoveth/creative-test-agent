import json
from datetime import datetime, timezone

from src.modules.test_runs.models import TestRun
from src.modules.test_runs.pipeline import run_pipeline
from src.modules.test_runs.schemas import (
    AudienceReaction,
    BrandbookCompliance,
    ComplianceViolation,
    CreateTestRunRequest,
    FindingItem,
    RiskEntry,
    ScorecardEntry,
    TestRunResponse,
)
from src.shared.db.repository import db_session, json_dumps, json_loads
from src.shared.llm.factory import get_llm_provider
from src.shared.llm.policy import validate_llm_provider


def _to_response(run: TestRun) -> TestRunResponse:
    findings_data = json_loads(run.structured_findings_json) or {}
    compliance_raw = findings_data.get("brandbook_compliance") or {}
    return TestRunResponse(
        id=run.id,
        creative_asset_id=run.creative_asset_id,
        brand_profile_id=run.brand_profile_id,
        audience_profile_ids=json_loads(run.audience_profile_ids_json) or [],
        rubric_id=run.rubric_id,
        status=run.status,
        input_context=json_loads(run.input_context_json) or {},
        project_id=run.project_id,
        findings=[FindingItem(**f) if isinstance(f, dict) else f for f in (findings_data.get("findings") or [])],
        summary=run.summary or "",
        overall_score=run.overall_score or 0.0,
        scorecard=[ScorecardEntry(**s) if isinstance(s, dict) else s for s in (findings_data.get("scorecard") or [])],
        risks=[RiskEntry(**r) if isinstance(r, dict) else r for r in (findings_data.get("risks") or [])],
        audience_reactions=[AudienceReaction(**a) if isinstance(a, dict) else a for a in (findings_data.get("audience_reactions") or [])],
        brandbook_compliance=BrandbookCompliance(
            overall_verdict=compliance_raw.get("overall_verdict", "compliant"),
            violations=[ComplianceViolation(**v) if isinstance(v, dict) else v for v in (compliance_raw.get("violations") or [])],
            recommendations=compliance_raw.get("recommendations", []),
            compliance_score=compliance_raw.get("compliance_score", 10.0),
        ),
        final_recommendation=run.final_recommendation or "",
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


def _findings_to_json(findings, scorecard, risks, audience_reactions, brandbook_compliance=None) -> str:
    def _val(item, key):
        return item[key] if isinstance(item, dict) else getattr(item, key, "")

    data = {
        "findings": [{"criterion": _val(f, "criterion"), "score": _val(f, "score"), "explanation": _val(f, "explanation")} for f in (findings or [])],
        "scorecard": [{"criterion": _val(s, "criterion"), "score": _val(s, "score"), "rationale": _val(s, "rationale"), "recommendation": _val(s, "recommendation")} for s in (scorecard or [])],
        "risks": [{"risk_type": _val(r, "risk_type"), "level": _val(r, "level"), "description": _val(r, "description"), "mitigation": _val(r, "mitigation")} for r in (risks or [])],
        "audience_reactions": [{"audience_profile_id": _val(a, "audience_profile_id"), "segment_name": _val(a, "segment_name"), "reaction": _val(a, "reaction"), "positive_triggers": _val(a, "positive_triggers"), "objections": _val(a, "objections"), "engagement_probability": _val(a, "engagement_probability")} for a in (audience_reactions or [])],
    }
    if brandbook_compliance:
        data["brandbook_compliance"] = brandbook_compliance
    return json.dumps(data, default=str)


def get_test_run_by_asset(asset_id: str) -> TestRun | None:
    with db_session() as db:
        run = (
            db.query(TestRun)
            .filter(TestRun.creative_asset_id == asset_id)
            .order_by(TestRun.created_at.desc())
            .first()
        )
        if run is None:
            return None
        db.expunge(run)
        return run


def create_test_run(req: CreateTestRunRequest) -> TestRunResponse:
    with db_session() as db:
        run = TestRun(
            creative_asset_id=req.creative_asset_id,
            brand_profile_id=req.brand_profile_id,
            audience_profile_ids_json=json_dumps(req.audience_profile_ids),
            rubric_id=req.rubric_id,
            input_context_json=json_dumps(req.input_context),
            project_id=req.project_id,
        )
        db.add(run)
        db.flush()
        db.refresh(run)
        return _to_response(run)


def list_test_runs() -> list[TestRunResponse]:
    with db_session() as db:
        runs = db.query(TestRun).order_by(TestRun.created_at.desc()).all()
        return [_to_response(r) for r in runs]


def get_test_run(run_id: str) -> TestRunResponse | None:
    with db_session() as db:
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if run is None:
            return None
        return _to_response(run)


def run_test_run(run_id: str, audit_writer=None) -> TestRunResponse:
    with db_session() as db:
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if run is None:
            raise ValueError(f"Test run {run_id} not found")

        validate_llm_provider()

        if audit_writer:
            audit_writer("test_run_started", "test_run", run_id, {})

        provider = get_llm_provider()
        run.status = "running"
        db.flush()

        creative_asset_id = run.creative_asset_id
        brand_profile_id = run.brand_profile_id
        audience_profile_ids = json_loads(run.audience_profile_ids_json) or []
        rubric_id = run.rubric_id

    try:
        result = run_pipeline(
            creative_asset_id=creative_asset_id,
            brand_profile_id=brand_profile_id,
            audience_profile_ids=audience_profile_ids,
            rubric_id=rubric_id,
            provider=provider,
        )

        with db_session() as db:
            fresh = db.query(TestRun).filter(TestRun.id == run_id).first()
            fresh.structured_findings_json = _findings_to_json(
                result["findings"], result["scorecard"], result["risks"], result["audience_reactions"],
                brandbook_compliance=result.get("brandbook_compliance"),
            )
            fresh.summary = result["summary"]
            fresh.overall_score = result.get("overall_score", 0.0)
            fresh.final_recommendation = result["final_recommendation"]
            fresh.status = "completed"
            fresh.completed_at = datetime.now(timezone.utc)
            db.flush()
            db.refresh(fresh)

            if audit_writer:
                audit_writer("test_run_completed", "test_run", run_id, {
                    "findings_count": len(result["findings"]),
                    "final_recommendation": result["final_recommendation"],
                })

            return _to_response(fresh)

    except Exception:
        with db_session() as db:
            failed = db.query(TestRun).filter(TestRun.id == run_id).first()
            failed.status = "failed"
            failed.completed_at = datetime.now(timezone.utc)
            db.flush()
        raise
