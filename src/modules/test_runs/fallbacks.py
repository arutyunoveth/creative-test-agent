"""Stage fallback outputs for when local model output is unavailable or invalid."""


FALLBACK_CREATIVE_SUMMARY = {
    "summary": "Creative summary could not be generated reliably.",
    "key_message": "",
    "tone": "",
    "target_audience_vibe": "",
}

FALLBACK_AUDIENCE_SIMULATION = {
    "reaction": "Audience simulation could not be generated reliably.",
    "positive_triggers": [],
    "objections": [],
    "engagement_probability": 0,
}

FALLBACK_BRAND_SAFETY = {
    "overall_risk_level": "unknown",
    "risks": [],
    "brand_fit_score": 0,
    "claims_compliance": "unknown",
}

FALLBACK_BRANDBOOK_COMPLIANCE = {
    "overall_verdict": "insufficient_context",
    "violations": [],
    "recommendations": [],
    "compliance_score": 0,
}

FALLBACK_RUBRIC_SCORING = {
    "scorecard": [],
    "overall_score": 0,
    "strengths": [],
    "weaknesses": [],
}

FALLBACK_FINAL_RECOMMENDATION = {
    "final_recommendation": "revise",
    "rationale": "Final recommendation could not be generated reliably. Defaulting to revise.",
    "top_actions": ["Review creative manually"],
    "confidence": "low",
}

FALLBACK_REPORT_NORMALIZATION = {
    "creative_summary": FALLBACK_CREATIVE_SUMMARY,
    "audience_simulation": FALLBACK_AUDIENCE_SIMULATION,
    "brand_safety": FALLBACK_BRAND_SAFETY,
    "brandbook_compliance": FALLBACK_BRANDBOOK_COMPLIANCE,
    "rubric_scoring": FALLBACK_RUBRIC_SCORING,
    "final_recommendation": FALLBACK_FINAL_RECOMMENDATION,
}

FALLBACKS: dict[str, dict] = {
    "creative_summary": FALLBACK_CREATIVE_SUMMARY,
    "audience_simulation": FALLBACK_AUDIENCE_SIMULATION,
    "brand_safety_review": FALLBACK_BRAND_SAFETY,
    "brandbook_compliance_review": FALLBACK_BRANDBOOK_COMPLIANCE,
    "rubric_scoring": FALLBACK_RUBRIC_SCORING,
    "final_recommendation": FALLBACK_FINAL_RECOMMENDATION,
    "report_input_normalization": FALLBACK_REPORT_NORMALIZATION,
}


def get_fallback(stage_name: str) -> dict:
    return FALLBACKS.get(stage_name, {})


def has_fallback(stage_name: str) -> bool:
    return stage_name in FALLBACKS
