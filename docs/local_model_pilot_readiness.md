# Local Model Pilot Readiness

This document summarises the steps required to run the Creative Test Agent with local models in a pilot setting.

## Prerequisites

- Ollama or LM Studio running locally
- A model profile configured pointing to the local provider

## Configuration

Set environment variables for local-only operation:

```bash
export CTA_LLM_PROVIDER=ollama
export CTA_VISION_PROVIDER=stub
export CTA_LOCAL_ONLY_MODE=true
export CTA_ALLOW_CLOUD_LLM=false
export CTA_ENABLE_AUTH=false
```

## Setup Steps

1. **Install local model** — pull a model via Ollama, e.g. `ollama pull qwen2.5:7b`
2. **Create model profile** — via UI at `/ui/model-profiles/new` or API
3. **Verify health** — `POST /model-profiles/{id}/health` should report reachable
4. **Register prompts** — `make register-prompts` (or `python scripts/register_prompts.py`)
5. **Run evaluation** — `make eval-stub` to verify the evaluation harness works

### Using the local model diagnostic script

```bash
make check-local-model                          # uses ollama-local profile
python scripts/check_local_model.py --profile ollama-local
python scripts/check_local_model.py --profile lmstudio-local --smoke
```

The diagnostic script checks profile existence, provider allowlist, URL locality,
health check, simple prompt output, and structured JSON prompt parseability.

### If using a real local model

```bash
make eval-local   # smoke test with ollama-local profile (2 cases)
```

For full local-model evaluation, the `run_evaluation.py` script accepts `--profile ollama-local`. The evaluation will use the configured model profile to run the stub pipeline with real inference (future enhancement).

## Verification

```bash
make pilot-check          # closed-loop + demo readiness + model profile checks
make client-pilot-check   # client pack build
make check-server         # full server readiness check including profiles and evals
```

## Trace Diagnostics

Prompt traces are automatically created for every LLM stage call. Use the
trace UI at `/ui/prompt-traces` to inspect:

- Stage, provider, model
- JSON parse success/failure
- Repair attempts and steps
- Validation warnings and errors
- Latency

See [prompt_tracing.md](prompt_tracing.md) and [json_recovery.md](json_recovery.md).

## Known Limitations

- The stub pipeline is deterministic and does not use a model even when a local profile is selected
- Full local model inference during evaluation requires the real pipeline integration (planned for Sprint 18+)
- Health check only verifies HTTP reachability, not model availability
- Prompt registry stores hashes and versions but the active version is not yet wired into the test run pipeline
