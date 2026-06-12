"""
Export all pilot data to a local JSON file.

Usage:
    python scripts/export_pilot_data.py

Output:
    data/exports/pilot_export_YYYYMMDD_HHMMSS.json
"""

import json
import os
import sys
from datetime import datetime, timezone

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def export_pilot_data() -> str:
    """Export all pilot data to a JSON file.

    Returns the path to the created export file.
    """
    from src.shared.db.repository import db_session, json_loads
    from src.modules.brand_profiles.models import BrandProfile
    from src.modules.audience_profiles.models import AudienceProfile
    from src.modules.creative_assets.models import CreativeAsset
    from src.modules.test_rubrics.models import TestRubric
    from src.modules.test_runs.models import TestRun
    from src.modules.report_generator.models import Report
    from src.modules.audit_log.models import AuditEvent

    now = datetime.now(timezone.utc)
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "exports")
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, f"pilot_export_{now.strftime('%Y%m%d_%H%M%S')}.json")

    def _serialize(instances, skip_fields=None):
        skip = set(skip_fields or [])
        result = []
        for inst in instances:
            row = {}
            for col in inst.__table__.columns:
                if col.name in skip:
                    continue
                val = getattr(inst, col.name)
                if isinstance(val, datetime):
                    val = val.isoformat()
                row[col.name] = val
            result.append(row)
        return result

    with db_session() as db:
        data = {
            "exported_at": now.isoformat(),
            "app": "Creative Test Agent",
            "brand_profiles": _serialize(db.query(BrandProfile).all()),
            "audience_profiles": _serialize(db.query(AudienceProfile).all()),
            "creative_assets": _serialize(db.query(CreativeAsset).all()),
            "test_rubrics": _serialize(db.query(TestRubric).all()),
            "test_runs": _serialize(db.query(TestRun).all()),
            "reports": _serialize(db.query(Report).all()),
            "audit_events": _serialize(db.query(AuditEvent).all()),
        }

    with open(export_path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return os.path.abspath(export_path)


def main():
    path = export_pilot_data()
    print(f"Pilot data exported to: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
