# Project Workspaces

**Sprint 15 — Real Pilot Operations**

Project workspaces provide an organizational structure for real pilot operations: clients own projects, and each project acts as a workspace that scopes brand profiles, audiences, creative assets, brandbooks, knowledge, test runs, reports, and exports.

## Architecture

```
Client (NovaBank Corp)
  └── Project (Freelancer Card Campaign 2026)
        ├── Creative Assets
        ├── Brand Profile
        ├── Audience Profiles
        ├── Brandbooks
        ├── Knowledge Items
        ├── Test Runs
        ├── Reports
        └── Exports
```

## Key Concepts

- **Clients**: Top-level organizational entity. Contains metadata (industry, contact info).
- **Projects**: Belong to a client. Each project is a workspace with a status (draft/active/completed/archived).
- **Project-scoped entities**: Creative assets, brand profiles, audience profiles, brandbooks, knowledge items, test runs, reports, and exports all have an optional `project_id` field.

## UI Routes

| Route | Description |
|-------|-------------|
| `GET /ui/clients` | List all clients |
| `GET /ui/clients/new` | Create a new client |
| `GET /ui/clients/{id}` | Client detail with project list |
| `GET /ui/projects` | List all projects |
| `GET /ui/projects/new` | Create a new project |
| `GET /ui/projects/{id}` | Project workspace dashboard |
| `GET /ui/projects/{id}/test-runs/new` | Project-scoped test run form |
| `GET /ui/projects/{id}/compare` | Project-scoped comparison |
| `GET /ui/projects/{id}/reports` | Project reports list |
| `GET /ui/projects/{id}/exports` | Project exports list |
| `GET /ui/clients/{client_id}/projects/new` | Create project for specific client |

## Project Workspace Dashboard

The project detail page (`GET /ui/projects/{id}`) is the central workspace with:
- Counts of all scoped entities
- Quick-action links to create new entities pre-scoped to the project
- Project history timeline

## Project History

The `/projects/{id}/history` endpoint aggregates activity from:
- Creative assets created within the project
- Test runs linked to the project
- Reports generated from project-scoped runs
- Audit events related to the project

## Configuration

Set `CTA_ENABLE_PROJECTS=true` (not yet implemented, planned) to control visibility of project features.

## Auth Roles

| Role | Clients/Projects |
|------|-----------------|
| Viewer | View only |
| Analyst | View + create creative assets, test runs, brandbooks, knowledge notes |
| Manager | View + create clients, projects, manage workflow |
| Admin | Full access |

## Demo Profile

The `novabank_demo.json` profile now includes a `client` and `project` section. Running `load_pilot_profile.py` creates:
1. NovaBank Corp client
2. Freelancer Card Campaign 2026 project
3. Brand profile, audience profiles, rubric, creative assets (as before)

## Test Coverage

- `test_clients_projects_ui.py` — UI pages for clients/projects, form submissions, project detail dashboard
- `test_projects_history.py` — Project history timeline
- `test_project_scoped_forms.py` — Creating entities with project_id
- Additional tests in `test_clients_projects_api.py` (existing)
