# Plan_ServiceOPS Role-based Attention Queue Design

Visibility rules for daily work planning and team attention management

## Overview

This document defines role-based visibility rules for Plan_ServiceOPS Team Attention Queue. The goal is to help each role see the right level of waiting, blocked-flow, and attention-reason information without exposing unnecessary team or personal operational details.

本文件定義 Plan_ServiceOPS Team Attention Queue 的角色分層可視規則。目標是讓不同角色看到合適層級的等待、卡關與注意原因資訊，同時避免不必要暴露團隊或個人的維運細節。

* This is a design document, not an implementation.
* Plan_ServiceOPS is for daily operations planning, not employee monitoring.
* `attention_reason` explains why work is waiting. It is not a performance punishment label.
* Team Attention Queue should help supervisors understand where coordination is needed while protecting operators.

## Role Model

| Role       | Purpose                                              |
| ---------- | ---------------------------------------------------- |
| viewer     | Limited overview and demo-safe attention summary     |
| operator   | Personal work queue and assigned attention items     |
| supervisor | Team attention queue and coordination view           |
| admin      | Cross-team operations visibility and governance view |

| Role       | 中文說明                   |
| ---------- | ---------------------- |
| viewer     | 有限總覽與 demo-safe 團隊注意摘要 |
| operator   | 個人今日待辦與被指派相關注意事項       |
| supervisor | 團隊注意事項與協調視角            |
| admin      | 跨團隊營運可視與治理視角           |

## Visibility Principles

1. Least visibility by default.
2. Operators should see work they own, are assigned to, or need to act on.
3. Supervisors should see team-level waiting reasons and coordination blockers.
4. Viewers should not see unnecessary owner-level or personal operational details.
5. Admins may see cross-team safe operational metadata.
6. Attention reasons explain why work is waiting; they should not become blame labels.
7. Team Attention Queue should protect operators by making external blockers visible.
8. Source status can be preserved as metadata, but user-facing status should remain simplified.
9. SLA / due date / risk indicators may be visible by role, but should be contextualized.
10. Future write actions must go through ServiceOps / AuditOps, not directly through Plan_ServiceOPS.

Plan_ServiceOPS 的角色分層不是為了監控個人，而是為了讓每日工作排序、團隊卡點與主管協調更清楚。

## Queue Types

| Queue                | 中文     | Purpose                                                                                                       |
| -------------------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| My Today Queue       | 我的今日待辦 | Shows work the current operator should handle today                                                           |
| Team Attention Queue | 團隊注意事項 | Shows waiting, blocked-flow, risk, SLA, approval, vendor, user, schedule, evidence, or budget attention items |

* My Today Queue 偏個人行動。
* Team Attention Queue 偏團隊協調。
* Team Attention Queue 不等於「所有卡住的票都給所有人看」。
* Team Attention Queue 應該依角色顯示不同粒度。

## Endpoint Visibility Matrix

Future Plan_ServiceOPS API design:

| Endpoint                                   | viewer                   | operator                      | supervisor                | admin                      |
| ------------------------------------------ | ------------------------ | ----------------------------- | ------------------------- | -------------------------- |
| GET /api/plan-serviceops/dashboard         | aggregate only           | personal + assigned attention | team attention            | cross-team attention       |
| GET /api/plan-serviceops/today-tickets     | hidden or empty          | own today tickets             | team member summary       | cross-team summary         |
| GET /api/plan-serviceops/team-tickets      | count / summary only     | assigned project/team subset  | full team attention queue | cross-team attention queue |
| GET /api/plan-serviceops/project-deadlines | public/demo-safe summary | assigned projects             | team projects             | cross-team projects        |
| GET /api/plan-serviceops/summary           | aggregate only           | personal + assigned summary   | team summary              | cross-team summary         |

* viewer 預設不看 `team_tickets` 明細。
* operator 不應看到其他團隊的所有 attention ticket。
* supervisor 可看 team queue，但不應變成逐人監控。
* admin 可看跨團隊 safe operational metadata，但仍應避免不必要個人化曝光。

## Field-level Visibility Matrix

Team ticket field visibility:

| Field                       | viewer               | operator          | supervisor                       | admin |
| --------------------------- | -------------------- | ----------------- | -------------------------------- | ----- |
| ticket_id                   | hidden or demo-safe  | assigned          | team                             | yes   |
| source_id                   | hidden               | assigned          | team                             | yes   |
| type                        | aggregate            | yes               | yes                              | yes   |
| title                       | safe summary         | assigned          | team                             | yes   |
| owner                       | hidden               | own / assigned    | team-visible or masked by policy | yes   |
| status                      | yes                  | yes               | yes                              | yes   |
| status_label / zh           | yes                  | yes               | yes                              | yes   |
| attention_reason            | aggregate or summary | assigned          | yes                              | yes   |
| attention_reason_label / zh | yes                  | yes               | yes                              | yes   |
| source_status               | hidden               | trace if assigned | trace metadata                   | yes   |
| source_waiting_text         | hidden               | assigned          | team                             | yes   |
| display_badge / zh          | yes                  | yes               | yes                              | yes   |
| waiting_reason              | hidden               | assigned          | team                             | yes   |
| sla                         | aggregate            | assigned          | team                             | yes   |
| due_at                      | hidden or coarse     | assigned          | team                             | yes   |
| source                      | hidden               | assigned          | team                             | yes   |

