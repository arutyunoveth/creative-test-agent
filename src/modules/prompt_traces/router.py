from fastapi import APIRouter, HTTPException, Query

from src.modules.prompt_traces.service import get_trace, list_traces

router = APIRouter(prefix="/prompt-traces", tags=["prompt_traces"])


@router.get("")
def get_prompt_traces(
    test_run_id: str | None = Query(None),
    evaluation_run_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return list_traces(
        test_run_id=test_run_id,
        evaluation_run_id=evaluation_run_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{trace_id}")
def get_prompt_trace(trace_id: str):
    trace = get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Prompt trace not found")
    return trace
