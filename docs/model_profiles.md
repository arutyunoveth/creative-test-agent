# Model Profiles

Model profiles define how the system connects to local LLM providers for inference. Each profile stores provider type, model name, base URL, and connection settings.

## Supported Providers

| Provider | Status | Base URL Default |
|----------|--------|-----------------|
| `stub` | Built-in | N/A |
| `ollama` | Local | `http://localhost:11434` |
| `lmstudio` | Local | `http://localhost:1234` |

## Configuration Files

Default profiles ship as JSON in `config/model_profiles/`:

- `stub.json` — enabled, default for demo
- `ollama.example.json` — template for Ollama
- `lmstudio.example.json` — template for LM Studio

### Loading from config

```bash
curl -X POST http://localhost:8000/model-profiles/load-from-config
```

This scans `config/model_profiles/*.json` (skipping `.example.json` files) and creates a DB record for each.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/model-profiles` | List all profiles |
| POST | `/model-profiles` | Create a new profile |
| GET | `/model-profiles/{id}` | Get profile by ID |
| POST | `/model-profiles/{id}/health` | Check provider reachability |
| POST | `/model-profiles/load-from-config` | Load from config files |

## Health Check

`POST /model-profiles/{id}/health` attempts HTTP connection:

- **stub**: always reachable
- **ollama** / **lmstudio**: tries GET on base_url; warns if cloud URLs detected
- **forbidden providers**: returns unreachable with warning

## Provider Policy

- Allowed: `stub`, `ollama`, `lmstudio`
- Forbidden: `openai`, `anthropic`, `gemini`, `perplexity`, `claude`, `azure_openai`

Any attempt to create a profile with a forbidden provider returns a 400 error.

## UI

Navigate to `/ui/model-profiles` to list, create, view details, and check health.
