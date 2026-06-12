# Advanced Exports

## Current state

- HTML report generation — working
- Markdown report generation — working
- JSON export — working via API
- **DOCX export** — real Word document via `python-docx`
- **PPTX export** — real PowerPoint via `python-pptx`
- **PDF-ready HTML** — print-ready HTML with CSS for browser "Save as PDF"
- DOCX/PPTX stub endpoints — kept for backward compatibility

## Export job model

| Field | Type | Description |
|-------|------|-------------|
| id | str | UUID |
| entity_type | str | Type of source entity (report, comparison) |
| entity_id | str | Source entity ID |
| export_type | str | docx, pptx, html, pdf_stub, docx_stub, pptx_stub, json, markdown |
| status | str | created, running, completed, failed |
| file_path | str? | Path to exported file |
| error_message | str? | Error details if failed |
| created_at | datetime | Creation timestamp |
| completed_at | datetime? | Completion timestamp |

## Export endpoints

```
GET  /exports
GET  /exports/{job_id}
GET  /exports/{job_id}/download
POST /exports/report/{report_id}/docx
POST /exports/report/{report_id}/pptx
POST /exports/report/{report_id}/pdf
POST /exports/comparison/docx?test_run_ids=...
POST /exports/comparison/pptx?test_run_ids=...
POST /exports/report/{report_id}/docx_stub  — legacy
POST /exports/report/{report_id}/pptx_stub  — legacy
```

## DOCX/PPTX

- Real document generation using `python-docx` and `python-pptx`
- No LibreOffice required
- All content sections included (title, summary, scorecard, risks, recommendations, compliance)
- Client-facing mode: softer language, no debug/internal details

## PDF-Ready Export

- Print-ready HTML with CSS for `@media print`
- Open in browser → Print → Save as PDF
- No system-level PDF generator required

## Comparison exports

- DOCX and PPTX exports for A/B comparison results
- Uses the first test run's full report as the basis

## Security

- Path traversal protection on download
- Only completed jobs downloadable
- Files served with appropriate Content-Type

## Configuration

```env
CTA_EXPORTS_ROOT=./data/exports
```

See `docs/advanced_report_exports.md` for full documentation.
