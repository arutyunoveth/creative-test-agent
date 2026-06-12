import re
from collections import Counter

from src.modules.knowledge_base.models import KnowledgeItem
from src.modules.knowledge_base.schemas import KnowledgeItemResponse
from src.shared.db.repository import db_session, json_loads


class SearchResult:
    def __init__(self, item: KnowledgeItemResponse, score: float, matched_terms: list[str]):
        self.item = item
        self.score = score
        self.matched_terms = matched_terms


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_\-]{2,}", text)
    return tokens


def _phrase_matches(text: str, phrases: list[str]) -> int:
    text_lower = text.lower()
    count = 0
    for phrase in phrases:
        words = phrase.strip().split()
        if len(words) <= 1:
            continue
        if phrase.lower() in text_lower:
            count += 1
    return count


def keyword_search(
    query: str,
    client_id: str | None = None,
    project_id: str | None = None,
    source_type: str | None = None,
    max_results: int = 20,
) -> list[SearchResult]:
    if not query or not query.strip():
        return []

    query_tokens = _tokenize(query)
    query_tokens_set = set(query_tokens)
    query_lower = query.lower()

    if not query_tokens_set:
        return []

    results: list[SearchResult] = []

    with db_session() as db:
        q = db.query(KnowledgeItem)
        if client_id:
            q = q.filter(KnowledgeItem.client_id == client_id)
        if project_id:
            q = q.filter(KnowledgeItem.project_id == project_id)
        if source_type:
            q = q.filter(KnowledgeItem.source_type == source_type)
        items = q.all()

        for item in items:
            text = (item.title or "") + " " + (item.content or "")
            tokens = _tokenize(text)
            if not tokens:
                continue

            token_overlap = len(query_tokens_set & set(tokens))
            if token_overlap == 0:
                continue

            title_tokens = _tokenize(item.title or "")
            title_overlap = len(query_tokens_set & set(title_tokens))

            phrase_count = _phrase_matches(text, [query])

            query_freq = sum(1 for t in tokens if t in query_tokens_set)
            total_tokens = len(tokens)
            tf_score = query_freq / max(total_tokens, 1)

            score = (
                token_overlap * 1.0
                + tf_score * 5.0
                + title_overlap * 3.0
                + phrase_count * 4.0
            )

            if item.client_id and query_lower in (item.client_id.lower() or ""):
                score += 2.0
            if item.project_id and query_lower in (item.project_id.lower() or ""):
                score += 1.5

            tags = json_loads(item.tags_json)
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and query_lower in tag.lower():
                        score += 1.0
                        break

            matched = list(query_tokens_set & set(tokens))
            response = KnowledgeItemResponse(
                id=item.id,
                source_type=item.source_type,
                source_id=item.source_id,
                client_id=item.client_id,
                project_id=item.project_id,
                title=item.title,
                content=item.content,
                tags=tags if isinstance(tags, list) else [],
                metadata=json_loads(item.metadata_json),
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            results.append(SearchResult(item=response, score=score, matched_terms=matched))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:max_results]
