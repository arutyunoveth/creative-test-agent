"""Tests for brandbook text chunking."""

from src.modules.brandbooks.chunking import TextChunk, chunk_text


def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_short():
    chunks = chunk_text("Short text.", chunk_size=1200, overlap=150)
    assert len(chunks) == 1
    assert chunks[0].text == "Short text."
    assert chunks[0].index == 0


def test_chunk_text_multiple():
    text = "Word. " * 500
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c.text) <= 200
    assert chunks[0].index == 0
    assert chunks[1].index == 1


def test_chunk_metadata():
    text = "Hello world. " * 100
    chunks = chunk_text(text, chunk_size=300, overlap=30)
    c = chunks[0]
    assert isinstance(c, TextChunk)
    assert c.char_start >= 0
    assert c.char_end > c.char_start
    assert c.word_count > 0


def test_chunk_overlap_contains_shared_text():
    text = "This is a test sentence. " * 200
    chunks = chunk_text(text, chunk_size=400, overlap=50)
    if len(chunks) >= 2:
        end_of_first = chunks[0].text[-30:]
        start_of_second = chunks[1].text[:30]
        overlap = set(end_of_first.split()) & set(start_of_second.split())
        assert len(overlap) > 0


def test_chunk_sentence_aware():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert any("First paragraph" in c.text for c in chunks)
    assert any("Second paragraph" in c.text for c in chunks)
    assert any("Third paragraph" in c.text for c in chunks)


def test_chunk_at_1000_limit():
    text = "word " * 2000
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) <= 1000
