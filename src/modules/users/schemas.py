from datetime import datetime

from pydantic import BaseModel

from .models import UserRole


class CreateUserRequest(BaseModel):
    email: str
    display_name: str
    role: UserRole = UserRole.viewer
    is_active: bool = True
    password: str | None = None


class UpdateUserRequest(BaseModel):
    display_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    is_active: bool
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime | None = None


class SystemUserInfo(BaseModel):
    user_id: str = "system"
    display_name: str = "System"
    role: str = "admin"
    is_active: bool = True
    auth_enabled: bool = False


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserLoginResponse(BaseModel):
    token: str
    user_id: str
    display_name: str
    role: str
