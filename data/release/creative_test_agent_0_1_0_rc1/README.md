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

## Report Exports

Reports can be exported to real document files — all generated locally:

| Format | Endpoint | Description |
|--------|----------|-------------|
| DOCX | `POST /exports/report/{id}/docx` | Word document with tables, styling, full content |
| PPTX | `POST /exports/report/{id}/pptx` | PowerPoint presentation (7-10 slides) |
| PDF-ready | `POST /exports/report/{id}/pdf` | Print-ready HTML for browser "Save as PDF" |
| DOCX comparison | `POST /exports/comparison/docx` | Comparison report as Word document |
| PPTX comparison | `POST /exports/comparison/pptx` | Comparison report as presentation |

Download via `GET /exports/{job_id}/download`. See [docs/advanced_report_exports.md](docs/advanced_report_exports.md).

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
| `CTA_VISION_PROVIDER` | `stub` | Vision provider (stub, local_ocr, local_vlm, hybrid) |
| `CTA_ENABLE_LOCAL_OCR` | `false` | Enable local OCR (Tesseract) |
| `CTA_ENABLE_LOCAL_VLM` | `false` | Enable local VLM (Ollama) |
| `CTA_VISION_MODEL` | — | Model name for local VLM |
| `CTA_VISION_BASE_URL` | — | Base URL for local VLM |
| `CTA_VISION_TIMEOUT_SECONDS` | `60` | Timeout for vision requests |
| `CTA_ENABLE_KNOWLEDGE_AUTO_INGEST` | `true` | Auto-ingest brandbooks to knowledge base |
| `CTA_KB_CHUNK_SIZE_CHARS` | `1200` | Chunk size for brandbook ingestion |
| `CTA_KB_CHUNK_OVERLAP_CHARS` | `150` | Overlap between brandbook chunks |
| `CTA_KB_CONTEXT_MAX_ITEMS` | `8` | Max knowledge items for context builder |
| `CTA_KB_CONTEXT_MAX_CHARS` | `6000` | Max chars for context builder |
| `CTA_EXPORTS_ROOT` | `./data/exports` | Directory for generated export files |

## Persistence

Data is stored in a local SQLite database by default. See [docs/persistence.md](docs/persistence.md) for full documentation.

### Commands

```bash
# Check database health
curl http://localhost:8000/health/db

# Seed demo data
python scripts/seed_demo_data.py

# Reset demo data (keeps user data)
python scripts/reset_demo_data.py

# Export all pilot data to JSON
python scripts/export_pilot_data.py
```

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

## Pilot QA

Acceptance tests, closed-loop verification, and demo readiness checks. See [docs/pilot_qa.md](docs/pilot_qa.md) for full documentation.

```bash
# Full pilot check
make pilot-check

# Or step by step
python -m pytest tests/ -v
python scripts/check_closed_loop.py
python scripts/check_demo_readiness.py
```

## Client Pilot Pack

The client pilot pack bundles documentation, configuration profiles, and scripts for client delivery:

```bash
# Build the client pilot pack (directory + ZIP)
make build-client-pack

# Quick validation
make client-pilot-check
```

The pack includes:
- **7 Russian docs**: scope, security statement, technical overview, onboarding questions, success criteria, commercial outline, pilot profile format
- **Pilot profiles**: NovaBank demo profile (`novabank_demo.json`) and client template (`client_pilot_template.json`)
- **Scripts**: `load_pilot_profile.py`, `seed_demo_data.py`, `check_closed_loop.py`, `check_demo_readiness.py`, `export_pilot_data.py`
- **Makefile** with pilot commands

Load a pilot profile into the database:

```bash
python scripts/load_pilot_profile.py config/pilot_profiles/novabank_demo.json
```

The loader is idempotent — running it multiple times creates no duplicates.

See [docs/client_pilot/](docs/client_pilot/) for the full documentation pack.

## Server Deployment Foundation

Deployment foundation for server-ready pilot setup. See [docs/deployment/](docs/deployment/) for full documentation.

```bash
# Server readiness check
make check-server

# Docker
make docker-build
make docker-up
make docker-down
make docker-logs
```

