from fastapi import APIRouter, HTTPException, Query, Request

from src.modules.audit_log.service import write_audit_event
from src.modules.reviews.recommendation_extractor import (
    extract_changes_from_report,
    extract_concerns_from_report,
)
from src.modules.reviews.schemas import (
    CreateReviewRequest,
    ReviewResponse,
    UpdateReviewRequest,
)
from src.modules.reviews.service import (
    create_review,
    get_review,
    get_reviews_for_asset,
    list_reviews,
    update_review,
)
from src.shared.security.auth import get_current_user_from_request

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _get_user_role(request: Request) -> str:
    user = get_current_user_from_request(request)
    return user.get("role", "viewer")


@router.post("", response_model=ReviewResponse, status_code=201)
def post_create_review(body: CreateReviewRequest, request: Request):
    from src.modules.creative_assets.service import get_asset
    asset = get_asset(body.creative_asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Creative asset not found")
    try:
        review = create_review(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    write_audit_event("review_created", "creative_review", review.id, {
        "creative_asset_id": review.creative_asset_id,
        "project_id": review.project_id,
        "reviewer": review.reviewer,
    })
    return review


@router.get("", response_model=list[ReviewResponse])
def get_reviews(
    request: Request,
    creative_asset_id: str | None = Query(None),
    project_id: str | None = Query(None),
    status: str | None = Query(None),
):
    return list_reviews(
        creative_asset_id=creative_asset_id,
        project_id=project_id,
        status=status,
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review_by_id(review_id: str):
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.patch("/{review_id}", response_model=ReviewResponse)
def patch_review(review_id: str, body: UpdateReviewRequest, request: Request):
    role = _get_user_role(request)
    review, error = update_review(review_id, body, user_role=role)
    if review is None:
        status_code = 403 if error and "admin" in error else 404
        detail = error or "Review not found"
        raise HTTPException(status_code=status_code, detail=detail)
    write_audit_event("review_updated", "creative_review", review_id, {
        "status": body.status,
        "decision": body.decision,
        "rating": body.rating,
    })
    return review


@router.post("/from-report/{report_id}", response_model=ReviewResponse, status_code=201)
def post_create_review_from_report(report_id: str, request: Request):
    from src.modules.report_generator.service import get_report
    from src.modules.creative_assets.service import get_asset

    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    from src.modules.test_runs.service import get_test_run
    run = get_test_run(report.test_run_id) if report.test_run_id else None
    asset_id = run.creative_asset_id if run else None

    if not asset_id:
        raise HTTPException(status_code=400, detail="Report has no associated creative asset")

    asset = get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Associated creative asset not found")

    concerns = extract_concerns_from_report(report)
    requested_changes = extract_changes_from_report(report)
    user = get_current_user_from_request(request)

    review = create_review(CreateReviewRequest(
        creative_asset_id=asset_id,
        report_id=report_id,
        project_id=asset.project_id,
        reviewer=user.get("display_name", "system"),
        reviewer_id=user.get("user_id"),
        summary=f"Review generated from report {report_id}",
        concerns=concerns or None,
        revision_requests=concerns or None,
        requested_changes=requested_changes,
        feedback_details={"source_report_id": report_id},
    ))

    write_audit_event("review_from_report", "creative_review", review.id, {
        "report_id": report_id,
        "creative_asset_id": asset_id,
    })
    return review


@router.post("/{review_id}/save-to-knowledge", response_model=dict)
def post_save_review_to_knowledge(review_id: str, request: Request):
    from src.shared.config.settings import get_settings

    settings = get_settings()
    if not settings.enable_review_auto_learning:
        return {"saved": False, "reason": "Auto-learning is disabled"}

    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
    from src.modules.knowledge_base.service import create_knowledge_item

    content_parts = []
    if review.summary:
        content_parts.append(f"Summary: {review.summary}")
    if review.strengths:
        content_parts.append(f"Strengths: {review.strengths}")
    if review.concerns:
        content_parts.append(f"Concerns: {review.concerns}")
    if review.revision_requests:
        content_parts.append(f"Revision Requests: {review.revision_requests}")

    if not content_parts:
        return {"saved": False, "reason": "Review has no substantive content to save"}

    content = "\n".join(content_parts)

    tags = ["review", review.status]
    if review.decision:
        tags.append(review.decision)

    item = create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="client_feedback",
        source_id=review_id,
        project_id=review.project_id,
        title=f"Review Feedback: {review.id[:8]}...",
        content=content,
        tags=tags,
    ))

    write_audit_event("review_saved_to_knowledge", "creative_review", review_id, {
        "knowledge_item_id": item.id,
        "status": review.status,
        "decision": review.decision,
    })

    return {"saved": True, "knowledge_item_id": item.id}
