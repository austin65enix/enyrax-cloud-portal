# Team_AgentOps Agent Run Log Schema Design

Safe metadata schema for human-AI team collaboration records

## Overview

Team_AgentOps Agent Run Log Schema defines the safe metadata model for tracking AI agent work across projects, tickets, outputs, human reviews, and delivery outcomes.

Team_AgentOps Agent Run Log Schema 定義 AI Agent 工作紀錄的安全 metadata 模型，用來追蹤 Agent 在專案、工單、產出、人工審核與交付結果中的貢獻。

This is a schema design, not a DB migration. The first version stores safe metadata only.

* Do not store full prompt.
* Do not store full response.
* Do not store raw session logs.
* Do not store credentials, secrets, or API keys.
* Do not store full home paths.
* Store a safe reference for Agent output instead of raw output content whenever possible.
* Team_AgentOps is for governance and protection, not employee surveillance scoring.

## Schema Goals

* Record who triggered each AI Agent run.
* Record which project, ticket, and task the Agent run belongs to.
* Record start and end times.
* Record status: running / done / failed / review_needed.
* Record output type: commit / doc / test / report / analysis.
* Record output reference.
* Record reviewer and review status.
* Record safe token and cost operational estimates.
* Support dashboard KPI.
* Support Team Scorecard.
* Support AuditOps / ProjectOps / ServiceOps integration.

## Non-goals

This design does not include:

* no DB migration
* no API implementation
* no frontend implementation
* no raw prompt storage
* no raw response storage
* no raw session log storage
* no credential storage
* no automatic employee scoring
* no automatic approval
* no billing-grade cost reporting
* no content-based project inference

## Core Tables

### team_agent_runs

| Field            | Type               | Required | Description                                                     |
| ---------------- | ------------------ | -------: | --------------------------------------------------------------- |
| id               | integer            |      yes | Internal run id                                                 |
| run_uid          | text               |      yes | Stable external-safe id                                         |
| agent_name       | text               |      yes | Codex / Claude Code / Copilot / Internal Agent                  |
| agent_type       | text               |      yes | coding / analysis / document / test / automation                |
| triggered_by     | text               |      yes | Human user id or display name                                   |
| project_id       | integer nullable   |       no | Linked ProjectOps project                                       |
| project_name     | text nullable      |       no | Safe project label                                              |
| ticket_id        | integer nullable   |       no | Linked ServiceOps ticket                                        |
| ticket_label     | text nullable      |       no | Safe ticket label                                               |
| task_title       | text               |      yes | Safe task summary                                               |
| task_type        | text               |      yes | development / test / documentation / investigation / deployment |
| status           | text               |      yes | running / done / failed / review_needed                         |
| started_at       | timestamp          |      yes | Start time                                                      |
| ended_at         | timestamp nullable |       no | End time                                                        |
| duration_seconds | integer nullable   |       no | Computed or supplied duration                                   |
| output_type      | text nullable      |       no | commit / doc / test_report / analysis_report / release_note     |
| output_ref       | text nullable      |       no | Commit hash, PR, doc path, artifact id                          |
| output_summary   | text nullable      |       no | Safe short summary only                                         |
| reviewer         | text nullable      |       no | Human reviewer                                                  |
| review_status    | text               |      yes | pending / approved / rejected / rework / not_required           |
| review_required  | boolean            |      yes | Whether human review is required                                |
| token_estimate   | integer nullable   |       no | Operational estimate only                                       |
| cost_estimate    | numeric nullable   |       no | Optional operational estimate                                   |
| risk_level       | text               |      yes | low / caution / high                                            |
| created_at       | timestamp          |      yes | Record creation time                                            |
| updated_at       | timestamp          |      yes | Last update time                                                |

### team_agent_reviews

