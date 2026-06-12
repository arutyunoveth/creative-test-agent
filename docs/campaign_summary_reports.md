# Campaign Summary Reports

After a batch run completes, you can generate campaign-level summary reports.

## Report Formats

| Format | Endpoint | Description |
|---|---|---|
| JSON | `GET /batches/{id}/report?format=json` | Machine-readable summary |
| Markdown | `GET /batches/{id}/report?format=markdown` | Human-readable text report |
| HTML | `GET /batches/{id}/report?format=html` | Web-viewable HTML report |
| DOCX | `POST /batches/{id}/export/docx` | Word document export |
| PPTX | `POST /batches/{id}/export/pptx` | PowerPoint presentation |
| PDF | `POST /batches/{id}/export/pdf` | PDF-ready HTML export |

## Report Sections

All reports include:

1. **Executive Summary** — best creative, average score, overview
2. **Batch Overview** — total, completed, failed, skipped counts
3. **Best Performing Creative** — which variant scored highest
4. **Scorecard Overview** — min, max, avg, distribution
5. **Risk Overview** — top recurring risks
6. **Brandbook Compliance** — compliant vs non-compliant distribution
7. **Recommendations** — top recurring recommendations
8. **Appendix: Tested Variants** — per-variant details (asset, status, score)

## Exports

Exports are created as `ExportJob` records. The file path is returned in the response. Files are stored under `CTA_EXPORTS_ROOT` (default: `./data/exports`).

## Example

```bash
# Generate markdown report
curl "http://localhost:8000/batches/{batch_id}/report?format=markdown"

# Export as DOCX
curl -X POST "http://localhost:8000/batches/{batch_id}/export/docx"

# Get JSON summary
curl "http://localhost:8000/batches/{batch_id}/summary"
```
