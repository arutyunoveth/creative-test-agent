"""Tests for bootstrap admin script."""

import os
import sys


def _clear_settings_cache():
    from src.shared.config.settings import get_settings
    get_settings.cache_clear()


def test_bootstrap_admin_imports():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import scripts.bootstrap_admin  # noqa: F401


def test_bootstrap_admin_has_main():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from scripts.bootstrap_admin import main
    assert callable(main)


def test_bootstrap_admin_creates_admin(monkeypatch):
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_EMAIL", "bootstrap@test.local")
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_PASSWORD", "bootstrap-strong-pw")
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_NAME", "Bootstrap Admin")
    monkeypatch.setenv("CTA_ENABLE_AUTH", "true")
    monkeypatch.setenv("CTA_SECRET_KEY", "test-secret-for-bootstrap")
    _clear_settings_cache()

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from scripts.bootstrap_admin import bootstrap_admin

    result = bootstrap_admin()
    assert result is True

    result2 = bootstrap_admin()
    assert result2 is True


def test_bootstrap_admin_fails_without_email(monkeypatch):
    monkeypatch.delenv("CTA_BOOTSTRAP_ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("CTA_BOOTSTRAP_ADMIN_PASSWORD", raising=False)
    _clear_settings_cache()

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from scripts.bootstrap_admin import bootstrap_admin

    result = bootstrap_admin()
    assert result is False


def test_bootstrap_admin_fails_short_password(monkeypatch):
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_EMAIL", "shortpw@test.local")
    monkeypatch.setenv("CTA_BOOTSTRAP_ADMIN_PASSWORD", "short")
    _clear_settings_cache()

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from scripts.bootstrap_admin import bootstrap_admin

    result = bootstrap_admin()
    assert result is False
