from fastapi import APIRouter, Depends, HTTPException, Query

from src.modules.audit_log.service import write_audit_event
from src.modules.test_runs.schemas import CreateTestRunRequest, TestRunResponse
from src.modules.test_runs.service import create_test_run, get_test_run, run_test_run
from src.shared.errors import AppError

router = APIRouter(prefix="/test-runs", tags=["test-runs"])


@router.post("", response_model=TestRunResponse, status_code=201)
def post_create_test_run(body: CreateTestRunRequest):
    run = create_test_run(body)
    write_audit_event("test_run_created", "test_run", run.id, {"creative_asset_id": run.creative_asset_id})
    return run


@router.get("/{run_id}", response_model=TestRunResponse)
def get_test_run_by_id(run_id: str):
    run = get_test_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    return run


@router.post("/{run_id}/run", response_model=TestRunResponse)
def post_run_test_run(run_id: str):
    try:
        return run_test_run(run_id, audit_writer=write_audit_event)
    except ValueError:
        raise HTTPException(status_code=404, detail="Test run not found")
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{run_id}/prompt-traces")
def get_test_run_prompt_traces(run_id: str, limit: int = Query(50, ge=1, le=1000), offset: int = Query(0, ge=0)):
    from src.modules.prompt_traces.service import list_traces
    return list_traces(test_run_id=run_id, limit=limit, offset=offset)
