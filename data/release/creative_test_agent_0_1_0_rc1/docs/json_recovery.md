# JSON Recovery

Local LLMs often produce malformed JSON. The JSON recovery layer attempts to fix common issues without calling any external service.

## Why JSON Recovery Exists

Real local LLMs (Ollama, LM Studio) frequently:
- Wrap JSON in conversational text
- Add markdown code fences around JSON
- Include trailing commas
- Use single quotes instead of double
- Add text after the JSON block

The stub provider always returns clean JSON, but real models don't.

## Recovery Pipeline

### 1. Direct Parse

First attempt: `json.loads(raw_text)`. If it works, no recovery needed.

### 2. Markdown Fence Removal

If the text starts with ```` ``` ````, the fences and language tag are stripped:
- ````json {"key": "value"}```` → `{"key": "value"}`
- ```` {"key": "value"}```` → `{"key": "value"}`

### 3. Text Trimming

If JSON is embedded in prose, the text before the first `{` and after the last `}` is removed:
- `Here is the result: {"key": "value"} Thanks!` → `{"key": "value"}`

### 4. Trailing Comma Removal

Trailing commas in objects and arrays are removed:
- `{"key": "value",}` → `{"key": "value"}`
- `[1, 2, 3,]` → `[1, 2, 3]`

## What is NOT Repaired

The recovery layer does NOT attempt:
- AI/generative repair (no LLM call)
- Fixing misspelled field names
- Reconstructing missing fields
- Semantic corrections
- Schema-aware recovery (that's the validation layer)

If repair fails, the stage uses its fallback output.

## Repair Result Shape

Successful repair:
```json
{
  "repaired": true,
  "repair_steps": ["removed_markdown_fence", "trimmed_outer_text"],
  "data": {"key": "value"}
}
```

Failed repair:
```json
{
  "repaired": false,
  "error": "json_parse_failed",
  "data": null
}
```

## Integration

The repair is called automatically in `_call_llm_json` when `stage_name` is provided. All 6 pipeline stages pass their stage name, so recovery is always active in live mode.

## Limitations

- Repair is conservative — it will not attempt risky transformations
- Some malformed JSON will remain unrepairable and trigger fallback
- No cloud fallback for JSON repair
- Does not handle deeply nested structural errors
