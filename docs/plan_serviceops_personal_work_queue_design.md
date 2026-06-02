# Plan_ServiceOPS Personal Work Queue Design

Personal Work Queue Dashboard for daily IT operations

## Overview

Plan_ServiceOPS is a personal daily work queue dashboard for IT operators. It brings together today’s personal tickets, team queue bottlenecks, and project deadlines into one focused view.

Plan_ServiceOPS 是給維運人員每天打開使用的個人工作中控台。它把今日個人待辦、團隊卡住的工單、以及專案截止日集中到同一個畫面，讓使用者不用進多個系統查詢，也能知道今天優先處理什麼。

Plan_ServiceOPS 不取代 ServiceOps，也不取代 ProjectOps。它是 ServiceOps + ProjectOps 的個人入口層，價值是「一打開就知道今天要做什麼」。

## Product Positioning

| Module          | Purpose          |
| --------------- | ---------------- |
| ServiceOps      | 全部維運工單管理 |
| ProjectOps      | 專案時程與狀態   |
| Plan_ServiceOPS | 個人每日工作中控台 |
| SOC             | 資安事件來源     |
| Audit           | 操作紀錄與證據留存 |

ServiceOps 管全部工單，ProjectOps 管專案時程，Plan_ServiceOPS 則把個人今天需要看的事項集中成每日工作入口。

## MVP v0.1 Scope

第一版只做以下 5 個功能：

1. 今日待辦 Ticket 清單
2. 團隊待辦 Ticket 清單
3. 專案截止日 D-Day 顯示
4. Ticket 狀態切換：Pending / Doing / Done
5. 依優先度排序：High → Medium → Low

第一版不要做太複雜。可以使用 demo data 或 existing API aggregation，先聚焦「開頁面知道今天要幹嘛」。

## Page Route Proposal

### Option A

```text
/serviceops/personal/
```

優點：

* 表示它是 ServiceOps 的個人視角。
* 不會讓模組太分散。

### Option B

```text
/plan-serviceops/
```

優點：

* 產品名稱清楚。
* 可以獨立成 Portal card。

建議採用：

```text
/plan-serviceops/
```

原因：

* 它不是原本 ServiceOps 的子頁而已，而是新的 daily operations dashboard。
* 未來可以接 ServiceOps、ProjectOps、SOC、Audit 多個來源。

## Homepage Card Copy

英文：

```text
Plan_ServiceOPS helps IT operators see today’s work, team workload, and project deadlines in one dashboard.
```

中文：

```text
Plan_ServiceOPS 將個人待辦、團隊工單與專案期限整合成每日維運工作中控台。
```

Short label：

```text
Personal Work Queue
```

中文短標：

```text
個人工作中控台
```

## Page Structure

### 1. Today / 今日待辦 Ticket

用途：

```text
顯示目前登入使用者今天需要處理的 ticket。
```

欄位：

| Field           | Example                |
| --------------- | ---------------------- |
| Ticket ID       | TCK-20260601-001       |
| Title           | ERP Test VM Request    |
| Priority        | High / Medium / Low    |
| Status          | Pending / Doing / Done |
| Assignee        | atn                    |
| Due Time        | Today 17:30            |
| Related Project | ERP Upgrade            |

### 2. Team Queue / 團隊待辦 Ticket

用途：

```text
顯示團隊目前正在等待、卡住或需要注意的工單。
```

欄位：

| Field          | Example                                          |
| -------------- | ------------------------------------------------ |
| Ticket ID      | TCK-xxx                                          |
| Type           | Infra / Helpdesk / SOC / DBA                     |
| Owner          | User / Team                                      |
| Status         | Pending / Doing / Blocked                        |
| Waiting Reason | Waiting user / Waiting approval / Waiting vendor |
| SLA            | Today / Tomorrow / Overdue                       |

### 3. Project Deadline / 專案截止日

用途：

```text
顯示接近截止日的專案，以及剩餘天數。
```

欄位：

| Field                | Example                      |
| -------------------- | ---------------------------- |
| Project Name         | ERP Upgrade                  |
| Owner                | atn                          |
| Deadline             | 2026-06-15                   |
| Remaining Days       | D-14                         |
| Status               | On Track / At Risk / Delayed |
| Related Ticket Count | 5                            |