| Field        | Type          | Required | Description                |
| ------------ | ------------- | -------: | -------------------------- |
| id           | integer       |      yes | Internal review id         |
| review_uid   | text          |      yes | Stable review id           |
| agent_run_id | integer       |      yes | Linked team_agent_runs id  |
| reviewer     | text          |      yes | Human reviewer             |
| decision     | text          |      yes | approve / reject / rework  |
| comment      | text nullable |       no | Safe review comment        |
| reviewed_at  | timestamp     |      yes | Review timestamp           |
| evidence_ref | text nullable |       no | Safe reference to evidence |
| created_at   | timestamp     |      yes | Record creation time       |

### team_agent_outputs

| Field        | Type          | Required | Description                         |
| ------------ | ------------- | -------: | ----------------------------------- |
| id           | integer       |      yes | Internal output id                  |
| agent_run_id | integer       |      yes | Linked run                          |
| output_type  | text          |      yes | commit / file / doc / test / report |
| output_ref   | text          |      yes | Safe artifact reference             |
| output_title | text nullable |       no | Safe title                          |
| checksum     | text nullable |       no | Optional integrity hash             |
| created_at   | timestamp     |      yes | Record creation time                |

## Allowed Values

### agent_type

* coding
* analysis
* document
* test
* automation
* workflow

### task_type

* development
* test
* documentation
* investigation
* deployment
* review
* release
* backup
* security

### status

* running
* done
* failed
* review_needed
* cancelled

### review_status

* pending
* approved
* rejected
* rework
* not_required

### risk_level

* low
* caution
* high

### output_type

* commit
* pull_request
* doc
* test_report
* analysis_report
* release_note
* backup_report
* screenshot
* artifact

## Safety Boundary

* Store safe metadata only.
* Do not store full prompt.
* Do not store full response.
* Do not store raw session logs.
* Do not store command output.
* Do not store file diff content.
* Do not store credentials, secrets, API keys, tokens, private keys.
* Do not store full home paths.
* Do not infer project / task from unrestricted content.
* Store references to artifacts instead of raw artifact contents.
* Token and cost values are operational estimates, not billing-grade values.
* Team scorecard metrics are governance indicators, not employee surveillance scores.

Team_AgentOps 的資料模型目標是治理與保護，不是監控員工。它只保存必要的安全 metadata，讓 AI 協作能被追蹤、審核與交付。

## Example Run Record

```json
{
  "run_uid": "tagent-run-20260601-001",
  "agent_name": "Codex",
  "agent_type": "coding",
  "triggered_by": "atn",
  "project_id": 21,
  "project_name": "Plan_ServiceOPS API-backed Dashboard",
  "ticket_id": null,
  "ticket_label": null,
  "task_title": "Switch frontend to API fallback",
  "task_type": "development",
  "status": "done",
  "started_at": "2026-06-01T10:00:00+08:00",
  "ended_at": "2026-06-01T10:45:00+08:00",
  "duration_seconds": 2700,
  "output_type": "commit",
  "output_ref": "28d5c29",
  "output_summary": "Updated Plan_ServiceOPS frontend to use API-first dashboard data with demo fallback.",
  "reviewer": "atn",
  "review_status": "approved",
  "review_required": true,
  "token_estimate": 42800,
  "cost_estimate": null,
  "risk_level": "low"
}
```

## Integration Mapping

### AgentOps

* Team_AgentOps may consume safe AgentOps run metadata.
* It must not consume raw prompt / response.
* It may use token estimates, status, model name, and review health.

### ProjectOps

* `project_id` links agent work to project progress.
* Project pages can show human tasks vs agent tasks.
* Agent contribution can become milestone evidence.

### ServiceOps

* `ticket_id` links agent work to service tickets.
* Ticket pages can show whether Agent helped investigation, fix, test, or documentation.
* Ticket closure still requires human review.

### AuditOps

* Review approval, rejection, rework, merge, deploy, and close can be audit events.
* AuditOps stores operation trail, not raw AI content.

## API Concept

This section is a design only. It does not implement any API.

