from src.modules.audit_log.models import AuditEvent
from src.modules.audit_log.schemas import AuditEventResponse
from src.shared.db.repository import db_session, json_dumps, json_loads


def _to_response(e: AuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=e.id,
        event_type=e.event_type,
        entity_type=e.entity_type,
        entity_id=e.entity_id,
        payload=json_loads(e.payload_json) or {},
        created_at=e.created_at,
    )


def write_audit_event(
    event_type: str,
    entity_type: str,
    entity_id: str,
    payload: dict | None = None,
) -> AuditEventResponse:
    with db_session() as db:
        event = AuditEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_json=json_dumps(payload or {}),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        return _to_response(event)


def list_audit_events() -> list[AuditEventResponse]:
    with db_session() as db:
        events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).all()
        return [_to_response(e) for e in events]
