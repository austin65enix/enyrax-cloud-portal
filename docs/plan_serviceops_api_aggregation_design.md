# Plan_ServiceOPS API Aggregation Design

Read-only aggregation layer for personal work queue dashboard

## Overview

Plan_ServiceOPS API Aggregation layer is a read-only aggregation layer that combines existing ServiceOps tickets and ProjectOps projects into a personal daily work queue dashboard.

Plan_ServiceOPS API Aggregation layer 是一個唯讀聚合層，用來把既有 ServiceOps tickets 與 ProjectOps projects 整合成個人每日工作中控台需要的資料。它不取代 ServiceOps 或 ProjectOps，也不建立新的主資料來源，而是把既有資料轉換成「今日待辦、團隊待辦、專案截止日」三個視角。

* 第一版是 read-only。
* 不新增獨立資料表。
* 不複製 ServiceOps / ProjectOps 主資料。
* 不改變 ServiceOps ticket 狀態語義。
* 不改變 ProjectOps project 狀態語義。
* API aggregation 只負責整理與排序資料。
* 前端 `/plan-serviceops/` 未來可以從 demo data 切換到這些 API。

## Product Positioning

| Layer               | Responsibility                        |
| ------------------- | ------------------------------------- |
| ServiceOps          | Source of operational tickets         |
| ProjectOps          | Source of project timeline and status |
| Plan_ServiceOPS API | Read-only aggregation layer           |
| Plan_ServiceOPS UI  | Personal daily work queue dashboard   |

ServiceOps 是工單主資料來源，ProjectOps 是專案主資料來源，Plan_ServiceOPS API 不新增新的工作資料，而是把這些資料整理成每日個人工作視角。

## Proposed API Endpoints

```text
GET /api/plan-serviceops/summary
GET /api/plan-serviceops/today-tickets
GET /api/plan-serviceops/team-tickets
GET /api/plan-serviceops/project-deadlines
GET /api/plan-serviceops/dashboard
```

* `/summary` 回傳 summary cards。
* `/today-tickets` 回傳目前使用者的今日個人待辦。
* `/team-tickets` 回傳團隊待辦、blocked、waiting approval、waiting vendor 等狀態。
* `/project-deadlines` 回傳接近截止日的 project deadlines。
* `/dashboard` 可一次回傳 summary + today tickets + team tickets + project deadlines，方便前端一次 fetch。

第一版建議：

```text
優先實作 /api/plan-serviceops/dashboard
```

理由：

* Static demo 頁面目前是單頁 dashboard。
* 一次 fetch 可以降低前端複雜度。
* 後續再拆分 endpoints。

## Response Schema Design

### 5.1 Dashboard Response

```json
{
  "generated_at": "2026-06-01T09:00:00+08:00",
  "viewer": {
    "role": "operator",
    "user": "atn",
    "scope": "personal"
  },
  "summary": {
    "today_tickets": 5,
    "doing": 2,
    "overdue": 1,
    "nearest_deadline_days": 14,
    "nearest_deadline_label": "D-14",
    "blocked_team_tickets": 3
  },
  "today_tickets": [],
  "team_tickets": [],
  "project_deadlines": [],
  "warnings": []
}
```

### 5.2 Today Ticket Item

```json
{
  "ticket_id": "TCK-20260601-001",
  "source_id": 101,
  "title": "ERP Test VM Request",
  "priority": "High",
  "status": "Pending",
  "assignee": "atn",
  "due_time": "Today 17:30",
  "due_at": "2026-06-01T17:30:00+08:00",
  "related_project": "ERP Upgrade",
  "related_project_id": 12,
  "is_overdue": false,
  "source": "serviceops"
}
```

### 5.3 Team Ticket Item

```json
{
  "ticket_id": "TCK-TEAM-001",
  "source_id": 201,
  "type": "Infra",
  "title": "Firewall Rule Change",
  "owner": "Infra Team",
  "status": "Blocked",
  "waiting_reason": "Waiting approval",
  "sla": "Today",
  "due_at": "2026-06-01T18:00:00+08:00",
  "source": "serviceops"
}
```

### 5.4 Project Deadline Item

