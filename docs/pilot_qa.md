# Pilot QA

## Overview

The Pilot QA layer validates that the application is ready for client demonstrations. It covers:

- **Demo acceptance flow** — full NovaBank scenario end-to-end
- **Report quality** — required sections, forbidden internal language in client-facing mode
- **Closed-loop compliance** — no cloud providers, no external APIs, safe defaults
- **Demo readiness** — files, scripts, configuration checks

## Running Acceptance Tests

```bash
python -m pytest tests/test_pilot_demo_acceptance_flow.py -v
python -m pytest tests/test_pilot_report_quality.py -v
python -m pytest tests/test_pilot_closed_loop_acceptance.py -v
```

Or all pilot tests:

```bash
python -m pytest tests/test_pilot_*.py -v
```

## Running Closed-Loop Check

```bash
python scripts/check_closed_loop.py
```

Checks:

1. Forbidden cloud SDK packages (`openai`, `anthropic`, `google-cloud-vision`, etc.) are not installed.
2. Environment variables have safe values (`CTA_LOCAL_ONLY_MODE=true`, `CTA_ALLOW_CLOUD_LLM=false`).
3. `CTA_LLM_PROVIDER` is one of: `stub`, `ollama`, `lmstudio`.
4. `CTA_VISION_PROVIDER` is one of: `stub`, `local_ocr`, `local_vlm`, `hybrid`.
5. HTTP health endpoints (`/health`, `/health/db`, `/llm/health`, `/vision/health`) are reachable (skipped if the app is not running).

Output:

```text
Closed-loop check: PASS
```

or:

```text
Closed-loop check: FAIL
  - google.cloud.vision is not installed
  - CTA_LOCAL_ONLY_MODE=false
```

## Running Demo Readiness Check

```bash
python scripts/check_demo_readiness.py
```

Checks:

1. Database connection works.
2. At least 3 demo creative files exist in `data/demo/`.
3. UI templates are present.
4. Pilot export script is importable.
5. Closed-loop configuration is safe.
6. pytest is available.

Output:

```text
Demo readiness: PASS
```

or:

```text
Demo readiness: FAIL
  - Demo creative directory: not found
```

## Full Pilot Check

```bash
make pilot-check
```

This runs:

1. `pytest` (all tests)
2. `python scripts/check_closed_loop.py`
3. `python scripts/check_demo_readiness.py`

## Understanding PASS/FAIL

| Check | PASS | FAIL |
|-------|------|------|
| All tests | All tests pass | Any test fails |
| Closed-loop | All cloud checks pass, env is safe | Cloud SDK found, env misconfigured |
| Demo readiness | DB works, files exist, scripts importable | DB error, missing files, broken imports |

## Troubleshooting Common Failures

| Failure | Likely Cause | Solution |
|---------|-------------|----------|
| `openai is not installed` | openai package found | Run `pip uninstall openai` |
| `CTA_LOCAL_ONLY_MODE` not set | Missing .env | Copy `.env.example` to `.env` |
| `Demo creative files: 0 found` | Demo data not seeded | Run `python scripts/seed_demo_data.py` |
| `UI template: creative_assets not found` | Missing templates dir | Verify `src/modules/ui/templates/` exists |
| `httpx not available` | httpx not installed for HTTP checks | `pip install httpx` or skip HTTP checks |
| Report section missing | Stub mode issue | Check `pipeline.py` or report renderer |
