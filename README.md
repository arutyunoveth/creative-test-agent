# Creative Test Agent

Local-first backend for pre-testing marketing creatives before presenting ideas to clients.

## Core Principle

**Closed-loop processing.** All data stays local. Cloud LLM providers are disabled by default. No creative assets, brand data, or test results leave your machine unless explicitly configured.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```

Open http://localhost:8000/ for the local web UI or http://localhost:8000/docs for the interactive API docs.

## Environment Variables

All settings are prefixed with `CTA_`. Copy `.env.example` to `.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_DEBUG` | `false` | Enable debug logging |
| `CTA_DATABASE_URL` | `sqlite:///./creative_test_agent.db` | Database connection string |
| `CTA_LOCAL_ONLY_MODE` | `true` | Enforce local-only processing |
| `CTA_ALLOW_CLOUD_LLM` | `false` | Allow cloud LLM providers |
| `CTA_LLM_PROVIDER` | `stub` | LLM provider (stub, ollama, lmstudio) |
| `CTA_LLM_MODEL` | — | Model name for local LLM provider |
| `CTA_LLM_BASE_URL` | — | Base URL for local LLM provider |
| `CTA_LLM_TIMEOUT_SECONDS` | `60` | Timeout for LLM requests |
| `CTA_STORAGE_ROOT` | `./data/storage` | Local file storage root |
| `CTA_MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload file size in MB |
| `CTA_ALLOWED_UPLOAD_TYPES` | `txt,md,pdf,png,jpg,jpeg,webp` | Comma-separated allowed upload extensions |
| `CTA_RUN_LOCAL_LLM_SMOKE_TESTS` | `false` | Run optional local LLM smoke tests |

## Demo / Pilot Package

The project includes a ready-to-use demo package for client presentations:

```bash
# Start the server
uvicorn src.main:app --reload

# In a second terminal, seed demo data (NovaBank freelancer card scenario)
python scripts/seed_demo_data.py

# Open http://localhost:8000/
```

The demo includes:
- **NovaBank** brand profile (fictional)
- **3 audience segments** (Beginner Freelancer, Experienced Self-Employed, Skeptical Small Business Owner)
- **3 creative variants** (Practical, Freedom, and a Risky variant for brand safety demo)
- **Default rubric** with 8 criteria
- **Client-facing summary** in Russian

See [docs/demo_pilot.md](docs/demo_pilot.md), [docs/client_pitch_summary.md](docs/client_pitch_summary.md), and [docs/pilot_checklist.md](docs/pilot_checklist.md) for full details.

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/agents` | GET | List agent roles |
| `/agents/register` | POST | Register a new agent role |
| `/creative-assets` | GET/POST | Manage creative materials |
| `/creative-assets/upload` | POST | Upload a creative file (txt, md, pdf, png, jpg, webp) |
| `/brand-profiles` | GET/POST | Manage brand profiles |
| `/audience-profiles` | GET/POST | Manage audience profiles |
| `/test-rubrics` | GET/POST | Manage scoring rubrics |
| `/test-runs` | POST | Create a test run |
| `/test-runs/{id}` | GET | Get test run details |
| `/test-runs/{id}/run` | POST | Execute a test run |
| `/reports/{test_run_id}` | GET | Generate report (supports `?format=` and `?mode=`) |
| `/reports/compare` | POST | A/B comparison of completed test runs |
| `/audit-log` | GET | View audit trail |
| `/llm/health` | GET | LLM provider health check |

## Architecture

See [docs/architecture.md](docs/architecture.md), [docs/closed_loop_requirements.md](docs/closed_loop_requirements.md), [docs/mvp_scope.md](docs/mvp_scope.md), [docs/local_llm_setup.md](docs/local_llm_setup.md), [docs/file_intake.md](docs/file_intake.md), [docs/reporting.md](docs/reporting.md), [docs/local_web_ui.md](docs/local_web_ui.md), [docs/demo_pilot.md](docs/demo_pilot.md), [docs/client_pitch_summary.md](docs/client_pitch_summary.md), and [docs/pilot_checklist.md](docs/pilot_checklist.md) for detailed documentation.