Key env vars:
- `CTA_ENV` — environment name (`local`, `production`)
- `CTA_HOST` / `CTA_PORT` — bind address
- `CTA_ENABLE_AUTH` — enable authentication (default: false)
- `CTA_ENABLE_PROJECTS` — enable clients/projects (default: false)
- `CTA_ENABLE_BRANDBOOKS` — enable brandbook upload (default: false)
- `CTA_ENABLE_ADVANCED_EXPORTS` — enable advanced export jobs (default: false)

## Authentication and Roles

Authentication and role-based access control. See [docs/auth_roles.md](docs/auth_roles.md) for full documentation.

**Auth disabled by default** (`CTA_ENABLE_AUTH=false`):
- All API and UI work without login.
- `GET /auth/me` returns a system user stub.
- All write endpoints are accessible.

**Auth enabled** (`CTA_ENABLE_AUTH=true`):
- Login via `POST /auth/login` returns a signed session cookie.
- Roles: `admin`, `manager`, `analyst`, `viewer`.
- Write protection middleware blocks POST/PUT/PATCH/DELETE for viewers.
- User management API (`/users`) only accessible by admins.
- Bootstrap admin: `python scripts/bootstrap_admin.py`.
- Session cookies are `httponly`, signed with `CTA_SECRET_KEY`.

```bash
# Bootstrap admin (run once)
CTA_ENABLE_AUTH=true \
CTA_SECRET_KEY=your-secret \
CTA_BOOTSTRAP_ADMIN_EMAIL=admin@example.com \
CTA_BOOTSTRAP_ADMIN_PASSWORD=your-strong-password \
python scripts/bootstrap_admin.py
```

Limitations: no OAuth/SSO, no password reset, no MFA, no server-side sessions.

## Clients and Projects

Client and project management backend API. See [docs/clients_projects_history.md](docs/clients_projects_history.md) for full documentation.

```text
GET  /clients
POST /clients
GET  /clients/{client_id}
GET  /clients/{client_id}/projects
GET  /projects
POST /projects
GET  /projects/{project_id}
GET  /projects/{project_id}/history
```

Existing entities now support optional `project_id` (backward compatible).

## Brandbooks and Knowledge Base

Brandbook upload and local knowledge storage. See [docs/brandbooks_knowledge_base.md](docs/brandbooks_knowledge_base.md) for full documentation.

```text
POST /brandbooks/upload  (txt, md, pdf)
GET  /brandbooks
GET  /brandbooks/{brandbook_id}
POST /knowledge-base
GET  /knowledge-base
GET  /knowledge-base/{item_id}
```

No embeddings/RAG in this sprint — structured local storage only.

## Model Profiles

Model profiles define local LLM provider connections. See [docs/model_profiles.md](docs/model_profiles.md) for full documentation.

```text
GET  /model-profiles
POST /model-profiles
GET  /model-profiles/{id}
POST /model-profiles/{id}/health
POST /model-profiles/load-from-config
```

```bash
# Load stub profile from config
make register-prompts    # register prompt versions
make eval-stub           # run evaluation with stub provider
```

## Prompt Registry

Prompt templates are versioned with SHA-256 hashing. See `scripts/register_prompts.py`.

```bash
python scripts/register_prompts.py
```

## Evaluation Harness

Run test cases against the pipeline to verify quality. See [docs/evaluation_harness.md](docs/evaluation_harness.md) and [docs/local_model_pilot_readiness.md](docs/local_model_pilot_readiness.md).

```bash
make eval-stub    # run all cases with stub
make eval-local   # smoke test with ollama-local
```

## Advanced Exports

Export job foundation with DOCX/PPTX stubs. See [docs/advanced_exports.md](docs/advanced_exports.md) for full documentation.

```text
GET  /exports
GET  /exports/{job_id}
POST /exports/report/{report_id}/docx_stub
POST /exports/report/{report_id}/pptx_stub
```

