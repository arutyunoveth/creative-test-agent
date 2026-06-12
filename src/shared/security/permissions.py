from fastapi import Depends, HTTPException

from src.shared.config.settings import get_settings

from .auth import get_current_user_from_request

WRITE_ROLES = {"admin", "manager", "analyst"}
MANAGE_ROLES = {"admin"}
ADMIN_ONLY = {"admin"}


def _current_user(current_user: dict = Depends(get_current_user_from_request)):
    return current_user


def require_auth(current_user: dict = Depends(get_current_user_from_request)):
    if not get_settings().enable_auth:
        return current_user
    if current_user.get("user_id") == "system":
        return current_user
    return current_user


def require_role(*roles: str):
    def _check(current_user: dict = Depends(get_current_user_from_request)):
        settings = get_settings()
        if not settings.enable_auth:
            return current_user
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.get('role')}' not allowed. Required: {', '.join(roles)}",
            )
        return current_user
    return _check


def require_write(current_user: dict = Depends(get_current_user_from_request)):
    settings = get_settings()
    if not settings.enable_auth:
        return current_user
    role = current_user.get("role", "")
    if role not in WRITE_ROLES:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{role}' does not have write permission",
        )
    return current_user


def require_admin(current_user: dict = Depends(get_current_user_from_request)):
    settings = get_settings()
    if not settings.enable_auth:
        return current_user
    role = current_user.get("role", "")
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Role '{role}' does not have admin permission",
        )
    return current_user


def role_at_least(min_role: str) -> callable:
    hierarchy = {"viewer": 0, "analyst": 1, "manager": 2, "admin": 3}

    def _check(current_user: dict = Depends(get_current_user_from_request)):
        settings = get_settings()
        if not settings.enable_auth:
            return current_user
        user_role = current_user.get("role", "viewer")
        if hierarchy.get(user_role, 0) < hierarchy.get(min_role, 0):
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user_role}' insufficient. Minimum required: {min_role}",
            )
        return current_user
    return _check
