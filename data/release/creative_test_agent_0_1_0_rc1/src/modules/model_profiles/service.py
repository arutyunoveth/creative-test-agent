import json
import os

from src.modules.model_profiles.models import ModelProfile
from src.modules.model_profiles.schemas import (
    CreateModelProfileRequest,
    ModelProfileHealth,
    ModelProfileResponse,
)
from src.shared.db.repository import db_session, json_dumps, json_loads

ALLOWED_PROVIDERS = {"stub", "ollama", "lmstudio"}
FORBIDDEN_PROVIDERS = {"openai", "anthropic", "gemini", "perplexity", "claude", "azure_openai"}

LOCAL_ONLY_PROVIDERS = {"ollama", "lmstudio"}


def _check_url_is_allowed(base_url: str, provider: str) -> list[str]:
    warnings: list[str] = []
    if provider in LOCAL_ONLY_PROVIDERS:
        if base_url and ("api.openai.com" in base_url or "api.anthropic.com" in base_url or "api.gemini" in base_url):
            warnings.append(f"Cloud URL detected for local-only provider '{provider}': {base_url}")
    return warnings


def _to_response(p: ModelProfile) -> ModelProfileResponse:
    return ModelProfileResponse(
        id=p.id,
        profile_name=p.profile_name,
        provider=p.provider,
        model=p.model,
        base_url=p.base_url,
        enabled=p.enabled,
        default_for_demo=p.default_for_demo,
        timeout_seconds=p.timeout_seconds,
        notes=p.notes,
        metadata=json_loads(p.metadata_json) or {},
        created_at=p.created_at,
    )


def create_profile(req: CreateModelProfileRequest) -> ModelProfileResponse:
    if req.provider in FORBIDDEN_PROVIDERS:
        raise ValueError(f"Provider '{req.provider}' is not allowed")
    if req.provider not in ALLOWED_PROVIDERS:
        raise ValueError(f"Provider '{req.provider}' is not recognized. Allowed: {', '.join(sorted(ALLOWED_PROVIDERS))}")
    with db_session() as db:
        profile = ModelProfile(
            profile_name=req.profile_name,
            provider=req.provider,
            model=req.model,
            base_url=req.base_url,
            enabled=req.enabled,
            default_for_demo=req.default_for_demo,
            timeout_seconds=req.timeout_seconds,
            notes=req.notes,
            metadata_json=json_dumps(req.metadata),
        )
        db.add(profile)
        db.flush()
        db.refresh(profile)
        return _to_response(profile)


def list_profiles() -> list[ModelProfileResponse]:
    with db_session() as db:
        profiles = db.query(ModelProfile).order_by(ModelProfile.profile_name).all()
        return [_to_response(p) for p in profiles]


def get_profile(profile_id: str) -> ModelProfileResponse | None:
    with db_session() as db:
        p = db.query(ModelProfile).filter(ModelProfile.id == profile_id).first()
        if p is None:
            return None
        return _to_response(p)


def check_profile_health(profile_id: str) -> ModelProfileHealth:
    profile = get_profile(profile_id)
    if profile is None:
        raise ValueError(f"Model profile not found: {profile_id}")

    warnings: list[str] = []

    if profile.provider == "stub":
        return ModelProfileHealth(
            profile_id=profile.id,
            profile_name=profile.profile_name,
            provider=profile.provider,
            reachable=True,
            detail="Stub provider is always available.",
            warnings=warnings,
        )

    if profile.provider in FORBIDDEN_PROVIDERS:
        warnings.append(f"Provider '{profile.provider}' is forbidden.")
        return ModelProfileHealth(
            profile_id=profile.id,
            profile_name=profile.profile_name,
            provider=profile.provider,
            reachable=False,
            detail="Forbidden provider.",
            warnings=warnings,
        )

    if profile.provider in LOCAL_ONLY_PROVIDERS:
        url_warnings = _check_url_is_allowed(profile.base_url or "", profile.provider)
        warnings.extend(url_warnings)

    try:
        import http.client
        base = (profile.base_url or "").rstrip("/")
        if not base:
            raise ValueError("base_url is required for local providers")
        host = base.replace("http://", "").replace("https://", "").split(":")[0]
        port = int(base.split(":")[-1]) if ":" in base.split("//")[-1] else 80
        conn = http.client.HTTPConnection(host, port, timeout=profile.timeout_seconds)
        conn.request("GET", "/")
        resp = conn.getresponse()
        conn.close()
        reachable = True
        detail = f"Provider reachable (HTTP {resp.status})."
    except Exception as e:
        reachable = False
        detail = f"Provider unreachable: {e}"
        warnings.append(f"Health check failed: {e}")

    return ModelProfileHealth(
        profile_id=profile.id,
        profile_name=profile.profile_name,
        provider=profile.provider,
        reachable=reachable,
        detail=detail,
        warnings=warnings,
    )


def load_profile_from_config(config_path: str) -> ModelProfileResponse:
    with open(config_path) as f:
        data = json.load(f)
    req = CreateModelProfileRequest(
        profile_name=data["profile_name"],
        provider=data["provider"],
        model=data["model"],
        base_url=data.get("base_url"),
        enabled=data.get("enabled", False),
        default_for_demo=data.get("default_for_demo", False),
        timeout_seconds=data.get("timeout_seconds", 60),
        notes=data.get("notes"),
    )
    return create_profile(req)
