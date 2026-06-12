# Local Web UI

## Overview

The Sprint 5 UI provides a minimal local web interface for the Creative Test Agent. It allows marketing managers and agency team members to complete the full creative pre-testing workflow without using curl or the OpenAPI docs.

## Quickstart

```bash
uvicorn src.main:app --reload --port 8000
```

Then open:

```
http://localhost:8000/
```

## Pages

| Route | Description |
|-------|-------------|
| `GET /` or `GET /ui` | Dashboard with status and recent runs |
| `/ui/creative-assets` | List all creative assets |
| `/ui/creative-assets/new` | Create text or upload file creative |
| `/ui/creative-assets/{id}` | Asset detail with metadata |
| `/ui/brand-profiles` | List brand profiles |
| `/ui/brand-profiles/new` | Create brand profile |
| `/ui/brand-profiles/{id}` | Brand profile detail |
| `/ui/audience-profiles` | List audience profiles |
| `/ui/audience-profiles/new` | Create audience profile |
| `/ui/audience-profiles/{id}` | Audience profile detail |
| `/ui/test-runs` | List test runs |
| `/ui/test-runs/new` | Create test run with asset, brand, audience |
| `/ui/test-runs/{id}` | Test run detail with findings, run button |
| `/ui/test-runs/{id}/run` | Launch analysis |
| `/ui/reports/{run_id}` | View report with export links |
| `/ui/compare` | A/B comparison form |
| `/ui/compare` (POST) | Comparison result |

## Full Demo Flow

1. **Open** `http://localhost:8000/` — see dashboard with local-only status.
2. **Create a brand profile** — `/ui/brand-profiles/new` (optional).
3. **Create an audience profile** — `/ui/audience-profiles/new` (optional).
4. **Create a creative asset** — `/ui/creative-assets/new` (text or file upload).
5. **Create a test run** — `/ui/test-runs/new`, select the asset.
6. **Run analysis** — on the test run detail page, click "Run Analysis".
7. **View report** — after completion, click "View Report".
8. **Export** — use JSON, Markdown, HTML, or client-facing HTML links.
9. **Create a second test run** — repeat steps 4-6 with different content.
10. **Compare** — go to `/ui/compare`, select both runs, see the result.

## Local-Only Status

Every page displays a status banner in the header:

```
Closed-loop mode: ON  ·  Cloud LLMs: BLOCKED  ·  Provider: stub
```

This makes it immediately clear that the system is operating in fully local mode.

## Running with Local LLMs

If you have Ollama or LM Studio configured:

1. Set `CTA_LLM_PROVIDER=ollama` (or `lmstudio`) in `.env`.
2. Configure the model and base URL.
3. Restart the server.
4. The dashboard will show the updated provider and model name.

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests pass with `CTA_LLM_PROVIDER=stub` — no Ollama or LM Studio required.

## Limitations

- **No JavaScript framework** — minimal JS used only for file/text toggle on the new asset page.
- **No authentication** — the UI is intended for local use only.
- **No pagination** — lists show all items (acceptable for local MVP).
- **No CSS framework** — pure hand-written CSS, no external libraries.
- **In-memory data** — all data resets on server restart.
- **PDF export** — only `pdf_stub` is available; real PDF rendering is planned for a future sprint.

## Known Non-Goals

- No production deployment setup.
- No multi-tenant or SaaS logic.
- No user authentication or permissions.
- No real-time updates or WebSocket.
- No mobile-responsive design (desktop-only).
