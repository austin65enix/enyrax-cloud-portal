# Team_AgentOps Product Concept Design

Managing human teams and AI agents as one governed delivery workflow

## Overview

Team_AgentOps is the ENYRAX module for managing how human teams and AI agents collaborate on projects, tickets, reviews, and delivery outcomes.

Team_AgentOps 是 ENYRAX 用來管理人類團隊與 AI Agent 協作的模組，負責追蹤 Agent 任務、專案進度、產出成果、人工審核與使用紀錄。

Team_AgentOps 不是單純記錄誰用了 AI。Team_AgentOps 是把 AI Agent 納入正式工作流程，讓 AI Agent 從個人工具，變成企業可管理、可稽核、可追蹤的正式團隊資源。重點是專案貢獻、人工審核、責任邊界與使用者保護。

## One-line Positioning

Team_AgentOps 讓 AI Agent 成為可管理、可稽核、可衡量貢獻的正式團隊成員。

Team_AgentOps turns AI agents into manageable, auditable, and measurable contributors within enterprise teams.

Team_AgentOps 是企業 AI 混合車隊的 Pit Wall，記錄每一次 Agent 出車、進站、調校、審核與交付。

Team_AgentOps is the pit wall for enterprise human-AI teams, tracking every agent run, review, adjustment, and delivery outcome.

## Problem Statement

企業導入 AI Agent 後，需要回答新的管理與治理問題：

* 哪些 Agent 正在跑？
* 是誰啟動的？
* 用在哪個專案？
* 處理哪張 ticket？
* 有沒有改 code？
* 有沒有產生測試結果？
* 有沒有失敗、卡住、超出 token / credit？
* 產出是否經過人工 review？
* 最後是否真的推進專案進度？

Without Team_AgentOps, AI agent usage can become shadow AI: individual usage without records, review, responsibility boundaries, or delivery traceability.

如果沒有 Team_AgentOps，AI Agent 使用很容易變成 shadow AI：每個人私下使用，做了什麼沒有紀錄，產出有沒有審核不知道，出問題也難以追蹤責任。

## Module Positioning in ENYRAX

| Module        | Responsibility                              |
| ------------- | ------------------------------------------- |
| SOC           | 資安事件與風險監控                                   |
| ServiceOps    | 工單、維運、服務請求                                  |
| ProjectOps    | 專案、里程碑、交付進度                                 |
| AuditOps      | 操作紀錄、稽核軌跡                                   |
| AgentOps      | AI Agent execution telemetry and governance |
| Team_AgentOps | 團隊 AI Agent 使用管理、專案貢獻與人工審核流程                |

AgentOps observes individual AI agent runs. Team_AgentOps connects those runs back to human teams, project progress, review workflows, and delivery accountability.

AgentOps 偏向觀測單次 AI Agent 執行紀錄；Team_AgentOps 則把這些執行紀錄接回團隊、專案進度、人工審核與交付責任。

## Core Concepts

### 1. Agent Run Log

記錄每一次 AI Agent 執行。

| Field            | Description                              |
| ---------------- | ---------------------------------------- |
| Agent Name       | Codex、Claude Code、Copilot、Internal Agent |
| Triggered By     | 啟動者                                      |
| Project          | 所屬專案                                     |
| Task / Ticket    | 對應任務或工單                                  |
| Start / End Time | 執行時間                                     |
| Status           | Running / Done / Failed / Review Needed  |
| Output           | Commit、文件、測試報告、分析結果                      |
| Cost             | Token、Credit、執行時間                        |
| Reviewer         | 人工審核者                                    |

### 2. Project Agent Contribution

把 Agent 任務接回 ProjectOps 專案進度。

| Project                   | Human Tasks | Agent Tasks | Progress |
| ------------------------- | ----------: | ----------: | -------- |
| ServiceOps Personal Queue |           3 |           5 | 80%      |
| SOC Incident Timeline     |           2 |           4 | 65%      |
| Backup Healthcheck        |           1 |           3 | 90%      |
| AgentOps Dashboard        |           4 |           6 | 55%      |

### 3. Human Review Flow

```text
Create Task
→ Assign to Human / Agent / Human + Agent
→ Agent Executes
→ Output Generated
→ Human Review
→ Approve / Rework / Reject
→ Merge / Deploy / Close
```

* AI Agent 做完不等於完成。
* Team_AgentOps 要把人工 review 作為正式流程。
* Review 後才能 merge / deploy / close task。

### 4. Team Scorecard

| Metric                 | Meaning     |
| ---------------------- | ----------- |
| Agent Usage Rate       | 團隊導入 AI 程度  |
| Review Pass Rate       | AI 產出品質     |
| Task Completion Impact | 對專案進度貢獻     |
| Rework Rate            | 需要返工比例      |
| Cost per Task          | 每個任務的 AI 成本 |
| Human Saved Time       | 預估節省工時      |
| Audit Coverage         | 是否有完整紀錄     |

## Product Value

### For Managers

