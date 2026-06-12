from src.shared.llm.structured_output.result import StageResult


# Stage schemas match the prompt template output shapes
STAGE_SCHEMAS: dict[str, dict] = {
    "creative_summary": {
        "required": ["summary", "key_message", "tone", "target_audience_vibe"],
        "type_map": {
            "summary": str,
            "key_message": str,
            "tone": str,
            "target_audience_vibe": str,
        },
    },
    "audience_simulation": {
        "required": ["reaction", "positive_triggers", "objections", "engagement_probability"],
        "type_map": {
            "reaction": str,
            "positive_triggers": list,
            "objections": list,
            "engagement_probability": (int, float),
        },
    },
    "brand_safety_review": {
        "required": ["overall_risk_level", "risks", "brand_fit_score", "claims_compliance"],
        "type_map": {
            "overall_risk_level": str,
            "risks": list,
            "brand_fit_score": (int, float),
            "claims_compliance": str,
        },
    },
    "brandbook_compliance_review": {
        "required": ["overall_verdict", "violations", "recommendations", "compliance_score"],
        "type_map": {
            "overall_verdict": str,
            "violations": list,
            "recommendations": list,
            "compliance_score": (int, float),
        },
    },
    "rubric_scoring": {
        "required": ["scorecard", "overall_score", "strengths", "weaknesses"],
        "type_map": {
            "scorecard": list,
            "overall_score": (int, float),
            "strengths": list,
            "weaknesses": list,
        },
    },
    "final_recommendation": {
        "required": ["final_recommendation", "rationale", "top_actions", "confidence"],
        "type_map": {
            "final_recommendation": str,
            "rationale": str,
            "top_actions": list,
            "confidence": str,
        },
    },
    "report_input_normalization": {
        "required": [
            "creative_summary", "audience_simulation", "brand_safety",
            "brandbook_compliance", "rubric_scoring", "final_recommendation",
        ],
        "type_map": {
            "creative_summary": dict,
            "audience_simulation": dict,
            "brand_safety": dict,
            "brandbook_compliance": dict,
            "rubric_scoring": dict,
            "final_recommendation": dict,
        },
    },
}


def _check_type(value, expected_type) -> str | None:
    if expected_type is None:
        return None
    if isinstance(expected_type, tuple):
        if not isinstance(value, expected_type):
            return f"expected type {expected_type}, got {type(value).__name__}"
    elif not isinstance(value, expected_type):
        return f"expected type {expected_type.__name__}, got {type(value).__name__}"
    return None


def validate_stage_output(stage_name: str, data: dict) -> StageResult:
    result = StageResult(stage_name=stage_name, parsed_data=data)

    schema = STAGE_SCHEMAS.get(stage_name)
    if schema is None:
        result.validation_warnings.append(f"No schema defined for stage '{stage_name}'")
        return result

    # Check required top-level keys
    for key in schema.get("required", []):
        if key not in data:
            result.validation_errors.append(f"Missing required top-level key: '{key}'")
        else:
            type_check = _check_type(data[key], schema["type_map"].get(key))
            if type_check:
                result.validation_errors.append(f"Key '{key}': {type_check}")

    # Check nested required fields
    for parent_key, nested_keys in schema.get("nested_required", {}).items():
        if parent_key not in data:
            continue
        parent_val = data[parent_key]
        if not isinstance(parent_val, dict):
            result.validation_errors.append(f"'{parent_key}' is not a dict, cannot check nested fields")
            continue
        for field in nested_keys:
            if field not in parent_val:
                result.validation_errors.append(f"Missing required field: '{parent_key}.{field}'")
            else:
                nested_type = schema.get("nested_types", {}).get(parent_key, {}).get(field)
                type_check = _check_type(parent_val[field], nested_type)
                if type_check:
                    result.validation_errors.append(f"Field '{parent_key}.{field}': {type_check}")

    return result
