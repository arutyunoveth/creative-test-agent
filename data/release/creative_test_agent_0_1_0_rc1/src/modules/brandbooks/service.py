import os

from src.shared.db.repository import db_session, json_dumps, json_loads

from .models import BrandbookDocument
from .schemas import BrandbookContextResult, BrandbookDocumentResponse


def create_brandbook_from_text(title: str, document_type: str, text_content: str,
                                client_id: str | None = None,
                                project_id: str | None = None,
                                brand_profile_id: str | None = None,
                                metadata: dict | None = None) -> BrandbookDocumentResponse:
    with db_session() as db:
        doc = BrandbookDocument(
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
            title=title,
            document_type=document_type,
            text_content=text_content,
            extracted_text=text_content,
            metadata_json=json_dumps(metadata),
        )
        db.add(doc)
        db.flush()
        db.refresh(doc)
        return _to_response(doc)


def create_brandbook_from_file(title: str, document_type: str, file_path: str,
                                extracted_text: str,
                                client_id: str | None = None,
                                project_id: str | None = None,
                                brand_profile_id: str | None = None,
                                metadata: dict | None = None) -> BrandbookDocumentResponse:
    with db_session() as db:
        doc = BrandbookDocument(
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
            title=title,
            document_type=document_type,
            file_path=file_path,
            text_content=None,
            extracted_text=extracted_text,
            metadata_json=json_dumps(metadata),
        )
        db.add(doc)
        db.flush()
        db.refresh(doc)
        return _to_response(doc)


def list_brandbooks(client_id: str | None = None, project_id: str | None = None) -> list[BrandbookDocumentResponse]:
    with db_session() as db:
        q = db.query(BrandbookDocument)
        if client_id:
            q = q.filter(BrandbookDocument.client_id == client_id)
        if project_id:
            q = q.filter(BrandbookDocument.project_id == project_id)
        docs = q.order_by(BrandbookDocument.created_at.desc()).all()
        return [_to_response(d) for d in docs]


def get_brandbook(doc_id: str) -> BrandbookDocumentResponse | None:
    with db_session() as db:
        doc = db.query(BrandbookDocument).filter(BrandbookDocument.id == doc_id).first()
        return _to_response(doc) if doc else None


def get_brandbook_context(project_id: str | None = None,
                           brand_profile_id: str | None = None) -> BrandbookContextResult:
    snippets: list[str] = []
    total_chars = 0
    with db_session() as db:
        q = db.query(BrandbookDocument)
        if project_id:
            q = q.filter(BrandbookDocument.project_id == project_id)
        if brand_profile_id:
            q = q.filter(BrandbookDocument.brand_profile_id == brand_profile_id)
        docs = q.all()
        for doc in docs:
            text = doc.extracted_text or doc.text_content or ""
            if text.strip():
                snippets.append(text.strip())
                total_chars += len(text.strip())
    return BrandbookContextResult(snippets=snippets, total_chars=total_chars)


def _to_response(doc: BrandbookDocument) -> BrandbookDocumentResponse:
    return BrandbookDocumentResponse(
        id=doc.id,
        client_id=doc.client_id,
        project_id=doc.project_id,
        brand_profile_id=doc.brand_profile_id,
        title=doc.title,
        document_type=doc.document_type,
        text_content=doc.text_content or doc.extracted_text,
        metadata=json_loads(doc.metadata_json),
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )
