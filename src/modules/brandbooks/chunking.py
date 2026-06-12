import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    index: int
    text: str
    char_start: int
    char_end: int
    word_count: int


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 150,
) -> list[TextChunk]:
    if not text or not text.strip():
        return []

    text = text.strip()
    if len(text) <= chunk_size:
        return [
            TextChunk(
                index=0,
                text=text,
                char_start=0,
                char_end=len(text),
                word_count=len(text.split()),
            )
        ]

    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            break_point = _find_break(text, start, end)
            if break_point > start:
                end = break_point

        chunk_text_slice = text[start:end].strip()
        if chunk_text_slice:
            chunks.append(
                TextChunk(
                    index=index,
                    text=chunk_text_slice,
                    char_start=start,
                    char_end=end,
                    word_count=len(chunk_text_slice.split()),
                )
            )

        next_start = end - overlap
        if next_start <= start:
            next_start = end
        start = next_start
        index += 1

        if index > 1000:
            break

    return chunks


def _find_break(text: str, start: int, end: int) -> int:
    segment = text[start:end]
    for delim in ("\n\n", "\n", ". ", "! ", "? "):
        pos = segment.rfind(delim)
        if pos != -1 and pos > len(segment) * 0.3:
            return start + pos + len(delim)
    for delim in (", ", "; ", ": ", " — ", " – "):
        pos = segment.rfind(delim)
        if pos != -1 and pos > len(segment) * 0.3:
            return start + pos + len(delim)
    return end
