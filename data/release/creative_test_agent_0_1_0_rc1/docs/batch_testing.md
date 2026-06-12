# Batch Creative Testing

Batch testing allows you to test multiple creative variants together as a campaign, with a local job queue and aggregated summary.

## Concepts

- **BatchRun**: a campaign-level container for testing multiple creatives together
- **BatchRunItem**: a single creative within a batch, with its own test run and report
- **Summary**: aggregated results across all completed items (scores, risks, compliance, recommendations)
- **Comparison**: A/B comparison of all completed items in a batch

## Workflow

1. Create a batch with creative asset IDs, audience profiles, brand profile, and rubric
2. Queue the batch — this creates job queue entries for each item
3. Run all items synchronously (or run one at a time)
4. View summary — aggregated scores, top risks, best creative
5. Compare variants — uses the existing comparison engine
6. Export — DOCX, PPTX, or PDF-ready HTML

## Local Job Queue

The job queue is a local SQLite-backed queue. It is **not** Celery, Redis, or an external broker.

- Jobs are stored in the `job` table
- `run_next_job()` claims and processes one queued job
- `run_pending_jobs(limit)` processes up to N pending jobs
- Failed jobs can be retried (up to `max_attempts`)
- No background daemon — processing is triggered explicitly

## API Endpoints

### Batches

| Method | Path | Description |
|---|---|---|
| `POST` | `/batches` | Create a new batch |
| `GET` | `/batches` | List batches (filter by `project_id`, `status`) |
| `GET` | `/batches/{id}` | Get batch details |
| `POST` | `/batches/{id}/queue` | Queue batch — creates items and jobs |
| `POST` | `/batches/{id}/run-next` | Run one pending item |
| `POST` | `/batches/{id}/run-all` | Run all items synchronously |
| `POST` | `/batches/{id}/cancel` | Cancel batch |
| `GET` | `/batches/{id}/items` | List batch items |
| `GET` | `/batches/{id}/summary` | Get aggregated summary |
| `POST` | `/batches/{id}/compare` | Compare all completed items |
| `GET` | `/batches/{id}/report?format=json\|markdown\|html` | Campaign summary report |
| `POST` | `/batches/{id}/export/docx` | Export batch report as DOCX |
| `POST` | `/batches/{id}/export/pptx` | Export batch report as PPTX |
| `POST` | `/batches/{id}/export/pdf` | Export batch report as PDF |

### Jobs

| Method | Path | Description |
|---|---|---|
| `POST` | `/jobs` | Enqueue a new job |
| `GET` | `/jobs` | List jobs (filter by `job_type`, `status`) |
| `GET` | `/jobs/{id}` | Get job details |
| `POST` | `/jobs/claim-next` | Claim next queued job |
| `POST` | `/jobs/{id}/complete` | Mark job completed |
| `POST` | `/jobs/{id}/fail` | Mark job failed |
| `POST` | `/jobs/{id}/cancel` | Cancel job |
| `POST` | `/jobs/{id}/retry` | Retry failed job |

## Permissions

When `CTA_ENABLE_AUTH=true`:
- Viewer: view batches and reports
- Analyst: create and run batches
- Manager/Admin: cancel and retry batches

When auth disabled: all actions are permitted.

## Limitations

- `run-all` is synchronous — it processes items one by one in the same request
- No background worker daemon — jobs are processed on demand
- No distributed queue — all jobs live in the same SQLite database
- For large batches (100+ items), consider running multiple `run-all` calls
