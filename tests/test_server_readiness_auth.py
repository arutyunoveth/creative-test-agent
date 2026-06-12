"""Tests for server readiness checks related to auth."""

import os
import sys


def test_check_server_readiness_settings_auth():
    """check_server_readiness checks auth settings."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.shared.config.settings import get_settings
    s = get_settings()
    assert hasattr(s, "enable_auth")
    assert hasattr(s, "secret_key")
    assert hasattr(s, "session_cookie_name")
    assert hasattr(s, "session_ttl_hours")
    assert hasattr(s, "password_min_length")
    assert hasattr(s, "bootstrap_admin_email")
    assert hasattr(s, "bootstrap_admin_password")
    assert hasattr(s, "bootstrap_admin_name")


def test_makefile_has_bootstrap_admin():
    """Makefile includes bootstrap-admin command."""
    makefile = os.path.join(os.path.dirname(__file__), "..", "Makefile")
    assert os.path.isfile(makefile)
    with open(makefile) as f:
        content = f.read()
    assert "bootstrap-admin" in content


def test_env_example_has_auth_vars():
    """.env.example includes auth-related variables."""
    example = os.path.join(os.path.dirname(__file__), "..", ".env.example")
    assert os.path.isfile(example)
    with open(example) as f:
        content = f.read()
    assert "CTA_SESSION_COOKIE_NAME" in content
    assert "CTA_SESSION_TTL_HOURS" in content
    assert "CTA_PASSWORD_MIN_LENGTH" in content
    assert "CTA_BOOTSTRAP_ADMIN_EMAIL" in content
    assert "CTA_BOOTSTRAP_ADMIN_PASSWORD" in content
    assert "CTA_BOOTSTRAP_ADMIN_NAME" in content


def test_auth_docs_exist():
    """docs/auth_roles.md exists."""
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "auth_roles.md")
    assert os.path.isfile(path)


def test_pilot_check_still_works():
    """pilot-check still in Makefile."""
    makefile = os.path.join(os.path.dirname(__file__), "..", "Makefile")
    with open(makefile) as f:
        content = f.read()
    assert "pilot-check" in content
    assert "client-pilot-check" in content
