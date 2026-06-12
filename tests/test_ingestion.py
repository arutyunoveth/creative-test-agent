"""Tests for brandbook ingestion into knowledge base."""

import pytest

from src.modules.brandbooks.ingestion import ingest_brandbook
from src.modules.brandbooks.service import create_brandbook_from_text
from src.modules.knowledge_base.service import list_knowledge_items


def test_ingest_brandbook_creates_knowledge_items():
    doc = create_brandbook_from_text(
        title="Ingest Test",
        document_type="brandbook",
        text_content="This is a test brandbook document with enough content to create multiple chunks for testing purposes. " * 30,
    )
    count = ingest_brandbook(doc.id)
    assert count >= 1
    items = list_knowledge_items(source_type="brandbook")
    ingested = [i for i in items if i.source_id == doc.id]
    assert len(ingested) == count


def test_ingest_empty_brandbook_raises():
    doc = create_brandbook_from_text(
        title="Empty Doc",
        document_type="other",
        text_content="",
    )
    with pytest.raises(ValueError, match="brandbook_empty"):
        ingest_brandbook(doc.id)


def test_ingest_nonexistent_brandbook_raises():
    with pytest.raises(ValueError, match="brandbook_not_found"):
        ingest_brandbook("nonexistent-id")


def test_ingest_is_idempotent():
    doc = create_brandbook_from_text(
        title="Idempotent Test",
        document_type="brandbook",
        text_content="Idempotent test content for brandbook ingestion. " * 20,
    )
    count1 = ingest_brandbook(doc.id)
    count2 = ingest_brandbook(doc.id)
    assert count1 == count2
    items = list_knowledge_items(source_type="brandbook")
    ingested = [i for i in items if i.source_id == doc.id]
    assert len(ingested) == count1


def test_ingest_sets_correct_source_type():
    doc = create_brandbook_from_text(
        title="Source Type Test",
        document_type="claims_policy",
        text_content="Claims policy content. " * 50,
    )
    ingest_brandbook(doc.id)
    items = list_knowledge_items(source_type="brandbook")
    ingested = [i for i in items if i.source_id == doc.id]
    assert len(ingested) >= 1
    for item in ingested:
        assert item.source_type == "brandbook"
        assert item.source_id == doc.id


def test_ingest_sets_tags():
    doc = create_brandbook_from_text(
        title="Tag Test",
        document_type="tone_of_voice",
        text_content="Tone of voice guidelines. " * 40,
    )
    ingest_brandbook(doc.id)
    items = list_knowledge_items(source_type="brandbook")
    ingested = [i for i in items if i.source_id == doc.id]
    assert len(ingested) >= 1
    all_tags = set()
    for item in ingested:
        all_tags.update(item.tags)
    assert "tone_of_voice" in all_tags
    assert "brandbook" in all_tags
