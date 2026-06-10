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
        extracted_text=asset.extracted_text,
        original_filename=asset.original_filename,
        file_path=asset.file_path,
        mime_type=asset.mime_type,
        file_size_bytes=asset.file_size_bytes,
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


def create_asset_from_file(
    title: str,
    asset_type: str,
    file_path: str,
    original_filename: str,
    mime_type: str,
    file_size_bytes: int,
    text_content: str | None = None,
    extracted_text: str | None = None,
    metadata: dict | None = None,
) -> CreativeAssetResponse:
    asset = CreativeAsset(
        asset_id=str(uuid4()),
        title=title,
        asset_type=asset_type,
        text_content=text_content,
        file_path=file_path,
        metadata=metadata or {},
        extracted_text=extracted_text,
        original_filename=original_filename,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
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


def get_asset_model(asset_id: str) -> CreativeAsset | None:
    return _store.get(asset_id)
