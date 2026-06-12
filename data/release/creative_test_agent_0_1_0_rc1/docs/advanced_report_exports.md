# Advanced Report Exports

## Overview

The Advanced Report Exports system generates real, downloadable document files from test run reports — all locally, without any cloud conversion APIs.

## Export Types

| Type | Format | Description |
|------|--------|-------------|
| DOCX | `.docx` | Word document with full report content, tables, and styling |
| PPTX | `.pptx` | PowerPoint presentation (7-10 slides) |
| PDF-ready HTML | `.html` | Print-ready HTML file with CSS for browser "Save as PDF" |
| HTML | `.html` | Standard HTML report |
| JSON | `.json` | Structured data export |
| Markdown | `.md` | Plain text markdown |

## DOCX Generation

Uses `python-docx` to create Word documents.

**Content structure:**
- Title and mode label
- Executive Summary
- Creative Overview
- Main Message
- Audience Reactions (per segment)
- Scorecard table
- Brand Safety and Risks table
- Visual Analysis Notes
- Recommendations
- Final Recommendation
- Appendix (internal mode only)

**Styling:**
- Calibri font, 11pt body text
- Heading 1/2 for sections
- Light Shading Accent 1 tables
- Client-facing mode: no internal/debug details

## PPTX Generation

Uses `python-pptx` to create PowerPoint presentations.

**Slide structure (7-10 slides):**
1. Title / Creative Pre-Test Summary
2. Creative Overview
3. Executive Summary
4. Scorecard
5. Audience Reactions
6. Brand Safety Risks
7. Visual Analysis Notes (if present)
8. Recommendations
9. Final Recommendation
10. Appendix (optional)

**Styling:**
- Clean white background
- Widescreen 16:9 format
- Bullet lists and tables
- No external fonts or images

## PDF-Ready Export

Since no system-level PDF generator (LibreOffice) is required, the PDF endpoint creates a print-ready HTML file:

- Full report content with print CSS
- `@media print` styles for page breaks and formatting
- Open in browser → Print → Save as PDF

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/exports/report/{id}/docx` | Export report to DOCX |
| POST | `/exports/report/{id}/pptx` | Export report to PPTX |
| POST | `/exports/report/{id}/pdf` | Export PDF-ready HTML |
| POST | `/exports/comparison/docx?test_run_ids=...` | Export comparison to DOCX |
| POST | `/exports/comparison/pptx?test_run_ids=...` | Export comparison to PPTX |
| GET | `/exports/{job_id}/download` | Download export file |
| GET | `/exports` | List export jobs |
| GET | `/exports/{job_id}` | Get export job details |

Backward-compatible stub endpoints remain:
- `POST /exports/report/{id}/docx_stub`
- `POST /exports/report/{id}/pptx_stub`

## Download Security

- Path traversal protection: all files must be under `exports_root`
- Only completed jobs can be downloaded
- Appropriate Content-Type headers set per file type
- File names use entity ID prefix + timestamp

## Export Jobs

Each export creates a job record:

| Field | Description |
|-------|-------------|
| id | UUID |
| entity_type | report, comparison |
| entity_id | Source entity UUID |
| export_type | docx, pptx, html, json, markdown |
| status | created → running → completed / failed |
| file_path | Local path to generated file |
| error_message | Error details if failed |

## Configuration

```env
CTA_EXPORTS_ROOT=./data/exports
```

Directory is created automatically on first export. Generated exports must not be committed to git.

## Limitations (Sprint 14)

- DOCX/PPTX: basic styling, no custom templates
- PDF: print-ready HTML only (no native PDF library)
- No embedded images from creative assets
- No batch exports
- No email delivery

## No Cloud Conversion Guarantee

All exports are generated locally:
- No Google Docs API
- No Microsoft Graph API
- No Canva API
- No external PDF conversion APIs
- No cloud storage
