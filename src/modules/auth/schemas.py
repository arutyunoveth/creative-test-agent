from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str = "Login successful"
    user_id: str
    display_name: str
    role: str
    token: str


class MeResponse(BaseModel):
    user_id: str
    display_name: str
    role: str
    is_active: bool
    auth_enabled: bool
