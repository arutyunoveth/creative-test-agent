from src.modules.reviews.models import CreativeReview
from src.modules.reviews.schemas import (
    VALID_DECISIONS,
    VALID_STATUSES,
    CreateReviewRequest,
    ReviewResponse,
    UpdateReviewRequest,
)
from src.shared.db.repository import db_session, json_dumps, json_loads


VALID_TRANSITIONS = {
    "draft": {"in_review"},
    "in_review": {"changes_requested", "approved", "rejected", "archived"},
    "changes_requested": {"in_review", "archived"},
    "approved": {"archived"},
    "rejected": {"archived"},
    "archived": set(),
}


def _to_response(r: CreativeReview) -> ReviewResponse:
    return ReviewResponse(
        id=r.id,
        creative_asset_id=r.creative_asset_id,
        report_id=r.report_id,
        project_id=r.project_id,
        reviewer=r.reviewer,
        reviewer_id=r.reviewer_id,
        status=r.status,
        decision=r.decision,
        rating=r.rating,
        summary=r.summary,
        strengths=r.strengths,
        concerns=r.concerns,
        revision_requests=r.revision_requests,
        feedback_details=json_loads(r.feedback_details_json) if r.feedback_details_json else {},
        requested_changes=json_loads(r.requested_changes_json) if r.requested_changes_json else [],
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _check_status_transition(current: str, new: str) -> str | None:
    if current == new:
        return None
    allowed = VALID_TRANSITIONS.get(current, set())
    if new not in allowed:
        return f"Cannot transition from '{current}' to '{new}'"
    if new not in VALID_STATUSES:
        return f"Invalid status: '{new}'"
    return None


def create_review(req: CreateReviewRequest) -> ReviewResponse:
    with db_session() as db:
        if req.decision and req.decision not in VALID_DECISIONS:
            raise ValueError(f"Invalid decision: '{req.decision}'")

        review = CreativeReview(
            creative_asset_id=req.creative_asset_id,
            report_id=req.report_id,
            project_id=req.project_id,
            reviewer=req.reviewer,
            reviewer_id=req.reviewer_id,
            status="draft",
            decision=req.decision,
            rating=req.rating,
            summary=req.summary,
            strengths=req.strengths,
            concerns=req.concerns,
            revision_requests=req.revision_requests,
            feedback_details_json=json_dumps(req.feedback_details),
            requested_changes_json=json_dumps(req.requested_changes),
        )
        db.add(review)
        db.flush()
        db.refresh(review)
        return _to_response(review)


def get_review(review_id: str) -> ReviewResponse | None:
    with db_session() as db:
        r = db.query(CreativeReview).filter(CreativeReview.id == review_id).first()
        if r is None:
            return None
        return _to_response(r)


def list_reviews(
    creative_asset_id: str | None = None,
    project_id: str | None = None,
    status: str | None = None,
) -> list[ReviewResponse]:
    with db_session() as db:
        q = db.query(CreativeReview)
        if creative_asset_id:
            q = q.filter(CreativeReview.creative_asset_id == creative_asset_id)
        if project_id:
            q = q.filter(CreativeReview.project_id == project_id)
        if status:
            q = q.filter(CreativeReview.status == status)
        reviews = q.order_by(CreativeReview.created_at.desc()).all()
        return [_to_response(r) for r in reviews]


def update_review(
    review_id: str,
    req: UpdateReviewRequest,
    user_role: str = "viewer",
) -> tuple[ReviewResponse | None, str | None]:
    with db_session() as db:
        r = db.query(CreativeReview).filter(CreativeReview.id == review_id).first()
        if r is None:
            return None, None

        if req.status:
            error = _check_status_transition(r.status, req.status)
            if error:
                return None, error

            if req.status in ("approved", "rejected") and user_role not in ("admin", "manager"):
                return None, "Only admin or manager can approve or reject reviews"

            r.status = req.status

        if req.decision is not None:
            if req.decision not in VALID_DECISIONS:
                return None, f"Invalid decision: '{req.decision}'"
            r.decision = req.decision

        if req.rating is not None:
            if req.rating < 1 or req.rating > 5:
                return None, "Rating must be between 1 and 5"
            r.rating = req.rating

        if req.summary is not None:
            r.summary = req.summary
        if req.strengths is not None:
            r.strengths = req.strengths
        if req.concerns is not None:
            r.concerns = req.concerns
        if req.revision_requests is not None:
            r.revision_requests = req.revision_requests
        if req.feedback_details is not None:
            r.feedback_details_json = json_dumps(req.feedback_details)
        if req.requested_changes is not None:
            r.requested_changes_json = json_dumps(req.requested_changes)

        db.flush()
        db.refresh(r)
        return _to_response(r), None


def get_reviews_for_asset(asset_id: str) -> list[ReviewResponse]:
    return list_reviews(creative_asset_id=asset_id)


def get_review_model(review_id: str) -> CreativeReview | None:
    with db_session() as db:
        r = db.query(CreativeReview).filter(CreativeReview.id == review_id).first()
        if r is None:
            return None
        db.expunge(r)
        return r