* 看到 AI Agent 對專案進度的實際貢獻。
* 追蹤 pending review、failed runs、成本與交付結果。
* 避免只知道「團隊有用 AI」，但不知道 AI 做了什麼。

### For Engineers

* 保護自己，證明 AI 產出有經過 review、測試與版本控管。
* 讓 AI 協作從黑箱變成可追蹤工作紀錄。
* 避免出問題時被簡化成「是不是你亂用 AI」。

### For Audit / Governance

* 建立 AI 使用證據鏈。
* 保留 Agent task、review、output、project linkage。
* 降低 shadow AI 風險。

### For Project Delivery

* 將 AI Agent 任務納入 ProjectOps。
* 讓 human tasks 與 agent tasks 一起反映在 progress 中。
* 將 AI 使用轉換為可衡量的 delivery contribution。

## Dashboard Concept

Team_AgentOps Dashboard 上方 KPI cards：

| Card           | Meaning               |
| -------------- | --------------------- |
| Active Agents  | 目前執行中的 Agent          |
| Pending Review | 等待人工審核的 Agent 產出      |
| Project Impact | Agent 對專案進度的貢獻        |
| Failed Runs    | 失敗或中斷的任務              |
| Usage Cost     | Token / Credit / 時間成本 |

### Agent Activity Timeline

```text
22:10 Codex completed ServiceOps UI update
21:45 Claude generated SOC incident test cases
21:20 Codex updated backup healthcheck script
20:55 Human review approved Task #147
```

### Project Agent Contribution

```text
Project: Plan_ServiceOPS Personal Version

Human:
- Defined use case
- Reviewed UI
- Tested workflow

Agent:
- Generated prototype
- Updated frontend
- Modified documentation
- Created release notes
```

## Data Model Concept

以下是第一版概念資料表，不實作 DB migration。

### team_agent_runs

| Field          | Type               | Description                             |
| -------------- | ------------------ | --------------------------------------- |
| id             | integer            | internal id                             |
| agent_name     | text               | Codex / Claude / Copilot                |
| triggered_by   | text               | user id / name                          |
| project_id     | integer nullable   | linked ProjectOps project               |
| ticket_id      | integer nullable   | linked ServiceOps ticket                |
| task_title     | text               | task description                        |
| status         | text               | running / done / failed / review_needed |
| started_at     | timestamp          | start time                              |
| ended_at       | timestamp nullable | end time                                |
| output_type    | text               | commit / doc / test / report            |
| output_ref     | text nullable      | commit hash / doc path / PR             |
| reviewer       | text nullable      | reviewer                                |
| review_status  | text               | pending / approved / rejected / rework  |
| token_estimate | integer nullable   | operational estimate                    |
| cost_estimate  | numeric nullable   | optional                                |
| notes          | text nullable      | safe summary only                       |

### team_agent_reviews

| Field        | Type      | Description               |
| ------------ | --------- | ------------------------- |
| id           | integer   | internal id               |
| agent_run_id | integer   | linked agent run          |
| reviewer     | text      | human reviewer            |
| decision     | text      | approve / reject / rework |
| comment      | text      | review comment            |
| reviewed_at  | timestamp | review time               |

注意：

* 這只是 concept，不要實作 DB migration。
* prompt / response content 不應存入第一版。
* full raw session 不應存入第一版。
* output_ref 應指向 safe artifact / commit / document reference。

## Integration with Existing Modules

### AgentOps

* AgentOps 提供 agent run telemetry、token estimate、review health、snapshot governance。
* Team_AgentOps 可消費 AgentOps 的 aggregate / safe metadata。
* Team_AgentOps 不應讀 raw prompt / response。

### ProjectOps

* 將 Agent runs 綁到 project。
* Agent contribution 可以影響 project progress / milestone evidence。
* Project view 可顯示 human tasks vs agent tasks。

### ServiceOps

* 將 Agent runs 綁到 ticket。
* Ticket 可顯示是否有 Agent 協助分析、修復、文件或測試。
* Agent output 需要 human review 才能 close ticket。

### AuditOps

* 記錄 review、approve、reject、deploy、close 等操作。
* 提供責任邊界與稽核證據。

## Safety and Privacy Boundary

* Team_AgentOps v1 should store safe metadata only。
* Do not store full prompt / response content。
* Do not store raw session logs。
* Do not store credentials、secrets、API keys。
* Do not store full home paths。
* Do not infer project/task from content without approved allowlist。
* Store output references, not raw output when possible。
* Human review decision should be stored, but sensitive content should remain in source system or safe artifact store。
* AI usage records are for governance and protection, not employee surveillance。

Team_AgentOps 的目標不是監控員工，而是保護使用者與團隊：讓 AI 協作有紀錄、有審核、有責任邊界。

## MVP Scope

第一版只做設計，不實作。

未來 MVP 可包含：

1. Static Team_AgentOps dashboard prototype
2. Demo agent run log
3. Project contribution sample
4. Human review status sample
5. Team scorecard mock metrics
6. Interview demo talk track

