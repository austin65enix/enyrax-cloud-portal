# Team_AgentOps API-backed Dashboard Release Note

Version: `v0.6.28-team-agentops-api-backed-dashboard`

## Overview

Team_AgentOps API-backed Dashboard upgrades the static human-AI team operations prototype into an API-backed dashboard powered by safe demo fixtures and read-only Team_AgentOps endpoints.

Team_AgentOps API-backed Dashboard 將原本的人類團隊與 AI Agent 協作治理 static prototype，升級為由 safe demo fixtures 與 read-only Team_AgentOps API 支撐的 dashboard。

Team_AgentOps does not replace AgentOps. Team_AgentOps is the team management and project collaboration layer above AgentOps. This release connects the Agent run schema, demo fixtures, read-only API, frontend API fallback, and screenshot baseline into one fixture-backed dashboard release.

This remains a demo / fixture-backed stage. It does not connect to a production DB, perform mutation, store prompts / responses / raw sessions, or implement employee surveillance scoring.

## Completed Scope

* Task #166: Team_AgentOps Agent Run Log Schema Design
* Task #167: Team_AgentOps Demo Data Fixture Design
* Task #168: Team_AgentOps Read-only Fixture API Prototype
* Task #169: Team_AgentOps Frontend API Switch with Fixture Fallback
* Task #170: Team_AgentOps Static Dashboard Screenshot Baseline
* Task #172: Team_AgentOps API-backed Dashboard Release Note

## Key Features

### Safe Agent Run Schema

Designed a conceptual safe metadata schema for Team_AgentOps:

* `team_agent_runs`
* `team_agent_reviews`
* `team_agent_outputs`

The schema tracks agent runs, project linkage, ticket linkage, output references, human reviews, token / cost estimates, and risk. It does not store prompt / response content, raw sessions, command output, diff content, credentials, secrets, or full home paths.

已設計 Team_AgentOps safe metadata schema，定義 Agent 執行、人工審核、產出 reference 的概念資料表。只保存 metadata 與 artifact reference，不保存完整 AI 對話內容。

### Safe Demo Fixtures

Added:

* `data/team-agentops/demo_agent_runs.json`
* `data/team-agentops/demo_agent_reviews.json`
* `data/team-agentops/demo_agent_outputs.json`
* `data/team-agentops/demo_project_contribution.json`
* `data/team-agentops/demo_scorecard.json`
* `data/team-agentops/README.md`

Fixture record counts:

* 6 agent runs
* 4 human reviews
* 6 output references
* 5 project contribution records
* 1 governance scorecard

Fixtures contain safe demo metadata only and do not include raw prompts, responses, raw sessions, command output, file diffs, credentials, secrets, API keys, or full home paths.

Fixtures 只包含安全 demo metadata，不包含真實 prompt、response、raw sessions、command output、file diff、credentials、secrets、API keys 或完整 home paths。

### Read-only Fixture API

Endpoints:

```text
GET /api/team-agentops/dashboard
GET /api/team-agentops/runs
GET /api/team-agentops/runs/{run_uid}
GET /api/team-agentops/reviews/pending
GET /api/team-agentops/projects/contribution
GET /api/team-agentops/scorecard
```

APIs read allowlisted JSON fixtures only. APIs are read-only: no DB writes, fixture mutation, audit write, or content inference.

### Dashboard API Summary

Current public API verification:

```text
source: fixture
mode: read_only
active_agents: 3
pending_review: 1
project_impact_percent: 78
failed_runs: 1
usage_cost_tokens: 118000
timeline_count: 6
project_count: 5
warnings: []
```

### Frontend API DATA / DEMO FALLBACK

* `/team-agentops/` now fetches `/api/team-agentops/dashboard`.
* API success mode displays `API DATA / API 資料`.
* API failure or invalid schema displays `DEMO FALLBACK / DEMO 備援`.
* Local demo data remains available as fallback.
* The page never goes blank when API is unavailable.

`/team-agentops/` 會優先讀取 `/api/team-agentops/dashboard`。API 成功時顯示 `API DATA / API 資料`。API 失敗或 schema 不完整時顯示 `DEMO FALLBACK / DEMO 備援`。頁面保留本機 demo data，不會因 API 不可用而空白。

### Safety Boundary

API and UI retain:

* safe metadata only
* no prompt / response storage
* no raw sessions
* no credentials / secrets
* no API keys
* no full home paths
* not employee surveillance
* operational estimates only
* read-only mode

Team_AgentOps 的資料模型與 API 目標是治理與保護，不是監控員工；它只保存必要 metadata，讓 AI 協作可追蹤、可審核、可交付。

### Screenshot Baseline Checklist

