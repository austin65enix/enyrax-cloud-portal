# Team_AgentOps Role-based API Filtering Design

Safe visibility rules for human-AI team collaboration records

## Overview

This document defines role-based filtering rules for future Team_AgentOps APIs. The goal is to keep AI agent collaboration records useful for team governance while preventing unnecessary exposure of project, ticket, review, and user-level metadata.

本文件定義 Team_AgentOps 未來 API 的角色分層可視規則。目標是在保留 AI Agent 協作治理價值的同時，避免不必要暴露專案、工單、審核與使用者層級 metadata。

This is a design document, not a backend implementation. The current APIs remain fixture-backed and read-only. Filtering will be applied to future API behavior. The goal is minimum necessary visibility. Team_AgentOps is for governance and protection, not employee surveillance.

## Role Model

| Role       | Purpose                                              |
| ---------- | ---------------------------------------------------- |
| viewer     | Limited read-only overview                           |
| operator   | Personal and assigned-team collaboration visibility |
| supervisor | Team-level review and delivery visibility            |
| admin      | Cross-team governance and configuration visibility   |

| Role       | 中文說明                                                    |
| ---------- | ----------------------------------------------------------- |
| viewer     | 只能看有限摘要與安全總覽                                    |
| operator   | 可看自己啟動或與自己任務相關的 Agent 紀錄                   |
| supervisor | 可看團隊層級的 pending review、failed runs、project contribution |
| admin      | 可看跨團隊治理資料與設定視角                                |

## Visibility Principles

1. Least privilege by default.
2. Safe metadata only.
3. No raw prompt / response exposure.
4. No raw session exposure.
5. No credentials / secrets / full path exposure.
6. Review records are visible only when role needs them.
7. Personal run visibility should not become surveillance.
8. Aggregated metrics are preferred over user-level detail for viewer / supervisor dashboards.
9. Admin access should still avoid raw AI content.
10. All future write flows must also create AuditOps evidence.

Team_AgentOps 的角色分層不是為了監控員工，而是為了讓 AI 協作在企業裡有適當的可視性、審核流程與責任邊界。

## Endpoint Visibility Matrix

| Endpoint                                     | viewer                           | operator                        | supervisor                | admin                           |
| -------------------------------------------- | -------------------------------- | ------------------------------- | ------------------------- | ------------------------------- |
| GET /api/team-agentops/dashboard             | aggregated only                  | personal + team summary         | team summary              | cross-team summary              |
| GET /api/team-agentops/runs                  | limited recent public/demo runs  | own / assigned project runs     | team runs                 | all safe metadata runs          |
| GET /api/team-agentops/runs/{run_uid}        | only visible if public/demo-safe | own / assigned / reviewed runs  | team runs                 | all safe metadata runs          |
| GET /api/team-agentops/reviews/pending       | hidden or count only             | own pending review items        | team pending review list  | all pending reviews             |
| GET /api/team-agentops/projects/contribution | public/demo project summary      | assigned project contribution   | team project contribution | cross-team project contribution |
| GET /api/team-agentops/scorecard             | aggregate only                   | personal/team blended aggregate | team aggregate            | cross-team aggregate            |

* viewer should not see user-level reviewer / triggered_by detail unless demo-safe.
* operator should not see personal run detail from other teams.
* supervisor should see team status without turning the dashboard into a per-person surveillance tool.
* admin should not see raw prompt / response content or secrets.

## Field-level Visibility Matrix

The following matrix applies to `team_agent_runs` fields:

| Field                 | viewer         | operator       | supervisor                       | admin        |
| --------------------- | -------------- | -------------- | -------------------------------- | ------------ |
| run_uid               | yes            | yes            | yes                              | yes          |
| agent_name            | yes            | yes            | yes                              | yes          |
| agent_type            | yes            | yes            | yes                              | yes          |
| triggered_by          | masked         | own / assigned | team-visible or masked by policy | yes          |
| project_id            | limited        | assigned       | team                             | yes          |
| project_name          | yes            | yes            | yes                              | yes          |
| ticket_id             | hidden         | assigned       | team                             | yes          |
| ticket_label          | limited        | assigned       | team                             | yes          |
| task_title            | safe summary   | safe summary   | safe summary                     | safe summary |
| status                | yes            | yes            | yes                              | yes          |
| started_at / ended_at | coarse         | yes            | yes                              | yes          |
| output_ref            | limited        | assigned       | team                             | yes          |
| output_summary        | safe summary   | safe summary   | safe summary                     | safe summary |
| reviewer              | hidden         | if related     | team-visible or masked           | yes          |
| review_status         | yes            | yes            | yes                              | yes          |
| token_estimate        | aggregate only | own / assigned | aggregate preferred              | yes          |
| cost_estimate         | aggregate only | limited        | aggregate preferred              | yes          |
| risk_level            | yes            | yes            | yes                              | yes          |

