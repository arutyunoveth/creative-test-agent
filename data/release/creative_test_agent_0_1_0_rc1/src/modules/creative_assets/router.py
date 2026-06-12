import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.modules.audit_log.service import write_audit_event
from src.modules.creative_assets.schemas import (
    CreateCreativeAssetRequest,
    CreateVersionRequest,
    CreativeAssetResponse,
    VersionChainResponse,
)
from src.modules.creative_assets.service import (
    create_asset,
    create_asset_from_file,
    create_version,
    get_asset,
    get_version_chain,
    get_versions,
    list_assets,
)
from src.modules.creative_assets.upload import process_upload
from src.shared.config.settings import get_settings
from src.shared.db.repository import json_dumps, json_loads
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


@router.post("/{asset_id}/create-version", response_model=CreativeAssetResponse, status_code=201)
def post_create_version(asset_id: str, body: CreateVersionRequest):
    existing = get_asset(asset_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    version = create_version(asset_id, body)
    if version is None:
        raise HTTPException(status_code=404, detail="Parent asset not found")
    write_audit_event("creative_version_created", "creative_asset", version.id, {
        "parent_asset_id": asset_id,
        "version_number": version.version_number,
        "version_label": version.version_label,
        "revision_source": version.revision_source,
    })
    return version


@router.get("/{asset_id}/versions", response_model=list[CreativeAssetResponse])
def get_asset_versions(asset_id: str):
    existing = get_asset(asset_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return get_versions(asset_id)


@router.get("/{asset_id}/version-chain", response_model=VersionChainResponse)
def get_asset_version_chain(asset_id: str):
    existing = get_asset(asset_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return get_version_chain(asset_id)


@router.post("/compare-versions", response_model=dict)
def compare_asset_versions(body: dict):
    from src.modules.report_generator.comparison import compare_test_runs
    from src.modules.report_generator.service import generate_report
    from src.modules.test_runs.service import get_test_run_by_asset

    asset_ids = body.get("asset_ids", [])
    if not asset_ids or len(asset_ids) < 2:
        raise HTTPException(status_code=400, detail="At least two asset IDs are required")

    assets = []
    for aid in asset_ids:
        a = get_asset(aid)
        if a is None:
            raise HTTPException(status_code=404, detail=f"Asset not found: {aid}")
        assets.append(a)

    version_data = []
    for a in assets:
        run = get_test_run_by_asset(a.id)
        comparison = None
        if run and run.status == "completed":
            report = generate_report(run.id, "internal", "json")
            if report:
                comparison = {
                    "overall_score": report.scorecard[0].get("score") if report.scorecard else None,
                    "scorecard": report.scorecard,
                    "risks": report.risks,
                    "recommendations": report.recommendations,
                    "final_recommendation": report.final_recommendation,
                }
        version_data.append({
            "asset_id": a.id,
            "title": a.title,
            "version_number": a.version_number,
            "version_label": a.version_label,
            "revision_summary": a.revision_summary,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "comparison": comparison,
            "has_report": comparison is not None,
        })

    return {"assets": version_data}


@router.get("/{asset_id}/image")
def get_asset_image(asset_id: str):
    asset = get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.asset_type not in ("image",):
        raise HTTPException(status_code=400, detail="Asset is not an image")
    if not asset.file_path:
        raise HTTPException(status_code=404, detail="Image file path missing")
    resolved = os.path.abspath(asset.file_path)
    storage_root = os.path.abspath(get_settings().storage_root)
    if os.path.commonpath([resolved, storage_root]) != storage_root:
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(resolved, media_type=asset.mime_type or "image/png")


@router.post("/{asset_id}/analyze-visual", response_model=CreativeAssetResponse)
def analyze_visual(asset_id: str):
    write_audit_event("visual_analysis_requested", "creative_asset", asset_id, {})
    asset = get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Only works for image assets
    if asset.asset_type not in ("image",):
        write_audit_event("visual_analysis_failed", "creative_asset", asset_id,
                          {"error": "not_an_image_asset", "asset_type": asset.asset_type})
        raise HTTPException(status_code=400, detail=f"Visual analysis requires an image asset, got '{asset.asset_type}'.")

    file_path = asset.file_path
    if not file_path:
        write_audit_event("visual_analysis_failed", "creative_asset", asset_id,
                          {"error": "no_file_path"})
        raise HTTPException(status_code=400, detail="Asset has no file path.")

    from src.shared.vision.factory import get_vision_analyzer
    from src.modules.creative_assets.service import _update_asset_metadata

    try:
        analyzer = get_vision_analyzer()
        result = analyzer.analyze_image(file_path)
        result_dict = result.model_dump()

        # Update asset metadata with visual analysis
        meta = json_loads(asset.metadata) if asset.metadata else {}
        meta["visual_analysis"] = result_dict
        _update_asset_metadata(asset_id, json_dumps(meta))

        # Update extracted_text if OCR detected text
        if result_dict.get("detected_text"):
            from src.modules.creative_assets.service import _update_asset_extracted_text
            _update_asset_extracted_text(asset_id, result_dict["detected_text"])

        write_audit_event("visual_analysis_completed", "creative_asset", asset_id, {
            "provider": result_dict.get("provider", ""),
            "warnings": result_dict.get("warnings", []),
        })
    except Exception as exc:
        write_audit_event("visual_analysis_failed", "creative_asset", asset_id,
                          {"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"Visual analysis failed: {exc}")

    return get_asset(asset_id)
