# Clients, Projects and History

## Client model

| Field | Type | Description |
|-------|------|-------------|
| id | str | UUID |
| name | str | Client name |
| industry | str? | Industry |
| description | str? | Description |
| contact_name | str? | Contact person |
| contact_email | str? | Contact email |
| metadata | dict | Custom metadata |
| created_at | datetime | Creation timestamp |
| updated_at | datetime? | Update timestamp |

## Project model

| Field | Type | Description |
|-------|------|-------------|
| id | str | UUID |
| client_id | str | Parent client |
| name | str | Project name |
| description | str? | Description |
| status | str | draft / active / completed / archived |
| metadata | dict | Custom metadata |
| created_at | datetime | Creation timestamp |
| updated_at | datetime? | Update timestamp |

## API endpoints

```
GET  /clients
POST /clients
GET  /clients/{client_id}
GET  /clients/{client_id}/projects

GET  /projects
POST /projects
GET  /projects/{project_id}
GET  /projects/{project_id}/history
```

## Project history

`GET /projects/{project_id}/history` returns a timeline of:

- Creative assets linked to the project
- Test runs
- Reports
- Audit events

## Linking existing entities to project

All existing entities now have an optional `project_id` field:

- Creative assets
- Brand profiles
- Audience profiles
- Test rubrics
- Test runs
- Reports

When `project_id` is not provided, everything works as before (backward compatible).

## Demo mode

Demo mode works without a project_id — no changes to the existing demo flow.

## Future UI plan

- Project selector in dashboard
- Client workspace view
- Timeline visualization
- Project-level filtering across all entities
