from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class TestRun(Base):
    __tablename__ = "test_run"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    creative_asset_id: Mapped[str] = mapped_column(String(255))
    brand_profile_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audience_profile_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    rubric_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="created")
    input_context_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_findings_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_recommendation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
