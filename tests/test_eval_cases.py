"""Eval case data file tests."""

import json
from pathlib import Path


CASES_DIR = Path(__file__).parent.parent / "data" / "eval_cases"


def test_all_cases_loadable():
    assert CASES_DIR.is_dir(), f"Eval cases directory not found: {CASES_DIR}"
    files = sorted(CASES_DIR.glob("*.json"))
    assert len(files) >= 5, f"Expected at least 5 eval case files, found {len(files)}"


def _load(case_id: str) -> dict:
    path = CASES_DIR / f"{case_id}.json"
    assert path.is_file(), f"Case file not found: {path}"
    with open(path) as f:
        return json.load(f)


def _check_case_structure(case: dict, case_id: str):
    assert "case_id" in case, f"{case_id}: missing case_id"
    assert "title" in case, f"{case_id}: missing title"
    assert "creative_text" in case, f"{case_id}: missing creative_text"
    assert "expected" in case, f"{case_id}: missing expected"
    expected = case["expected"]
    assert isinstance(expected.get("must_detect_risk"), bool), f"{case_id}: must_detect_risk must be bool"
    assert isinstance(expected.get("must_detect_brandbook_violation", False), bool), f"{case_id}: must_detect_brandbook_violation must be bool"
    assert expected.get("min_risk_severity", "low") in ("low", "medium", "high"), f"{case_id}: invalid min_risk_severity"


def test_novabank_variant_a():
    case = _load("novabank_variant_a")
    _check_case_structure(case, "novabank_variant_a")
    assert case["expected"]["must_detect_risk"] is False
    assert case["expected"]["must_detect_brandbook_violation"] is False


def test_novabank_variant_b():
    case = _load("novabank_variant_b")
    _check_case_structure(case, "novabank_variant_b")
    assert case["expected"]["must_detect_risk"] is False


def test_novabank_variant_c_risky():
    case = _load("novabank_variant_c_risky")
    _check_case_structure(case, "novabank_variant_c_risky")
    assert case["expected"]["must_detect_risk"] is True
    assert case["expected"]["min_risk_severity"] == "medium"


def test_brandbook_claim_policy_violation():
    case = _load("brandbook_claim_policy_violation")
    _check_case_structure(case, "brandbook_claim_policy_violation")
    assert case["expected"]["must_detect_risk"] is True
    assert case["expected"]["must_detect_brandbook_violation"] is True
    assert case["expected"]["min_risk_severity"] == "high"


def test_tone_of_voice_mismatch():
    case = _load("tone_of_voice_mismatch")
    _check_case_structure(case, "tone_of_voice_mismatch")
    assert case["expected"]["must_detect_risk"] is True
    assert case["expected"]["min_risk_severity"] == "medium"
