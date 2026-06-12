from src.shared.config.settings import get_settings
from src.shared.db.repository import db_session, json_dumps, json_loads
from src.shared.security.password import hash_password, verify_password

from .models import User, UserRole
from .schemas import (CreateUserRequest, SystemUserInfo, UpdateUserRequest,
                      UserLoginRequest, UserLoginResponse, UserResponse)


def get_system_user() -> SystemUserInfo:
    return SystemUserInfo()


def get_current_user_id() -> str:
    return "system"


def create_user(req: CreateUserRequest) -> UserResponse:
    with db_session() as db:
        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise ValueError(f"User with email '{req.email}' already exists")

        pw_hash = None
        if req.password:
            settings = get_settings()
            if len(req.password) < settings.password_min_length:
                raise ValueError(f"Password must be at least {settings.password_min_length} characters")
            pw_hash = hash_password(req.password)

        user = User(
            email=req.email,
            display_name=req.display_name,
            role=req.role,
            is_active=req.is_active,
            password_hash=pw_hash,
        )
        db.add(user)
        db.flush()
        db.refresh(user)
        return _to_response(user)


def update_user(user_id: str, req: UpdateUserRequest) -> UserResponse:
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise ValueError("User not found")
        if req.display_name is not None:
            user.display_name = req.display_name
        if req.role is not None:
            user.role = req.role
        if req.is_active is not None:
            user.is_active = req.is_active
        db.flush()
        db.refresh(user)
        return _to_response(user)


def deactivate_user(user_id: str) -> UserResponse:
    return update_user(user_id, UpdateUserRequest(is_active=False))


def get_user_by_email(email: str) -> UserResponse | None:
    with db_session() as db:
        user = db.query(User).filter(User.email == email).first()
        return _to_response(user) if user else None


def authenticate_user(req: UserLoginRequest) -> UserLoginResponse:
    with db_session() as db:
        user = db.query(User).filter(User.email == req.email).first()
        if user is None:
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("User account is inactive")
        if not user.password_hash:
            raise ValueError("User has no password set")

        if not verify_password(req.password, user.password_hash):
            raise ValueError("Invalid email or password")

        from src.shared.security.session import create_session_token

        token = create_session_token(user.id, user.role, user.display_name)
        return UserLoginResponse(
            token=token,
            user_id=user.id,
            display_name=user.display_name,
            role=user.role,
        )


def list_users() -> list[UserResponse]:
    with db_session() as db:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return [_to_response(u) for u in users]


def get_user(user_id: str) -> UserResponse | None:
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        return _to_response(user) if user else None


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        is_active=user.is_active,
        metadata=json_loads(user.metadata_json),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
