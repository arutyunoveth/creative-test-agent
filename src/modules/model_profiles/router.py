from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.modules.model_profiles.schemas import (
    CreateModelProfileRequest,
    ModelProfileResponse,
)
from src.modules.model_profiles.service import (
    check_profile_health,
    create_profile,
    get_profile,
    list_profiles,
    load_profile_from_config,
)

router = APIRouter(prefix="/model-profiles", tags=["model_profiles"])

CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config" / "model_profiles"


@router.get("", response_model=list[ModelProfileResponse])
def get_model_profiles():
    return list_profiles()


@router.post("", response_model=ModelProfileResponse, status_code=201)
def post_model_profile(body: CreateModelProfileRequest):
    try:
        return create_profile(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{profile_id}", response_model=ModelProfileResponse)
def get_model_profile(profile_id: str):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Model profile not found")
    return profile


@router.post("/{profile_id}/health")
def post_model_profile_health(profile_id: str):
    from src.modules.model_profiles.service import check_profile_health
    try:
        return check_profile_health(profile_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/load-from-config")
def post_load_from_config():
    loaded = []
    for fpath in sorted(CONFIG_DIR.glob("*.json")):
        if fpath.name.endswith(".example.json"):
            continue
        try:
            profile = load_profile_from_config(str(fpath))
            loaded.append(profile.profile_name)
        except Exception:
            pass
    return {"loaded": loaded}
