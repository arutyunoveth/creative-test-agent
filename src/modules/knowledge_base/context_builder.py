from src.modules.knowledge_base.schemas import KnowledgeItemResponse
from src.shared.config.settings import get_settings


class ContextResult:
    def __init__(self, text: str, items_used: int, total_available: int, truncated: bool):
        self.text = text
        self.items_used = items_used
        self.total_available = total_available
        self.truncated = truncated


def build_context(
    query: str,
    client_id: str | None = None,
    project_id: str | None = None,
    source_type: str | None = None,
    max_items: int | None = None,
    max_chars: int | None = None,
) -> ContextResult:
    from src.modules.knowledge_base.search import keyword_search

    settings = get_settings()
    max_items = max_items or settings.kb_context_max_items
    max_chars = max_chars or settings.kb_context_max_chars

    results = keyword_search(
        query=query,
        client_id=client_id,
        project_id=project_id,
        source_type=source_type,
        max_results=max_items,
    )

    if not results:
        return ContextResult(text="", items_used=0, total_available=0, truncated=False)

    total_available = len(results)
    parts: list[str] = []
    chars_used = 0
    truncated = False

    for r in results:
        item_text = r.item.content or ""
        if not item_text.strip():
            continue

        header = f"[{r.item.title}]"
        entry = f"{header}\n{item_text.strip()}\n"
        entry_len = len(entry)

        if chars_used + entry_len > max_chars:
            truncated = True
            if not parts:
                available = max_chars - len(header) - 2
                if available > 20:
                    entry = f"{header}\n{item_text.strip()[:available]}\n[Truncated at character limit]"
                    parts.append(entry)
            break

        parts.append(entry)
        chars_used += entry_len

    text = "\n".join(parts)

    if truncated or len(parts) < total_available:
        truncated = True
        text += (
            f"\n\n[Context truncated: {len(parts)} of {total_available} items shown. "
            f"Refine your query for more specific results.]"
        )

    return ContextResult(
        text=text,
        items_used=len(parts),
        total_available=total_available,
        truncated=truncated,
    )
