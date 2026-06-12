from src.shared.db.repository import db_session, json_dumps, json_loads

from .models import KnowledgeItem
from .schemas import CreateKnowledgeItemRequest, KnowledgeItemResponse


def create_knowledge_item(req: CreateKnowledgeItemRequest) -> KnowledgeItemResponse:
    with db_session() as db:
        item = KnowledgeItem(
            source_type=req.source_type,
            source_id=req.source_id,
            client_id=req.client_id,
            project_id=req.project_id,
            title=req.title,
            content=req.content,
            tags_json=json_dumps(req.tags),
        )
        db.add(item)
        db.flush()
        db.refresh(item)
        return _to_response(item)


def list_knowledge_items(client_id: str | None = None,
                          project_id: str | None = None,
                          source_type: str | None = None) -> list[KnowledgeItemResponse]:
    with db_session() as db:
        q = db.query(KnowledgeItem)
        if client_id:
            q = q.filter(KnowledgeItem.client_id == client_id)
        if project_id:
            q = q.filter(KnowledgeItem.project_id == project_id)
        if source_type:
            q = q.filter(KnowledgeItem.source_type == source_type)
        items = q.order_by(KnowledgeItem.created_at.desc()).all()
        return [_to_response(i) for i in items]


def get_knowledge_item(item_id: str) -> KnowledgeItemResponse | None:
    with db_session() as db:
        item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        return _to_response(item) if item else None


def _to_response(item: KnowledgeItem) -> KnowledgeItemResponse:
    return KnowledgeItemResponse(
        id=item.id,
        source_type=item.source_type,
        source_id=item.source_id,
        client_id=item.client_id,
        project_id=item.project_id,
        title=item.title,
        content=item.content,
        tags=json_loads(item.tags_json) if isinstance(json_loads(item.tags_json), list) else [],
        metadata=json_loads(item.metadata_json),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