* viewer 主要看 aggregate / summary / demo-safe label。
* operator 主要看自己的與被指派範圍。
* supervisor 可看團隊層級細節，但要避免個人 ranking。
* admin 可看跨團隊 safe metadata。
* `source_waiting_text` 可能包含業務細節，viewer 不應看到。

## Role Behavior Design

### viewer

* Dashboard 可看 summary cards。
* Team Attention Queue 可為空或只顯示 aggregate count。
* 可看到 attention reason distribution，例如：
  * `waiting_approval: 4`
  * `waiting_vendor: 5`
* 不看 owner、ticket_id、`source_waiting_text`。
* 空狀態要顯示：
  * `No team attention tickets available for this role.`
  * `目前此角色沒有可顯示的團隊注意事項。`

### operator

* 可看自己的 My Today Queue。
* 可看自己負責、指派、或參與專案相關的 attention items。
* 可看 waiting reason 與 due date。
* 不看其他團隊的完整 queue。
* 若 ticket 等自己補 evidence / user clarification，應出現在 My Today Queue。

### supervisor

* 可看完整 team attention queue。
* 需要看 `attention_reason`、SLA、`due_at`、owner、`source_waiting_text`。
* 可依 `attention_reason` 分組：
  * Waiting Approval
  * Waiting Vendor
  * Waiting User Reply
  * Waiting Schedule
  * Waiting Evidence
  * Risk Attention
  * Budget Attention
* 不應顯示個人排名式 score。
* 目標是協調流程，不是責怪人。

### admin

* 可看跨團隊 attention queue。
* 可看 `source_status` trace metadata。
* 可做 governance / audit / operations review。
* 未來仍需 production auth policy。
* 不應直接在 Plan_ServiceOPS 執行 mutation，write flow 應回到 ServiceOps / AuditOps。

## Attention Reason Distribution

Future summary responses may include:

```json
{
  "attention_reason_distribution": {
    "waiting_approval": 4,
    "waiting_vendor": 5,
    "waiting_user_reply": 0,
    "waiting_schedule": 0,
    "waiting_evidence": 0,
    "risk_attention": 0,
    "budget_attention": 0
  }
}
```

| Role       | Distribution        |
| ---------- | ------------------- |
| viewer     | yes, aggregate only |
| operator   | assigned scope      |
| supervisor | team scope          |
| admin      | cross-team scope    |

* distribution 可讓 viewer 也知道團隊卡在哪裡，但不暴露個人 ticket 明細。
* supervisor 則可點進 team attention details。
* admin 可看跨團隊分布。

## Sorting and Priority Rules

Team Attention Queue sorting recommendation:

1. Critical / High risk。
2. SLA overdue。
3. Waiting Approval。
4. Waiting Vendor。
5. Waiting User Reply。
6. Waiting Schedule。
7. Waiting Evidence。
8. Budget Attention。
9. Due date ascending。
10. Created / updated time descending。

* 主管視角應優先看到需要決策或協調的項目。
* operator 視角應優先看到自己能立即處理的項目。
* viewer 視角只看 aggregate，不需要排序明細。

## API Role Source

The first version may reuse:

* `X-Demo-Role`
* existing demo role switcher
* fallback role: `viewer`

Future production authorization should use:

* authenticated user session
* team membership
* ticket owner / assignee
* project membership
* supervisor relationship
* admin policy

X-Demo-Role is for demo and development only. It is not production authorization.

X-Demo-Role 只適合 demo 與開發階段，不是正式 production 授權機制。

## UI Recommendation

### Viewer

* 顯示 Team Attention Summary。
* 顯示 attention reason distribution。
* Team Attention Queue 明細可空。

### Operator

* 顯示 My Today Queue。
* 顯示 Assigned Attention Items。
* Badge 使用：
  * `Pending · Waiting Approval`
  * `待處理 · 等待核准`

### Supervisor

* 顯示 Team Attention Queue。
* 可依 reason group / priority / SLA filter。
* `source_status` 顯示為小字 trace metadata。
* 不顯示 individual score ranking。

### Admin

* 顯示 cross-team attention summary。
* 提供 governance / audit review view。
* 不直接執行 mutation。

## Safety and Human Factors

* Attention reason is not a blame label.
* It should explain waiting conditions.
* It protects operators by showing why a ticket cannot move forward.
* It helps supervisors coordinate approval, vendor, user, schedule, evidence, risk, or budget blockers.
* It should not become a personal punishment or performance score.
* Source status is trace metadata, not the main user-facing message.

attention_reason 的目標是說明流程卡點，不是標記誰做得不好。它讓主管知道該協調什麼，也讓處理人員能被清楚理解與保護。

## Future Implementation Plan

* Phase 1：Document role model and attention queue visibility
* Phase 2：Add role-aware attention reason distribution to API
* Phase 3：Filter `team_tickets` by `X-Demo-Role` in Plan_ServiceOPS API
* Phase 4：Update frontend role switcher or reuse existing demo role session
* Phase 5：Add supervisor grouping by `attention_reason`
* Phase 6：Design approval / evidence / closure workflow integration
* Phase 7：Replace `X-Demo-Role` with production auth policy

## Task #184 Handoff

Next recommended task:

```text
Task #184：Plan_ServiceOPS Role-based Attention Queue API Prototype
```

Scope:

* Add role-aware filtering to Plan_ServiceOPS read-only API.
* Use `X-Demo-Role` for viewer / operator / supervisor / admin.
* Add viewer metadata and `visibility_note`.
* Add `attention_reason_distribution`.
* Keep API read-only.
* Do not implement production auth.
* Do not add write API.
* Do not modify ServiceOps source flow.

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
