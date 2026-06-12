from src.modules.creative_assets.models import CreativeAsset
from src.modules.creative_assets.schemas import (
    CreateCreativeAssetRequest,
    CreateVersionRequest,
    CreativeAssetResponse,
    VersionChainResponse,
)
from src.shared.db.repository import db_session, json_dumps, json_loads


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
        project_id=asset.project_id,
        metadata=json_loads(asset.metadata_json),
        created_at=asset.created_at,
        parent_asset_id=asset.parent_asset_id,
        version_label=asset.version_label,
        version_number=asset.version_number,
        revision_summary=asset.revision_summary,
        revision_source=asset.revision_source,
    )


def create_asset(req: CreateCreativeAssetRequest) -> CreativeAssetResponse:
    with db_session() as db:
        asset = CreativeAsset(
            title=req.title,
            asset_type=req.asset_type,
            text_content=req.text_content,
            file_path=req.file_path,
            project_id=req.project_id,
            metadata_json=json_dumps(req.metadata),
        )
        db.add(asset)
        db.flush()
        db.refresh(asset)
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
    project_id: str | None = None,
) -> CreativeAssetResponse:
    with db_session() as db:
        asset = CreativeAsset(
            title=title,
            asset_type=asset_type,
            text_content=text_content,
            extracted_text=extracted_text,
            original_filename=original_filename,
            file_path=file_path,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            project_id=project_id,
            metadata_json=json_dumps(metadata or {}),
        )
        db.add(asset)
        db.flush()
        db.refresh(asset)
        return _to_response(asset)


def list_assets() -> list[CreativeAssetResponse]:
    with db_session() as db:
        assets = db.query(CreativeAsset).order_by(CreativeAsset.created_at.desc()).all()
        return [_to_response(a) for a in assets]


def get_asset(asset_id: str) -> CreativeAssetResponse | None:
    with db_session() as db:
        asset = db.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
        if asset is None:
            return None
        return _to_response(asset)


def _update_asset_metadata(asset_id: str, metadata_json: str) -> None:
    with db_session() as db:
        asset = db.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
        if asset:
            asset.metadata_json = metadata_json
            db.flush()


def _update_asset_extracted_text(asset_id: str, text: str) -> None:
    with db_session() as db:
        asset = db.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
        if asset:
            asset.extracted_text = text
            db.flush()


def get_asset_model(asset_id: str) -> CreativeAsset | None:
    with db_session() as db:
        asset = db.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
        if asset is None:
            return None
        db.expunge(asset)
        return asset


def create_version(asset_id: str, req: CreateVersionRequest) -> CreativeAssetResponse | None:
    with db_session() as db:
        parent = db.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
        if parent is None:
            return None

        max_version = (
            db.query(CreativeAsset.version_number)
            .filter(
                (CreativeAsset.id == asset_id)
                | (CreativeAsset.parent_asset_id == asset_id)
            )
            .order_by(CreativeAsset.version_number.desc().nullslast())
            .first()
        )
        next_version = (max_version[0] or 0) + 1 if max_version else 1

        version = CreativeAsset(
            title=req.title or parent.title,
            asset_type=parent.asset_type,
            text_content=req.text_content or parent.text_content,
            extracted_text=parent.extracted_text,
            original_filename=parent.original_filename,
            file_path=parent.file_path,
            mime_type=parent.mime_type,
            file_size_bytes=parent.file_size_bytes,
            project_id=parent.project_id,
            parent_asset_id=asset_id,
            version_label=req.version_label,
            version_number=next_version,
            revision_summary=req.revision_summary,
            revision_source=req.revision_source,
            metadata_json=json_dumps(req.metadata or json_loads(parent.metadata_json) or {}),
        )
        db.add(version)
        db.flush()
        db.refresh(version)
        return _to_response(version)


def get_versions(asset_id: str) -> list[CreativeAssetResponse]:
    with db_session() as db:
        versions = (
            db.query(CreativeAsset)
            .filter(
                (CreativeAsset.id == asset_id)
                | (CreativeAsset.parent_asset_id == asset_id)
            )
            .order_by(CreativeAsset.version_number.asc().nullsfirst())
            .all()
        )
        return [_to_response(v) for v in versions]


def get_version_chain(asset_id: str) -> VersionChainResponse:
    with db_session() as db:
        target = db.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
        if target is None:
            return VersionChainResponse(versions=[])

        root_id = asset_id
        current = target
        while current.parent_asset_id:
            root_id = current.parent_asset_id
            current = db.query(CreativeAsset).filter(CreativeAsset.id == root_id).first()
            if current is None:
                break

        root = db.query(CreativeAsset).filter(CreativeAsset.id == root_id).first()
        all_in_chain = (
            db.query(CreativeAsset)
            .filter(
                (CreativeAsset.id == root_id)
                | (CreativeAsset.parent_asset_id == root_id)
            )
            .order_by(CreativeAsset.version_number.asc().nullsfirst())
            .all()
        )
        return VersionChainResponse(
            root=_to_response(root) if root else None,
            versions=[_to_response(v) for v in all_in_chain],
        )
