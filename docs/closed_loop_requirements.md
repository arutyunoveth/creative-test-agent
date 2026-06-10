# Closed-Loop Requirements

## Principle

All processing MUST happen locally. No creative assets, brand data, audience profiles, or test results may be transmitted to external cloud services unless explicitly configured by the operator.

## Default Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `CTA_LOCAL_ONLY_MODE` | `true` | Enforces local-only processing |
| `CTA_ALLOW_CLOUD_LLM` | `false` | Disables cloud LLM providers |
| `CTA_LLM_PROVIDER` | `stub` | Stub provider that returns deterministic output |

## Provider Policy

| Provider | Local Only Mode | Allowed |
|----------|----------------|---------|
| stub     | -              | Always  |
| ollama   | true           | Yes     |
| lmstudio | true           | Yes     |
| openai   | true           | Forbidden |
| anthropic| true           | Forbidden |
| gemini   | true           | Forbidden |
| perplexity| true          | Forbidden |

When `allow_cloud_llm=True` and `local_only_mode=False`, cloud providers become permitted.

## Enforcement

The `validate_llm_provider()` function in `src/shared/llm/policy.py` is called before any LLM interaction. It raises `AppError(code="cloud_llm_forbidden")` if the current provider violates the policy.

## Local Storage

- Creative assets are stored under `CTA_STORAGE_ROOT` (default `./data/storage`).
- The `LocalStorage` class provides the abstraction for local file I/O.
- No external blob storage is configured in this sprint.

## Audit Trail

Every critical action produces an audit event:

- creative_asset_created
- brand_profile_created
- audience_profile_created
- test_run_created
- test_run_started
- test_run_completed
- report_generated

Audit events are stored in memory for Sprint 1.

## Future Local Providers

### Ollama

To add Ollama support:
1. Create `src/shared/llm/ollama.py` implementing `LLMProvider`
2. Set `CTA_LLM_PROVIDER=ollama` and `CTA_LLM_BASE_URL=http://localhost:11434`
3. Provider will be allowed automatically when `local_only_mode=True`

### LM Studio

To add LM Studio support:
1. Create `src/shared/llm/lmstudio.py` implementing `LLMProvider`
2. Set `CTA_LLM_PROVIDER=lmstudio` and `CTA_LLM_BASE_URL=http://localhost:1234`
3. Provider will be allowed automatically when `local_only_mode=True`
