import os

from fastapi import APIRouter, HTTPException, Query, UploadFile

from src.modules.audit_log.service import write_audit_event
from src.shared.config.settings import get_settings

from .schemas import BrandbookDocumentResponse
from .service import (create_brandbook_from_file, create_brandbook_from_text,
                      get_brandbook, list_brandbooks)


def _auto_ingest_if_enabled(doc_id: str) -> None:
    settings = get_settings()
    if settings.enable_knowledge_auto_ingest:
        try:
            from src.modules.brandbooks.ingestion import ingest_brandbook
            ingest_brandbook(doc_id, auto=True)
        except Exception:
            pass

router = APIRouter(prefix="/brandbooks", tags=["brandbooks"])

ALLOWED_BRANDBOOK_TYPES = {"txt", "md", "pdf"}


@router.post("/upload", response_model=BrandbookDocumentResponse, status_code=201)
async def post_upload_brandbook(
    file: UploadFile,
    title: str | None = Query(None),
    document_type: str = Query("brandbook"),
    client_id: str | None = Query(None),
    project_id: str | None = Query(None),
    brand_profile_id: str | None = Query(None),
):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename")

    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_BRANDBOOK_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}")

    effective_title = title or file.filename

    if ext == "txt":
        raw = await file.read()
        text = raw.decode("utf-8", errors="replace")
        doc = create_brandbook_from_text(
            title=effective_title,
            document_type=document_type,
            text_content=text,
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
        )
    elif ext == "md":
        raw = await file.read()
        text = raw.decode("utf-8", errors="replace")
        doc = create_brandbook_from_text(
            title=effective_title,
            document_type=document_type,
            text_content=text,
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
        )
    elif ext == "pdf":
        from src.modules.creative_assets.parsers.pdf_parser import parse_pdf

        raw = await file.read()
        parsed = parse_pdf(raw)
        text = parsed.extracted_text or ""
        settings = get_settings()
        storage_path = os.path.join(settings.storage_root, "brandbooks")
        os.makedirs(storage_path, exist_ok=True)
        file_dst = os.path.join(storage_path, file.filename)
        with open(file_dst, "wb") as f:
            f.write(raw)
        doc = create_brandbook_from_file(
            title=effective_title,
            document_type=document_type,
            file_path=file_dst,
            extracted_text=text,
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    write_audit_event("brandbook_uploaded", "brandbook_document", doc.id, {"title": doc.title})
    _auto_ingest_if_enabled(doc.id)
    return doc


@router.post("/{brandbook_id}/ingest", status_code=200)
def post_ingest_brandbook(brandbook_id: str):
    from src.modules.brandbooks.ingestion import ingest_brandbook

    try:
        chunk_count = ingest_brandbook(brandbook_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    write_audit_event("brandbook_ingested", "brandbook_document", brandbook_id, {"chunks": chunk_count})
    return {"status": "ok", "chunks_created": chunk_count, "brandbook_id": brandbook_id}


@router.get("", response_model=list[BrandbookDocumentResponse])
def get_brandbooks(client_id: str | None = Query(None), project_id: str | None = Query(None)):
    return list_brandbooks(client_id=client_id, project_id=project_id)


@router.get("/{brandbook_id}", response_model=BrandbookDocumentResponse)
def get_brandbook_by_id(brandbook_id: str):
    doc = get_brandbook(brandbook_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Brandbook document not found")
    return doc
