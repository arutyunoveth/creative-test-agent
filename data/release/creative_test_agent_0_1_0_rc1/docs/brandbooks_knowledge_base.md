# Brandbooks and Knowledge Base

## Brandbook upload

The brandbook module allows uploading brand guidelines documents:

- **Document types**: brandbook, tone_of_voice, claims_policy, legal_guidelines, campaign_brief, other
- **Supported formats**: txt, md, pdf
- **Local storage**: files stored in `data/storage/brandbooks/`
- **Text extraction**: PDFs parsed with existing local parser

### API

```
POST /brandbooks/upload        (multipart file upload)
POST /brandbooks/{id}/ingest   (ingest to knowledge base)
GET  /brandbooks
GET  /brandbooks/{brandbook_id}
```

### Context hook

`get_brandbook_context(project_id, brand_profile_id)` returns concatenated extracted text from related brandbook documents for use in test run workflows.

### Ingestion

Brandbooks can be ingested into the knowledge base as structured chunks:

- **Auto-ingest**: Enabled by default (`CTA_ENABLE_KNOWLEDGE_AUTO_INGEST=true`). Creates knowledge items on upload.
- **Manual ingest**: `POST /brandbooks/{id}/ingest` — idempotent (deletes stale chunks first).
- **Chunking**: Configurable size (default 1200 chars) and overlap (default 150 chars), sentence-aware breakpoints.

## Knowledge Base

The knowledge base module stores structured knowledge items:

| Field | Type | Description |
|-------|------|-------------|
| id | str | UUID |
| source_type | str | brandbook, manual_note, report_finding, client_feedback, other |
| source_id | str? | Reference to source entity |
| client_id | str? | Client context |
| project_id | str? | Project context |
| title | str | Item title |
| content | str? | Item content |
| tags | list[str] | Tags for filtering |

### API

```
POST /knowledge-base                      (create item)
POST /knowledge-base/manual-note          (create manual note)
GET  /knowledge-base?source_type=...      (list items)
GET  /knowledge-base/search?q=...         (keyword search)
GET  /knowledge-base/{item_id}
```

### Search

Local keyword search with:
- Token overlap scoring
- Phrase match boost (4x)
- Title match boost (3x)
- Client/project ID boost
- Tag match boost
- TF (term frequency) score

## Brandbook Compliance Pipeline

The brandbook compliance stage (`brandbook_compliance_review`) is the 4th stage in the 6-stage pipeline. It:

1. Collects brandbook context linked to the test run's brand profile.
2. Checks creative text for forbidden claims and tone violations.
3. Returns a verdict (`compliant`, `needs_revision`, `non_compliant`) with violations and recommendations.
4. Appears in reports (internal: full details; client-facing: simplified label).
5. Penalizes compliance violations in A/B comparison scoring.

## Learning Loop

- `POST /reports/{id}/save-findings-to-knowledge` saves findings and compliance violations as knowledge items.
- `POST /knowledge-base/manual-note` allows ad-hoc knowledge entries.

## No cloud processing

- All processing is local (chunking, keyword search, context building)
- No embeddings, vector search, or cloud AI
- SQLite storage for all knowledge items

## Configuration

| Variable | Default | Description |
|---|---|---|
| `CTA_ENABLE_KNOWLEDGE_AUTO_INGEST` | `true` | Auto-ingest brandbooks on upload |
| `CTA_KB_CHUNK_SIZE_CHARS` | `1200` | Characters per chunk |
| `CTA_KB_CHUNK_OVERLAP_CHARS` | `150` | Overlap between chunks |
| `CTA_KB_CONTEXT_MAX_ITEMS` | `8` | Max items in context |
| `CTA_KB_CONTEXT_MAX_CHARS` | `6000` | Max chars in context |

See also:
- `docs/brandbook_compliance_workflow.md`
- `docs/knowledge_context_engine.md`
