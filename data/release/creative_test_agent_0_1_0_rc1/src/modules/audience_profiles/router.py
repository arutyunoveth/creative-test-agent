from fastapi import APIRouter, HTTPException

from src.modules.audit_log.service import write_audit_event
from src.modules.audience_profiles.schemas import (
    AudienceProfileResponse,
    CreateAudienceProfileRequest,
)
from src.modules.audience_profiles.service import create_profile, get_profile, list_profiles

router = APIRouter(prefix="/audience-profiles", tags=["audience-profiles"])


@router.post("", response_model=AudienceProfileResponse, status_code=201)
def post_create_profile(body: CreateAudienceProfileRequest):
    profile = create_profile(body)
    write_audit_event("audience_profile_created", "audience_profile", profile.id, {"name": profile.name})
    return profile


@router.get("", response_model=list[AudienceProfileResponse])
def get_profiles():
    return list_profiles()


@router.get("/{profile_id}", response_model=AudienceProfileResponse)
def get_profile_by_id(profile_id: str):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Audience profile not found")
    return profile
