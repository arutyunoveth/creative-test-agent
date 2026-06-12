"""Tests for users/roles foundation module."""

from src.modules.users.models import UserRole, User
from src.modules.users.service import get_system_user, list_users, get_current_user_id
from src.shared.config.settings import get_settings


def test_user_role_enum():
    """UserRole enum has expected values."""
    assert UserRole.admin == "admin"
    assert UserRole.manager == "manager"
    assert UserRole.analyst == "analyst"
    assert UserRole.viewer == "viewer"


def test_auth_disabled_by_default():
    """CTA_ENABLE_AUTH is False by default."""
    s = get_settings()
    assert s.enable_auth is False


def test_system_user_returns_correct_info():
    """get_system_user() returns system user context."""
    info = get_system_user()
    assert info.user_id == "system"
    assert info.display_name == "System"
    assert info.role == "admin"
    assert info.auth_enabled is False


def test_get_current_user_id_returns_system():
    """get_current_user_id() returns 'system' when auth disabled."""
    assert get_current_user_id() == "system"


def test_user_model_has_all_fields():
    """User model has expected columns."""
    cols = {c.name for c in User.__table__.columns}
    expected = {"id", "email", "display_name", "role", "is_active",
                "password_hash", "metadata_json", "created_at", "updated_at"}
    assert cols >= expected, f"Missing: {expected - cols}"


def test_list_users_returns_list():
    """list_users() returns a list (possibly empty)."""
    users = list_users()
    assert isinstance(users, list)
