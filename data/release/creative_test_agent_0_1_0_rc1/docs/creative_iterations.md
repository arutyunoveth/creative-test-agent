# Creative Iterations (Versioning)

The system supports versioning creative assets without mutating originals. Each version is a new `CreativeAsset` row linked to its parent via `parent_asset_id`.

## How Versioning Works

- **Original asset**: has `version_number = None`, `parent_asset_id = None`
- **New version**: created by `POST /creative-assets/{asset_id}/create-version` — copies metadata from the parent, increments `version_number`, creates a new `CreativeAsset` row
- **Version chain**: linked list from root → latest via `parent_asset_id`; `GET /creative-assets/{asset_id}/version-chain` walks the chain to the root

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/creative-assets/{asset_id}/create-version` | Create a new version of an asset |
| `GET` | `/creative-assets/{asset_id}/versions` | List all versions (including original) |
| `GET` | `/creative-assets/{asset_id}/version-chain` | Get version chain from root asset |
| `POST` | `/creative-assets/compare-versions` | Compare two or more versions by their completed test reports |

## Version Fields

| Field | Type | Description |
|---|---|---|
| `parent_asset_id` | `str \| None` | ID of the asset this version was derived from |
| `version_label` | `str \| None` | Human-readable label (e.g. "Final", "v2") |
| `version_number` | `int \| None` | Auto-incremented version number |
| `revision_summary` | `str \| None` | Free-text summary of what changed |
| `revision_source` | `str \| None` | One of: `original`, `manual_revision`, `report_recommendation`, `client_feedback`, `imported` |

## Version Comparison

`POST /creative-assets/compare-versions` accepts `{"asset_ids": ["id1", "id2", ...]}` and returns scorecard, risks, recommendations, and overall scores from each version's completed test run report. If a version has no completed report, `has_report` is `false`.
