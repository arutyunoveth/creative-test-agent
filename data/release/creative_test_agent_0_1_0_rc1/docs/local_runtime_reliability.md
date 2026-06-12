# Local Runtime Reliability

When using real local LLMs (Ollama, LM Studio) instead of the stub provider, the system must handle unreliable outputs gracefully. This document explains the reliability layer.

## The Problem

Local LLMs can:
- return invalid JSON (trailing commas, missing braces)
- wrap JSON in prose or markdown fences
- omit required fields
- return empty responses
- timeout under load

Without protection, these failures would crash the pipeline or produce unusable reports.

## Reliability Stack

Every live LLM stage goes through:

```
raw response
→ JSON extraction (extract JSON from text)
→ JSON repair (fix common issues)
→ schema validation (check required fields)
→ fallback (if validation fails)
→ trace (record diagnostics)
→ stage output
```

### 1. JSON Extraction ([`json_extractor.py`](../src/shared/llm/structured_output/json_extractor.py))

Extracts valid JSON from:
- Raw JSON: `{"key": "value"}`
- Prose-wrapped: `Here is the result: {"key": "value"}`
- Markdown fences: ````json\n{"key": "value"}\n````

Returns `None` if no JSON found — does not raise exceptions.

### 2. JSON Repair ([`json_repair.py`](../src/shared/llm/structured_output/json_repair.py))

Lightweight local repair without calling any LLM:

1. Remove markdown fences
2. Trim text before first `{` and after last `}`
3. Remove trailing commas

Returns repair steps and data, or `repaired: false` with error.

### 3. Schema Validation ([`schema_validator.py`](../src/shared/llm/structured_output/schema_validator.py))

Validates stage output against per-stage schemas:
- Required top-level keys
- Value types (str, list, float, etc.)
- Returns warnings and errors without crashing

### 4. Fallback Policy ([`fallbacks.py`](../src/modules/test_runs/fallbacks.py))

If validation fails, each stage has a safe fallback output with:
- Default values for all fields
- Warning markers in output
- No data loss for other stages

### 5. Prompt Tracing ([`prompt_traces`](../src/modules/prompt_traces/))

Every stage call creates a trace record with:
- extraction success/failure
- repair status
- validation warnings/errors
- latency
- prompt preview (truncated)

Traces are stored in the `prompt_trace` table and viewable at `/ui/prompt-traces`.

## Configuration

```env
CTA_ENABLE_PROMPT_TRACING=true
CTA_PROMPT_TRACE_STORE_FULL=false
CTA_PROMPT_TRACE_PREVIEW_CHARS=2000
CTA_PROMPT_TRACE_MAX_FULL_CHARS=20000
```

Default: tracing enabled, full prompts not stored, preview limited to 2000 chars.

## Limitations

- Repairs are conservative — they fix syntax but not semantics
- Fallbacks are static templates, not AI-generated
- No cloud fallback for JSON repair
- Token counting is estimated, not precise
