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
    extracted_text: str | None = None
    original_filename: str | None = None
    file_path: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    metadata: dict
    created_at: datetime
