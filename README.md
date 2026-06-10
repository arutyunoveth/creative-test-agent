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

Open http://localhost:8000/docs for the interactive API docs.

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
| `CTA_RUN_LOCAL_LLM_SMOKE_TESTS` | `false` | Run optional local LLM smoke tests |

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
| `/brand-profiles` | GET/POST | Manage brand profiles |
| `/audience-profiles` | GET/POST | Manage audience profiles |
| `/test-rubrics` | GET/POST | Manage scoring rubrics |
| `/test-runs` | POST | Create a test run |
| `/test-runs/{id}` | GET | Get test run details |
| `/test-runs/{id}/run` | POST | Execute a test run |
| `/reports/{test_run_id}` | GET | Generate report from test run |
| `/audit-log` | GET | View audit trail |
| `/llm/health` | GET | LLM provider health check |

## Architecture

See [docs/architecture.md](docs/architecture.md), [docs/closed_loop_requirements.md](docs/closed_loop_requirements.md), [docs/mvp_scope.md](docs/mvp_scope.md), and [docs/local_llm_setup.md](docs/local_llm_setup.md) for detailed documentation.
