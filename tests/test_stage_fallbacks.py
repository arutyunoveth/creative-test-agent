"""Stage fallback tests."""

from src.modules.test_runs.fallbacks import (
    FALLBACK_CREATIVE_SUMMARY,
    FALLBACK_AUDIENCE_SIMULATION,
    FALLBACK_BRAND_SAFETY,
    FALLBACK_BRANDBOOK_COMPLIANCE,
    FALLBACK_RUBRIC_SCORING,
    FALLBACK_FINAL_RECOMMENDATION,
    FALLBACK_REPORT_NORMALIZATION,
    FALLBACKS,
    get_fallback,
    has_fallback,
)


def test_creative_summary_fallback_exists():
    assert isinstance(FALLBACK_CREATIVE_SUMMARY, dict)
    assert "summary" in FALLBACK_CREATIVE_SUMMARY
    assert "key_message" in FALLBACK_CREATIVE_SUMMARY


def test_audience_simulation_fallback_exists():
    assert isinstance(FALLBACK_AUDIENCE_SIMULATION, dict)
    assert "reaction" in FALLBACK_AUDIENCE_SIMULATION


def test_brand_safety_fallback_exists():
    assert isinstance(FALLBACK_BRAND_SAFETY, dict)
    assert "risks" in FALLBACK_BRAND_SAFETY
    assert "overall_risk_level" in FALLBACK_BRAND_SAFETY


def test_brandbook_compliance_fallback_exists():
    assert isinstance(FALLBACK_BRANDBOOK_COMPLIANCE, dict)
    assert "overall_verdict" in FALLBACK_BRANDBOOK_COMPLIANCE
    assert "violations" in FALLBACK_BRANDBOOK_COMPLIANCE


def test_rubric_scoring_fallback_exists():
    assert isinstance(FALLBACK_RUBRIC_SCORING, dict)
    assert "scorecard" in FALLBACK_RUBRIC_SCORING
    assert "overall_score" in FALLBACK_RUBRIC_SCORING


def test_final_recommendation_fallback_exists():
    assert isinstance(FALLBACK_FINAL_RECOMMENDATION, dict)
    assert "final_recommendation" in FALLBACK_FINAL_RECOMMENDATION


def test_report_normalization_fallback_exists():
    assert isinstance(FALLBACK_REPORT_NORMALIZATION, dict)
    assert "creative_summary" in FALLBACK_REPORT_NORMALIZATION


def test_all_stages_have_fallback():
    expected = [
        "creative_summary",
        "audience_simulation",
        "brand_safety_review",
        "brandbook_compliance_review",
        "rubric_scoring",
        "final_recommendation",
        "report_input_normalization",
    ]
    for stage in expected:
        assert stage in FALLBACKS, f"Missing fallback for {stage}"
        assert has_fallback(stage)


def test_get_fallback_creative_summary():
    fb = get_fallback("creative_summary")
    assert fb["summary"] == "Creative summary could not be generated reliably."


def test_get_fallback_final_recommendation():
    fb = get_fallback("final_recommendation")
    assert fb["final_recommendation"] == "revise"


def test_get_fallback_unknown():
    fb = get_fallback("nonexistent_stage")
    assert fb == {}


def test_has_fallback_unknown():
    assert not has_fallback("nonexistent_stage")


def test_fallback_brandbook_verdict():
    assert FALLBACK_BRANDBOOK_COMPLIANCE["overall_verdict"] == "insufficient_context"


def test_fallback_brand_safety_risks_is_list():
    assert isinstance(FALLBACK_BRAND_SAFETY["risks"], list)
    assert len(FALLBACK_BRAND_SAFETY["risks"]) == 0
