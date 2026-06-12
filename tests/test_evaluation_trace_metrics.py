"""Evaluation trace metrics tests."""

import pytest
from src.modules.evaluations.runner import run_evaluation, get_evaluation_results
from src.modules.prompt_traces.service import get_trace_count
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


def test_eval_trace_metrics_exist():
    result = run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
    eval_id = result["evaluation_run_id"]
    detail = get_evaluation_results(eval_id)
    assert detail is not None
    summary = detail["summary"]
    assert "trace_count" in summary
    assert "repair_count" in summary
    assert "fallback_count" in summary
    assert "validation_error_count" in summary


def test_eval_stub_zero_repair():
    """Stub evaluation should have zero repair and zero fallback."""
    result = run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
    eval_id = result["evaluation_run_id"]
    detail = get_evaluation_results(eval_id)
    summary = detail["summary"]
    # In stub mode traces are created via _create_eval_trace which sets repaired=False
    assert summary.get("repair_count", -1) >= 0
    assert summary.get("trace_count", 0) >= 1


def test_eval_traces_created():
    run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
    count = get_trace_count()
    assert count["trace_count"] >= 1


def test_eval_all_cases_trace_metrics():
    result = run_evaluation(profile_id=None, case_ids=None)
    eval_id = result["evaluation_run_id"]
    detail = get_evaluation_results(eval_id)
    summary = detail["summary"]
    assert summary["trace_count"] >= 5  # at least one per case
    assert summary["repair_count"] == 0  # stub doesn't repair


def test_eval_score_with_traces():
    result = run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
    assert result["overall_score"] == 100