DOCX/PPTX stubs create placeholder text files. Real generation will replace stubs in a future sprint.

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/health/db` | GET | Database health check |
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
| `/users/me` | GET | Current user info |
| `/clients` | GET/POST | Manage clients |
| `/clients/{id}/projects` | GET | Client projects |
| `/projects` | GET/POST | Manage projects |
| `/projects/{id}/history` | GET | Project timeline |
| `/brandbooks/upload` | POST | Upload brandbook file |
| `/brandbooks` | GET | List brandbooks |
| `/knowledge-base` | GET/POST | Manage knowledge items |
| `/exports` | GET | List export jobs |
| `/exports/report/{id}/docx_stub` | POST | DOCX stub export |
| `/exports/report/{id}/pptx_stub` | POST | PPTX stub export |
| `/model-profiles` | GET/POST | Manage model profiles |
| `/model-profiles/{id}/health` | POST | Check profile reachability |
| `/model-profiles/load-from-config` | POST | Load profiles from config files |
| `/prompt-registry` | GET | List prompt versions |
| `/prompt-registry/active/{stage_name}` | GET | Get active prompt for stage |
| `/evaluations/run` | POST | Run evaluation |
| `/evaluations` | GET | List evaluation runs |
| `/evaluations/{id}` | GET | Evaluation run detail |
| `/evaluations/{id}/results` | GET | Evaluation case results |
| `/llm/health` | GET | LLM provider health check |
| `/vision/health` | GET | Vision provider health check |

## Server Deployment & Operations

The application can be deployed for pilot operations using Docker Compose or directly on a server.

```bash
# Copy server env profile
cp .env.server.example .env.server

# Build and start via Docker
make server-build
make server-up

# Bootstrap admin user
make server-bootstrap-admin

# Verify server readiness
make server-check

# Backup data
make server-backup
```

See deployment documentation for full details:

- [Server Deployment Guide (RU)](docs/deployment/server_deployment_guide_ru.md)
- [Docker Server Profile](docs/deployment/docker_server_profile.md)
- [Backup & Restore (RU)](docs/deployment/backup_restore_ru.md)
- [Maintenance (RU)](docs/deployment/maintenance_ru.md)
- [Environment Reference](docs/deployment/env_reference.md)
- [Docker Setup](docs/deployment/docker_setup.md)

## Vision Analysis

Local-first visual analysis for image assets — no cloud OCR or vision APIs required. See [docs/local_vision_setup.md](docs/local_vision_setup.md) for full documentation.

Key capabilities:

- Default stub mode (`CTA_VISION_PROVIDER=stub`) — zero dependencies.
- Optional local OCR via Tesseract (`CTA_VISION_PROVIDER=local_ocr`).
- Optional local VLM via Ollama (`CTA_VISION_PROVIDER=local_vlm`).
- Combined hybrid mode (`CTA_VISION_PROVIDER=hybrid`).
- Visual context integrated into test run workflows and reports.
- Image preview endpoint with path traversal protection.
- Dedicated `/vision/health` endpoint.
- Full closed-loop policy — cloud vision providers forbidden.

## Architecture

See [docs/architecture.md](docs/architecture.md), [docs/closed_loop_requirements.md](docs/closed_loop_requirements.md), [docs/mvp_scope.md](docs/mvp_scope.md), [docs/local_llm_setup.md](docs/local_llm_setup.md), [docs/local_vision_setup.md](docs/local_vision_setup.md), [docs/file_intake.md](docs/file_intake.md), [docs/reporting.md](docs/reporting.md), [docs/local_web_ui.md](docs/local_web_ui.md), [docs/demo_pilot.md](docs/demo_pilot.md), [docs/client_pitch_summary.md](docs/client_pitch_summary.md), [docs/pilot_checklist.md](docs/pilot_checklist.md), and [docs/persistence.md](docs/persistence.md) for detailed documentation.

## Documentation

- [Product Overview (RU)](docs/product_overview_ru.md)
- [Operator Guide (RU)](docs/operator_guide_ru.md)
- [Final Pilot Checklist (RU)](docs/final_pilot_checklist_ru.md)
- [Guided Demo Flow (RU)](docs/client_pilot/guided_demo_flow_ru.md)

See `docs/` for full documentation catalog.
