from datetime import datetime

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: str
    event_type: str
    entity_type: str
    entity_id: str
    payload: dict
    created_at: datetime
