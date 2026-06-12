"""Tests for learning loop: save findings and manual notes."""

from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
from src.modules.knowledge_base.service import create_knowledge_item, get_knowledge_item


def test_manual_note_creation():
    item = create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Test Manual Note",
        content="This is a test note.",
        tags=["test", "manual"],
    ))
    assert item.source_type == "manual_note"
    assert item.title == "Test Manual Note"
    assert item.content == "This is a test note."
    assert "test" in item.tags


def test_manual_note_default_source_type():
    item = create_knowledge_item(CreateKnowledgeItemRequest(
        title="Default Type Note",
        content="This should get default source_type.",
    ))
    assert item.source_type == "other"


def test_save_findings_creates_items():
    from src.modules.knowledge_base.service import create_knowledge_item as create_ki
    from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest as CKIReq

    item = create_ki(CKIReq(
        source_type="report_finding",
        source_id="run-123",
        title="Finding: message_clarity (7.5/10)",
        content="The core message is reasonably clear.",
        tags=["message_clarity", "score_7", "auto_saved"],
    ))
    assert item is not None
    assert item.source_type == "report_finding"
    assert item.source_id == "run-123"
    assert "auto_saved" in item.tags


def test_save_findings_violations():
    from src.modules.knowledge_base.service import create_knowledge_item as create_ki
    from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest as CKIReq

    item = create_ki(CKIReq(
        source_type="report_finding",
        source_id="test-run-id",
        title="Compliance: forbidden_claim_miracle",
        content="Contains forbidden claim: 'miracle'",
        tags=["compliance", "high", "auto_saved"],
    ))
    assert item is not None
    assert item.source_type == "report_finding"
    assert "compliance" in item.tags
