# Human Feedback Loop — Learning from Reviews

The system can automatically save review feedback to the knowledge base, creating a closed feedback loop where human input enriches the context used by future test runs.

## How It Works

1. A reviewer creates or updates a review with feedback (`summary`, `strengths`, `concerns`, `revision_requests`)
2. `POST /reviews/{review_id}/save-to-knowledge` creates a `KnowledgeItem` with:
   - `source_type = "client_feedback"`
   - `source_id = <review_id>`
   - `tags` including `review`, the current status, and decision
3. The knowledge item is then available for context retrieval during future test runs

## Auto-Learning Setting

`CTA_ENABLE_REVIEW_AUTO_LEARNING` (default: `true`) controls whether `save-to-knowledge` is allowed. When disabled, the endpoint returns `{"saved": false, "reason": "Auto-learning is disabled"}`.

To disable:
```bash
export CTA_ENABLE_REVIEW_AUTO_LEARNING=false
```

## Creating a New Version from Review Feedback

After a review is completed, a new version of the creative asset can be created that incorporates the feedback:

```bash
curl -X POST /creative-assets/{asset_id}/create-version \
  -H "Content-Type: application/json" \
  -d '{
    "revision_source": "client_feedback",
    "revision_summary": "Addressed concerns from review {review_id}"
  }'
```

## Feedback → Knowledge → Better Testing

The full loop:
1. Asset is tested → report generated
2. Review created from report recommendations
3. Review feedback saved to knowledge base
4. Future test runs retrieve the feedback as context
5. Asset revised → new version → retested
