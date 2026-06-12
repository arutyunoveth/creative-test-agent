from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from src.shared.config.settings import get_settings
from src.shared.security.auth import get_current_user_from_request
from src.shared.security.session import decode_session_token

from .schemas import LoginRequest, LoginResponse, MeResponse
from .service import login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def auth_login(body: LoginRequest, request: Request):
    settings = get_settings()
    if not settings.enable_auth:
        return {"message": "Auth is disabled in local/demo mode", "auth_enabled": False}

    try:
        result = login(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    response = JSONResponse(content=result)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=result["token"],
        httponly=True,
        max_age=settings.session_ttl_hours * 3600,
        samesite="lax",
    )
    return response


@router.post("/logout")
def auth_logout(request: Request):
    settings = get_settings()
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key=settings.session_cookie_name)
    return response


@router.get("/me")
def auth_me(current_user: dict = Depends(get_current_user_from_request)):
    settings = get_settings()
    return {
        "user_id": current_user["user_id"],
        "display_name": current_user["display_name"],
        "role": current_user["role"],
        "is_active": current_user.get("is_active", True),
        "auth_enabled": settings.enable_auth,
    }
