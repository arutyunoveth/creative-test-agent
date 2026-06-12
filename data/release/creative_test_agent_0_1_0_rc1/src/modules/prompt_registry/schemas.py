from datetime import datetime

from pydantic import BaseModel


class PromptVersionResponse(BaseModel):
    id: str
    stage_name: str
    version: str
    template_path: str
    template_hash: str
    is_active: bool
    metadata: dict = {}
    created_at: datetime
