from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class CreativeAsset(Base):
    __tablename__ = "creative_asset"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    asset_type: Mapped[str] = mapped_column(String(50))
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_asset_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    version_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version_number: Mapped[int | None] = mapped_column(nullable=True)
    revision_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
