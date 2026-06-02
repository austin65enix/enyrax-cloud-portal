# Plan_ServiceOPS Status and Attention Reason Design

Separating ticket progress state from blocking or attention reasons

## Overview

Plan_ServiceOPS should separate the main ticket progress status from the reason why a ticket needs attention. Instead of using Blocked as a primary status, the product should keep simple progress statuses and use attention_reason to explain waiting, approval, vendor, user, schedule, evidence, or risk conditions.

Plan_ServiceOPS 應該將工單的主要進度狀態，與需要注意或卡關的原因分開。不要把 Blocked 當成主要狀態，而是保留簡單的進度狀態，再用 attention_reason 說明等待核准、等待廠商、等待使用者、等待排程、等待證據或風險注意等情境。

* `Blocked` 不再建議作為 Plan_ServiceOPS 的主狀態。
* `Blocked` 可保留為內部技術語意或衍生顯示，但產品畫面優先使用 attention reason。
* 主狀態應該回答：「這張票處理到哪裡？」
* attention reason 應該回答：「為什麼這張票需要注意或暫時不能往下走？」
* 這樣可以保護處理人員，讓主管知道是流程卡住，不是沒有人處理。

## Product Positioning

Plan_ServiceOPS 是 ServiceOps 的每日作戰看板：幫個人知道今天該做什麼，也幫主管看到團隊哪裡卡住。

Plan_ServiceOPS is a daily operations cockpit for ServiceOps, helping operators know what to handle today and helping supervisors see where the team is blocked.

The goal is not only ticket tracking. The goal is priority planning, team attention visibility, and blocked-flow explanation.

Plan_ServiceOPS 的目標不只是工單追蹤，而是工作優先順序管理、團隊注意事項可視化，以及卡關原因說明。

## Main Status Design

| Status      | 中文  | Meaning          |
| ----------- | --- | ---------------- |
| Pending     | 待處理 | 已建立，等待處理、排程或前置條件 |
| In Progress | 處理中 | 已開始執行或正在處理       |
| Done        | 已完成 | 已完成並可留存紀錄        |

* `Pending` 可以包含尚未開始、等待排程、等待核准、等待使用者等情境。
* `In Progress` 表示處理人員已開始執行。
* `Done` 表示已完成，未來可接 evidence / audit / close record。
* 主狀態不應承載太多阻塞原因。
* `Blocked` 不作為主狀態，避免一般使用者誤解。

## Attention Reason Design

| Attention Reason   | 中文    | Meaning               |
| ------------------ | ----- | --------------------- |
| Waiting Approval   | 等待核准  | 等主管、變更、採購、維護窗口或預算核准   |
| Waiting Vendor     | 等待廠商  | 等 SI、原廠、維護商或外部服務商回覆   |
| Waiting User Reply | 等待使用者 | 等需求單位、使用者或業務窗口確認      |
| Waiting Schedule   | 等待排程  | 等維護時間、人力安排或作業窗口       |
| Waiting Evidence   | 等待證據  | 等處理紀錄、截圖、驗證結果或結案證據    |
| Risk Attention     | 風險注意  | 涉及資安、備份、容量、服務中斷或高影響風險 |
| Budget Attention   | 預算注意  | 涉及採購、費用、預算或成本中心確認     |
| None               | 無     | 沒有特別注意原因              |

* `attention_reason` 是輔助標籤，不是主狀態。
* 一張 ticket 可以先支援單一 attention_reason。
* 未來可擴充成多個 reasons array。
* `attention_reason = Waiting Approval` 時，主狀態通常仍是 `Pending`。
* `attention_reason = Risk Attention` 可與 `Pending` 或 `In Progress` 同時存在。

## Status and Attention Reason Examples

| Ticket Situation | Status      | Attention Reason   | Display     |
| ---------------- | ----------- | ------------------ | ----------- |
| 新工單尚未排程          | Pending     | None               | 待處理         |
| 等主管核准維護時間        | Pending     | Waiting Approval   | 待處理 · 等待核准  |
| 等廠商回覆報價或技術確認     | Pending     | Waiting Vendor     | 待處理 · 等待廠商  |
| 等使用者補充需求         | Pending     | Waiting User Reply | 待處理 · 等待使用者 |
| 已開始 patch 測試     | In Progress | Risk Attention     | 處理中 · 風險注意  |
| 已完成並補上截圖證據       | Done        | None               | 已完成         |
| 已完成但等待驗證截圖       | Done        | Waiting Evidence   | 已完成 · 等待證據  |

Blocked becomes a derived interpretation, not the primary status. For example, Pending + Waiting Approval can be interpreted as blocked by approval, but the user-facing display should be Waiting Approval.

Blocked 可以作為衍生解讀，而不是主要狀態。例如 Pending + Waiting Approval 可以理解成被簽核卡住，但使用者畫面優先顯示 Waiting Approval / 等待核准。

## UI Copy Recommendation

### English

```text
Status: Pending
Reason: Waiting Approval
```

### Chinese

```text
狀態：待處理
原因：等待核准
```

Card badge 建議：

```text
Pending · Waiting Approval
待處理 · 等待核准
```

不要只顯示：

```text
BLOCKED
```

* `BLOCKED` 可以保留為 internal / developer-level semantic。
* 對一般使用者，建議顯示 waiting reason。
* 如需警示，可用 amber badge 或 attention icon。
* `Blocked / 卡關` 可作為 secondary tooltip，而不是主標籤。

