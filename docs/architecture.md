# Architecture

## Overview

Creative Test Agent is a local-first backend for pre-testing marketing creatives. It follows a modular backend architecture inspired by the [ai-corporation](https://github.com/arutyunoveth/ai-corporation) repository, but adapted for a completely different domain: marketing creative pre-testing rather than procurement/tender management.

## Modular Layout

```
src/
  main.py                  # FastAPI app entry point
  shared/                  # Cross-cutting concerns
    api/errors.py          # Centralized exception handlers
    config/settings.py     # Pydantic-settings configuration
    db/                    # SQLAlchemy base + session
    errors.py              # AppError base class
    llm/                   # LLM provider abstraction
    security/              # Closed-loop security policy
    storage/               # Local file storage
  modules/                 # Domain modules
    agent_registry/
    creative_assets/
    brand_profiles/
    audience_profiles/
    test_rubrics/
    test_runs/
    report_generator/
    audit_log/
```

## Key Design Decisions

- **Closed-loop by default**: No data leaves the local environment. Cloud LLM providers are forbidden unless explicitly opted in.
- **LLM abstraction**: Providers implement a simple `generate(prompt, metadata) -> dict` interface. The stub provider is the default; Ollama and LM Studio adapters can be added later.
- **In-memory MVP**: Sprint 1 uses in-memory storage to accelerate development. A future migration to SQLAlchemy models is prepared.
- **Audit trail**: Key actions are recorded via the audit_log module for traceability.

## Inspiration from ai-corporation (without copying)

The following architectural patterns were inspired by ai-corporation:

- FastAPI application scaffolding with module-based routers
- `src/modules` + `src/shared` directory separation
- Pydantic-settings with env_prefix for configuration
- Centralized error handling via exception handlers
- Alembic migration setup
- Bounded agent workflow pattern (agent_registry)
- Healthcheck endpoint

The following are explicitly NOT copied:

- Tender/procurement domain entities (tender, supplier, RFQ, TKP, bid, contract, delivery, payment, claim)
- Supplier evaluation workflows
- Procurement-specific state machines

## Future Evolution

1. Replace in-memory stores with SQLAlchemy models + Alembic migrations
2. Add real local LLM providers (Ollama, LM Studio)
3. Extend agent workflows with human review checkpoints
4. Add file parsing for image/video creative formats
