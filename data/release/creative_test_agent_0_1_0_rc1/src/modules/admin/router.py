"""Admin maintenance endpoints for server operations."""

import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from src.shared.config.settings import get_settings
from src.shared.db.session import check_db_connection
from src.shared.security.permissions import require_admin, role_at_least

from .schemas import DatabaseStatus, MaintenanceStatus, StorageStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def _check_migration_status():
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine
        from alembic.runtime.migration import MigrationContext

        settings = get_settings()
        alembic_cfg = Config(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "alembic.ini")
        )
        script = ScriptDirectory.from_config(alembic_cfg)
        head = script.get_current_head()

        engine = create_engine(settings.database_url)
        conn = engine.connect()
        mctx = MigrationContext.configure(conn)
        db_rev = mctx.get_current_revision()
        conn.close()
        engine.dispose()

        up_to_date = head == db_rev if head and db_rev else None
        return head, db_rev, up_to_date
    except Exception:
        return None, None, None


def _check_writable(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        test_file = os.path.join(path, ".write_test")
        open(test_file, "w").close()
        os.remove(test_file)
        return True
    except Exception:
        return False


def _count_files(path: str) -> int:
    count = 0
    for root, _dirs, files in os.walk(path):
        count += len(files)
    return count


def _total_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for fn in files:
            try:
                total += os.path.getsize(os.path.join(root, fn))
            except Exception:
                pass
    return total


@router.get("/maintenance/status", response_model=MaintenanceStatus)
def get_maintenance_status(
    current_user: dict = Depends(role_at_least("admin")),
):
    from src.modules.audit_log.service import write_audit_event
    settings = get_settings()
    head, db_rev, up_to_date = _check_migration_status()
    write_audit_event("maintenance_status_requested", "maintenance", "system", {"env": settings.env})
    logger.info("Maintenance status requested (env=%s)", settings.env)

    return MaintenanceStatus(
        env=settings.env,
        database_connected=check_db_connection(),
        database_url_type="sqlite",
        storage_writable=_check_writable(settings.storage_root),
        exports_writable=_check_writable(settings.exports_root),
        backup_root_writable=_check_writable(settings.backup_root),
        migration_head=head,
        migration_db_revision=db_rev,
        migration_up_to_date=up_to_date,
        closed_loop_enabled=settings.local_only_mode,
        auth_enabled=settings.enable_auth,
        enable_projects=settings.enable_projects,
        llm_provider=settings.llm_provider,
        vision_provider=settings.vision_provider,
        checked_at=datetime.now(timezone.utc),
    )


@router.get("/maintenance/storage", response_model=StorageStatus)
def get_storage_status(
    current_user: dict = Depends(role_at_least("admin")),
):
    settings = get_settings()
    storage_path = os.path.abspath(settings.storage_root)
    exports_path = os.path.abspath(settings.exports_root)
    backup_path = os.path.abspath(settings.backup_root)
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(exports_path, exist_ok=True)
    os.makedirs(backup_path, exist_ok=True)

    return StorageStatus(
        storage_root=str(storage_path),
        writable=_check_writable(storage_path),
        total_files=_count_files(storage_path),
        total_size_bytes=_total_size(storage_path),
        exports_root=str(exports_path),
        exports_writable=_check_writable(exports_path),
        backup_root=str(backup_path),
        backup_writable=_check_writable(backup_path),
    )


@router.get("/maintenance/database", response_model=DatabaseStatus)
def get_database_status(
    current_user: dict = Depends(role_at_least("admin")),
):
    settings = get_settings()
    connected = check_db_connection()
    head, db_rev, up_to_date = _check_migration_status()

    table_count = 0
    if connected:
        try:
            from sqlalchemy import create_engine, inspect
            engine = create_engine(settings.database_url)
            inspector = inspect(engine)
            table_count = len(inspector.get_table_names())
            engine.dispose()
        except Exception:
            pass

    return DatabaseStatus(
        connected=connected,
        url_type="sqlite",
        table_count=table_count,
        migration_head=head,
        migration_db_revision=db_rev,
        migration_up_to_date=up_to_date,
    )
