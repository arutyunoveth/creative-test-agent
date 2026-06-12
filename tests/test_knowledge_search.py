"""Tests for knowledge base keyword search."""

from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
from src.modules.knowledge_base.search import SearchResult, keyword_search
from src.modules.knowledge_base.service import create_knowledge_item, list_knowledge_items


def setup_search_data():
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Brand Tone Guidelines",
        content="Our brand tone is friendly and approachable. We avoid aggressive language.",
        tags=["tone", "brand", "guidelines"],
    ))
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Claims Policy",
        content="Never make guaranteed income claims. Avoid absolute statements.",
        tags=["claims", "policy", "compliance"],
    ))
    create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="manual_note",
        title="Visual Style Guide",
        content="Use brand colors: blue and white. Logo must be placed top-left.",
        tags=["visual", "brand", "style"],
    ))


def test_search_empty_query():
    results = keyword_search("")
    assert results == []


def test_search_no_match():
    results = keyword_search("xyznonexistent123")
    assert results == []


def test_search_basic():
    setup_search_data()
    results = keyword_search("brand")
    assert len(results) >= 1
    for r in results:
        assert isinstance(r, SearchResult)
        assert r.score > 0


def test_search_with_query_match():
    setup_search_data()
    results = keyword_search("tone")
    assert len(results) >= 1
    match = results[0]
    assert "tone" in match.item.title.lower() or "tone" in (match.item.content or "").lower()


def test_search_returns_scored():
    setup_search_data()
    results = keyword_search("brand tone")
    assert len(results) >= 1
    for i in range(len(results) - 1):
        assert results[i].score >= results[i + 1].score


def test_search_matched_terms():
    setup_search_data()
    results = keyword_search("brand guidelines")
    assert len(results) >= 1
    assert len(results[0].matched_terms) >= 1


def test_search_max_results():
    for i in range(5):
        create_knowledge_item(CreateKnowledgeItemRequest(
            source_type="manual_note",
            title=f"Search Item {i}",
            content=f"Searchable content item number {i}.",
        ))
    results = keyword_search("searchable", max_results=3)
    assert len(results) <= 3


def test_search_with_filters():
    setup_search_data()
    results = keyword_search("brand", source_type="manual_note")
    assert len(results) >= 1
    for r in results:
        assert r.item.source_type == "manual_note"
