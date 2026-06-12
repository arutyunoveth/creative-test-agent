from datetime import datetime
from pydantic import BaseModel


class MaintenanceStatus(BaseModel):
    env: str
    database_connected: bool
    database_url_type: str
    storage_writable: bool
    exports_writable: bool
    backup_root_writable: bool
    migration_head: str | None = None
    migration_db_revision: str | None = None
    migration_up_to_date: bool | None = None
    closed_loop_enabled: bool
    auth_enabled: bool
    enable_projects: bool
    llm_provider: str
    vision_provider: str
    checked_at: datetime


class StorageStatus(BaseModel):
    storage_root: str
    writable: bool
    total_files: int
    total_size_bytes: int
    exports_root: str
    exports_writable: bool
    backup_root: str
    backup_writable: bool


class DatabaseStatus(BaseModel):
    connected: bool
    url_type: str
    table_count: int
    migration_head: str | None = None
    migration_db_revision: str | None = None
    migration_up_to_date: bool | None = None
