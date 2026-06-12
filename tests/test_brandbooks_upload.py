"""Tests for brandbook upload and context hook."""

from src.modules.brandbooks.service import (
    create_brandbook_from_text,
    get_brandbook_context,
    list_brandbooks,
)
from src.modules.brandbooks.schemas import BrandbookContextResult


def test_create_brandbook_from_text():
    """Brandbook can be created from text."""
    doc = create_brandbook_from_text(
        title="Test Brandbook",
        document_type="brandbook",
        text_content="This is a test brandbook document.",
    )
    assert doc.title == "Test Brandbook"
    assert doc.document_type == "brandbook"
    assert doc.id is not None


def test_list_brandbooks():
    """list_brandbooks returns a list."""
    docs = list_brandbooks()
    assert isinstance(docs, list)


def test_brandbook_context_returns_result():
    """get_brandbook_context returns BrandbookContextResult."""
    result = get_brandbook_context()
    assert isinstance(result, BrandbookContextResult)
    assert hasattr(result, "snippets")
    assert hasattr(result, "total_chars")


def test_brandbook_context_with_created_doc():
    """Created brandbook content is included in context."""
    create_brandbook_from_text(
        title="Context Test Doc",
        document_type="claims_policy",
        text_content="We do not make guarantees about financial outcomes.",
    )
    result = get_brandbook_context()
    assert len(result.snippets) >= 1
    assert result.total_chars > 0


def test_brandbook_create_with_project():
    """Brandbook can be created with project_id and client_id."""
    doc = create_brandbook_from_text(
        title="Project Brandbook",
        document_type="tone_of_voice",
        text_content="Brand tone is friendly and professional.",
        client_id="client_123",
        project_id="project_456",
        brand_profile_id="bp_789",
    )
    assert doc.client_id == "client_123"
    assert doc.project_id == "project_456"
    assert doc.brand_profile_id == "bp_789"


def test_brandbook_all_fields_in_response():
    """BrandbookDocumentResponse includes all expected fields."""
    doc = create_brandbook_from_text(
        title="Full Fields Doc",
        document_type="legal_guidelines",
        text_content="Legal content here.",
    )
    assert doc.title == "Full Fields Doc"
    assert doc.document_type == "legal_guidelines"
    assert doc.text_content == "Legal content here."
    assert doc.created_at is not None
