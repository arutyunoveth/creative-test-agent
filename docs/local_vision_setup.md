# Local Vision Setup

## Overview

The visual analysis subsystem provides optional local-first image analysis: extraction of visual descriptions, text detection (OCR), layout analysis, and brand safety risk detection — all without cloud APIs.

## Default Stub Mode

By default `CTA_VISION_PROVIDER=stub`, which returns deterministic placeholder results. This is the safe default — no OCR runtime, no VLM model, no GPU required:

```json
{
  "provider": "stub",
  "visual_summary": "Stub visual summary — no real vision provider configured.",
  "detected_text": "",
  "layout_notes": [],
  "visual_risks": [],
  "warnings": ["vision_stub_mode"]
}
```

## Closed-Loop Vision Policy

```text
Allowed providers:     stub, local_ocr, local_vlm, hybrid
Forbidden providers:   google_vision, aws_textract, azure_ocr,
                       openai_vision, gemini_vision, claude_vision
```

Rules:

- `stub` — always allowed.
- `local_ocr` — allowed only if `CTA_ENABLE_LOCAL_OCR=true`.
- `local_vlm` — allowed only if `CTA_ENABLE_LOCAL_VLM=true`.
- `hybrid` — allowed only if OCR or VLM is enabled.
- Any cloud vision provider is always forbidden in local-only mode.

Error codes:

| Code | Meaning |
|------|---------|
| `cloud_vision_forbidden` | Cloud vision provider rejected |
| `local_ocr_disabled` | OCR requested but not enabled |
| `local_vlm_disabled` | VLM requested but not enabled |
| `hybrid_disabled` | Hybrid requested but neither OCR nor VLM enabled |
| `unsupported_vision_provider` | Unknown provider name |

## Supported Image Types

Images are parsed using Pillow. Supported upload formats:

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- WebP (`.webp`)

Non-image uploads (txt, md, pdf) are parsed by their respective parsers and produce no visual analysis metadata.

## How Visual Analysis Is Stored

When an image is uploaded, the image parser runs `get_vision_analyzer().analyze_image()` during parsing. The normalized `VisionResult` is stored in `metadata.visual_analysis`:

```json
{
  "provider": "stub",
  "visual_summary": "...",
  "detected_text": "...",
  "layout_notes": ["..."],
  "visual_risks": [
    {
      "risk_type": "...",
      "level": "low|medium|high",
      "description": "...",
      "mitigation": "..."
    }
  ],
  "warnings": ["..."],
  "metadata": {}
}
```

Visual analysis can also be triggered on demand via `POST /creative-assets/{id}/analyze-visual`.

## How Visual Notes Enter Reports

During report generation, `_build_visual_notes()` extracts `visual_analysis` from the asset's metadata and formats it as human-readable text. The result is:

- Stored in the `report.visual_notes` column.
- Included in markdown reports as `## Visual Analysis Notes`.
- Included in HTML reports as a dedicated visual notes section.
- In `client_facing` mode, technical `stub` warnings are softened to `limited`.

## API Reference

### GET /vision/health

Returns the current vision provider status:

```json
{
  "provider": "stub",
  "local_ocr_enabled": false,
  "local_vlm_enabled": false,
  "available": true,
  "warnings": []
}
```

### POST /creative-assets/{id}/analyze-visual

Triggers visual analysis on an existing image asset. Updates asset metadata and optionally extracted_text. Returns the updated asset.

| Status | Meaning |
|--------|---------|
| 200 | Analysis complete |
| 400 | Asset is not an image |
| 404 | Asset not found |
| 500 | Analysis error |

Audit events: `visual_analysis_requested`, `visual_analysis_completed`, `visual_analysis_failed`.

### GET /creative-assets/{id}/image

Serves the image file for preview. Only works for image assets. Prevents path traversal outside storage root.

### GET /creative-assets/{id}

Returns the asset including metadata. To view visual analysis, inspect `metadata.visual_analysis`.

## Local OCR

### Prerequisites

1. Install Tesseract OCR engine:
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt install tesseract-ocr`
   - Windows: Download from GitHub

2. Install Python package:
   ```bash
   pip install pytesseract
   ```

3. Configure:
   ```env
   CTA_VISION_PROVIDER=local_ocr
   CTA_ENABLE_LOCAL_OCR=true
   ```

### Behaviour

- If Tesseract is installed and `pytesseract` is available, text is extracted from images.
- If Tesseract is not installed, the analyzer returns a `local_ocr_unavailable` warning without crashing.
- If OCR is not enabled, the policy returns `local_ocr_disabled`.

## Local VLM (Vision-Language Model)

### Prerequisites

1. Install Ollama: https://ollama.ai

2. Pull a vision-capable model:
   ```bash
   ollama pull qwen3-vl:8b
   ```

3. Configure:
   ```env
   CTA_VISION_PROVIDER=local_vlm
   CTA_ENABLE_LOCAL_VLM=true
   CTA_VISION_BASE_URL=http://localhost:11434
   CTA_VISION_MODEL=qwen3-vl:8b
   ```

### Behaviour

- Uses Ollama-compatible `/api/chat` API with base64-encoded images.
- If the VLM is unreachable or returns an error, a `local_vlm_unavailable` warning is returned.
- The adapter does not call any cloud API.

## Hybrid Mode

Combines OCR + VLM: OCR extracts detected text, VLM provides visual description and layout notes.

```env
CTA_VISION_PROVIDER=hybrid
CTA_ENABLE_LOCAL_OCR=true
CTA_ENABLE_LOCAL_VLM=true
CTA_VISION_BASE_URL=http://localhost:11434
```

## No Cloud OCR/Vision Guarantee

This system never calls:

- Google Vision API
- AWS Textract
- Azure OCR
- OpenAI Vision
- Gemini Vision
- Claude Vision
- Any other cloud vision/OCR service

All analysis is performed locally (stub, local OCR via Tesseract, local VLM via Ollama).

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `local_ocr_disabled` | OCR not enabled | Set `CTA_ENABLE_LOCAL_OCR=true` |
| `local_ocr_unavailable` | Tesseract not installed or pytesseract not installed | Install Tesseract and `pip install pytesseract` |
| `local_vlm_disabled` | VLM not enabled | Set `CTA_ENABLE_LOCAL_VLM=true` |
| `local_vlm_unavailable` | Ollama not running or model not pulled | Start Ollama (`ollama serve`), pull model (`ollama pull <model>`) |
| `vision_stub_mode` | Default stub provider | No action needed — this is the safe default |
| `Image file not found` | File deleted or path invalid | Re-upload the image |
| `cloud_vision_forbidden` | Tried to use cloud provider | Only use `stub`, `local_ocr`, `local_vlm`, or `hybrid` |
| `unsupported_vision_provider` | Typo or unknown provider | Check `CTA_VISION_PROVIDER` value |

## Smoke Tests

Optional smoke tests for local VLM can be enabled:

```env
CTA_RUN_LOCAL_VISION_SMOKE_TESTS=true
```

These tests are skipped by default and require a running VLM.
