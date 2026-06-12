from src.modules.brand_profiles.models import BrandProfile
from src.modules.brand_profiles.schemas import (
    BrandProfileResponse,
    CreateBrandProfileRequest,
)
from src.shared.db.repository import db_session, json_dumps, json_loads


def _to_response(profile: BrandProfile) -> BrandProfileResponse:
    return BrandProfileResponse(
        id=profile.id,
        name=profile.name,
        tone_of_voice=profile.tone_of_voice,
        target_audience=profile.target_audience,
        restrictions=profile.restrictions,
        claims_policy=profile.claims_policy,
        metadata=json_loads(profile.metadata_json) or {},
        created_at=profile.created_at,
    )


def create_profile(req: CreateBrandProfileRequest) -> BrandProfileResponse:
    with db_session() as db:
        profile = BrandProfile(
            name=req.name,
            tone_of_voice=req.tone_of_voice,
            target_audience=req.target_audience,
            restrictions=req.restrictions,
            claims_policy=req.claims_policy,
            metadata_json=json_dumps(req.metadata),
        )
        db.add(profile)
        db.flush()
        db.refresh(profile)
        return _to_response(profile)


def list_profiles() -> list[BrandProfileResponse]:
    with db_session() as db:
        profiles = db.query(BrandProfile).order_by(BrandProfile.created_at.desc()).all()
        return [_to_response(p) for p in profiles]


def get_profile(profile_id: str) -> BrandProfileResponse | None:
    with db_session() as db:
        profile = db.query(BrandProfile).filter(BrandProfile.id == profile_id).first()
        if profile is None:
            return None
        return _to_response(profile)
