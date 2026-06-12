"""Schema validation tests."""

from src.shared.llm.structured_output.schema_validator import (
    STAGE_SCHEMAS,
    validate_stage_output,
)


def test_all_stages_have_schemas():
    expected = [
        "creative_summary",
        "audience_simulation",
        "brand_safety_review",
        "brandbook_compliance_review",
        "rubric_scoring",
        "final_recommendation",
        "report_input_normalization",
    ]
    for s in expected:
        assert s in STAGE_SCHEMAS, f"Missing schema for {s}"


def test_creative_summary_valid():
    data = {
        "summary": "A test summary.",
        "key_message": "Key message.",
        "tone": "informative",
        "target_audience_vibe": "general",
    }
    result = validate_stage_output("creative_summary", data)
    assert len(result.validation_errors) == 0
    assert result.success


def test_creative_summary_missing_field():
    data = {"summary": "Only summary."}
    result = validate_stage_output("creative_summary", data)
    assert len(result.validation_errors) > 0
    assert "key_message" in str(result.validation_errors) or "tone" in str(result.validation_errors)


def test_creative_summary_wrong_type():
    data = {"summary": 123, "key_message": "msg", "tone": "t", "target_audience_vibe": "v"}
    result = validate_stage_output("creative_summary", data)
    assert len(result.validation_errors) > 0


def test_brandbook_compliance_valid():
    data = {
        "overall_verdict": "compliant",
        "violations": [],
        "recommendations": ["Keep it up"],
        "compliance_score": 8.5,
    }
    result = validate_stage_output("brandbook_compliance_review", data)
    assert len(result.validation_errors) == 0


def test_brandbook_compliance_missing_violations():
    data = {"overall_verdict": "compliant"}
    result = validate_stage_output("brandbook_compliance_review", data)
    assert len(result.validation_errors) > 0


def test_rubric_scoring_valid():
    data = {
        "scorecard": [{"criterion": "clarity", "score": 7.0, "rationale": "good", "recommendation": ""}],
        "overall_score": 7.0,
        "strengths": ["clarity"],
        "weaknesses": [],
    }
    result = validate_stage_output("rubric_scoring", data)
    assert len(result.validation_errors) == 0


def test_rubric_scoring_wrong_type():
    data = {
        "scorecard": "not a list",
        "overall_score": 7.0,
        "strengths": [],
        "weaknesses": [],
    }
    result = validate_stage_output("rubric_scoring", data)
    assert len(result.validation_errors) > 0


def test_final_recommendation_valid():
    data = {
        "final_recommendation": "show_to_client",
        "rationale": "Good creative.",
        "top_actions": ["Ship it"],
        "confidence": "high",
    }
    result = validate_stage_output("final_recommendation", data)
    assert len(result.validation_errors) == 0


def test_final_recommendation_missing():
    data = {}
    result = validate_stage_output("final_recommendation", data)
    assert len(result.validation_errors) > 0


def test_audience_simulation_valid():
    data = {
        "reaction": "Positive",
        "positive_triggers": ["Clear message"],
        "objections": ["None"],
        "engagement_probability": 8,
    }
    result = validate_stage_output("audience_simulation", data)
    assert len(result.validation_errors) == 0


def test_brand_safety_valid():
    data = {
        "overall_risk_level": "low",
        "risks": [],
        "brand_fit_score": 8.0,
        "claims_compliance": "compliant",
    }
    result = validate_stage_output("brand_safety_review", data)
    assert len(result.validation_errors) == 0


def test_report_normalization_valid():
    data = {
        "creative_summary": {},
        "audience_simulation": {},
        "brand_safety": {},
        "brandbook_compliance": {},
        "rubric_scoring": {},
        "final_recommendation": {},
    }
    result = validate_stage_output("report_input_normalization", data)
    assert len(result.validation_errors) == 0


def test_report_normalization_missing():
    data = {"creative_summary": {}}
    result = validate_stage_output("report_input_normalization", data)
    assert len(result.validation_errors) > 0


def test_unknown_stage():
    data = {"foo": "bar"}
    result = validate_stage_output("unknown_stage", data)
    assert len(result.validation_warnings) > 0
