from datetime import datetime

from pydantic import BaseModel


class CreateBrandProfileRequest(BaseModel):
    name: str
    tone_of_voice: str | None = None
    target_audience: str | None = None
    restrictions: str | None = None
    claims_policy: str | None = None


class BrandProfileResponse(BaseModel):
    id: str
    name: str
    tone_of_voice: str | None = None
    target_audience: str | None = None
    restrictions: str | None = None
    claims_policy: str | None = None
    created_at: datetime