## Plan_ServiceOPS Layout Recommendation

| Section              | 中文     | Purpose                    |
| -------------------- | ------ | -------------------------- |
| My Today Queue       | 我的今日待辦 | 顯示今天我需要處理或補資料的 ticket      |
| Team Attention Queue | 團隊注意事項 | 顯示團隊目前等待、卡關、需要主管注意的 ticket |

### My Today Queue

包含：

* 指派給我的 ticket。
* 今天到期的 ticket。
* SLA 快到期的 ticket。
* 我正在處理中的 ticket。
* 需要我補資料或補 evidence 的 ticket。

### Team Attention Queue

包含：

* Waiting Approval。
* Waiting Vendor。
* Waiting User Reply。
* Waiting Schedule。
* Waiting Evidence。
* Risk Attention。
* Budget Attention。
* Critical / High priority tickets。
* SLA 快逾期 tickets。

## API and Data Model Concept

未來 Plan_ServiceOPS aggregation API 可回傳：

```json
{
  "ticket_id": 101,
  "title": "Linux Kernel CVE-2026-46333 remediation",
  "status": "pending",
  "status_label": "Pending",
  "status_label_zh": "待處理",
  "attention_reason": "waiting_approval",
  "attention_reason_label": "Waiting Approval",
  "attention_reason_label_zh": "等待核准",
  "priority": "high",
  "risk_level": "critical",
  "assignee": "infra-team",
  "due_date": "2026-06-05",
  "display_badge": "Pending · Waiting Approval",
  "display_badge_zh": "待處理 · 等待核准"
}
```

設計原則：

* API 可以保留 normalized enum。
* UI 顯示使用 label / zh label。
* `blocked` 可以由 `attention_reason != none` 或 specific reasons 推導，但不作為主狀態。
* 未來若 ServiceOps 仍有 blocked 狀態，Plan_ServiceOPS 可以在 aggregation layer 轉換為 `Pending + attention_reason`。

## Mapping from Existing Blocked

| Existing Status / Waiting Text | New Status             | Attention Reason                    |
| ------------------------------ | ---------------------- | ----------------------------------- |
| Blocked + Waiting approval     | Pending                | Waiting Approval                    |
| Blocked + Waiting vendor       | Pending                | Waiting Vendor                      |
| Blocked + Waiting user         | Pending                | Waiting User Reply                  |
| Blocked + Waiting schedule     | Pending                | Waiting Schedule                    |
| Blocked + Waiting evidence     | Pending or Done        | Waiting Evidence                    |
| Blocked + security risk        | Pending or In Progress | Risk Attention                      |
| Blocked + budget               | Pending                | Budget Attention                    |
| Blocked + unknown reason       | Pending                | Risk Attention or None with warning |

The aggregation layer should preserve the original source status as source_status if needed, but the Plan_ServiceOPS user-facing status should use the simplified model.

Aggregation layer 可以保留原始 source_status 供追蹤，但 Plan_ServiceOPS 使用者畫面應採用簡化後的 status + attention_reason。

## Role Consideration

### Operator

* 需要知道今天自己要做什麼。
* 需要知道哪些 ticket 等自己補資料或處理。
* 不需要看到所有團隊阻塞細節。

### Supervisor

* 需要看到 Team Attention Queue。
* 需要知道哪些 ticket 等核准、廠商、使用者、排程或預算。
* 需要看 blocked-flow reason，避免誤會工程師沒做事。

### Viewer

* 只看 aggregate / demo-safe status。
* 不看敏感個人處理細節。

### Admin

* 可看跨團隊狀態。
* 仍應避免把 attention reason 變成個人績效懲罰工具。

## Product Value

* 對 Operator：知道今天該先做什麼。
* 對 Supervisor：知道團隊哪裡卡住。
* 對 IT Manager：知道阻塞是流程、廠商、使用者、預算還是風險。
* 對工程師：避免被誤解成沒處理，因為卡關原因被清楚標示。
* 對企業：把工單狀態從單純 tracking 變成 operations planning。

This protects operators by showing why a ticket cannot move forward.

這個設計可以保護處理人員，因為它清楚顯示工單為什麼暫時不能往下一步。

## Non-goals

本任務不做：

* no frontend implementation
* no backend implementation
* no DB migration
* no API change
* no ServiceOps behavior change
* no ProjectOps behavior change
* no release tag
* no production workflow change

## Future Tasks

* Task #178：Plan_ServiceOPS Attention Reason Demo Data Update
* Task #179：Plan_ServiceOPS Frontend Attention Reason UI Update
* Task #180：Plan_ServiceOPS API Attention Reason Mapping
* Task #181：Plan_ServiceOPS Role-based Attention Queue Design
* Task #182：Plan_ServiceOPS Release Note

## Task #178 Attention Reason Demo Data Update

* Task #178 updates Plan_ServiceOPS demo / aggregation response semantics.
* Blocked source status is normalized to Pending.
* Waiting / blocking reasons are exposed as `attention_reason`.
* API response now supports `status_label`, zh label, `attention_reason` label, `source_status`, `source_waiting_text`, and display badges.
* This prepares Task #179 frontend UI update.
* No DB, migration, ServiceOps source behavior, ProjectOps behavior, release, or deployment changes.