```json
{
  "project_id": 12,
  "project_name": "ERP Upgrade",
  "owner": "atn",
  "deadline": "2026-06-15",
  "remaining_days": 14,
  "deadline_label": "D-14",
  "status": "On Track",
  "related_ticket_count": 5,
  "source": "projectops"
}
```

## Mapping from Existing ServiceOps / ProjectOps Data

### ServiceOps → Today Tickets

來源：

* existing `serviceops_tickets`

候選欄位：

| Plan_ServiceOPS Field | Source                                   |
| --------------------- | ---------------------------------------- |
| ticket_id             | generated display ID or ticket id        |
| source_id             | serviceops ticket id                     |
| title                 | serviceops title                         |
| priority              | serviceops priority / sla_level fallback |
| status                | serviceops status / progress_status      |
| assignee              | owner / assignee                         |
| due_at                | serviceops due_at                        |
| related_project       | project name / linked project            |
| is_overdue            | computed from due_at                     |

若 existing schema 沒有某些欄位，第一版可以：

* fallback to demo-compatible placeholder
* return `null`
* derive from existing fields conservatively

### ServiceOps → Team Tickets

來源：

* serviceops tickets with:
  * status pending / doing / blocked
  * waiting reason
  * SLA today / overdue
  * not archived
  * not done

### ProjectOps → Project Deadlines

來源：

* existing `projectops_projects`

候選欄位：

| Plan_ServiceOPS Field | Source         |
| --------------------- | -------------- |
| project_id            | projectops id  |
| project_name          | title          |
| owner                 | owner          |
| deadline              | end_date       |
| remaining_days        | computed       |
| status                | project status |
| related_ticket_count  | linked_tickets |

## Filtering Rules

### Today Tickets

第一版規則：

* assignee / owner matches current viewer when available。
* due_at is today or overdue。
* status not done。
* archived / deleted tickets excluded。
* sort:
  1. overdue first
  2. High → Medium → Low
  3. due_at ascending
  4. created_at descending

### Team Tickets

第一版規則：

* include pending / doing / blocked。
* exclude done / archived / deleted。
* include tickets with SLA today / overdue / waiting reason。
* sort:
  1. blocked first
  2. overdue first
  3. SLA today
  4. priority
  5. updated_at descending

### Project Deadlines

第一版規則：

* projects with end_date not null。
* deadline within next 30 days。
* exclude completed / archived if status supports it。
* sort by remaining_days ascending。
* show max 5 or 10 projects。

## Role and Scope Rules

| Role             | Scope                                        |
| ---------------- | -------------------------------------------- |
| Preview / Viewer | read-only demo data or limited read-only API |
| Operator         | own today tickets + limited team queue       |
| Supervisor       | team queue + workload summary                |
| Admin            | cross-team view                              |

* Infra 成員聚焦個人待辦。
* 主管可看 team queue 與 workload。
* Admin 可看跨團隊。
* 第一版 API 可以先使用 `X-Demo-Role`。
* 真實 auth 整合留到後續任務。

## Status Mapping

Plan_ServiceOPS 顯示狀態：

| Display Status | Source Status Examples             |
| -------------- | ---------------------------------- |
| Pending        | pending, open, not_started         |
| Doing          | doing, in_progress                 |
| Done           | done, closed                       |
| Blocked        | blocked, waiting, pending_approval |

注意：

* 第一版 read-only API 不改原始 status。
* 若未來要從 Plan_ServiceOPS 切換狀態，必須呼叫 ServiceOps existing update API，而不是在 Plan_ServiceOPS 建新狀態。

## Priority Mapping

Plan_ServiceOPS 顯示 priority：

| Display Priority | Source Examples                    |
| ---------------- | ---------------------------------- |
| High             | high, critical, urgent, SLA urgent |
| Medium           | medium, normal                     |
| Low              | low                                |

若 ServiceOps 沒有 priority，可用：

1. `sla_level`
2. `due_at`
3. status / overdue
4. fallback Medium

## Deadline and D-Day Computation

* `remaining_days = deadline_date - today`
* today 使用伺服器日期或指定 timezone。
* 若 remaining_days > 0，顯示 `D-N`。
* 若 remaining_days = 0，顯示 `Today`。
* 若 remaining_days < 0，顯示 `Overdue N days`。
* deadline within 30 days should be shown in project deadlines。
* timezone 第一版以 Asia/Taipei 為預設設計。