`masked` means that the API may return `hidden`, `team_member`, `reviewer`, or a role-safe alias. viewer / supervisor dashboards should prefer aggregate values to avoid a personal surveillance experience. `output_summary` must remain a safe short summary.

## Dashboard Filtering Behavior

The future `/api/team-agentops/dashboard` role behavior should be:

### viewer

* active_agents: aggregate only
* pending_review: count only
* project_impact_percent: aggregate only
* failed_runs: aggregate only
* usage_cost_tokens: aggregate only
* timeline: demo-safe / public-safe items only
* project contribution: summary only
* scorecard: governance aggregate only

### operator

* active_agents: own + assigned project related
* pending_review: items assigned to operator or projects operator belongs to
* timeline: own triggered runs + assigned project runs
* project contribution: assigned projects
* scorecard: personal/team blended aggregate, no punitive score

### supervisor

* active_agents: team aggregate
* pending_review: team pending review queue
* timeline: team-safe runs
* project contribution: team projects
* scorecard: team aggregate, no individual ranking unless explicitly approved

### admin

* cross-team safe metadata
* configuration visibility
* governance reporting
* still no raw prompt / response / session / secrets

## Filtering Rules by Data Type

### Agent Runs

* filter by role scope
* filter by project assignment
* filter by ticket assignment
* filter by reviewer relation
* filter by triggered_by relation
* never filter by reading raw content

### Reviews

* viewer sees count only or demo-safe review status
* operator sees own pending reviews
* supervisor sees team pending review list
* admin sees all safe metadata reviews

### Outputs

* output_ref visibility follows run visibility
* output content is never embedded
* sensitive artifact access is controlled by source system

### Scorecard

* viewer sees aggregate
* operator sees personal/team blended safe aggregate
* supervisor sees team aggregate
* admin sees cross-team aggregate
* scorecard is not employee surveillance score

## API Role Source

The first version may use:

* `X-Demo-Role` header
* existing demo auth / role switcher
* fallback role: `viewer`

Future production behavior may use:

* authenticated user session
* group membership
* project assignment
* ticket assignment
* reviewer assignment
* admin policy

X-Demo-Role is for demo and development only. It is not a production authorization mechanism.

X-Demo-Role 只適合 demo 與開發階段，不是正式 production 授權機制。

## Response Shape Examples

### Viewer Dashboard Example

```json
{
  "viewer": {
    "role": "viewer",
    "scope": "limited"
  },
  "summary": {
    "active_agents": 3,
    "pending_review": 1,
    "project_impact_percent": 78,
    "failed_runs": 1,
    "usage_cost_tokens": 118000
  },
  "agent_activity_timeline": [],
  "visibility_note": "Limited aggregate view for viewer role."
}
```

### Operator Dashboard Example

```json
{
  "viewer": {
    "role": "operator",
    "scope": "personal_plus_assigned"
  },
  "summary": {
    "active_agents": 2,
    "pending_review": 1,
    "project_impact_percent": 82,
    "failed_runs": 0,
    "usage_cost_tokens": 42800
  },
  "visibility_note": "Shows own and assigned project agent activity."
}
```

### Supervisor Dashboard Example

```json
{
  "viewer": {
    "role": "supervisor",
    "scope": "team"
  },
  "visibility_note": "Shows team-level governance and review queue without raw AI content."
}
```

## Safety Boundary

* Role-based filtering does not relax safe metadata boundary.
* No role can access raw prompt / response through Team_AgentOps.
* No role can access raw session logs.
* No role can access credentials / secrets / API keys.
* No role should receive full home paths.
* Admin still receives safe metadata only.
* Token and cost values are operational estimates.
* Scorecard is governance indicator, not employee surveillance.

即使是 admin，也只能透過 Team_AgentOps 取得 safe metadata，不能取得完整 prompt、response、raw session 或 secrets。

## Future Implementation Plan

1. Phase 1: Document role model and visibility rules
2. Phase 2: Add role field to Team_AgentOps API responses
3. Phase 3: Implement demo role filtering using `X-Demo-Role`
4. Phase 4: Connect role switcher to frontend display
5. Phase 5: Integrate project / ticket assignment rules
6. Phase 6: Add AuditOps evidence for future review write flows
7. Phase 7: Replace demo role with production auth policy

## Task #175 Handoff

Task #175: Team_AgentOps Demo Role Filtering Prototype

Scope:

* Add `X-Demo-Role` support to read-only Team_AgentOps API.
* Return viewer metadata in API response.
* Filter dashboard/runs/pending reviews/project contribution by demo role.
* Keep all APIs read-only.
* Do not implement production auth.
* Do not add write API.
