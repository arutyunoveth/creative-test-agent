from uuid import uuid4

from sqlalchemy import Float, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class PromptTrace(Base):
    __tablename__ = "prompt_trace"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    test_run_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    evaluation_run_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    stage_name: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    prompt_version_id: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_hash: Mapped[str] = mapped_column(String(64))
    prompt_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_success: Mapped[bool] = mapped_column(Boolean, default=False)
    repaired: Mapped[bool] = mapped_column(Boolean, default=False)
    repair_steps_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_warnings_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_errors_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    token_estimate_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_estimate_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
