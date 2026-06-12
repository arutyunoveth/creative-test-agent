import json
from datetime import datetime, timezone

from src.modules.prompt_traces.models import PromptTrace
from src.modules.prompt_traces.schemas import PromptTraceResponse
from src.shared.config.settings import get_settings
from src.shared.db.repository import db_session, json_dumps, json_loads


def _to_response(t: PromptTrace) -> PromptTraceResponse:
    return PromptTraceResponse(
        id=t.id,
        test_run_id=t.test_run_id,
        evaluation_run_id=t.evaluation_run_id,
        stage_name=t.stage_name,
        provider=t.provider,
        model=t.model,
        prompt_version_id=t.prompt_version_id,
        prompt_hash=t.prompt_hash,
        prompt_preview=t.prompt_preview,
        raw_response_preview=t.raw_response_preview,
        parsed_success=t.parsed_success,
        repaired=t.repaired,
        repair_steps=json_loads(t.repair_steps_json) or [],
        validation_warnings=json_loads(t.validation_warnings_json) or [],
        validation_errors=json_loads(t.validation_errors_json) or [],
        latency_ms=t.latency_ms,
        token_estimate_input=t.token_estimate_input,
        token_estimate_output=t.token_estimate_output,
        metadata=json_loads(t.metadata_json) or {},
        created_at=t.created_at,
    )


def _preview(text: str | None, max_chars: int = 2000) -> str | None:
    if not text:
        return None
    preview = text[:max_chars]
    if len(text) > max_chars:
        preview += "..."
    return preview


def _store_full() -> bool:
    return get_settings().prompt_trace_store_full


def create_trace(
    test_run_id: str | None = None,
    evaluation_run_id: str | None = None,
    stage_name: str = "",
    provider: str = "",
    model: str = "",
    prompt_version_id: str | None = None,
    prompt_hash: str = "",
    prompt_text: str | None = None,
    raw_response: str | None = None,
    parsed_success: bool = False,
    repaired: bool = False,
    repair_steps: list[str] | None = None,
    validation_warnings: list[str] | None = None,
    validation_errors: list[str] | None = None,
    latency_ms: float | None = None,
    token_estimate_input: int | None = None,
    token_estimate_output: int | None = None,
    metadata: dict | None = None,
) -> PromptTraceResponse:
    if not get_settings().enable_prompt_tracing:
        return PromptTraceResponse(
            id="", stage_name=stage_name, provider=provider, model=model,
            prompt_hash=prompt_hash, parsed_success=parsed_success, repaired=repaired,
            created_at=datetime.now(timezone.utc),
        )

    max_preview = get_settings().prompt_trace_preview_chars
    store_full = _store_full()

    if store_full:
        prompt_preview = prompt_text[:get_settings().prompt_trace_max_full_chars] if prompt_text else None
        raw_preview = raw_response[:get_settings().prompt_trace_max_full_chars] if raw_response else None
    else:
        prompt_preview = _preview(prompt_text, max_preview)
        raw_preview = _preview(raw_response, max_preview)

    with db_session() as db:
        trace = PromptTrace(
            test_run_id=test_run_id,
            evaluation_run_id=evaluation_run_id,
            stage_name=stage_name,
            provider=provider,
            model=model,
            prompt_version_id=prompt_version_id,
            prompt_hash=prompt_hash,
            prompt_preview=prompt_preview,
            raw_response_preview=raw_preview,
            parsed_success=parsed_success,
            repaired=repaired,
            repair_steps_json=json_dumps(repair_steps or []),
            validation_warnings_json=json_dumps(validation_warnings or []),
            validation_errors_json=json_dumps(validation_errors or []),
            latency_ms=latency_ms,
            token_estimate_input=token_estimate_input,
            token_estimate_output=token_estimate_output,
            metadata_json=json_dumps(metadata or {}),
        )
        db.add(trace)
        db.flush()
        db.refresh(trace)
        return _to_response(trace)


def list_traces(
    test_run_id: str | None = None,
    evaluation_run_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PromptTraceResponse]:
    with db_session() as db:
        query = db.query(PromptTrace)
        if test_run_id:
            query = query.filter(PromptTrace.test_run_id == test_run_id)
        if evaluation_run_id:
            query = query.filter(PromptTrace.evaluation_run_id == evaluation_run_id)
        traces = query.order_by(PromptTrace.created_at.desc()).offset(offset).limit(limit).all()
        return [_to_response(t) for t in traces]


def get_trace(trace_id: str) -> PromptTraceResponse | None:
    with db_session() as db:
        t = db.query(PromptTrace).filter(PromptTrace.id == trace_id).first()
        if t is None:
            return None
        return _to_response(t)


def get_trace_count(
    test_run_id: str | None = None,
    evaluation_run_id: str | None = None,
) -> dict:
    traces = list_traces(test_run_id=test_run_id, evaluation_run_id=evaluation_run_id, limit=10000)
    repair_count = sum(1 for t in traces if t.repaired)
    fallback_count = sum(1 for t in traces if "fallback_used" in t.metadata.get("fallback_used", ""))
    validation_error_count = sum(1 for t in traces if t.validation_errors)
    return {
        "trace_count": len(traces),
        "repair_count": repair_count,
        "fallback_count": 0,
        "validation_error_count": validation_error_count,
    }
