# Brandbook Compliance Workflow

## Overview

The Brandbook Compliance stage is the 4th step in the 6-stage creative pre-test pipeline, inserted between `brand_safety_review` and `rubric_scoring`. It checks creative content against brandbook guidelines to identify violations (forbidden claims, tone mismatches, policy breaches).

## How It Works

1. **Context Collection**: The pipeline automatically collects brandbook documents linked to the same `brand_profile_id` as the test run. Up to 3 full-text snippets are passed as context.
2. **Text Analysis**: The creative text is analyzed against brandbook rules.
3. **Stub Mode** (default): Deterministic detection of:
   - Forbidden claims (e.g., "cure", "guaranteed results", "miracle")
   - Tone violations (aggressive, too casual, too formal language)
4. **Live Mode**: LLM prompt with full brand context + compliance rules → JSON response.

## Pipeline Integration

| Stage | Function |
|---|---|
| 1 | `creative_summary` |
| 2 | `audience_simulation` |
| 3 | `brand_safety_review` |
| **4** | **`brandbook_compliance_review`** |
| 5 | `rubric_scoring` |
| 6 | `final_recommendation` |

## Output Structure

```json
{
  "overall_verdict": "compliant | needs_revision | non_compliant",
  "violations": [
    {
      "rule": "forbidden_claim_cure",
      "severity": "high | medium | low",
      "details": "Contains forbidden claim: 'cure'..."
    }
  ],
  "recommendations": ["Fix violation X..."],
  "compliance_score": 7.5
}
```

## Report Integration

- **Internal mode**: Full violation table with severity, compliance score, recommendations.
- **Client-facing mode**: Simplified "Passed / Needs Attention" label.
- **A/B Comparison**: Compliance violations penalize the effective score (`non_compliant` = -2.0, `needs_revision` = -1.0, plus `(10 - score) * 0.3`).

## Configuration

- Controlled by `CTA_ENABLE_KNOWLEDGE_AUTO_INGEST` (default: `true`) for auto-ingestion on brandbook upload.
- Chunk size: `CTA_KB_CHUNK_SIZE_CHARS` (default: 1200), overlap: `CTA_KB_CHUNK_OVERLAP_CHARS` (default: 150).
