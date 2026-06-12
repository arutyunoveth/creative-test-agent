# Demo / Pilot Package

## Purpose

The demo package allows you to present the Creative Test Agent to a potential client (marketing agency) with a pre-populated fictional scenario and a complete walkthrough.

## What the System Demonstrates

- **Closed-loop local-first architecture** — all data stays on the local machine.
- **Structured creative pre-testing** — systematic evaluation of ad creatives before client presentation.
- **Multi-segment audience testing** — how different audience segments react to the same creative.
- **Brand safety checks** — detection of risky claims and over-promising language.
- **A/B comparison** — head-to-head comparison of creative variants.
- **Client-facing reporting** — polished HTML reports suitable for client presentation.

## Demo Scenario

Fictional brand: **NovaBank** — a debit card for freelancers and self-employed professionals.

Three creative variants:

| Variant | Style | Description |
|---------|-------|-------------|
| A | Practical / Clear | Straightforward product feature explanation |
| B | Emotional / Freedom | Aspirational messaging about financial control |
| C | Risky / Overclaim | Intentionally contains problematic claims (for brand safety demo) |

## Setup

### Prerequisites

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Start the server

```bash
uvicorn src.main:app --reload
```

### Seed demo data

In a separate terminal:

```bash
python scripts/seed_demo_data.py
```

You should see:

```
✓ Brand profile 'NovaBank' created.
✓ Audience profile 'Beginner Freelancer' created.
...
Demo data seeded successfully.
```

The seed script is **idempotent** — running it multiple times will not create duplicates.

### Open the UI

```
http://localhost:8000/
```

## Full Demo Walkthrough

### 1. Dashboard

- Open `http://localhost:8000/`
- Confirm the **closed-loop banner** at the top:
  - `Closed-loop mode: ON`
  - `Cloud LLMs: BLOCKED`
  - `Provider: stub`

### 2. Verify Demo Data

- **Creative Assets** (`/ui/creative-assets`): 3 demo variants should be visible.
- **Brand Profiles** (`/ui/brand-profiles`): NovaBank profile.
- **Audience Profiles** (`/ui/audience-profiles`): 3 audience segments.
- Dashboard shows entity counts.

### 3. Create and Run a Test

1. Go to **Test Runs** → **New Test Run**.
2. Select "NovaBank Freelancer Card — Practical Variant" as the creative.
3. Optionally select the NovaBank brand profile.
4. Optionally select one or more audience profiles.
5. Click **Create Test Run**.
6. On the detail page, click **Run Analysis**.
7. Wait for completion (status changes to `completed`).

### 4. View Report

1. On the completed test run page, click **View Report**.
2. Review the scorecard, risks, recommendations, and final recommendation.
3. Use the export links to view:
   - **JSON** — raw structured data.
   - **Markdown** — full text report.
   - **HTML** — styled HTML page.
   - **Client HTML** — client-facing version (hides debug details).
   - **PDF Stub** — placeholder for future PDF export.

### 5. Repeat for Other Variants

Create and run test runs for Variant B (Freedom) and Variant C (Risky).

Variant C should trigger **brand safety flags** due to overclaims like "guarantees full control" and "zero risks."

### 6. A/B Comparison

1. Go to **Compare** (`/ui/compare`).
2. Select two or more completed test runs.
3. Select report mode (Internal or Client-Facing).
4. Click **Compare**.
5. Review:
   - Winner / No Clear Winner.
   - Score deltas per criterion.
   - Variant summaries with strengths and weaknesses.
   - Recommendation.

### 7. Client-Facing Report

1. Open a completed report.
2. Click **Client HTML** export link.
3. Notice the polished language, no debug details, and constructive framing.

## Running with a Local LLM

The demo works in **stub mode** by default (no LLM required). To get more realistic scoring:

### Ollama

```bash
# In .env:
CTA_LLM_PROVIDER=ollama
CTA_LLM_MODEL=llama3.2
CTA_LLM_BASE_URL=http://localhost:11434
```

### LM Studio

```bash
# In .env:
CTA_LLM_PROVIDER=lmstudio
CTA_LLM_MODEL=local-model
CTA_LLM_BASE_URL=http://localhost:1234/v1
```

## Known Limitations

- **In-memory storage** — all data resets when the server restarts (acceptable for demo).
- **Stub mode scoring** — scores are deterministic but not realistic; a real LLM provides more nuanced evaluation.
- **No OCR** — image files are stored but text extraction from images is not implemented.
- **PDF text-only** — scanned PDFs without embedded text are not processed.
- **No video analysis** — video file support is a placeholder.
- **No authentication** — the UI is intended for local demo use only.

## Suggested Next Steps After Demo

- Clarify whether the client needs a real local LLM for pilot (Ollama with Llama 3 is a good default).
- Discuss file formats the client typically uses (text, PDF, images).
- Discuss the expected report structure and whether client-facing format meets requirements.
- Clarify deployment environment (local laptop, agency server, etc.).
- Discuss NDA and data security requirements.
