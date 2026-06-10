from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.modules.audit_log.service import write_audit_event
from src.modules.creative_assets.schemas import (
    CreateCreativeAssetRequest,
    CreativeAssetResponse,
)
from src.modules.creative_assets.service import create_asset, create_asset_from_file, get_asset, list_assets
from src.modules.creative_assets.upload import process_upload
from src.shared.errors import AppError

router = APIRouter(prefix="/creative-assets", tags=["creative-assets"])


@router.post("", response_model=CreativeAssetResponse, status_code=201)
def post_create_asset(body: CreateCreativeAssetRequest):
    asset = create_asset(body)
    write_audit_event("creative_asset_created", "creative_asset", asset.id, {"title": asset.title})
    return asset


@router.post("/upload", response_model=CreativeAssetResponse, status_code=201)
async def post_upload_asset(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    metadata: str | None = Form(None),
):
    content = await file.read()
    import json
    meta = json.loads(metadata) if metadata else {}

    try:
        result = process_upload(
            filename=file.filename or "unnamed",
            content=content,
            content_type=file.content_type,
        )
    except AppError:
        write_audit_event("creative_file_rejected", "creative_asset", file.filename or "unknown", {"error": "validation failed"})
        raise

    display_title = title or result["original_filename"]
    asset = create_asset_from_file(
        title=display_title,
        asset_type=result["asset_type"],
        file_path=result["file_path"],
        original_filename=result["original_filename"],
        mime_type=result["mime_type"],
        file_size_bytes=result["file_size_bytes"],
        extracted_text=result["extracted_text"],
        metadata={**meta, **result.get("parser_metadata", {}), "warnings": result.get("warnings", [])},
    )

    write_audit_event("creative_file_uploaded", "creative_asset", asset.id, {
        "title": asset.title,
        "original_filename": result["original_filename"],
        "mime_type": result["mime_type"],
        "file_size_bytes": result["file_size_bytes"],
        "parser": result.get("parser_name", ""),
        "warnings": result.get("warnings", []),
    })

    if result.get("warnings"):
        write_audit_event("creative_file_parsed", "creative_asset", asset.id, {
            "warnings": result["warnings"],
        })

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
