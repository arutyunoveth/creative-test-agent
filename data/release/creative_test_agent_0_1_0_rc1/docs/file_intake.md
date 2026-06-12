# File Intake and Local Parsing

## Overview

Creative Test Agent supports uploading real creative asset files through the API. All file processing happens locally — no data is sent to external services.

## Supported File Types

| Extension | MIME Type | Asset Type | Parser | Text Extraction |
|-----------|-----------|------------|--------|-----------------|
| `.txt` | `text/plain` | text | TextParser | Full UTF-8 text |
| `.md` | `text/markdown` | text | TextParser | Full UTF-8 text |
| `.pdf` | `application/pdf` | pdf | PdfParser | Page-by-page text |
| `.png` | `image/png` | image | ImageParser | Metadata only (no OCR) |
| `.jpg`/`.jpeg` | `image/jpeg` | image | ImageParser | Metadata only (no OCR) |
| `.webp` | `image/webp` | image | ImageParser | Metadata only (no OCR) |

## Upload Endpoint

```text
POST /creative-assets/upload
```

### Request

Multipart form data:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | The creative asset file |
| `title` | String | No | Display title (defaults to filename) |
| `metadata` | JSON string | No | Optional metadata dict |

### Example

```bash
curl -X POST "http://localhost:8000/creative-assets/upload" \
  -F "file=@sample.pdf" \
  -F "title=Sample campaign concept"
```

Then create a test run based on the uploaded asset:

```bash
curl -X POST "http://localhost:8000/test-runs" \
  -H "Content-Type: application/json" \
  -d '{
    "creative_asset_id": "<asset_id_from_upload>",
    "audience_profile_ids": [],
    "input_context": {}
  }'
```

Execute the test run:

```bash
curl -X POST "http://localhost:8000/test-runs/<run_id>/run"
```

Get the report:

```bash
curl "http://localhost:8000/reports/<run_id>"
```

## Validation Rules

| Check | Error Code | Behaviour |
|-------|-----------|-----------|
| File extension | `unsupported_file_type` | Rejected |
| File size > limit | `file_too_large` | Rejected |
| Empty file | `empty_file` | Rejected |
| Path traversal | `unsafe_filename` | Rejected |
| Corrupt PDF | `file_parse_failed` | Rejected |
| Non-UTF-8 text | `file_parse_failed` | Rejected |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `CTA_STORAGE_ROOT` | `./data/storage` | Root directory for uploaded files |
| `CTA_MAX_UPLOAD_SIZE_MB` | `25` | Maximum file size in MB |
| `CTA_ALLOWED_UPLOAD_TYPES` | `txt,md,pdf,png,jpg,jpeg,webp` | Comma-separated allowed extensions |

## Storage

Files are stored under `CTA_STORAGE_ROOT` with UUID-based filenames to prevent collisions. The original filename is preserved only as metadata. Path traversal attempts are blocked.

## PDF Text Extraction

PDF files are parsed locally using `pypdf`. Text is extracted page by page. If a PDF contains no extractable text (e.g., scanned document), the asset is still created with a warning: `pdf_contains_no_extractable_text`.

## Image Processing

Images are processed locally using `Pillow`. The following metadata is extracted:

- Width and height
- Image format
- Color mode

Optical Character Recognition (OCR) is **not implemented** in this sprint. Uploading an image returns a warning: `image_text_extraction_not_implemented`. The image is stored and can still be used in the structured workflow, but visual content analysis is limited.

## Closed-Loop Guarantees

- All file processing is local. No data is sent to external APIs.
- No cloud OCR. No cloud storage. No cloud file conversion.
- Parser dependencies (`pypdf`, `Pillow`) are lightweight and local-only.
- Uploaded files never leave `CTA_STORAGE_ROOT`.

## Integration with Structured Workflow

When a test run is executed against an uploaded asset:

- If the asset has `text_content`, it is used as the creative context.
- If the asset has `extracted_text` (from file parsing), it is used instead.
- For images without OCR, the pipeline receives empty text but does not crash — it falls back to deterministic stub defaults.
- The pipeline uses `get_asset_model()` to access raw asset data including extracted text.
