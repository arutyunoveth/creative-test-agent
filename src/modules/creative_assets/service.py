from datetime import datetime
from uuid import uuid4

from src.modules.creative_assets.models import CreativeAsset
from src.modules.creative_assets.schemas import (
    CreateCreativeAssetRequest,
    CreativeAssetResponse,
)

_store: dict[str, CreativeAsset] = {}


def _to_response(asset: CreativeAsset) -> CreativeAssetResponse:
    return CreativeAssetResponse(
        id=asset.id,
        title=asset.title,
        asset_type=asset.asset_type,
        text_content=asset.text_content,
        file_path=asset.file_path,
        metadata=asset.metadata,
        created_at=asset.created_at,
    )


def create_asset(req: CreateCreativeAssetRequest) -> CreativeAssetResponse:
    asset = CreativeAsset(
        asset_id=str(uuid4()),
        title=req.title,
        asset_type=req.asset_type,
        text_content=req.text_content,
        file_path=req.file_path,
        metadata=req.metadata,
    )
    _store[asset.id] = asset
    return _to_response(asset)


def list_assets() -> list[CreativeAssetResponse]:
    return [_to_response(a) for a in _store.values()]


def get_asset(asset_id: str) -> CreativeAssetResponse | None:
    asset = _store.get(asset_id)
    if asset is None:
        return None
    return _to_response(asset)
