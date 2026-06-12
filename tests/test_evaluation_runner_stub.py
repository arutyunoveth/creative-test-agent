"""Evaluation runner stub tests."""

import pytest
from src.modules.evaluations.runner import (
    _load_case,
    _run_stub_pipeline,
    _check_assertions,
    run_evaluation,
    get_evaluation_results,
)
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


def test_load_all_cases():
    from src.modules.evaluations.runner import _list_case_ids
    case_ids = _list_case_ids()
    assert len(case_ids) >= 5
    for cid in case_ids:
        case = _load_case(cid)
        assert "creative_text" in case


def test_stub_pipeline_clean_case():
    case = _load_case("novabank_variant_a")
    result = _run_stub_pipeline(case)
    assert "overall_score" in result
    assert "risks" in result
    assert "brandbook_compliance" in result
    assert result["brandbook_compliance"]["overall_verdict"] == "compliant"


def test_stub_pipeline_risky_case():
    case = _load_case("novabank_variant_c_risky")
    result = _run_stub_pipeline(case)
    assert len(result["risks"]) > 0


def test_stub_pipeline_violation_case():
    case = _load_case("brandbook_claim_policy_violation")
    result = _run_stub_pipeline(case)
    assert result["brandbook_compliance"]["overall_verdict"] == "violation_detected"


def test_check_assertions_clean():
    case = _load_case("novabank_variant_a")
    expected = case["expected"]
    result = _run_stub_pipeline(case)
    failures, warnings, passed, total = _check_assertions(result, expected)
    assert len(failures) == 0
    assert passed > 0


def test_check_assertions_risky():
    case = _load_case("novabank_variant_c_risky")
    expected = case["expected"]
    result = _run_stub_pipeline(case)
    failures, warnings, passed, total = _check_assertions(result, expected)
    assert len(failures) == 0
    assert passed > 0


def test_check_assertions_violation():
    case = _load_case("brandbook_claim_policy_violation")
    expected = case["expected"]
    result = _run_stub_pipeline(case)
    failures, warnings, passed, total = _check_assertions(result, expected)
    assert len(failures) == 0


def test_run_evaluation_all_cases():
    result = run_evaluation(profile_id=None, case_ids=None)
    assert result["status"] == "completed"
    assert result["overall_score"] >= 0
    assert result["evaluation_run_id"] is not None


def test_run_evaluation_selected_cases():
    result = run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
    assert result["status"] == "completed"
    assert result["overall_score"] == 100


def test_get_evaluation_results():
    run_result = run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
    eval_id = run_result["evaluation_run_id"]
    results = get_evaluation_results(eval_id)
    assert results is not None
    assert results["id"] == eval_id
    assert len(results["results"]) == 1
    assert results["results"][0]["case_id"] == "novabank_variant_a"


def test_get_missing_evaluation():
    results = get_evaluation_results("nonexistent-id")
    assert results is None


def test_all_cases_pass_in_stub():
    """All 5 shipped eval cases should pass in stub mode."""
    result = run_evaluation(profile_id=None, case_ids=None)
    assert result["overall_score"] >= 50
