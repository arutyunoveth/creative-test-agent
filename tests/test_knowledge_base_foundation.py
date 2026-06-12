"""Tests for knowledge base foundation module."""

from src.modules.knowledge_base.models import KnowledgeSourceType
from src.modules.knowledge_base.service import (
    create_knowledge_item,
    list_knowledge_items,
    get_knowledge_item,
)
from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest


def test_knowledge_source_type_enum():
    """KnowledgeSourceType enum has expected values."""
    assert KnowledgeSourceType.brandbook == "brandbook"
    assert KnowledgeSourceType.manual_note == "manual_note"
    assert KnowledgeSourceType.report_finding == "report_finding"
    assert KnowledgeSourceType.client_feedback == "client_feedback"
    assert KnowledgeSourceType.other == "other"


def test_create_knowledge_item():
    """Knowledge item can be created."""
    item = create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Test Note",
        content="This is a test knowledge item.",
        tags=["test", "knowledge"],
    ))
    assert item.title == "Test Note"
    assert item.content == "This is a test knowledge item."
    assert "test" in item.tags
    assert item.id is not None


def test_list_knowledge_items():
    """list_knowledge_items returns a list."""
    items = list_knowledge_items()
    assert isinstance(items, list)


def test_get_knowledge_item():
    """Created knowledge item can be retrieved by ID."""
    item = create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="client_feedback",
        title="Client Feedback",
        content="Client mentioned they liked the report format.",
    ))
    retrieved = get_knowledge_item(item.id)
    assert retrieved is not None
    assert retrieved.id == item.id
    assert retrieved.title == "Client Feedback"


def test_get_knowledge_item_not_found():
    """get_knowledge_item returns None for unknown ID."""
    result = get_knowledge_item("nonexistent_id")
    assert result is None


def test_knowledge_item_with_client_project():
    """Knowledge item can have client_id and project_id."""
    item = create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="brandbook",
        source_id="bb_001",
        client_id="client_001",
        project_id="project_001",
        title="Scoped Item",
        content="Scoped knowledge content.",
    ))
    assert item.client_id == "client_001"
    assert item.project_id == "project_001"
    assert item.source_id == "bb_001"


def test_list_knowledge_items_filtered():
    """list_knowledge_items supports filtering by source_type."""
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="report_finding",
        title="Finding 1",
        content="First finding.",
    ))
    findings = list_knowledge_items(source_type="report_finding")
    assert len(findings) >= 1
    for f in findings:
        assert f.source_type == "report_finding"
