from datetime import datetime
from pydantic import BaseModel


class PromptTraceResponse(BaseModel):
    id: str
    test_run_id: str | None = None
    evaluation_run_id: str | None = None
    stage_name: str
    provider: str
    model: str
    prompt_version_id: str | None = None
    prompt_hash: str
    prompt_preview: str | None = None
    raw_response_preview: str | None = None
    parsed_success: bool
    repaired: bool
    repair_steps: list[str] = []
    validation_warnings: list[str] = []
    validation_errors: list[str] = []
    latency_ms: float | None = None
    token_estimate_input: int | None = None
    token_estimate_output: int | None = None
    metadata: dict = {}
    created_at: datetime
