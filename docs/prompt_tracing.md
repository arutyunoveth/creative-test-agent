# Prompt Tracing

Prompt traces record every LLM call made during test runs and evaluations, storing diagnostic information for debugging local model failures.

## Trace Entity

Each trace contains:

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `test_run_id` | Optional link to test run |
| `evaluation_run_id` | Optional link to evaluation |
| `stage_name` | Pipeline stage (e.g., creative_summary) |
| `provider` | LLM provider (stub, ollama, lmstudio) |
| `model` | Model name |
| `prompt_version_id` | Optional link to registered prompt version |
| `prompt_hash` | SHA-256 of prompt text |
| `prompt_preview` | First N characters (2000 by default) |
| `raw_response_preview` | First N characters of model output |
| `parsed_success` | Whether JSON was successfully parsed |
| `repaired` | Whether JSON repair was applied |
| `repair_steps_json` | List of repair actions taken |
| `validation_warnings_json` | Schema validation warnings |
| `validation_errors_json` | Schema validation errors |
| `latency_ms` | Round-trip time in milliseconds |
| `token_estimate_input` | Estimated input tokens |
| `token_estimate_output` | Estimated output tokens |
| `metadata_json` | Additional metadata |
| `created_at` | Timestamp |

## Privacy

By default, only the first 2000 characters of prompts and responses are stored. Full content is not saved unless explicitly configured:

```env
CTA_PROMPT_TRACE_STORE_FULL=false  # default: save only preview
CTA_PROMPT_TRACE_PREVIEW_CHARS=2000   # preview length
```

Set `CTA_PROMPT_TRACE_STORE_FULL=true` to store full prompts (useful for debugging, but may increase storage use).

No secrets or credentials are stored in traces.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/prompt-traces` | List all traces (with optional `test_run_id` or `evaluation_run_id` filter) |
| GET | `/prompt-traces/{trace_id}` | Get single trace detail |
| GET | `/test-runs/{test_run_id}/prompt-traces` | Traces for a test run |
| GET | `/evaluations/{eval_id}/prompt-traces` | Traces for an evaluation run |

## UI

Navigate to `/ui/prompt-traces` to view all traces.

Each trace shows:
- Stage, provider, model
- Parse success/failure
- Repair status and steps
- Validation warnings/errors
- Prompt and response previews
- Latency

## Using Traces for Debugging

1. Run a test run or evaluation
2. Open `/ui/prompt-traces`
3. Look for traces with `✗ Parsed` or validation errors
4. Inspect the raw response preview to see what the model returned
5. Check if repair was applied and what steps were taken
6. Review latency — high latency may indicate model load issues

## Evaluation Trace Metrics

Evaluation summaries include trace metrics:

```json
{
  "trace_count": 5,
  "repair_count": 0,
  "fallback_count": 0,
  "validation_error_count": 0
}
```

Thresholds:
- `CTA_EVAL_MAX_REPAIR_COUNT=2` — warn if more than 2 repairs
- `CTA_EVAL_MAX_FALLBACK_COUNT=0` — warn if any fallback used

## Configuration Reference

```env
CTA_ENABLE_PROMPT_TRACING=true        # enable/disable tracing
CTA_PROMPT_TRACE_STORE_FULL=false     # store full prompts
CTA_PROMPT_TRACE_PREVIEW_CHARS=2000   # preview truncation
CTA_PROMPT_TRACE_MAX_FULL_CHARS=20000 # max stored if full enabled
```