Added `docs/team_agentops_screenshot_baseline.md`. It defines desktop / tablet / mobile screenshot targets, covers the API DATA primary state and DEMO FALLBACK fallback state, and includes Safety Boundary, Shadow AI Risk, Team Scorecard, Timeline, and Project Contribution checks.

Browser tooling was unavailable, so PNG baselines were not generated yet.

## Current Verification

Re-verified against the public portal on 2026-06-01:

```text
/team-agentops/: HTTP 200

dashboard:
  source: fixture
  mode: read_only
  summary:
    active_agents: 3
    pending_review: 1
    project_impact_percent: 78
    failed_runs: 1
    usage_cost_tokens: 118000
  timeline_count: 6
  project_count: 5
  safety_boundary:
    safe_metadata_only: true
    no_prompt_response_storage: true
    no_raw_sessions: true
    no_credentials_or_secrets: true
    not_employee_surveillance: true
    operational_estimates_only: true
  warnings: []

runs:
  count: 6
  source: fixture
  mode: read_only
  warnings: []

pending reviews:
  count: 1
  source: fixture
  mode: read_only
  warnings: []

project contribution:
  count: 5
  source: fixture
  mode: read_only
  warnings: []

scorecard:
  metrics:
    agent_usage_rate_percent: 76
    review_pass_rate_percent: 84
    rework_rate_percent: 12
    cost_per_task_tokens: 3200
    audit_coverage_percent: 91
  notes:
    - Demo governance metrics only.
    - Not employee surveillance scoring.
    - Token values are operational estimates, not billing-grade cost data.
  source: fixture
  mode: read_only
  warnings: []
```

## Product Positioning

| Module        | Role                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------- |
| AgentOps      | AI Agent execution telemetry, preview quality, snapshot governance                          |
| Team_AgentOps | Human-AI team collaboration, safe agent run metadata, project contribution, review workflow |
| ProjectOps    | Project progress and delivery status                                                        |
| ServiceOps    | Tickets and operational work                                                                |
| AuditOps      | Review, approval, deployment, and audit evidence                                            |

AgentOps observes AI agent execution. Team_AgentOps turns safe agent run metadata into governed human-AI team delivery records.

AgentOps 觀測 AI Agent 執行；Team_AgentOps 則把安全 Agent run metadata 轉換成可治理的人機協作交付紀錄。

## Interview / Demo Talk Track

這一版 Team_AgentOps 已經從 static prototype 進一步升級為 API-backed dashboard。前端會先讀取 Team_AgentOps read-only API，API 會從 safe demo fixtures 回傳 Agent 執行、人工審核、專案貢獻與 scorecard 資料。

重點是它仍然保持 safe metadata only，不保存 prompt、response、raw session 或敏感憑證。這樣企業可以看見 AI Agent 對專案與團隊交付的貢獻，也能保留人工審核與責任邊界，但不會把系統做成員工監控工具。

This version upgrades Team_AgentOps from a static prototype into an API-backed dashboard. The frontend first reads the Team_AgentOps read-only API, which returns agent runs, human reviews, project contribution, and scorecard data from safe demo fixtures.

The key point is that it still keeps a safe metadata boundary. It does not store prompts, responses, raw sessions, or sensitive credentials. This allows enterprises to see how AI agents contribute to project delivery and team workflow, while preserving human review and accountability without turning the system into employee surveillance.

## Scope Boundary

This release does not include:

* no production DB integration
* no DB migration
* no write API
* no mutation
* no approval / reject workflow mutation
* no AgentOps parser changes
* no raw prompt / response storage
* no raw session storage
* no real token billing integration
* no employee surveillance scoring
* no deployment setting changes
* no screenshot PNG baseline yet

## Known Limitations

* API is fixture-backed, not production DB-backed.
* Frontend fallback uses local demo data.
* No write workflow yet.
* Human review flow is display-only.
* Scorecard metrics are demo governance metrics.
* Usage cost is operational estimate only.
* Browser screenshot tooling was unavailable, so screenshot baseline remains checklist-only.
* No role-based access control refinement yet.

## Recommended Next Steps

* Task #173: Team_AgentOps API-backed Dashboard Release Tag
* Task #174: Team_AgentOps Role-based API Filtering Design
* Task #175: Team_AgentOps Human Review Write Flow Design
* Task #176: Team_AgentOps Project Contribution API Refinement
* Task #177: Team_AgentOps Screenshot PNG Baseline
* Task #178: Team_AgentOps DB-backed Schema Migration Plan

## AgentOps Product Family Navigation

* Task #185 defines AgentOps as an AI Agent Governance product family.
* The family includes Server_AgentOps, Personal_AgentOps, and Team_AgentOps.
* Recommended navigation keeps AgentOps as the top-level entry and groups submodules under an AgentOps Hub.
* This avoids top navigation overload and prepares future Server / Personal AgentOps modules.
* No frontend, backend, DB, API, release, or deployment changes were made.