## Dashboard Summary Cards

Summary cards 放在頁面上方，目標是 3 秒內知道今天工作壓力。

中文：

```text
今日待辦：5
進行中：2
逾期：1
專案截止：D-14
團隊卡住：3
```

英文：

```text
Today Tickets: 5
Doing: 2
Overdue: 1
Nearest Deadline: D-14
Blocked Team Tickets: 3
```

## Wireframe

```text
┌──────────────────────────────────────────────┐
│ Plan_ServiceOPS 個人版                       │
│ Personal Work Queue Dashboard                │
├──────────────────────────────────────────────┤
│ 今日摘要                                     │
│ 今日待辦 5｜進行中 2｜逾期 1｜專案截止 D-14 │
├──────────────────────────────────────────────┤
│ 今日待辦 Ticket                              │
│ [High] ERP Test VM Request        17:30      │
│ [Med ] AD Account Unlock          15:00      │
│ [Low ] Printer Check              Tomorrow   │
├──────────────────────────────────────────────┤
│ 團隊待辦 Ticket                              │
│ Infra   Firewall Rule Change      Blocked    │
│ SOC     Suspicious SSH Alert      Pending    │
│ Helpdesk Account Unlock           Doing      │
├──────────────────────────────────────────────┤
│ 專案截止日                                   │
│ ERP Upgrade        2026-06-15      D-14      │
│ Wazuh Rollout      2026-06-20      D-19      │
└──────────────────────────────────────────────┘
```

## Data Source Design

第一版可以不建新 table，先用 API aggregation。

建議 API：

```text
GET /api/plan-serviceops/summary
GET /api/plan-serviceops/today-tickets
GET /api/plan-serviceops/team-tickets
GET /api/plan-serviceops/project-deadlines
```

資料來源：

* today tickets 可來自 ServiceOps tickets。
* team tickets 可來自 ServiceOps tickets。
* project deadlines 可來自 ProjectOps projects。
* future SOC ticket 可由 SOC incident 轉出。
* future Audit 可記錄狀態變更。

## Demo Data Proposal

### Today Tickets

```json
[
  {
    "ticket_id": "TCK-20260601-001",
    "title": "ERP Test VM Request",
    "priority": "High",
    "status": "Pending",
    "assignee": "atn",
    "due_time": "Today 17:30",
    "related_project": "ERP Upgrade"
  },
  {
    "ticket_id": "TCK-20260601-002",
    "title": "AD Account Unlock",
    "priority": "Medium",
    "status": "Doing",
    "assignee": "atn",
    "due_time": "Today 15:00",
    "related_project": "IAM Review"
  },
  {
    "ticket_id": "TCK-20260601-003",
    "title": "Wazuh Agent Install Check",
    "priority": "Low",
    "status": "Pending",
    "assignee": "atn",
    "due_time": "Tomorrow",
    "related_project": "Wazuh Rollout"
  }
]
```

### Team Tickets

```json
[
  {
    "ticket_id": "TCK-TEAM-001",
    "type": "Infra",
    "title": "Firewall Rule Change",
    "owner": "Infra Team",
    "status": "Blocked",
    "waiting_reason": "Waiting approval",
    "sla": "Today"
  },
  {
    "ticket_id": "TCK-TEAM-002",
    "type": "SOC",
    "title": "Suspicious SSH Alert",
    "owner": "SOC Team",
    "status": "Pending",
    "waiting_reason": "Waiting verification",
    "sla": "Today"
  }
]
```

### Project Deadlines

```json
[
  {
    "project_name": "ERP Upgrade",
    "owner": "atn",
    "deadline": "2026-06-15",
    "remaining_days": 14,
    "status": "On Track",
    "related_ticket_count": 5
  },
  {
    "project_name": "Wazuh Rollout",
    "owner": "atn",
    "deadline": "2026-06-20",
    "remaining_days": 19,
    "status": "At Risk",
    "related_ticket_count": 3
  }
]
```

## UI Style Direction