```text
GET /api/team-agentops/runs
GET /api/team-agentops/runs/{run_uid}
GET /api/team-agentops/projects/{project_id}/contribution
GET /api/team-agentops/reviews/pending
GET /api/team-agentops/scorecard
```

The first API version should be read-only.

A future write API for review decisions must:

* enforce role permission
* write AuditOps event
* avoid storing raw AI content
* validate output_ref and review decision

## Dashboard Metrics Mapping

The safe metadata schema supports the existing static prototype KPI:

| Dashboard KPI  | Source                                         |
| -------------- | ---------------------------------------------- |
| Active Agents  | team_agent_runs status running / recent active |
| Pending Review | review_status pending / status review_needed   |
| Project Impact | project-linked completed agent runs            |
| Failed Runs    | status failed                                  |
| Usage Cost     | token_estimate aggregate                       |

## Retention and Privacy

* Agent run metadata may be retained longer than raw operational data.
* Review decisions may be retained as audit evidence.
* Token and cost estimates must be labeled as operational estimates.
* `output_summary` should remain a short summary.
* If `output_ref` points to a sensitive artifact, the source system handles access control.
* Future retention policy should handle metadata, reviews, and artifact references separately.

## Future Implementation Plan

1. Phase 1: Static schema documentation
2. Phase 2: Demo JSON fixture
3. Phase 3: Read-only API prototype
4. Phase 4: UI switch to API with demo fallback
5. Phase 5: Human review write flow
6. Phase 6: AuditOps integration

## Task #167 Handoff

Task #167：Team_AgentOps Demo Data Fixture Design

Scope:

* Create safe demo JSON fixtures for agent runs, reviews, project contribution, and scorecard.
* Do not use raw prompts / responses.
* Do not use real credentials or secrets.
* Keep demo data aligned with `/team-agentops/` static dashboard.

## Task #167 Demo Data Fixture Design

* Task #167 adds safe demo JSON fixtures under `data/team-agentops/`.
* Fixtures include agent runs, reviews, outputs, project contribution, and scorecard.
* Fixtures align with the Team_AgentOps schema concept.
* Fixtures do not contain raw prompts, responses, raw sessions, command output, file diff content, credentials, secrets, API keys, or full home paths.
* Future tasks may use these fixtures for read-only API prototype or frontend demo data source.


## Task #168 Read-only Fixture API Prototype

* Added read-only fixture API endpoints for Team_AgentOps.
* API reads safe demo fixtures from `data/team-agentops/`.
* API exposes dashboard, runs, run detail, pending reviews, project contribution, and scorecard.
* Runs supports exact filtering by `status`, `review_status`, `project_id`, and `agent_name`; it does not perform content search.
* Team_AgentOps fixture API v1 remains read-only: it does not write files, write DB, create audit logs, or mutate AgentOps / ProjectOps / ServiceOps data.
* No DB migration.
* No mutation.
* No frontend switch yet.
* No raw prompt / response / raw session storage.


## Task #169 Frontend API Switch with Fixture Fallback

* `/team-agentops/` now fetches `GET /api/team-agentops/dashboard`.
* API success renders read-only fixture API data.
* API failure falls back to local demo data.
* API mode remains read-only.
* Dashboard does not create, update, approve, reject, or mutate agent records.
* Safety boundary remains safe metadata only.
* No backend, DB, API, fixture, parser, or release changes.

## Task #172 API-backed Dashboard Release Note

* Task #172 packages Tasks #166-#170 as `v0.6.28-team-agentops-api-backed-dashboard`.
* Release covers schema design, demo fixtures, read-only fixture API, frontend API fallback, and screenshot baseline checklist.
* Scope remains fixture-backed, read-only, safe metadata only.
* No backend behavior beyond read-only endpoints, no DB, no mutation, no parser changes, no deployment changes.
* Future work should proceed to release tag and then role-based filtering / review write flow design.
