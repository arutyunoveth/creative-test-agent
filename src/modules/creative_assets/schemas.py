from datetime import datetime

from pydantic import BaseModel


class CreateCreativeAssetRequest(BaseModel):
    title: str
    asset_type: str
    text_content: str | None = None
    file_path: str | None = None
    metadata: dict = {}


class CreativeAssetResponse(BaseModel):
    id: str
    title: str
    asset_type: str
    text_content: str | None = None
    file_path: str | None = None
    metadata: dict
    created_at: datetime
