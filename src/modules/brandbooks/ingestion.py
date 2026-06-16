from src.modules.brandbooks.chunking import TextChunk, chunk_text
from src.modules.brandbooks.service import get_brandbook
from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
from src.modules.knowledge_base.service import create_knowledge_item, list_knowledge_items
from src.shared.config.settings import get_settings


def ingest_brandbook(doc_id: str, auto: bool = False) -> int:
    doc = get_brandbook(doc_id)
    if doc is None:
        raise ValueError(f"brandbook_not_found: {doc_id}")

    text = doc.extracted_text or doc.text_content or ""
    if not text.strip():
        raise ValueError(f"brandbook_empty: {doc_id}")

    settings = get_settings()
    chunks = chunk_text(
        text,
        chunk_size=settings.kb_chunk_size_chars,
        overlap=settings.kb_chunk_overlap_chars,
    )

    existing = list_knowledge_items(
        client_id=doc.client_id,
        project_id=doc.project_id,
        source_type="brandbook",
    )
    stale_ids = [
        item.id
        for item in existing
        if item.source_id == doc_id
    ]
    for sid in stale_ids:
        from src.shared.db.repository import db_session
        from src.modules.knowledge_base.models import KnowledgeItem

        with db_session() as db:
            db.query(KnowledgeItem).filter(KnowledgeItem.id == sid).delete()
            db.flush()

    tags = [doc.document_type, "brandbook"]
    if auto:
        tags.append("auto_ingested")

    for chunk in chunks:
        title = f"{doc.title} — Chunk {chunk.index + 1}"
        create_knowledge_item(
            CreateKnowledgeItemRequest(
                source_type="brandbook",
                source_id=doc_id,
                client_id=doc.client_id,
                project_id=doc.project_id,
                title=title,
                content=chunk.text,
                tags=tags + [f"chunk_{chunk.index}"],
            )
        )

    return len(chunks)
