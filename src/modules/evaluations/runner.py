"""Evaluation runner — runs test pipeline against eval cases and checks assertions."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.shared.config.settings import get_settings

EVAL_CASES_DIR = Path(__file__).parent.parent.parent.parent / "data" / "eval_cases"

REQUIRED_REPORT_SECTIONS = [
    "Executive Summary",
    "Brand Safety and Risks",
    "Brandbook Compliance",
    "Final Recommendation",
]

FORBIDDEN_TERMS = ["traceback", "debug", "raw finding", "stub provider"]


def _load_case(case_id: str) -> dict:
    path = EVAL_CASES_DIR / f"{case_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Eval case not found: {case_id}")
    with open(path) as f:
        return json.load(f)


def _list_case_ids() -> list[str]:
    cases = []
    for f in sorted(EVAL_CASES_DIR.glob("*.json")):
        cases.append(f.stem)
    return cases


def _run_stub_pipeline(case: dict) -> dict:
    """Simulate pipeline output using stub logic."""
    text = case.get("creative_text", "")
    brand = case.get("brand_context", {})

    risk_detected = False
    compliance_detected = False
    risk_severity = "low"

    risky_terms = ["guaranteed", "zero risk", "guarantees", "only card", "forever"]
    tone_terms = ["CRAZY", "AMAZING", "BUY NOW", "!!!"]

    for term in risky_terms:
        if term.lower() in text.lower():
            risk_detected = True
            risk_severity = "high" if term in ("guaranteed", "zero risk", "guarantees") else risk_severity

    for term in tone_terms:
        if term in text:
            risk_detected = True
            risk_severity = "medium"

    violation_terms = ["guaranteed income", "zero risk", "guarantees full control", "only card"]
    for term in violation_terms:
        if term.lower() in text.lower():
            compliance_detected = True

    # Pressure language (CAPS + exclamation) also counts as compliance violation
    pressure_indicators = ["CRAZY", "AMAZING", "BUY NOW", "!!!"]
    for term in pressure_indicators:
        if term in text:
            compliance_detected = True

    return {
        "overall_score": 5.0,
        "summary": f"Stub evaluation of: {case.get('title', 'unknown')}",
        "findings": [
            {"criterion": "message_clarity", "score": 5.0, "explanation": "Stub assessment."},
        ],
        "scorecard": [
            {"criterion": "message_clarity", "score": 5.0, "rationale": "Stub.", "recommendation": ""},
        ],
        "risks": [
            {"risk_type": "claim_risk", "level": risk_severity, "description": "Stub risk assessment.", "mitigation": ""},
        ] if risk_detected else [],
        "audience_reactions": [],
        "final_recommendation": "Proceed with caution (stub evaluation).",
        "brandbook_compliance": {
            "overall_verdict": "violation_detected" if compliance_detected else "compliant",
            "violations": [
                {"rule": "no_exaggerated_claims", "severity": risk_severity, "details": "Stub: potential claim violation detected."}
            ] if compliance_detected else [],
            "recommendations": ["Review claims for compliance."] if compliance_detected else [],
            "compliance_score": 3.0 if compliance_detected else 10.0,
        },
    }


def _check_assertions(result: dict, expected: dict) -> tuple[list[str], list[str], int, int]:
    failures: list[str] = []
    warnings: list[str] = []
    passed = 0
    total = 0

    # Check risk detection
    must_detect_risk = expected.get("must_detect_risk", False)
    total += 1
    risks = result.get("risks", [])
    detected_risk = len(risks) > 0
    if must_detect_risk and not detected_risk:
        failures.append("Expected risk to be detected, but none found")
    elif not must_detect_risk and detected_risk:
        warnings.append("Risk detected but not expected")
    else:
        passed += 1

    # Check compliance
    must_detect_violation = expected.get("must_detect_brandbook_violation", False)
    total += 1
    compliance = result.get("brandbook_compliance", {})
    violations = compliance.get("violations", [])
    detected_violation = len(violations) > 0
    if must_detect_violation and not detected_violation:
        failures.append("Expected brandbook violation, but none found")
    elif not must_detect_violation and detected_violation:
        warnings.append("Brandbook violation detected but not expected")
    else:
        passed += 1

    # Check risk severity
    min_severity = expected.get("min_risk_severity", "low")
    total += 1
    severity_map = {"low": 0, "medium": 1, "high": 2}
    actual_severity = "low"
    if risks:
        actual_severity = max((r.get("level", "low") for r in risks), key=lambda x: severity_map.get(x, 0))
    if severity_map.get(actual_severity, 0) < severity_map.get(min_severity, 0):
        failures.append(f"Risk severity '{actual_severity}' below expected minimum '{min_severity}'")
    else:
        passed += 1

    # Check required report sections
    required = expected.get("required_report_sections", REQUIRED_REPORT_SECTIONS)
    for section in required:
        total += 1
        if section.lower() in result.get("summary", "").lower() or section.lower() in result.get("final_recommendation", "").lower():
            passed += 1
        else:
            warnings.append(f"Report section '{section}' not directly found in output summary")

    # Check forbidden terms
    forbidden = expected.get("forbidden_client_facing_terms", FORBIDDEN_TERMS)
    result_str = json.dumps(result).lower()
    for term in forbidden:
        total += 1
        if term.lower() in result_str:
            failures.append(f"Forbidden term '{term}' found in output")
        else:
            passed += 1

    return failures, warnings, passed, total


def _create_eval_trace(
    eval_id: str, case_id: str, provider: str, model: str,
    pipeline_result: dict, failures: list[str], warnings: list[str],
):
    from src.shared.config.settings import get_settings
    if not get_settings().enable_prompt_tracing:
        return
    import hashlib
    from src.modules.prompt_traces.service import create_trace

    create_trace(
        evaluation_run_id=eval_id,
        stage_name=f"eval_{case_id}",
        provider=provider,
        model=model,
        prompt_hash=hashlib.sha256(case_id.encode()).hexdigest(),
        prompt_text=None,
        raw_response=str(pipeline_result),
        parsed_success=len(failures) == 0,
        repaired=False,
        repair_steps=[],
        validation_warnings=warnings,
        validation_errors=failures,
        metadata={"case_id": case_id, "eval_type": "stub"},
    )


def run_evaluation(profile_id: str | None = None, case_ids: list[str] | None = None, mode: str = "stub") -> dict:
    from src.shared.db.repository import db_session, json_dumps, json_loads
    from src.modules.evaluations.models import EvaluationRun, EvaluationCaseResult

    all_case_ids = case_ids or _list_case_ids()
    eval_id = str(uuid4())
    provider = "stub"
    model = "stub"

    if profile_id:
        from src.modules.model_profiles.service import get_profile
        profile = get_profile(profile_id)
        if profile:
            provider = profile.provider
            model = profile.model

    with db_session() as db:
        run = EvaluationRun(
            id=eval_id,
            profile_id=profile_id,
            provider=provider,
            model=model,
            status="running",
        )
        db.add(run)
        db.flush()

    total_passed = 0
    total_checks = 0
    total_cases = len(all_case_ids)
    completed_cases = 0
    failed_cases = 0

    for case_id in all_case_ids:
        try:
            case = _load_case(case_id)
        except FileNotFoundError:
                with db_session() as db:
                    result = EvaluationCaseResult(
                        evaluation_run_id=eval_id,
                        case_id=case_id,
                        status="failed",
                        score=0,
                        passed=0,
                        total_checks=0,
                        failures_json=json_dumps([f"Case not found: {case_id}"]),
                    )
                    db.add(result)
                failed_cases += 1
                continue

        try:
            pipeline_result = _run_stub_pipeline(case)
            expected = case.get("expected", {})
            failures, warnings, passed, total = _check_assertions(pipeline_result, expected)

            score = 100 if not failures else max(0, 100 - (len(failures) * 25))
            status = "completed" if not failures else "completed"
            if failures:
                failed_cases += 1
            else:
                completed_cases += 1

            total_passed += passed
            total_checks += total

            with db_session() as db:
                result = EvaluationCaseResult(
                    evaluation_run_id=eval_id,
                    case_id=case_id,
                    status=status,
                    score=score,
                    passed=passed,
                    total_checks=total,
                    failures_json=json_dumps(failures),
                    warnings_json=json_dumps(warnings),
                    output_summary_json=json_dumps({
                        "overall_score": pipeline_result.get("overall_score"),
                        "risks_count": len(pipeline_result.get("risks", [])),
                        "compliance_verdict": pipeline_result.get("brandbook_compliance", {}).get("overall_verdict"),
                        "final_recommendation": pipeline_result.get("final_recommendation"),
                    }),
                )
                db.add(result)

            # Create prompt trace for evaluation case
            _create_eval_trace(eval_id, case_id, provider, model, pipeline_result, failures, warnings)

        except Exception as e:
            with db_session() as db:
                result = EvaluationCaseResult(
                    evaluation_run_id=eval_id,
                    case_id=case_id,
                    status="failed",
                    score=0,
                    passed=0,
                    total_checks=0,
                    failures_json=json_dumps([f"Runner error: {str(e)}"]),
                )
                db.add(result)
            failed_cases += 1

    overall_score = 100 if failed_cases == 0 else max(0, int(100 * (total_passed / max(total_checks, 1))))

    # Compute trace metrics
    from src.modules.prompt_traces.service import get_trace_count
    trace_metrics = get_trace_count(evaluation_run_id=eval_id)

    with db_session() as db:
        run = db.query(EvaluationRun).filter(EvaluationRun.id == eval_id).first()
        run.status = "completed" if failed_cases == 0 else "completed"
        run.summary_json = json_dumps({
            "total_cases": total_cases,
            "completed_cases": completed_cases,
            "failed_cases": failed_cases,
            "total_passed_checks": total_passed,
            "total_checks": total_checks,
            "overall_score": overall_score,
            "trace_count": trace_metrics.get("trace_count", 0),
            "repair_count": trace_metrics.get("repair_count", 0),
            "fallback_count": trace_metrics.get("fallback_count", 0),
            "validation_error_count": trace_metrics.get("validation_error_count", 0),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })
        db.flush()

    return {"evaluation_run_id": eval_id, "status": "completed", "overall_score": overall_score}


def get_evaluation_results(eval_id: str) -> dict | None:
    from src.shared.db.repository import db_session, json_loads
    from src.modules.evaluations.models import EvaluationRun, EvaluationCaseResult

    with db_session() as db:
        run = db.query(EvaluationRun).filter(EvaluationRun.id == eval_id).first()
        if run is None:
            return None
        results = db.query(EvaluationCaseResult).filter(
            EvaluationCaseResult.evaluation_run_id == eval_id
        ).order_by(EvaluationCaseResult.case_id).all()

        return {
            "id": run.id,
            "profile_id": run.profile_id,
            "provider": run.provider,
            "model": run.model,
            "status": run.status,
            "summary": json_loads(run.summary_json) or {},
            "metadata": json_loads(run.metadata_json) or {},
            "started_at": run.created_at,
            "results": [
                {
                    "id": r.id,
                    "evaluation_run_id": r.evaluation_run_id,
                    "case_id": r.case_id,
                    "status": r.status,
                    "score": r.score,
                    "passed": r.passed,
                    "total_checks": r.total_checks,
                    "failures": json_loads(r.failures_json) or [],
                    "warnings": json_loads(r.warnings_json) or [],
                    "output_summary": json_loads(r.output_summary_json) or {},
                    "created_at": r.created_at,
                }
                for r in results
            ],
        }
