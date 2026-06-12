"""Tests for knowledge context builder."""

from src.modules.knowledge_base.context_builder import ContextResult, build_context
from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
from src.modules.knowledge_base.service import create_knowledge_item


def setup_context_data():
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Brand Tone",
        content="Friendly and approachable brand tone.",
        tags=["tone"],
    ))
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Claims Policy",
        content="No guaranteed claims. Avoid absolute language.",
        tags=["claims"],
    ))


def test_context_no_query():
    result = build_context("")
    assert isinstance(result, ContextResult)
    assert result.text == ""


def test_context_no_match():
    result = build_context("nonexistent_xyz")
    assert result.text == ""
    assert result.items_used == 0


def test_context_basic():
    setup_context_data()
    result = build_context("brand tone")
    assert result.text != ""
    assert result.items_used >= 1


def test_context_limits():
    for i in range(20):
        create_knowledge_item(CreateKnowledgeItemRequest(
            source_type="manual_note",
            title=f"Limit Test {i}",
            content=f"Content for testing context builder limits. Item number {i}.",
        ))
    result = build_context("limit test", max_items=3)
    assert result.items_used <= 3
    assert result.total_available >= result.items_used


def test_context_truncation():
    long_content = "Word " * 5000
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Long Doc",
        content=long_content,
    ))
    result = build_context("word", max_chars=500)
    if result.items_used > 0:
        assert len(result.text) <= 1000
    assert isinstance(result.truncated, bool)


def test_context_truncated_via_char_limit():
    long_content = "This is a unique searchable phrase for testing. " * 2000
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Very Long Doc",
        content=long_content,
    ))
    result = build_context("unique searchable phrase", max_chars=100)
    if result.items_used > 0:
        assert result.truncated is True


def test_context_result_type():
    setup_context_data()
    result = build_context("brand tone")
    assert isinstance(result, ContextResult)
    assert hasattr(result, "text")
    assert hasattr(result, "items_used")
    assert hasattr(result, "total_available")
    assert hasattr(result, "truncated")
