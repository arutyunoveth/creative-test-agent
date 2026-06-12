import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CTA_", env_file=".env")

    app_name: str = "Creative Test Agent API"
    debug: bool = False
    database_url: str = "sqlite:///./creative_test_agent.db"
    local_only_mode: bool = True
    allow_cloud_llm: bool = False
    llm_provider: str = "stub"
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: int = 60
    storage_root: str = "./data/storage"
    max_upload_size_mb: int = 25
    allowed_upload_types: str = "txt,md,pdf,png,jpg,jpeg,webp"

    vision_provider: str = "stub"
    enable_local_ocr: bool = False
    enable_local_vlm: bool = False
    vision_model: str | None = None
    vision_base_url: str | None = None
    vision_timeout_seconds: int = 60
    run_local_vision_smoke_tests: bool = False

    env: str = "local"
    host: str = "127.0.0.1"
    port: int = 8000
    public_base_url: str = "http://localhost:8000"
    secret_key: str = ""

    enable_auth: bool = False
    enable_admin: bool = False
    enable_projects: bool = False
    enable_brandbooks: bool = False
    enable_advanced_exports: bool = False

    exports_root: str = "./data/exports"

    enable_review_auto_learning: bool = True
    enable_knowledge_auto_ingest: bool = True
    kb_chunk_size_chars: int = 1200
    kb_chunk_overlap_chars: int = 150
    kb_context_max_items: int = 8
    kb_context_max_chars: int = 6000

    session_cookie_name: str = "cta_session"
    session_ttl_hours: int = 12
    password_min_length: int = 10
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""
    bootstrap_admin_name: str = "Admin"

    cors_allowed_origins: str = ""
    trusted_hosts: str = "localhost,127.0.0.1"

    # Backup
    backup_root: str = "./data/backups"
    backup_include_uploads: bool = True
    backup_include_exports: bool = True

    # Prompt tracing
    enable_prompt_tracing: bool = True
    prompt_trace_store_full: bool = False
    prompt_trace_preview_chars: int = 2000
    prompt_trace_max_full_chars: int = 20000

    # Evaluation thresholds
    eval_max_repair_count: int = 2
    eval_max_fallback_count: int = 0

    # Logging
    log_level: str = "INFO"
    log_format: str = "plain"
    log_file: str = ""

    def is_development(self) -> bool:
        return self.env == "local"

    def is_stub_mode(self) -> bool:
        return self.llm_provider == "stub"

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.cors_allowed_origins:
            return []
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]

    def validate_server_settings(self) -> list[str]:
        errors: list[str] = []
        if self.env != "server":
            return errors
        if not self.secret_key:
            errors.append("CTA_SECRET_KEY must be set when CTA_ENV=server")
        elif self.secret_key == "change-this-secret-key":
            errors.append("CTA_SECRET_KEY must be changed from the default value")
        if not self.enable_auth:
            errors.append("CTA_ENABLE_AUTH is recommended when CTA_ENV=server")
        for name, path in [
            ("storage_root", self.storage_root),
            ("exports_root", self.exports_root),
            ("backup_root", self.backup_root),
        ]:
            if not os.access(os.path.dirname(os.path.abspath(path)), os.W_OK):
                errors.append(f"{name} directory is not writable: {path}")
        db_path = self.database_url.replace("sqlite:///", "")
        if db_path:
            db_dir = os.path.dirname(os.path.abspath(db_path))
            if not os.access(db_dir, os.W_OK):
                errors.append(f"Database directory is not writable: {db_dir}")
        return errors


@lru_cache()
def get_settings() -> Settings:
    return Settings()
