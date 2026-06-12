from fastapi import APIRouter, HTTPException, Query

from src.modules.evaluations.runner import get_evaluation_results, run_evaluation
from src.modules.evaluations.schemas import RunEvaluationRequest

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/run")
def post_run_evaluation(body: RunEvaluationRequest):
    try:
        result = run_evaluation(
            profile_id=body.profile_id,
            case_ids=body.case_ids,
            mode=body.mode,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def get_evaluations():
    from src.modules.evaluations.models import EvaluationRun
    from src.shared.db.repository import db_session, json_loads

    with db_session() as db:
        runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "profile_id": r.profile_id,
                "provider": r.provider,
                "model": r.model,
                "status": r.status,
                "summary": json_loads(r.summary_json) or {},
                "created_at": r.created_at,
            }
            for r in runs
        ]


@router.get("/{eval_id}")
def get_evaluation(eval_id: str):
    result = get_evaluation_results(eval_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return result


@router.get("/{eval_id}/results")
def get_evaluation_results_list(eval_id: str):
    result = get_evaluation_results(eval_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return result.get("results", [])


@router.get("/{eval_id}/prompt-traces")
def get_evaluation_prompt_traces(eval_id: str, limit: int = Query(50, ge=1, le=1000), offset: int = Query(0, ge=0)):
    from src.modules.prompt_traces.service import list_traces
    return list_traces(evaluation_run_id=eval_id, limit=limit, offset=offset)