* MVP 不讀 raw agent sessions。
* MVP 不接 real token billing。
* MVP 不做 employee surveillance。
* MVP 不做 automatic performance scoring。
* MVP 不做 automatic approval。

## Interview Demo Talk Track

### 中文

我會把這個模組命名為 Team_AgentOps。它的重點不是單純記錄誰用了 AI，而是把 AI Agent 納入團隊正式工作流程。

每一次 Agent 執行都會記錄由誰啟動、屬於哪個專案、對應哪張 Ticket、產出什麼結果、是否經過人工 Review，以及最後是否推進專案進度。

這樣企業可以避免 shadow AI 的問題，也可以讓主管看見 AI 對團隊效率的實際貢獻。對使用者來說，這也是保護，因為所有 AI 協作都有紀錄、有審核、有責任邊界。

### English

I would call this module Team_AgentOps. The goal is not simply to record who used AI, but to bring AI agents into the formal team workflow.

Each agent run records who triggered it, which project it belongs to, which ticket it supports, what output it produced, whether it passed human review, and whether it actually moved project progress forward.

This helps enterprises reduce shadow AI risk and gives managers visibility into the real contribution of AI to team delivery. It also protects engineers because AI-assisted work becomes traceable, reviewed, and governed instead of remaining a black box.

## Non-goals

本任務不做：

* no frontend implementation
* no backend implementation
* no DB migration
* no API implementation
* no AgentOps parser changes
* no raw prompt / response storage
* no employee surveillance scoring
* no automatic approval
* no production data integration
* no RELEASE.md update

## Future Tasks

* Task #162：Team_AgentOps Static Dashboard Prototype
* Task #163：Team_AgentOps Visual QA and Interaction Review
* Task #164：Team_AgentOps Human Review Flow Design
* Task #165：Team_AgentOps Project Contribution View
* Task #166：Team_AgentOps Safety Boundary Review
* Task #167：Team_AgentOps Release Note

## Task #162 Static Dashboard Prototype

* Added `/team-agentops/` static prototype。
* Added Portal homepage card。
* Prototype uses demo data only。
* No backend、DB、API、AgentOps parser、ProjectOps、ServiceOps changes。
* Dashboard includes KPI cards、activity timeline、project contribution、human review flow、team scorecard、shadow AI risk panel。
* Safety boundary remains safe metadata only。
* No raw prompt / response storage。
* No employee surveillance scoring。

## Task #163 Visual QA and Interaction Review

* `/team-agentops/` static prototype 已完成 visual QA。
* Desktop、tablet、mobile responsive checks completed。
* Portal homepage Team_AgentOps card 已確認。
* Safety boundary 已確認。
* Shadow AI risk copy 已確認。
* No backend、DB、API、AgentOps parser、ProjectOps、ServiceOps、or deployment changes。
* Prototype remains a static demo with demo data only。

## Task #164 Static Prototype Release Note

* Task #164 packages Tasks #161-#163 as `v0.6.27-team-agentops-static-prototype`。
* Release covers product concept、static dashboard prototype、Portal homepage card、visual QA、safety boundary、and demo positioning。
* Release remains static demo only。
* No backend、DB、API、parser、ProjectOps、ServiceOps、AgentOps、or deployment changes were made。
* Future work should start with release tag and then schema design。

## Task #166 Agent Run Log Schema Design

* Task #166 defines future safe metadata schema for Team_AgentOps agent runs.
* It introduces conceptual tables for agent runs, reviews, and outputs.
* It keeps prompt / response / raw sessions out of scope.
* It prepares future read-only APIs and dashboard metrics.
* No DB migration, backend, frontend, or parser changes were made.

## Task #167 Demo Data Fixture Design

* Task #167 provides safe demo fixture data for the Team_AgentOps static dashboard and future read-only APIs.
* Demo fixtures support Agent Activity Timeline, Project Agent Contribution, Team Scorecard, and Human Review samples.
* Safe metadata boundary remains unchanged.
* No DB, backend, frontend, AgentOps parser, or production data changes.


## Task #168 Read-only Fixture API Prototype

* Added read-only fixture API endpoints for Team_AgentOps.
* API reads safe demo fixtures from `data/team-agentops/`.
* API exposes dashboard, runs, run detail, pending reviews, project contribution, and scorecard.
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

## Task #174 Role-based API Filtering Design

* Task #174 defines role-based visibility rules for future Team_AgentOps APIs.
* It covers viewer, operator, supervisor, and admin roles.
* It defines endpoint-level and field-level visibility.
* It keeps safe metadata boundary unchanged.
* No backend, frontend, DB, fixture, parser, or release changes were made.

## Task #175 Demo Role Filtering Prototype

* Task #175 implements demo role filtering for the Team_AgentOps read-only fixture API.
* Uses `X-Demo-Role` for viewer / operator / supervisor / admin.
* Adds viewer metadata and visibility notes to API responses.
* Applies endpoint-level role filtering and field masking.
* Keeps APIs fixture-backed and read-only.
* Does not implement production authorization.
* Does not add write APIs.
* Safe metadata boundary remains unchanged.
