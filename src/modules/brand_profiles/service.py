from uuid import uuid4

from src.modules.brand_profiles.models import BrandProfile
from src.modules.brand_profiles.schemas import (
    BrandProfileResponse,
    CreateBrandProfileRequest,
)

_store: dict[str, BrandProfile] = {}


def _to_response(profile: BrandProfile) -> BrandProfileResponse:
    return BrandProfileResponse(
        id=profile.id,
        name=profile.name,
        tone_of_voice=profile.tone_of_voice,
        target_audience=profile.target_audience,
        restrictions=profile.restrictions,
        claims_policy=profile.claims_policy,
        created_at=profile.created_at,
    )


def create_profile(req: CreateBrandProfileRequest) -> BrandProfileResponse:
    profile = BrandProfile(
        profile_id=str(uuid4()),
        name=req.name,
        tone_of_voice=req.tone_of_voice,
        target_audience=req.target_audience,
        restrictions=req.restrictions,
        claims_policy=req.claims_policy,
    )
    _store[profile.id] = profile
    return _to_response(profile)


def list_profiles() -> list[BrandProfileResponse]:
    return [_to_response(p) for p in _store.values()]


def get_profile(profile_id: str) -> BrandProfileResponse | None:
    profile = _store.get(profile_id)
    if profile is None:
        return None
    return _to_response(profile)
