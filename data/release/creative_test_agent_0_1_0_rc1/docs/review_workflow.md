# Review Workflow

The review module provides a structured human-in-the-loop review process for creative assets, with status transitions, decisions, and optional AI-powered recommendation extraction.

## Review Model

Each review is linked to a `CreativeAsset` and can optionally reference a `Report`. Key fields:

| Field | Type | Description |
|---|---|---|
| `creative_asset_id` | `str` | The asset being reviewed |
| `report_id` | `str \| None` | Source report (if created from a report) |
| `reviewer` | `str` | Name of the reviewer |
| `status` | `str` | Current workflow status |
| `decision` | `str \| None` | Final decision: `approve`, `revise`, `reject`, `needs_discussion` |
| `rating` | `int \| None` | Rating 1–5 |
| `summary`, `strengths`, `concerns`, `revision_requests` | `str \| None` | Free-text feedback |
| `requested_changes` | `list[dict]` | Structured change requests |

## Status Machine

```
draft ──→ in_review ──→ approved
                        → changes_requested ──→ in_review
                        → rejected
                        → archived
    ──→ archived
```

Valid transitions are enforced in the service layer.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/reviews` | Create a new review |
| `GET` | `/reviews` | List reviews (filterable by `creative_asset_id`, `project_id`, `status`) |
| `GET` | `/reviews/{id}` | Get a single review |
| `PATCH` | `/reviews/{id}` | Update status, decision, rating, or feedback fields |
| `POST` | `/reviews/from-report/{report_id}` | Auto-create a review from a report's recommendations |
| `POST` | `/reviews/{id}/save-to-knowledge` | Save review feedback to the knowledge base |

## Creating a Review from a Report

`POST /reviews/from-report/{report_id}` extracts recommendations and risks from the report and pre-fills the review's `concerns`, `revision_requests`, and `requested_changes` fields. This gives reviewers a head start.

## Permissions

When auth is disabled (default demo mode), any user can perform all actions. When auth is enabled:
- **Viewer**: can read reviews
- **Analyst**: can create and update reviews
- **Manager/Admin**: can approve or reject reviews
