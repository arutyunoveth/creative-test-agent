# Evaluation Harness

The evaluation harness runs predefined test cases through the creative test pipeline and checks the output against expected assertions.

## Eval Cases

Cases live in `data/eval_cases/` as JSON files. Each file contains:

- `case_id` — unique identifier
- `title` — human-readable name
- `creative_text` — the ad copy to evaluate
- `brand_context` — brand profile context
- `expected` — assertion rules:
  - `must_detect_risk` — true if the case should trigger risk detection
  - `must_detect_brandbook_violation` — true if the case should trigger a compliance violation
  - `min_risk_severity` — minimum severity expected (`low`, `medium`, `high`)
  - `required_report_sections` — list of sections the output should contain
  - `forbidden_client_facing_terms` — terms that must not appear in output

### Included Cases

| Case | Description | Expected |
|------|-------------|----------|
| `novabank_variant_a` | Clean NovaBank copy | No risks, no violations |
| `novabank_variant_b` | Alternative clean copy | No risks, no violations |
| `novabank_variant_c_risky` | Overclaiming copy | Risks detected, severity at least medium |
| `brandbook_claim_policy_violation` | Guaranteed income / zero risk | Risk + brandbook violation, severity high |
| `tone_of_voice_mismatch` | Aggressive CAPS copy | Risk detected, severity at least medium |

## Scoring

- Each case starts at 100
- -25 per assertion failure
- Overall score = percentage of checks passed

## Running Evaluations

### CLI

```bash
# Default stub evaluation
python scripts/run_evaluation.py --profile stub

# Smoke test (2 cases)
python scripts/run_evaluation.py --profile ollama-local --smoke
```

### Makefile

```bash
make eval-stub     # runs all cases with stub provider
make eval-local    # smoke test with ollama-local profile
```

### API

```bash
curl -X POST http://localhost:8000/evaluations/run \
  -H "Content-Type: application/json" \
  -d '{"profile_id": null, "case_ids": null, "mode": "stub"}'
```

### UI

Navigate to `/ui/evaluations` to view past runs or start a new evaluation.

## Stub Pipeline

The stub runner (`src/modules/evaluations/runner.py`) simulates:

- Risk detection (guaranteed, zero risk, BUY NOW, CRAZY, etc.)
- Brandbook compliance check (guaranteed income, zero risk, etc.)
- Report section presence verification
- Forbidden term scanning

Results are stored in `evaluation_run` and `evaluation_case_result` tables.

## Trace Metrics

Evaluation summaries now include reliability trace metrics:

```json
{
  "trace_count": 5,
  "repair_count": 0,
  "fallback_count": 0,
  "validation_error_count": 0
}
```

- `trace_count`: number of prompt traces created
- `repair_count`: how many JSON repairs were attempted
- `fallback_count`: how many stage fallbacks were used
- `validation_error_count`: schema validation failures

Thresholds (`CTA_EVAL_MAX_REPAIR_COUNT`, `CTA_EVAL_MAX_FALLBACK_COUNT`) are
defined in settings. See [prompt_tracing.md](prompt_tracing.md) and
[json_recovery.md](json_recovery.md) for details on trace diagnostics and
JSON repair.

## Adding a New Case

1. Create `<case_id>.json` in `data/eval_cases/`
2. Define creative text, brand context, and expected assertions
3. Run evaluation to verify
