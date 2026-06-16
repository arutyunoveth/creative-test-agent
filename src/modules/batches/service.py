import json
from datetime import datetime, timezone

from src.modules.batches.models import BatchRun, BatchRunItem
from src.modules.batches.schemas import (
    BatchRunItemResponse,
    BatchRunResponse,
    CreateBatchRequest,
)
from src.modules.job_queue.service import enqueue_job, get_job
from src.shared.db.repository import db_session, json_dumps, json_loads


def _to_response(batch: BatchRun) -> BatchRunResponse:
    return BatchRunResponse(
        id=batch.id,
        project_id=batch.project_id,
        name=batch.name,
        description=batch.description,
        status=batch.status,
        creative_asset_ids=json_loads(batch.creative_asset_ids_json) if batch.creative_asset_ids_json else [],
        audience_profile_ids=json_loads(batch.audience_profile_ids_json) if batch.audience_profile_ids_json else [],
        brand_profile_id=batch.brand_profile_id,
        test_rubric_id=batch.test_rubric_id,
        input_context=json_loads(batch.input_context_json) if batch.input_context_json else {},
        result_summary=json_loads(batch.result_summary_json) if batch.result_summary_json else {},
        created_by_user_id=batch.created_by_user_id,
        created_at=batch.created_at,
        started_at=batch.started_at,
        completed_at=batch.completed_at,
        updated_at=batch.updated_at,
    )


def _item_to_response(item: BatchRunItem) -> BatchRunItemResponse:
    return BatchRunItemResponse(
        id=item.id,
        batch_run_id=item.batch_run_id,
        creative_asset_id=item.creative_asset_id,
        audience_profile_id=item.audience_profile_id,
        test_run_id=item.test_run_id,
        report_id=item.report_id,
        job_id=item.job_id,
        status=item.status,
        score_summary=json_loads(item.score_summary_json) if item.score_summary_json else {},
        error_message=item.error_message,
        created_at=item.created_at,
        completed_at=item.completed_at,
    )


def create_batch(req: CreateBatchRequest) -> BatchRunResponse:
    with db_session() as db:
        batch = BatchRun(
            project_id=req.project_id,
            name=req.name,
            description=req.description,
            status="draft",
            creative_asset_ids_json=json_dumps(req.creative_asset_ids),
            audience_profile_ids_json=json_dumps(req.audience_profile_ids),
            brand_profile_id=req.brand_profile_id,
            test_rubric_id=req.test_rubric_id,
            input_context_json=json_dumps(req.input_context),
        )
        db.add(batch)
        db.flush()
        db.refresh(batch)
        return _to_response(batch)


def get_batch(batch_id: str) -> BatchRunResponse | None:
    with db_session() as db:
        batch = db.query(BatchRun).filter(BatchRun.id == batch_id).first()
        if batch is None:
            return None
        return _to_response(batch)


def list_batches(project_id: str | None = None, status: str | None = None) -> list[BatchRunResponse]:
    with db_session() as db:
        q = db.query(BatchRun)
        if project_id:
            q = q.filter(BatchRun.project_id == project_id)
        if status:
            q = q.filter(BatchRun.status == status)
        batches = q.order_by(BatchRun.created_at.desc()).all()
        return [_to_response(b) for b in batches]


def queue_batch(batch_id: str) -> BatchRunResponse | None:
    with db_session() as db:
        batch = db.query(BatchRun).filter(BatchRun.id == batch_id).first()
        if batch is None:
            return None
        if batch.status not in ("draft", "cancelled", "failed"):
            return _to_response(batch)

        asset_ids = json_loads(batch.creative_asset_ids_json) or []
        audience_ids = json_loads(batch.audience_profile_ids_json) or []

        batch.status = "queued"
        db.flush()

        for asset_id in asset_ids:
            item = BatchRunItem(
                batch_run_id=batch_id,
                creative_asset_id=asset_id,
                audience_profile_id=audience_ids[0] if audience_ids else None,
                status="pending",
            )
            db.add(item)
            db.flush()

            job = enqueue_job(
                job_type="run_test",
                entity_type="batch_item",
                entity_id=item.id,
                project_id=batch.project_id,
                payload={
                    "batch_item_id": item.id,
                    "creative_asset_id": asset_id,
                    "audience_profile_id": audience_ids[0] if audience_ids else None,
                    "brand_profile_id": batch.brand_profile_id,
                    "test_rubric_id": batch.test_rubric_id,
                    "input_context": json_loads(batch.input_context_json) or {},
                },
                _db=db,
            )
            item.job_id = job.id
            db.flush()

        db.refresh(batch)
        return _to_response(batch)


def run_next_item(batch_id: str) -> dict:
    batch = get_batch(batch_id)
    if batch is None:
        return {"error": "Batch not found"}

    items = list_batch_items(batch_id, status="pending")
    if not items:
        return {"error": "No pending items"}

    item = items[0]
    return _run_single_item(batch_id, item.id)


