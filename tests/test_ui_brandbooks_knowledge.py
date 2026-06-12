"""Tests for UI pages: brandbooks list/detail, knowledge base."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_ui_brandbooks_list():
    resp = client.get("/ui/brandbooks")
    assert resp.status_code in (200, 303)


def test_ui_brandbooks_new():
    resp = client.get("/ui/brandbooks/new")
    assert resp.status_code in (200, 303)


def test_ui_knowledge_base():
    resp = client.get("/ui/knowledge-base")
    assert resp.status_code in (200, 303)


def test_ui_knowledge_base_search():
    resp = client.get("/ui/knowledge-base?q=test")
    assert resp.status_code in (200, 303)


def test_ui_brandbooks_ingest_endpoint():
    from src.modules.brandbooks.service import create_brandbook_from_text

    doc = create_brandbook_from_text(
        title="UI Ingest Test",
        document_type="brandbook",
        text_content="UI test content for brandbook ingestion. " * 30,
    )
    resp = client.post(f"/ui/brandbooks/{doc.id}/ingest")
    assert resp.status_code in (200, 303, 302)


def test_ui_knowledge_base_post_note():
    resp = client.post("/ui/knowledge-base", data={
        "title": "UI Test Note",
        "content": "Created via UI test.",
        "tags": "test, ui",
    })
    assert resp.status_code in (200, 303, 302)


def test_brandbook_dashboard_count():
    resp = client.get("/ui")
    assert resp.status_code in (200, 303)
    assert resp.status_code != 500


def test_knowledge_base_search_api():
    from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
    from src.modules.knowledge_base.service import create_knowledge_item

    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="API Search Test",
        content="This is a searchable test item.",
        tags=["api-test"],
    ))
    resp = client.get("/knowledge-base/search?q=searchable")
    assert resp.status_code in (200, 422)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)
