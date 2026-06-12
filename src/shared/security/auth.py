from fastapi import Cookie, HTTPException, Request

from src.shared.config.settings import get_settings

from .session import decode_session_token

AUTH_DISABLED_USER = {
    "user_id": "system",
    "role": "admin",
    "display_name": "System",
    "is_active": True,
}


def get_current_user_from_request(request: Request) -> dict:
    settings = get_settings()
    if not settings.enable_auth:
        return dict(AUTH_DISABLED_USER)

    cookie_name = settings.session_cookie_name
    token = request.cookies.get(cookie_name)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = decode_session_token(token)
    if data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    from src.modules.users.models import User
    from src.shared.db.repository import db_session

    with db_session() as db:
        user = db.query(User).filter(User.id == data["user_id"]).first()
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        return {
            "user_id": user.id,
            "role": user.role,
            "display_name": user.display_name,
            "is_active": user.is_active,
        }
