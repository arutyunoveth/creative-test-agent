# Knowledge & Context Engine

## Overview

The Knowledge & Context Engine provides local-first storage, search, and retrieval for brand knowledge. It enables:
- **Ingestion**: Brandbook documents are chunked and stored as structured knowledge items.
- **Search**: Keyword-based search with token overlap, phrase matching, and boost factors.
- **Context Building**: Assembles search results into a truncated context string for LLM consumption.
- **Learning Loop**: Report findings can be saved back to the knowledge base as new items.
- **Manual Notes**: Users can add ad-hoc knowledge entries via UI or API.

## Architecture

```
Brandbook Upload → Chunking → Knowledge Items → Keyword Search → Context Builder → LLM Prompt
                         ↑                          ↑
                    Auto-ingest              Manual Notes / Report Findings
```

## Chunking (`src/modules/brandbooks/chunking.py`)

- Configurable chunk size (default: 1200 chars) and overlap (default: 150 chars).
- Sentence-aware breakpoints: prefers `\n\n`, `\n`, `. `, `! `, `? ` before splitting mid-sentence.
- Each chunk includes index, text, char range, and word count.

## Ingestion (`src/modules/brandbooks/ingestion.py`)

- `POST /brandbooks/{id}/ingest` — idempotent: deletes stale chunks for the same `source_id` before recreating.
- Auto-ingest on upload when `CTA_ENABLE_KNOWLEDGE_AUTO_INGEST=true` (default).
- Creates KnowledgeItems with `source_type=brandbook`, tags include document type, chunk index, and `auto_ingested`.

## Keyword Search (`src/modules/knowledge_base/search.py`)

- **Token overlap**: Intersection of query tokens and content tokens.
- **TF score**: Term frequency within the chunk.
- **Title boost**: Matches in title get 3x weight.
- **Phrase match**: Exact phrase matches get 4x weight.
- **Client/Project boost**: If query matches client_id or project_id.
- **Tag boost**: If query matches any tag.

## Context Builder (`src/modules/knowledge_base/context_builder.py`)

- Limits: `CTA_KB_CONTEXT_MAX_ITEMS` (default: 8), `CTA_KB_CONTEXT_MAX_CHARS` (default: 6000).
- Adds truncation warning when limits are hit.
- Returns `ContextResult` with text, items used, total available, and truncated flag.

## Learning Loop

- `POST /reports/{id}/save-findings-to-knowledge` — saves all findings + compliance violations as KnowledgeItems with `source_type=report_finding`.
- `POST /knowledge-base/manual-note` — creates a KnowledgeItem with `source_type=manual_note`.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/brandbooks/{id}/ingest` | Ingest brandbook to knowledge base |
| GET | `/knowledge-base/search?q=...` | Keyword search with filters |
| POST | `/knowledge-base/manual-note` | Create manual knowledge note |
| POST | `/reports/{id}/save-findings-to-knowledge` | Save report findings to KB |

## Configuration

| Variable | Default | Description |
|---|---|---|
| `CTA_ENABLE_KNOWLEDGE_AUTO_INGEST` | `true` | Auto-ingest brandbooks on upload |
| `CTA_KB_CHUNK_SIZE_CHARS` | `1200` | Characters per chunk |
| `CTA_KB_CHUNK_OVERLAP_CHARS` | `150` | Overlap between chunks |
| `CTA_KB_CONTEXT_MAX_ITEMS` | `8` | Max items in context |
| `CTA_KB_CONTEXT_MAX_CHARS` | `6000` | Max chars in context |
