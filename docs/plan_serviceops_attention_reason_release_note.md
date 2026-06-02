# Plan_ServiceOPS Attention Reason Release Note

Version: `v0.6.29-plan-serviceops-attention-reason-ui`

## Replacing user-facing Blocked status with status plus attention reason

## Overview

Plan_ServiceOPS Attention Reason UI improves the daily operations cockpit by separating ticket progress status from the reason a ticket needs attention. Instead of showing Blocked as the primary user-facing badge, the dashboard now displays clearer status plus attention reason labels such as Pending · Waiting Approval or In Progress · Waiting Vendor.

Plan_ServiceOPS Attention Reason UI 將工單進度狀態與需要注意的原因分開，改善每日作戰看板的可讀性。畫面不再把 Blocked 當成主要使用者 badge，而是顯示更清楚的狀態加原因，例如「待處理 · 等待核准」或「處理中 · 等待廠商」。

* `Blocked` 不再是 Plan_ServiceOPS 的主要使用者顯示語言。
* `Blocked` 可保留為 `source_status` / internal semantic。
* 使用者畫面優先顯示 `status + attention_reason`。
* 這讓主管更容易理解團隊卡點。
* 這也保護處理人員，避免被誤解成沒處理。

## Completed Scope

* Task #177：Plan_ServiceOPS Status and Attention Reason Design
* Task #178：Plan_ServiceOPS Attention Reason Demo Data Update
* Task #179：Plan_ServiceOPS Frontend Attention Reason UI Update
* Task #180：Plan_ServiceOPS Attention Reason Visual QA
* Task #181：Plan_ServiceOPS Attention Reason Release Note

## Key Changes

### Status Simplification

| Main Status | 中文 | Meaning |
| ----------- | --- | ------- |
| Pending | 待處理 | Waiting for handling, scheduling, approval, or prerequisite |
| In Progress | 處理中 | Work has started or is being processed |
| Done | 已完成 | Work is completed and can be recorded |

* `blocked` source status is normalized to `pending` for Plan_ServiceOPS display。
* User-facing status should answer：這張票處理到哪裡？
* Attention reason should answer：為什麼這張票需要注意或暫時不能往下走？

### Attention Reason Model

| `attention_reason` | Label | 中文 |
| ------------------ | ----- | --- |
| `waiting_approval` | Waiting Approval | 等待核准 |
| `waiting_vendor` | Waiting Vendor | 等待廠商 |
| `waiting_user_reply` | Waiting User Reply | 等待使用者 |
| `waiting_schedule` | Waiting Schedule | 等待排程 |
| `waiting_evidence` | Waiting Evidence | 等待證據 |
| `risk_attention` | Risk Attention | 風險注意 |
| `budget_attention` | Budget Attention | 預算注意 |
| `none` | None | 無 |

### API / Aggregation Response

API team ticket 現在支援：

* `status`
* `status_label`
* `status_label_zh`
* `attention_reason`
* `attention_reason_label`
* `attention_reason_label_zh`
* `source_status`
* `source_waiting_text`
* `display_badge`
* `display_badge_zh`

範例：

```json
{
  "status": "pending",
  "status_label": "Pending",
  "status_label_zh": "待處理",
  "attention_reason": "waiting_approval",
  "attention_reason_label": "Waiting Approval",
  "attention_reason_label_zh": "等待核准",
  "source_status": "blocked",
  "source_waiting_text": "Waiting approval",
  "display_badge": "Pending · Waiting Approval",
  "display_badge_zh": "待處理 · 等待核准"
}
```

### Frontend Badge UI

* Team Attention Queue now prefers `display_badge` / `display_badge_zh`.
* Old blocked-like data falls back to:
  * `Pending · Waiting Approval`
  * `待處理 · 等待核准`
* Unknown blocked-like data falls back to:
  * `Pending · Attention Needed`
  * `待處理 · 需要注意`
* `source_status` is shown only as weak trace metadata, not primary badge.

### Visual QA

* Supervisor API DATA checked.
* Viewer empty state checked.
* DEMO FALLBACK checked.
* Mobile badge wrapping checked.
* No primary `BLOCKED` badge remains.
* Dashboard remains read-only.

## Current Verification

Verified against production on 2026-06-02:

* `/plan-serviceops/`: HTTP 200.
* Supervisor role / scope: `supervisor` / `team`.
* Supervisor Team Attention Queue count: `9`.
* First badge: `In Progress · Waiting Vendor`.
* First badge zh: `處理中 · 等待廠商`.
* First status / reason / source status: `in_progress` / `waiting_vendor` / `pending`.
* Supervisor statuses: `in_progress`, `pending`.
* Supervisor attention reasons: `waiting_approval`, `waiting_vendor`.
* Supervisor warnings: `[]`.
* Viewer role / scope: `viewer` / `limited`.
* Viewer Team Attention Queue count: `0`.
* Viewer warnings: `[]`.

## Product Value

### For Operators

* 更清楚知道哪些工單只是等待前置條件。
* 不會被單純的 `Blocked` 誤解。
* 處理紀錄與等待原因更容易說明。

### For Supervisors

* 可以看到團隊哪裡卡住。
* 可區分等待核准、等待廠商、等待使用者、等待排程、等待證據、風險與預算。
* 可以更快決策或協調。

### For IT Managers

* 將 ticket tracking 提升為 operations planning。
* 能看出阻塞來自流程、外部廠商、使用者、預算或風險。
* 更適合管理每日作戰與團隊注意事項。

### For Engineers

This protects operators by showing why a ticket cannot move forward.

這個設計可以保護處理人員，因為它清楚顯示工單為什麼暫時不能往下一步。

## Before / After

| Before | After |
| ------ | ----- |
| `BLOCKED` | `Pending · Waiting Approval` |
| `Blocked` as primary status | `Pending` as status + `Waiting Approval` as reason |
| Hard for supervisors to know why blocked | Reason is visible directly |
| Easy to blame operator | Clear waiting reason protects operator |
| Ticket tracking | Operations planning |

這一版的重點不是改一個 badge，而是把「卡住」轉換成「目前狀態 + 卡關原因」。

## Scope Boundary

本 release 不包含：

* no DB migration
* no ServiceOps source behavior change
* no ProjectOps source behavior change
* no write API
* no approval workflow implementation
* no mutation
* no production workflow change
* no release tag yet
* no deployment config change

This release changes Plan_ServiceOPS aggregation and UI semantics. It does not change the underlying ServiceOps / ProjectOps workflows. Existing source status may still be preserved as `source_status`.

## Known Limitations

* Current production data may only contain waiting approval / vendor until more real cases exist.
* Some attention reasons are currently covered by fallback demo data.
* Full role-based attention queue design is still future work.
* Approval workflow is not implemented.
* Budget / evidence / schedule reasons need more production examples.
* Visual QA used static responsive checks if browser screenshot tooling was unavailable.

## Prepared Release Tag

Task #182 should create the prepared release tag. Task #181 does not create the tag.

```bash
git tag v0.6.29-plan-serviceops-attention-reason-ui
```

## Recommended Next Steps

* Task #182：Plan_ServiceOPS Attention Reason Release Tag
* Task #183：Plan_ServiceOPS Role-based Attention Queue Design
* Task #184：Plan_ServiceOPS Attention Reason API Refinement
* Task #185：Plan_ServiceOPS Approval Workflow Design
* Task #186：Plan_ServiceOPS Evidence / Closure Integration Design
* Task #187：Plan_ServiceOPS Screenshot Baseline
