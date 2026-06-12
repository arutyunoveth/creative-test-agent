from src.modules.audience_profiles.models import AudienceProfile
from src.modules.audience_profiles.schemas import (
    AudienceProfileResponse,
    CreateAudienceProfileRequest,
)
from src.shared.db.repository import db_session, json_dumps, json_loads


def _to_response(p: AudienceProfile) -> AudienceProfileResponse:
    return AudienceProfileResponse(
        id=p.id,
        name=p.name,
        segment_description=p.segment_description or "",
        pains=p.pains,
        motivations=p.motivations,
        objections=p.objections,
        metadata=json_loads(p.metadata_json) or {},
        created_at=p.created_at,
    )


def create_profile(req: CreateAudienceProfileRequest) -> AudienceProfileResponse:
    with db_session() as db:
        profile = AudienceProfile(
            name=req.name,
            segment_description=req.segment_description,
            pains=req.pains,
            motivations=req.motivations,
            objections=req.objections,
            metadata_json=json_dumps(req.metadata),
        )
        db.add(profile)
        db.flush()
        db.refresh(profile)
        return _to_response(profile)


def list_profiles() -> list[AudienceProfileResponse]:
    with db_session() as db:
        profiles = db.query(AudienceProfile).order_by(AudienceProfile.created_at.desc()).all()
        return [_to_response(p) for p in profiles]


def get_profile(profile_id: str) -> AudienceProfileResponse | None:
    with db_session() as db:
        profile = db.query(AudienceProfile).filter(AudienceProfile.id == profile_id).first()
        if profile is None:
            return None
        return _to_response(profile)
