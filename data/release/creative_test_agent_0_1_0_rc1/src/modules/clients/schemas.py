from datetime import datetime

from pydantic import BaseModel


class CreateClientRequest(BaseModel):
    name: str
    industry: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None


class ClientResponse(BaseModel):
    id: str
    name: str
    industry: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime | None = None
