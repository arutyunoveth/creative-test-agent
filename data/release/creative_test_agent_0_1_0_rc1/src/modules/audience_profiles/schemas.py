from datetime import datetime

from pydantic import BaseModel


class CreateAudienceProfileRequest(BaseModel):
    name: str
    segment_description: str
    pains: str | None = None
    motivations: str | None = None
    objections: str | None = None
    metadata: dict | None = None


class AudienceProfileResponse(BaseModel):
    id: str
    name: str
    segment_description: str
    pains: str | None = None
    motivations: str | None = None
    objections: str | None = None
    metadata: dict = {}
    created_at: datetime
