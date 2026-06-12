# Reporting

## Overview

The reporting module generates structured reports from completed creative test runs. It supports multiple formats, two report modes, versioning, and A/B comparison between test runs.

## Report Formats

| Format      | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `json`      | Full report object as JSON (default).                                       |
| `markdown`  | Human-readable Markdown with all sections, suitable for documentation.      |
| `html`      | Self-contained HTML page with embedded CSS, no external CDN dependencies.   |
| `pdf_stub`  | Placeholder for future PDF export — returns report object + HTML content.   |

## Report Modes

### `internal` (default)
For agency internal team use:
- Direct, critical language
- Risk details with severity indicators
- Full scorecard table
- Objections and confusion points from audience reactions
- Low-level improvement recommendations
- Appendix with technical test context (input context keys)

### `client_facing`
For polished client presentation:
- Softer, more constructive language
- No internal debug details (no "input context keys", no "model uncertainty")
- Focus on strengths and actionable recommendations
- Clean formatting suitable for sharing

## Markdown Structure

```
# Creative Pre-Test Report

## Executive Summary

## Creative Overview

## Main Message

## Audience Reactions

## Scorecard

## Brand Safety and Risks

## Recommendations

## Final Recommendation

## Appendix: Test Context
```

In `internal` mode, the report also includes **Top Strengths** and **Key Improvement Areas** sections.

## HTML Export

- Generated locally — no external CDN, no conversion services.
- Clean, readable layout with responsive CSS.
- Scorecard rendered as an HTML table.
- Risks and recommendations colour-coded by severity/priority.
- Final recommendation prominently highlighted.
- Internal/client_facing mode affects content inclusion.

## PDF Stub

PDF export interface is prepared but real PDF rendering is planned for a later sprint. When `format=pdf_stub` is requested:
- A full report object is returned (same as `json` + `html`).
- `report_format` is set to `pdf_stub`.
- The response includes both `report_markdown` and `report_html` content.

## Report Versioning

- Each combination of `test_run_id + report_mode + report_format` gets its own version sequence.
- First generation → version 1.
- Subsequent generations increment the version.
- Versions are tracked in-memory; reset on server restart (acceptable for MVP).

Audit events are written for every version generation (`report_generated`, `report_version_created`).

## A/B Comparison

### Endpoint

```
POST /reports/compare
Content-Type: application/json

{
  "test_run_ids": ["run-id-1", "run-id-2"],
  "report_mode": "internal"
}
```

### Logic

Comparison is deterministic (no LLM calls):

1. Extract scorecards from each test run's structured findings.
2. Calculate average score per run.
3. Penalise runs with high-severity risks (-0.5 points each).
4. Compare scores across criteria to produce `score_deltas`.
5. Winner = variant with highest effective score.
6. If score difference < 0.5 → `no_clear_winner` with `revise_both` recommendation.

### Response

```json
{
  "comparison_id": "...",
  "test_run_ids": ["...", "..."],
  "winner": "...",
  "rationale": "...",
  "score_deltas": [
    {
      "criterion": "message_clarity",
      "scores": { "run-id-1": 7, "run-id-2": 8 },
      "difference_summary": "..."
    }
  ],
  "variant_summaries": [
    {
      "test_run_id": "...",
      "summary": "...",
      "strengths": ["..."],
      "weaknesses": ["..."]
    }
  ],
  "recommendation": "..."
}
```

### Validation

- Minimum 2 test run IDs required.
- All test runs must exist.
- All test runs must be `completed`.
- All test runs must have structured findings.
- Unsupported report modes are rejected.

## Audit Events

| Event Type                     | Trigger                              |
|-------------------------------|--------------------------------------|
| `report_requested`            | GET /reports/{id}                     |
| `report_generated`            | Report successfully generated         |
| `report_exported`             | Report retrieved in specific format   |
| `report_version_created`      | New version of a report generated     |
| `comparison_report_requested` | POST /reports/compare initiated       |
| `comparison_report_generated` | Comparison completed successfully     |
| `comparison_report_failed`    | Comparison failed validation          |

## Local-Only Guarantee

- All report generation is purely local.
- No external APIs, no cloud LLM, no cloud storage.
- HTML is generated via Python string templates (no Jinja2 dependency).
- Comparison is fully deterministic using existing structured findings.

## API Examples

### JSON report (default)

```bash
curl "http://localhost:8000/reports/{test_run_id}"
```

### Markdown report

```bash
curl "http://localhost:8000/reports/{test_run_id}?format=markdown"
```

### HTML client-facing report

```bash
curl "http://localhost:8000/reports/{test_run_id}?format=html&mode=client_facing"
```

### PDF stub

```bash
curl "http://localhost:8000/reports/{test_run_id}?format=pdf_stub"
```

### A/B comparison

```bash
curl -X POST "http://localhost:8000/reports/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "test_run_ids": ["test-run-a", "test-run-b"],
    "report_mode": "internal"
  }'
```
