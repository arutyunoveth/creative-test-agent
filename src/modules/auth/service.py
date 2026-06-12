from src.modules.users.schemas import UserLoginRequest
from src.modules.users.service import authenticate_user


def login(email: str, password: str) -> dict:
    req = UserLoginRequest(email=email, password=password)
    result = authenticate_user(req)
    return {
        "message": "Login successful",
        "user_id": result.user_id,
        "display_name": result.display_name,
        "role": result.role,
        "token": result.token,
    }
