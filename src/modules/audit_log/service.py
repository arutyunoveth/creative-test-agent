from uuid import uuid4

from src.modules.audit_log.models import AuditEvent
from src.modules.audit_log.schemas import AuditEventResponse

_store: list[AuditEvent] = []


def _to_response(e: AuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=e.id,
        event_type=e.event_type,
        entity_type=e.entity_type,
        entity_id=e.entity_id,
        payload=e.payload,
        created_at=e.created_at,
    )


def write_audit_event(
    event_type: str,
    entity_type: str,
    entity_id: str,
    payload: dict | None = None,
) -> AuditEventResponse:
    event = AuditEvent(
        event_id=str(uuid4()),
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
    )
    _store.append(event)
    return _to_response(event)


def list_audit_events() -> list[AuditEventResponse]:
    return [_to_response(e) for e in _store]
