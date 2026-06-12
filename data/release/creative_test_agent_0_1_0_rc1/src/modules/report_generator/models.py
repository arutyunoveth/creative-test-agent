from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class Report(Base):
    __tablename__ = "report"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    test_run_id: Mapped[str] = mapped_column(String(255))
    project_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    report_mode: Mapped[str] = mapped_column(String(50), default="internal")
    report_format: Mapped[str] = mapped_column(String(50), default="json")
    version: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    main_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    audience_reactions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    scorecard_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    risks_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