* 延續 ENYRAX Portal 深色科技風格。
* 可以比 ServiceOps 更像「每日工作儀表板」。
* Summary cards 要醒目。
* Ticket list 要可快速掃讀。
* Priority 使用 High / Medium / Low badge。
* Status 使用 Pending / Doing / Done / Blocked badge。
* Deadline 使用 D-14 / D-7 / Overdue 顯示。

## Role / Permission Considerations

* 一般 Infra 成員只能看到自己的 today tickets。
* Infra 主管可以看到 team queue。
* Supervisor 可以看到 team workload。
* Admin / higher-level manager 可以看到跨 team view。
* 第一版 demo 可以先使用 X-Demo-Role 或現有 demo role switcher。

## Interview Talk Track

中文：

```text
我最近規劃了一個 Plan_ServiceOPS 個人版，它不是取代原本的 ServiceOps，而是把維運人員每天最需要看的三件事集中起來：今天待辦 ticket、團隊卡住的 ticket、以及專案截止日。這樣使用者一打開頁面，不用進多個系統查詢，就能知道今天優先處理什麼。
```

英文：

```text
I designed Plan_ServiceOPS as a personal work queue dashboard for IT operators. It does not replace the full ServiceOps module. Instead, it brings together the three things operators need to see every day: today’s tickets, blocked team tickets, and upcoming project deadlines. The goal is to help users know what to prioritize as soon as they open the page.
```

產品價值：

```text
它把傳統工單系統從被動查詢，改成每日主動工作中控台。
```

```text
It turns a traditional ticketing system from a passive query tool into a proactive daily operations cockpit.
```

## Non-goals

本任務不做：

* no frontend implementation
* no backend implementation
* no DB migration
* no API implementation
* no auth change
* no ServiceOps behavior change
* no ProjectOps behavior change
* no production data change

## Task #148 Handoff

下一步可以做：

```text
Task #148: Plan_ServiceOPS Personal Work Queue UI Prototype
```

範圍：

* 新增 `/plan-serviceops/` static page。
* 使用 demo data。
* 加入 Portal 首頁卡片。
* 不接 DB。
* 不改 ServiceOps existing flow。
* 先驗證 demo value。

## Task #148 UI Prototype

* 新增 `/plan-serviceops/` static prototype。
* 使用 demo data。
* 加入 Portal 首頁入口。
* 第一版不接 DB。
* 第一版不新增 API。
* 第一版不改 ServiceOps / ProjectOps existing flow。
* Status toggle 只做前端 demo state。

## Task #149 Visual QA and Interaction Review

* `/plan-serviceops/` 已完成 visual QA。
* 已檢查 desktop、tablet、mobile layout，包含 summary cards、ticket lists、priority / status badges、D-Day badges 與 responsive stacking。
* Today Ticket status toggle 已驗證：`Pending -> Doing -> Done -> Pending`，refresh 後恢復 demo data。
* Portal homepage `/plan-serviceops/` card 已驗證。
* 第一版仍為 static demo，demo data 不代表 production data。
* 未接 DB。
* 未新增 API。
* 未修改 ServiceOps / ProjectOps existing flow。

## Task #150 Release Note

* Task #150 packages Tasks #147-#149 as `v0.6.25-plan-serviceops-personal-work-queue`。
* Release covers design, static UI prototype, Portal homepage card, visual QA, and interaction QA。
* Release remains static demo only。
* No backend, DB, API, ServiceOps, ProjectOps, or deployment changes were made。
* Future work should start with API aggregation design。

## Task #152 API Aggregation Design

* Task #152 defines read-only API aggregation layer.
* Proposed primary endpoint: `/api/plan-serviceops/dashboard`.
* Sources: existing ServiceOps tickets and ProjectOps projects.
* No DB migration.
* No mutation.
* Future work should implement read-only API prototype before changing the frontend.

## Task #153 Read-only API Prototype

* Added `GET /api/plan-serviceops/dashboard`.
* API aggregates existing ServiceOps tickets and ProjectOps projects.
* API remains read-only.
* No DB migration.
* No new table.
* No mutation.
* Frontend remains static demo in this task.
* Future task can switch frontend to API with demo fallback.

