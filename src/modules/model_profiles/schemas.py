from datetime import datetime

from pydantic import BaseModel


class CreateModelProfileRequest(BaseModel):
    profile_name: str
    provider: str
    model: str
    base_url: str | None = None
    enabled: bool = False
    default_for_demo: bool = False
    timeout_seconds: int = 60
    notes: str | None = None
    metadata: dict = {}


class ModelProfileResponse(BaseModel):
    id: str
    profile_name: str
    provider: str
    model: str
    base_url: str | None = None
    enabled: bool
    default_for_demo: bool
    timeout_seconds: int
    notes: str | None = None
    metadata: dict = {}
    created_at: datetime


class ModelProfileHealth(BaseModel):
    profile_id: str
    profile_name: str
    provider: str
    reachable: bool
    detail: str = ""
    warnings: list[str] = []
