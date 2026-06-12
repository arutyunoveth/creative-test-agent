"""Project history — timeline of entities associated with a project."""

from datetime import datetime, timezone

from pydantic import BaseModel

from src.shared.db.repository import db_session


class TimelineEntry(BaseModel):
    id: str
    entity_type: str
    title: str
    detail: str
    timestamp: datetime


def get_project_history(project_id: str) -> list[dict]:
    entries: list[dict] = []

    def _add(model, entity_type: str, title_field: str, detail_field: str | None = None):
        with db_session() as db:
            items = db.query(model).filter(
                getattr(model, "project_id", None) == project_id
            ).all()
            for item in items:
                title = getattr(item, title_field, "")
                detail = ""
                if detail_field:
                    detail = str(getattr(item, detail_field, ""))
                ts = getattr(item, "created_at", datetime.now(timezone.utc))
                entries.append({
                    "id": item.id,
                    "entity_type": entity_type,
                    "title": title,
                    "detail": detail,
                    "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                })

    from src.modules.creative_assets.models import CreativeAsset
    from src.modules.test_runs.models import TestRun
    from src.modules.report_generator.models import Report
    from src.modules.audit_log.models import AuditEvent

    _add(CreativeAsset, "creative_asset", "title", "asset_type")
    _add(TestRun, "test_run", "id", "status")
    _add(Report, "report", "id", "report_type")
    _add(AuditEvent, "audit_event", "event_type", "entity_type")

    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries
