from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class ExportType(StrEnum):
    html = "html"
    pdf_stub = "pdf_stub"
    docx_stub = "docx_stub"
    pptx_stub = "pptx_stub"
    docx = "docx"
    pptx = "pptx"
    json = "json"
    markdown = "markdown"


class ExportStatus(StrEnum):
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"


class ExportJob(Base):
    __tablename__ = "export_job"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(255))
    export_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default=ExportStatus.created)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
