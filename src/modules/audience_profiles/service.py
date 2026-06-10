from uuid import uuid4

from src.modules.audience_profiles.models import AudienceProfile
from src.modules.audience_profiles.schemas import (
    AudienceProfileResponse,
    CreateAudienceProfileRequest,
)

_store: dict[str, AudienceProfile] = {}


def _to_response(p: AudienceProfile) -> AudienceProfileResponse:
    return AudienceProfileResponse(
        id=p.id,
        name=p.name,
        segment_description=p.segment_description,
        pains=p.pains,
        motivations=p.motivations,
        objections=p.objections,
        created_at=p.created_at,
    )


def create_profile(req: CreateAudienceProfileRequest) -> AudienceProfileResponse:
    profile = AudienceProfile(
        profile_id=str(uuid4()),
        name=req.name,
        segment_description=req.segment_description,
        pains=req.pains,
        motivations=req.motivations,
        objections=req.objections,
    )
    _store[profile.id] = profile
    return _to_response(profile)


def list_profiles() -> list[AudienceProfileResponse]:
    return [_to_response(p) for p in _store.values()]


def get_profile(profile_id: str) -> AudienceProfileResponse | None:
    profile = _store.get(profile_id)
    if profile is None:
        return None
    return _to_response(profile)
