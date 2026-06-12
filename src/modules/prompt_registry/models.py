import hashlib
from uuid import uuid4

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class PromptVersion(Base):
    __tablename__ = "prompt_version"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    stage_name: Mapped[str] = mapped_column(String(100))
    version: Mapped[str] = mapped_column(String(50))
    template_path: Mapped[str] = mapped_column(String(512))
    template_hash: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