The first API prototype keeps the personal work queue UI unchanged. The dashboard endpoint reads existing data only: it does not create tickets, update ticket status, update project status, write audit logs, or mutate ServiceOps or ProjectOps data.

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

## Task #177 Status and Attention Reason Design

* Task #177 separates main ticket status from attention reason.
* Main status becomes Pending / In Progress / Done.
* `Blocked` is no longer recommended as primary user-facing status.
* Waiting approval / vendor / user / schedule / evidence / budget / risk conditions move to attention_reason.
* This design improves supervisor visibility and protects operators by explaining why work is waiting.
* No frontend, backend, DB, API, fixture, or release changes were made.

## Task #178 Attention Reason Demo Data Update

* Task #178 updates Plan_ServiceOPS demo / aggregation response semantics.
* Blocked source status is normalized to Pending.
* Waiting / blocking reasons are exposed as `attention_reason`.
* API response now supports `status_label`, zh label, `attention_reason` label, `source_status`, `source_waiting_text`, and display badges.
* This prepares Task #179 frontend UI update.
* No DB, migration, ServiceOps source behavior, ProjectOps behavior, release, or deployment changes.

## Task #179 Frontend Attention Reason UI Update

* Task #179 updates `/plan-serviceops/` to render status + attention reason badges.
* Team Attention Queue now uses `display_badge` / `display_badge_zh`.
* `Blocked` is no longer the primary user-facing badge.
* Source status may remain available as trace metadata.
* API DATA and DEMO FALLBACK both support attention reason display.
* Viewer empty state remains safe.
* Dashboard remains read-only.
* No backend, DB, API, ServiceOps, ProjectOps, release, or deployment changes.

## Task #180 Attention Reason Visual QA

* Task #180 validates `/plan-serviceops/` attention reason UI.
* Supervisor role shows status + attention reason badges.
* Viewer role empty state remains safe.
* API DATA and DEMO FALLBACK both avoid `BLOCKED` as the primary badge.
* Badge layout and responsive behavior were checked.
* Dashboard remains read-only.
* No backend, DB, API, ServiceOps, ProjectOps, release, or deployment changes.

## Task #181 Attention Reason Release Note

* Task #181 packages Tasks #177-#180 as `v0.6.29-plan-serviceops-attention-reason-ui`.
* Release covers design, aggregation response shape, frontend badge UI, fallback behavior, and visual QA.
* Plan_ServiceOPS no longer uses `Blocked` as the primary user-facing badge.
* Scope remains read-only dashboard semantics; no DB, write API, ServiceOps / ProjectOps source behavior, release tag, or deployment changes.

## Task #183 Role-based Attention Queue Design

* Task #183 defines role-based visibility for Plan_ServiceOPS Team Attention Queue.
* It covers viewer, operator, supervisor, and admin.
* It defines endpoint-level and field-level visibility.
* It keeps `attention_reason` as a waiting / coordination explanation, not a blame label.
* It prepares Task #184 role-aware API prototype.
* No frontend, backend, DB, API, ServiceOps, ProjectOps, release, or deployment changes were made.

## Task #184 Role-based Attention Queue API Prototype

* Task #184 implements demo role filtering for the Plan_ServiceOPS read-only dashboard API.
* Uses `X-Demo-Role` for `viewer` / `operator` / `supervisor` / `admin`; missing or unknown values fall back to `viewer`.
* Adds `viewer` metadata, `visibility_note`, and `attention_reason_distribution`.
* Applies role-based `team_tickets` filtering: viewer receives aggregate-only attention distribution, operator receives personal / assigned demo scope, supervisor receives team scope, and admin receives cross-team safe metadata scope.
* Viewer 只看有限摘要，Team Attention 明細預設隱藏。
* `X-Demo-Role` is demo-only. It is not production authorization.
* The API remains read-only. It does not implement a write API, approval / reject action, DB migration, or ServiceOps / ProjectOps source-data mutation.
* Plan_ServiceOPS is daily operations planning, not employee surveillance or performance scoring.
* `attention_reason` explains waiting conditions. It is not a blame label.
* This prototype prepares a future frontend role display refinement.
