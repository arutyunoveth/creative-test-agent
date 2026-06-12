#!/usr/bin/env python3
"""
Create a backup of creative-test-agent data.

Usage:
    python scripts/backup_data.py [output_path]

If output_path is omitted, backup is saved to CTA_BACKUP_ROOT with
a timestamped filename.
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def get_entity_counts() -> dict:
    """Count entities in the database."""
    try:
        from src.shared.db.session import init_db
        from src.shared.db.repository import db_session

        init_db()
        counts = {
            "clients": 0,
            "projects": 0,
            "creative_assets": 0,
            "test_runs": 0,
            "reports": 0,
            "brandbooks": 0,
            "knowledge_items": 0,
            "export_jobs": 0,
        }
        models_map = {
            "clients": "src.modules.clients.models.Client",
            "projects": "src.modules.projects.models.Project",
            "creative_assets": "src.modules.creative_assets.models.CreativeAsset",
            "test_runs": "src.modules.test_runs.models.TestRun",
            "reports": "src.modules.report_generator.models.Report",
            "brandbooks": "src.modules.brandbooks.models.BrandbookDocument",
            "knowledge_items": "src.modules.knowledge_base.models.KnowledgeItem",
            "export_jobs": "src.modules.export_jobs.models.ExportJob",
        }
        with db_session() as db:
            for key, model_path in models_map.items():
                parts = model_path.split(".")
                mod = __import__(".".join(parts[:-1]), fromlist=[parts[-1]])
                model = getattr(mod, parts[-1])
                counts[key] = db.query(model).count()
        return counts
    except Exception:
        return {}


def _write_audit_log(event_type: str, detail: str) -> None:
    try:
        from src.shared.db.session import check_db_connection
        if check_db_connection():
            from src.modules.audit_log.service import write_audit_event
            write_audit_event(event_type, "backup", "system", {"detail": detail})
    except Exception:
        pass


def create_backup(output_path: str | None = None) -> str:
    from src.shared.config.settings import get_settings

    settings = get_settings()
    _write_audit_log("backup_created", f"Starting backup to {output_path or settings.backup_root}")
    backup_root = os.path.abspath(settings.backup_root)
    os.makedirs(backup_root, exist_ok=True)

    if output_path:
        backup_path = os.path.abspath(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_root, f"cta_backup_{timestamp}.zip")

    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_path = os.path.abspath(db_url.replace("sqlite:///", ""))
    else:
        db_path = None

    storage_root = os.path.abspath(settings.storage_root)
    exports_root = os.path.abspath(settings.exports_root)

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "app": "creative-test-agent",
        "database_url_type": "sqlite",
        "included": {
            "database": db_path is not None,
            "storage": settings.backup_include_uploads and os.path.isdir(storage_root),
            "exports": settings.backup_include_exports and os.path.isdir(exports_root),
        },
        "counts": get_entity_counts(),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        if db_path and os.path.isfile(db_path):
            shutil.copy2(db_path, os.path.join(tmpdir, "creative_test_agent.db"))

        if manifest["included"]["storage"]:
            shutil.copytree(storage_root, os.path.join(tmpdir, "storage"), dirs_exist_ok=True)

        if manifest["included"]["exports"]:
            shutil.copytree(exports_root, os.path.join(tmpdir, "exports"), dirs_exist_ok=True)

        with open(os.path.join(tmpdir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2, default=str)

        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmpdir):
                for fn in files:
                    file_path = os.path.join(root, fn)
                    arcname = os.path.relpath(file_path, tmpdir)
                    zf.write(file_path, arcname)

    print(f"Backup created: {backup_path}")
    print(f"  Database: {'included' if manifest['included']['database'] else 'not found'}")
    print(f"  Storage:  {'included' if manifest['included']['storage'] else 'skipped'}")
    print(f"  Exports:  {'included' if manifest['included']['exports'] else 'skipped'}")
    print(f"  Entities: {json.dumps(manifest['counts'], default=str)}")
    return backup_path


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        create_backup(output_path)
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
