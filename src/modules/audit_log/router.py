from fastapi import APIRouter

from src.modules.audit_log.schemas import AuditEventResponse
from src.modules.audit_log.service import list_audit_events

router = APIRouter(prefix="/audit-log", tags=["audit-log"])


@router.get("", response_model=list[AuditEventResponse])
def get_audit_log():
    return list_audit_events()
