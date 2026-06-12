from datetime import datetime, timedelta, timezone

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.shared.config.settings import get_settings

SESSION_DATA_KEY = "session_data"


def _get_serializer() -> URLSafeTimedSerializer:
    settings = get_settings()
    secret = settings.secret_key or "insecure-dev-secret-key-do-not-use-in-production"
    return URLSafeTimedSerializer(secret, salt="cta-session")


def create_session_token(user_id: str, role: str, display_name: str) -> str:
    s = _get_serializer()
    data = {
        "user_id": user_id,
        "role": role,
        "display_name": display_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    settings = get_settings()
    max_age = settings.session_ttl_hours * 3600
    return s.dumps(data)


def decode_session_token(token: str) -> dict | None:
    if not token:
        return None
    s = _get_serializer()
    settings = get_settings()
    max_age = settings.session_ttl_hours * 3600
    try:
        data = s.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None
