from fastapi import APIRouter, Depends, HTTPException

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
