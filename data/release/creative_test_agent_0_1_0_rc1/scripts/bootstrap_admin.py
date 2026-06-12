"""
Bootstrap admin user from environment variables.

Creates an admin user using:
    CTA_BOOTSTRAP_ADMIN_EMAIL
    CTA_BOOTSTRAP_ADMIN_PASSWORD
    CTA_BOOTSTRAP_ADMIN_NAME

Idempotent — will not create a duplicate admin.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.shared.config.settings import get_settings
from src.shared.db.session import init_db


def bootstrap_admin() -> bool:
    settings = get_settings()
    init_db()

    if not settings.bootstrap_admin_email or not settings.bootstrap_admin_password:
        print("Error: CTA_BOOTSTRAP_ADMIN_EMAIL and CTA_BOOTSTRAP_ADMIN_PASSWORD must be set.")
        return False

    if not settings.enable_auth:
        print("Warning: CTA_ENABLE_AUTH is false. The admin user will be created but auth is not enabled.")

    if len(settings.bootstrap_admin_password) < settings.password_min_length:
        print(f"Error: Password must be at least {settings.password_min_length} characters.")
        return False

    from src.modules.users.models import UserRole
    from src.modules.users.schemas import CreateUserRequest
    from src.modules.users.service import create_user, get_user_by_email

    existing = get_user_by_email(settings.bootstrap_admin_email)
    if existing:
        print(f"Admin user '{existing.email}' already exists (id={existing.id}).")
        return True

    user = create_user(CreateUserRequest(
        email=settings.bootstrap_admin_email,
        display_name=settings.bootstrap_admin_name,
        role=UserRole.admin,
        is_active=True,
        password=settings.bootstrap_admin_password,
    ))
    print(f"Admin user created: {user.email} (id={user.id}, role={user.role})")
    return True


def main():
    success = bootstrap_admin()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
