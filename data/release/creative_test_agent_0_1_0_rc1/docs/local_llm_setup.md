# Local LLM Setup Guide

## Overview

Creative Test Agent supports three LLM providers:

| Provider | Type | Default |
|----------|------|---------|
| `stub` | Deterministic fake output (no runtime needed) | **Default** |
| `ollama` | Local runtime via Ollama | Optional |
| `lmstudio` | Local runtime via LM Studio | Optional |

The stub provider is always the default to ensure tests and basic functionality work without installing any model runtime.

---

## Using the Stub Provider (default)

No configuration needed.

```env
CTA_LLM_PROVIDER=stub
```

The stub returns deterministic placeholder responses and does not require any running service.

---

## Configuring Ollama

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull a model

```bash
ollama pull qwen3:8b
```

Other recommended models for testing:
- `llama3.2:3b` — smaller, faster
- `mistral:7b` — good balance
- `qwen3:8b` — strong instruct following

### 3. Start Ollama

```bash
ollama serve
```

### 4. Configure the agent

```env
CTA_LLM_PROVIDER=ollama
CTA_LLM_MODEL=qwen3:8b
CTA_LLM_BASE_URL=http://localhost:11434
CTA_LLM_TIMEOUT_SECONDS=60
CTA_LOCAL_ONLY_MODE=true
CTA_ALLOW_CLOUD_LLM=false
```

### 5. Verify

```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response listing available models.

---

## Configuring LM Studio

### 1. Install LM Studio

Download from [lmstudio.ai](https://lmstudio.ai/).

### 2. Load a model

Open LM Studio, search for a model (e.g., `llama-3.2-3b-instruct`), download it, and load it.

### 3. Start the local API server

In LM Studio, click **"Start Server"** (typically on port `1234`).

### 4. Configure the agent

```env
CTA_LLM_PROVIDER=lmstudio
CTA_LLM_MODEL=local-model
CTA_LLM_BASE_URL=http://localhost:1234/v1
CTA_LLM_TIMEOUT_SECONDS=60
CTA_LOCAL_ONLY_MODE=true
CTA_ALLOW_CLOUD_LLM=false
```

The `model` field should match the model name shown in LM Studio (often `local-model` by default).

### 5. Verify

```bash
curl http://localhost:1234/v1/models
```

You should see a JSON response listing the loaded model.

---

## How It Works

### Provider selection

When a test run is executed, the `get_llm_provider()` factory selects the appropriate provider based on `CTA_LLM_PROVIDER`.

The closed-loop policy (`validate_llm_provider()`) is called before provider instantiation. Cloud providers like OpenAI, Anthropic, Gemini, and Perplexity are forbidden when `CTA_LOCAL_ONLY_MODE=true`.

### Health endpoint

`GET /llm/health` returns the current provider's status:

```json
{
  "provider": "ollama",
  "model": "qwen3:8b",
  "base_url": "http://localhost:11434",
  "available": true,
  "local_only_mode": true
}
```

For the stub provider, `available` is always `true`. For Ollama and LM Studio, `available` reflects whether the runtime is reachable.

---

## Running Optional Smoke Tests

To run tests that require a real local LLM runtime:

```bash
CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true python -m pytest tests/test_ollama_adapter_optional.py -v
CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true python -m pytest tests/test_lmstudio_adapter_optional.py -v
```

Without this environment variable, these tests are skipped:

```bash
python -m pytest tests/ -v
# ... test_ollama_adapter_optional.py skipped
# ... test_lmstudio_adapter_optional.py skipped
```

---

## Troubleshooting

### "Cannot connect to Ollama"

- Verify Ollama is running: `ollama serve`
- Check the base URL: `CTA_LLM_BASE_URL` should be `http://localhost:11434`
- Ensure no firewall is blocking the port

### "Cannot connect to LM Studio"

- Verify LM Studio's server is started (click "Start Server")
- Check the base URL: `CTA_LLM_BASE_URL` should be `http://localhost:1234/v1`
- The path `/v1` is required for LM Studio's OpenAI-compatible API

### Model not pulled / loaded

- Ollama: run `ollama pull <model-name>` before using
- LM Studio: download and load the model in the UI

### Timeout

- Increase `CTA_LLM_TIMEOUT_SECONDS` for slower machines
- Ensure the model fits in available RAM/VRAM

### Cloud LLM forbidden

If you see `code: "cloud_llm_forbidden"`:
- You tried to use a cloud provider (`openai`, `anthropic`, `gemini`, `perplexity`)
- Set `CTA_LOCAL_ONLY_MODE=false` and `CTA_ALLOW_CLOUD_LLM=true` only if you explicitly need cloud access

---

## Closed-Loop Reminder

Even with Ollama or LM Studio, all processing stays local:

- Model runs on your machine
- Creative assets are never uploaded to external servers
- Prompts and outputs stay in local memory and storage
- No data leaves your network

This is enforced by the closed-loop security policy in `src/shared/llm/policy.py`.
