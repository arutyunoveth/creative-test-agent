from fastapi import APIRouter, HTTPException

from src.modules.audit_log.service import write_audit_event
from src.modules.creative_assets.schemas import (
    CreateCreativeAssetRequest,
    CreativeAssetResponse,
)
from src.modules.creative_assets.service import create_asset, get_asset, list_assets

router = APIRouter(prefix="/creative-assets", tags=["creative-assets"])


@router.post("", response_model=CreativeAssetResponse, status_code=201)
def post_create_asset(body: CreateCreativeAssetRequest):
    asset = create_asset(body)
    write_audit_event("creative_asset_created", "creative_asset", asset.id, {"title": asset.title})
    return asset


@router.get("", response_model=list[CreativeAssetResponse])
def get_assets():
    return list_assets()


@router.get("/{asset_id}", response_model=CreativeAssetResponse)
def get_asset_by_id(asset_id: str):
    asset = get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