## Read-only Boundary

* Plan_ServiceOPS API Aggregation v1 is read-only。
* It does not create tickets。
* It does not update ticket status。
* It does not update project status。
* It does not write audit logs。
* It does not mutate ServiceOps or ProjectOps data。
* It only reads and aggregates existing data。

若未來要做 status update：

* 透過 ServiceOps existing update API。
* 必須寫 audit log。
* 必須套用 role permission。
* 不在本設計 v1 範圍內。

## Error Handling

建議：

* 如果 ServiceOps source unavailable：
  * return partial dashboard with warning。
* 如果 ProjectOps source unavailable：
  * return project_deadlines empty + warning。
* 如果 role unknown：
  * fallback viewer scope。
* 如果 no tickets：
  * return empty arrays，不回 500。
* warnings 放在 `warnings` array。

範例：

```json
{
  "warnings": [
    {
      "code": "projectops_unavailable",
      "message": "Project deadline data is temporarily unavailable."
    }
  ]
}
```

## Future Implementation Plan

### Phase 1：Read-only API Prototype

* Add `/api/plan-serviceops/dashboard`
* Aggregate existing ServiceOps / ProjectOps data
* Use X-Demo-Role
* No DB changes

### Phase 2：Frontend API Switch

* `/plan-serviceops/` fetches read-only API
* fallback to demo data if API unavailable
* preserve static demo copy

### Phase 3：Role-based Filtering

* operator sees own tickets
* supervisor sees team queue
* admin sees cross-team view

### Phase 4：Optional Status Update

* only if needed
* call existing ServiceOps API
* audit log required
* permission required

## Non-goals

本任務不做：

* no backend implementation
* no frontend implementation
* no DB migration
* no new table
* no status mutation
* no ServiceOps behavior change
* no ProjectOps behavior change
* no production data change
* no deployment change

## Task #153 Handoff

建議下一步：

```text
Task #153：Plan_ServiceOPS Read-only API Prototype
```

範圍：

* Implement `GET /api/plan-serviceops/dashboard`
* Read from existing in-memory / DB-backed ServiceOps and ProjectOps sources
* No DB migration
* No mutation
* Add backend tests or curl checks
* Do not modify frontend yet unless approved

## Task #153 Read-only API Prototype

* Added `GET /api/plan-serviceops/dashboard`.
* API aggregates existing ServiceOps tickets and ProjectOps projects.
* API remains read-only.
* No DB migration.
* No new table.
* No mutation.
* Frontend remains static demo in this task.
* Future task can switch frontend to API with demo fallback.

Task #153 reads existing ServiceOps and ProjectOps tables with `SELECT` queries only. It does not create tickets, update ticket status, update project status, write audit logs, or mutate ServiceOps or ProjectOps data.

The prototype uses the server local timestamp for `generated_at` and the server local date for D-Day computation. A future task can pin the application timezone to `Asia/Taipei` if deployment environments need an explicit timezone policy.

`X-Demo-Role` supports `viewer`, `operator`, `supervisor`, and `admin`. `preview` aliases to `viewer`, and unknown roles fall back to the limited `viewer` scope without changing existing authentication behavior.

## Task #154 Frontend API Switch with Demo Fallback

* `/plan-serviceops/` now fetches `GET /api/plan-serviceops/dashboard`.
* API success renders read-only aggregated data from existing ServiceOps / ProjectOps sources.
* API failure, non-200 responses, invalid JSON, or incomplete dashboard schema fall back to local demo data.
* API mode disables the Today Ticket status toggle.
* Demo fallback mode keeps the local `Pending -> Doing -> Done -> Pending` status toggle.
* Role, auth session, and relevant storage changes trigger a dashboard refetch.
* API warnings render as a non-blocking warning strip.
* No backend changes.
* No DB changes.
* No ServiceOps / ProjectOps mutation.

## Task #155 API-backed Frontend QA and Release Note

* Task #155 validates API-backed frontend behavior.
* API success renders read-only aggregated data.
* API failure falls back to local demo data.
* API mode disables status toggle.
* Demo mode preserves local status toggle.
* Release note prepared for `v0.6.26-plan-serviceops-api-backed-dashboard`.
