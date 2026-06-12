from datetime import datetime

from pydantic import BaseModel


VALID_STATUSES = {"draft", "in_review", "changes_requested", "approved", "rejected", "archived"}
VALID_DECISIONS = {"approve", "revise", "reject", "needs_discussion"}


class CreateReviewRequest(BaseModel):
    creative_asset_id: str
    report_id: str | None = None
    project_id: str | None = None
    reviewer: str = "system"
    reviewer_id: str | None = None
    summary: str | None = None
    strengths: str | None = None
    concerns: str | None = None
    revision_requests: str | None = None
    feedback_details: dict = {}
    requested_changes: list = []
    rating: int | None = None
    decision: str | None = None


class UpdateReviewRequest(BaseModel):
    status: str | None = None
    decision: str | None = None
    rating: int | None = None
    summary: str | None = None
    strengths: str | None = None
    concerns: str | None = None
    revision_requests: str | None = None
    feedback_details: dict | None = None
    requested_changes: list | None = None


class ReviewResponse(BaseModel):
    id: str
    creative_asset_id: str
    report_id: str | None = None
    project_id: str | None = None
    reviewer: str
    reviewer_id: str | None = None
    status: str
    decision: str | None = None
    rating: int | None = None
    summary: str | None = None
    strengths: str | None = None
    concerns: str | None = None
    revision_requests: str | None = None
    feedback_details: dict = {}
    requested_changes: list = []
    created_at: datetime
    updated_at: datetime | None = None
