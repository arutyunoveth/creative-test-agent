"""Process raw LLM responses through the structured output reliability layer.

Every live LLM stage call goes through:
  raw_response → extract → repair → validate → fallback → trace → stage result
"""

import time
import hashlib
from src.shared.llm.base import LLMProvider
from src.shared.llm.structured_output import (
    extract_json_candidate,
    repair_json,
    validate_stage_output,
    StageResult,
)
from src.modules.test_runs.fallbacks import get_fallback


def _compute_prompt_hash(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode()).hexdigest()


def process_stage_output(
    stage_name: str,
    raw_response: str | None,
    prompt_text: str | None = None,
    provider: LLMProvider | None = None,
    test_run_id: str | None = None,
    evaluation_run_id: str | None = None,
    prompt_version_id: str | None = None,
    latency_ms: float | None = None,
    token_estimate_input: int | None = None,
    token_estimate_output: int | None = None,
) -> StageResult:
    result = StageResult(stage_name=stage_name)
    result.raw_response = raw_response or ""
    result.latency_ms = latency_ms
    result.token_estimate_input = token_estimate_input
    result.token_estimate_output = token_estimate_output

    # If no response, use fallback
    if not raw_response or not raw_response.strip():
        result.fallback_used = True
        result.validation_errors.append("Empty response from provider")
        result.parsed_data = get_fallback(stage_name)
        _maybe_create_trace(result, prompt_text, provider, test_run_id, evaluation_run_id, prompt_version_id)
        return result

    # Extract JSON
    extracted = extract_json_candidate(raw_response)
    if extracted is not None:
        result.extracted = True
        result.parsed_data = extracted
    else:
        # Try repair
        repair_result = repair_json(raw_response)
        result.repaired = repair_result["repaired"]
        result.repair_steps = repair_result.get("repair_steps", [])
        if repair_result["repaired"] and repair_result["data"] is not None:
            result.extracted = True
            result.parsed_data = repair_result["data"]
        else:
            result.validation_errors.append(repair_result.get("error", "json_parse_failed"))

    # Schema validation
    if result.parsed_data is not None:
        validation = validate_stage_output(stage_name, result.parsed_data)
        result.validation_warnings = validation.validation_warnings
        result.validation_errors.extend(validation.validation_errors)

    # Fallback if errors exist
    if result.validation_errors:
        fallback = get_fallback(stage_name)
        if fallback:
            result.fallback_used = True
            result.parsed_data = fallback
        else:
            result.parsed_data = result.parsed_data or {}

    _maybe_create_trace(result, prompt_text, provider, test_run_id, evaluation_run_id, prompt_version_id)
    return result


def _get_provider_info(provider: LLMProvider | None) -> tuple[str, str]:
    if provider is None:
        return "unknown", "unknown"
    try:
        name = getattr(provider, "name", None)
    except Exception:
        name = None
    if not name:
        name = provider.__class__.__name__.replace("Provider", "").lower()
    try:
        model = getattr(provider, "model", None)
    except Exception:
        model = None
    if not model:
        model = "unknown"
    return name, model


def _maybe_create_trace(
    result: StageResult,
    prompt_text: str | None,
    provider: LLMProvider | None,
    test_run_id: str | None,
    evaluation_run_id: str | None,
    prompt_version_id: str | None,
):
    from src.shared.config.settings import get_settings
    if not get_settings().enable_prompt_tracing:
        return

    from src.modules.prompt_traces.service import create_trace

    provider_name, model_name = _get_provider_info(provider)
    prompt_hash = _compute_prompt_hash(prompt_text or "") if prompt_text else ""

    metadata = {}
    if result.fallback_used:
        metadata["fallback_used"] = "true"

    create_trace(
        test_run_id=test_run_id,
        evaluation_run_id=evaluation_run_id,
        stage_name=result.stage_name,
        provider=provider_name,
        model=model_name,
        prompt_version_id=prompt_version_id,
        prompt_hash=prompt_hash,
        prompt_text=prompt_text,
        raw_response=result.raw_response,
        parsed_success=result.success,
        repaired=result.repaired,
        repair_steps=result.repair_steps,
        validation_warnings=result.validation_warnings,
        validation_errors=result.validation_errors,
        latency_ms=result.latency_ms,
        token_estimate_input=result.token_estimate_input,
        token_estimate_output=result.token_estimate_output,
        metadata=metadata,
    )
