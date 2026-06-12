"""Tests for server env profile and settings validation."""
import os
from pathlib import Path


def test_env_server_example_exists():
    assert Path(".env.server.example").is_file()


def test_env_server_example_contains_required_vars():
    content = Path(".env.server.example").read_text()
    required = [
        "CTA_ENV=",
        "CTA_HOST=",
        "CTA_PORT=",
        "CTA_SECRET_KEY=",
        "CTA_ENABLE_AUTH=",
        "CTA_DATABASE_URL=",
        "CTA_STORAGE_ROOT=",
        "CTA_EXPORTS_ROOT=",
        "CTA_BACKUP_ROOT=",
        "CTA_LLM_PROVIDER=",
        "CTA_ENABLE_ADMIN=",
    ]
    for var in required:
        assert var in content, f"Missing {var} in .env.server.example"


def test_env_server_example_secret_key_is_placeholder():
    content = Path(".env.server.example").read_text()
    assert "change-this-secret-key" in content


def test_env_server_example_has_backup_settings():
    content = Path(".env.server.example").read_text()
    assert "CTA_BACKUP_ROOT" in content
    assert "CTA_BACKUP_INCLUDE_UPLOADS" in content
    assert "CTA_BACKUP_INCLUDE_EXPORTS" in content


def test_env_server_example_has_log_settings():
    content = Path(".env.server.example").read_text()
    assert "CTA_LOG_LEVEL" in content
    assert "CTA_LOG_FORMAT" in content
    assert "CTA_LOG_FILE" in content


def test_settings_has_backup_fields():
    from src.shared.config.settings import get_settings

    s = get_settings()
    assert hasattr(s, "backup_root")
    assert hasattr(s, "backup_include_uploads")
    assert hasattr(s, "backup_include_exports")


def test_settings_has_log_fields():
    from src.shared.config.settings import get_settings

    s = get_settings()
    assert hasattr(s, "log_level")
    assert hasattr(s, "log_format")
    assert hasattr(s, "log_file")


def test_server_validation_no_errors_in_local_env():
    from src.shared.config.settings import get_settings

    s = get_settings()
    errors = s.validate_server_settings()
    assert errors == [], f"Expected no errors in local env, got: {errors}"


def test_server_validation_detects_missing_secret():
    from src.shared.config.settings import Settings

    s = Settings(env="server", secret_key="")
    errors = s.validate_server_settings()
    assert any("CTA_SECRET_KEY must be set" in e for e in errors)


def test_server_validation_detects_default_secret():
    from src.shared.config.settings import Settings

    s = Settings(env="server", secret_key="change-this-secret-key")
    errors = s.validate_server_settings()
    assert any("must be changed" in e for e in errors)


def test_server_validation_recommends_auth():
    from src.shared.config.settings import Settings

    s = Settings(env="server", enable_auth=False)
    errors = s.validate_server_settings()
    assert any("CTA_ENABLE_AUTH is recommended" in e for e in errors)


def test_backup_settings_defaults():
    from src.shared.config.settings import Settings

    s = Settings()
    assert s.backup_root == "./data/backups"
    assert s.backup_include_uploads is True
    assert s.backup_include_exports is True


def test_log_settings_defaults():
    from src.shared.config.settings import Settings

    s = Settings()
    assert s.log_level == "INFO"
    assert s.log_format == "plain"
    assert s.log_file == ""
