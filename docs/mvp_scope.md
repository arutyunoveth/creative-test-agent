# Sprint 1 — MVP Scope

## Goal

Create a working FastAPI backend foundation for the Creative Test Agent project.

## In Scope

- FastAPI application with module routers
- Pydantic-settings configuration with `.env` support
- Centralized exception handling
- SQLAlchemy DB foundation (SQLite default, PostgreSQL ready)
- Alembic migration scaffolding
- Closed-loop LLM policy enforcement
- Stub LLM provider
- In-memory domain services for 8 modules:
  - agent_registry
  - creative_assets
  - brand_profiles
  - audience_profiles
  - test_rubrics
  - test_runs
  - report_generator
  - audit_log
- Closed-loop security policy
- Local storage abstraction
- Healthcheck endpoint
- Audit event trail
- Basic test suite (pytest + httpx)
- Documentation

## Explicit Non-Goals

- No frontend (UI will be built in a future sprint)
- No real file parsing (PDF, image, video)
- No real vision model integration
- No cloud LLM providers (OpenAI, Anthropic, Gemini, Perplexity)
- No model fine-tuning
- No production authentication or authorization
- No customer deployment automation (Docker Compose is for development)
- No database persistence (in-memory stores used; SQLAlchemy models exist as scaffolds)
- No real local LLM integration (Ollama, LM Studio; adapter pattern is ready but no implementation)
- No human review workflows (planned for future sprint)
- No async task queues
- No WebSocket support

## Success Criteria

1. `pytest` suite passes with all tests green
2. App imports successfully without cloud dependencies
3. No procurement/tender domain names appear in source code
4. `GET /health` returns correct response
5. Closed-loop policy correctly forbids cloud providers
6. Test run creation → execution → report pipeline works end-to-end
7. README quickstart is accurate and runnable
