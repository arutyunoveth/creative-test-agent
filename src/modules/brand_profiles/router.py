from fastapi import APIRouter, HTTPException

from src.modules.audit_log.service import write_audit_event
from src.modules.brand_profiles.schemas import (
    BrandProfileResponse,
    CreateBrandProfileRequest,
)
from src.modules.brand_profiles.service import create_profile, get_profile, list_profiles

router = APIRouter(prefix="/brand-profiles", tags=["brand-profiles"])


@router.post("", response_model=BrandProfileResponse, status_code=201)
def post_create_profile(body: CreateBrandProfileRequest):
    profile = create_profile(body)
    write_audit_event("brand_profile_created", "brand_profile", profile.id, {"name": profile.name})
    return profile


@router.get("", response_model=list[BrandProfileResponse])
def get_profiles():
    return list_profiles()


@router.get("/{profile_id}", response_model=BrandProfileResponse)
def get_profile_by_id(profile_id: str):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return profile
