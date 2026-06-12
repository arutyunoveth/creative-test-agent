from fastapi import APIRouter, Depends, HTTPException

from src.shared.config.settings import get_settings
from src.shared.security.permissions import get_current_user_from_request, require_admin

from .schemas import (CreateUserRequest, SystemUserInfo, UpdateUserRequest,
                      UserResponse)
from .service import (create_user, deactivate_user, get_user, list_users,
                      update_user)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_current_user(current_user: dict = Depends(get_current_user_from_request)):
    settings = get_settings()
    if not settings.enable_auth:
        return SystemUserInfo()
    return {
        "user_id": current_user["user_id"],
        "display_name": current_user["display_name"],
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "auth_enabled": True,
    }


@router.get("", response_model=list[UserResponse])
def get_users(current_user: dict = Depends(require_admin)):
    return list_users()


@router.post("", response_model=UserResponse, status_code=201)
def post_create_user(body: CreateUserRequest, current_user: dict = Depends(require_admin)):
    try:
        return create_user(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, current_user: dict = Depends(require_admin)):
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user(user_id: str, body: UpdateUserRequest, current_user: dict = Depends(require_admin)):
    try:
        return update_user(user_id, body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def post_deactivate_user(user_id: str, current_user: dict = Depends(require_admin)):
    try:
        return deactivate_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