def run_all_items(batch_id: str) -> int:
    from src.modules.test_runs.service import create_test_run, run_test_run

    batch = get_batch(batch_id)
    if batch is None:
        return 0

    with db_session() as db:
        b = db.query(BatchRun).filter(BatchRun.id == batch_id).first()
        if b:
            b.status = "running"
            b.started_at = datetime.now(timezone.utc)
            db.flush()

    items = list_batch_items(batch_id, status="pending")
    count = 0
    audience_ids = batch.audience_profile_ids or []
    brand_id = batch.brand_profile_id
    rubric_id = batch.test_rubric_id
    input_ctx = batch.input_context or {}

    for item in items:
        try:
            from src.modules.test_runs.schemas import CreateTestRunRequest

            tr = create_test_run(CreateTestRunRequest(
                creative_asset_id=item.creative_asset_id,
                brand_profile_id=brand_id,
                audience_profile_ids=audience_ids,
                rubric_id=rubric_id,
                project_id=batch.project_id,
                input_context=input_ctx,
            ))
            result = run_test_run(tr.id)

            with db_session() as db:
                db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item.id).first()
                if db_item:
                    db_item.test_run_id = tr.id
                    db_item.status = "completed"
                    db_item.completed_at = datetime.now(timezone.utc)
                    db_item.score_summary_json = json_dumps({
                        "overall_score": result.overall_score if hasattr(result, "overall_score") else None,
                        "status": result.status if hasattr(result, "status") else "completed",
                    })
                    db.flush()

            from src.modules.report_generator.service import generate_report
            report = generate_report(tr.id, "internal", "json")
            if report:
                with db_session() as db:
                    db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item.id).first()
                    if db_item:
                        db_item.report_id = report.id
                        db.flush()

            count += 1
        except Exception as e:
            with db_session() as db:
                db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item.id).first()
                if db_item:
                    db_item.status = "failed"
                    db_item.error_message = str(e)
                    db_item.completed_at = datetime.now(timezone.utc)
                    db.flush()

    with db_session() as db:
        b = db.query(BatchRun).filter(BatchRun.id == batch_id).first()
        if b:
            b.status = "completed" if count == len(items) else "failed"
            b.completed_at = datetime.now(timezone.utc)
            db.flush()

    return count


def cancel_batch(batch_id: str) -> BatchRunResponse | None:
    with db_session() as db:
        batch = db.query(BatchRun).filter(BatchRun.id == batch_id).first()
        if batch is None:
            return None
        batch.status = "cancelled"
        batch.completed_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(batch)

    items = list_batch_items(batch_id)
    for item in items:
        if item.status in ("pending", "queued", "running"):
            if item.job_id:
                from src.modules.job_queue.service import cancel_job
                cancel_job(item.job_id)
            with db_session() as db:
                db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item.id).first()
                if db_item:
                    db_item.status = "skipped"
                    db.flush()

    return get_batch(batch_id)


def _run_single_item(batch_id: str, item_id: str) -> dict:
    from src.modules.test_runs.schemas import CreateTestRunRequest
    from src.modules.test_runs.service import create_test_run, run_test_run
    from src.modules.report_generator.service import generate_report

    batch = get_batch(batch_id)
    if batch is None:
        return {"error": "Batch not found"}

    item = get_batch_item(item_id)
    if item is None:
        return {"error": "Item not found"}

    try:
        tr = create_test_run(CreateTestRunRequest(
            creative_asset_id=item.creative_asset_id,
            brand_profile_id=batch.brand_profile_id,
            audience_profile_ids=batch.audience_profile_ids or [],
            rubric_id=batch.test_rubric_id,
            project_id=batch.project_id,
            input_context=batch.input_context or {},
        ))
        result = run_test_run(tr.id)

        with db_session() as db:
            db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item_id).first()
            if db_item:
                db_item.test_run_id = tr.id
                db_item.status = "completed"
                db_item.completed_at = datetime.now(timezone.utc)
                db_item.score_summary_json = json_dumps({
                    "overall_score": result.overall_score if hasattr(result, "overall_score") else None,
                    "status": result.status if hasattr(result, "status") else "completed",
                })
                db.flush()

        report = generate_report(tr.id, "internal", "json")
        if report:
            with db_session() as db:
                db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item_id).first()
                if db_item:
                    db_item.report_id = report.id
                    db.flush()

        return {"item_id": item_id, "test_run_id": tr.id, "status": "completed"}
    except Exception as e:
        with db_session() as db:
            db_item = db.query(BatchRunItem).filter(BatchRunItem.id == item_id).first()
            if db_item:
                db_item.status = "failed"
                db_item.error_message = str(e)
                db_item.completed_at = datetime.now(timezone.utc)
                db.flush()
        return {"item_id": item_id, "status": "failed", "error": str(e)}


def list_batch_items(
    batch_run_id: str,
    status: str | None = None,
) -> list[BatchRunItemResponse]:
    with db_session() as db:
        q = db.query(BatchRunItem).filter(BatchRunItem.batch_run_id == batch_run_id)
        if status:
            q = q.filter(BatchRunItem.status == status)
        items = q.order_by(BatchRunItem.created_at.asc()).all()
        return [_item_to_response(i) for i in items]


def get_batch_item(item_id: str) -> BatchRunItemResponse | None:
    with db_session() as db:
        item = db.query(BatchRunItem).filter(BatchRunItem.id == item_id).first()
        if item is None:
            return None
        return _item_to_response(item)
