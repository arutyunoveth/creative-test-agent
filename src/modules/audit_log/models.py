from datetime import datetime, timezone


class AuditEvent:
    def __init__(
        self,
        event_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        payload: dict | None = None,
    ):
        self.id = event_id
        self.event_type = event_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.payload = payload or {}
        self.created_at = datetime.now(timezone.utc)
