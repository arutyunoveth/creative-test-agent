from fastapi import APIRouter, HTTPException, Query

from src.modules.audit_log.service import write_audit_event

from .schemas import (CreateKnowledgeItemRequest, KnowledgeItemResponse,
                      KnowledgeSearchResult)
from .service import (create_knowledge_item, get_knowledge_item,
                      list_knowledge_items)

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.post("", response_model=KnowledgeItemResponse, status_code=201)
def post_create_knowledge_item(body: CreateKnowledgeItemRequest):
    item = create_knowledge_item(body)
    write_audit_event("knowledge_item_created", "knowledge_item", item.id, {"title": item.title})
    return item


@router.get("", response_model=list[KnowledgeItemResponse])
def get_knowledge_items(client_id: str | None = Query(None),
                         project_id: str | None = Query(None),
                         source_type: str | None = Query(None)):
    return list_knowledge_items(client_id=client_id, project_id=project_id, source_type=source_type)


@router.post("/manual-note", response_model=KnowledgeItemResponse, status_code=201)
def post_manual_note(body: CreateKnowledgeItemRequest):
    body.source_type = "manual_note"
    item = create_knowledge_item(body)
    write_audit_event("knowledge_manual_note", "knowledge_item", item.id, {"title": item.title})
    return item


@router.get("/search", response_model=list[KnowledgeSearchResult])
def search_knowledge(
    q: str = Query(..., min_length=1),
    client_id: str | None = Query(None),
    project_id: str | None = Query(None),
    source_type: str | None = Query(None),
    max_results: int = Query(20, le=50),
):
    from src.modules.knowledge_base.search import keyword_search

    results = keyword_search(
        query=q,
        client_id=client_id,
        project_id=project_id,
        source_type=source_type,
        max_results=max_results,
    )
    return [
        KnowledgeSearchResult(
            item=r.item,
            score=round(r.score, 2),
            matched_terms=r.matched_terms,
        )
        for r in results
    ]


@router.get("/{item_id}", response_model=KnowledgeItemResponse)
def get_knowledge_item_by_id(item_id: str):
    item = get_knowledge_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return item
