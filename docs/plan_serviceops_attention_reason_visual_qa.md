# Plan_ServiceOPS Attention Reason Visual QA

## Overview

This document records Task #180 visual QA. The QA validates the Plan_ServiceOPS transition from a primary `Blocked` status badge to the `status + attention_reason` display model.

本文件記錄 Task #180 visual QA，驗證 Plan_ServiceOPS 從 `Blocked` 主狀態改為 `status + attention_reason` 顯示模型。

## Reviewed Page

* `/plan-serviceops/`
* API: `GET /api/plan-serviceops/dashboard`

## Visual QA Scope

* API DATA supervisor state.
* API DATA viewer empty state.
* DEMO FALLBACK state.
* Desktop, laptop, tablet, and mobile responsive review.
* Badge layout and attention reason style mapping.
* Read-only boundary and no mutation check.

## API Verification

Verified against `https://portal.soc-monitoring.dev` on 2026-06-02:

* `/plan-serviceops/`: HTTP `200 OK`.
* Supervisor role / scope: `supervisor` / `team`.
* Supervisor team_count: `9`.
* first_badge: `In Progress · Waiting Vendor`.
* first_badge_zh: `處理中 · 等待廠商`.
* Supervisor statuses: `in_progress`, `pending`.
* Supervisor attention_reasons: `waiting_approval`, `waiting_vendor`.
* Supervisor source_status for the first ticket: `pending`.
* Supervisor warnings: `[]`.
* Viewer role / scope: `viewer` / `limited`.
* Viewer team_count: `0`.
* Viewer warnings: `[]`.

## Responsive QA

Browser screenshot tooling was not available, so this QA used static HTML/CSS responsive checks and API validation.

執行環境沒有可用的瀏覽器截圖工具，因此本次 QA 以 HTML/CSS responsive 檢查與 API 驗證為主。

Static checks covered:

* Desktop `1440 x 1200`: summary cards remain a five-column grid and dashboard remains a two-column layout.
* Laptop `1366 x 900`: Team Attention Queue badges remain readable in the two-column dashboard.
* Tablet `820 x 1180`: the `max-width: 940px` breakpoint changes the dashboard to one column and the summary cards to three columns.
* Mobile `390 x 844`: the `max-width: 560px` breakpoint changes summary cards to two columns and attention badges to full-width blocks.
* Mobile wide `430 x 932`: `source_status` remains small trace text and does not compete with the main badge.
* Badge CSS uses `min-width: 0`, `max-width: 100%`, `overflow-wrap: anywhere`, and `word-break: break-word`.

## Badge QA

* API DATA renders `display_badge` and `display_badge_zh`.
* English `display_badge` can wrap and Chinese `display_badge_zh` remains visible.
* Badge layout does not compress the title or SLA / due date lines.
* `Status:` / `Reason:` and `狀態：` / `原因：` detail lines remain readable.
* `source_status` is retained only as weak trace text.
* No primary `BLOCKED` badge is rendered.
* Style mapping covers waiting reasons as amber, `risk_attention` as red, `budget_attention` as gold, and `none` as neutral. Additional mappings use violet for `waiting_schedule` and cyan for `waiting_evidence`.
* Badge text communicates the state without relying only on color.

## Empty State QA

Viewer API DATA returns an empty Team Attention Queue. The UI renders:

```text
No team attention tickets available for this role.
目前此角色沒有可顯示的團隊注意事項。
```

The empty result does not introduce `undefined`, `null`, or `NaN` output.

## Fallback QA

API failure, non-200 response, invalid JSON, or invalid schema enters DEMO FALLBACK. Local demo data uses `display_badge` and `display_badge_zh`.

The legacy blocked-like fallback ticket renders:

```text
Pending · Waiting Approval
待處理 · 等待核准
```

Legacy `blocked` input is normalized and is not rendered as the primary badge.

## Read-only Boundary

* No create, update, approve, or reject button was added.
* The dashboard fetch call remains `GET /api/plan-serviceops/dashboard`.
* No mutation API call or backend write was added.
* No `localStorage` write exists in `/plan-serviceops/`.
* The Today Ticket demo toggle remains limited to fallback local memory.
* `API mode is read-only.`
* `API 模式為唯讀。`

## Issues Found

The static review found a narrow-screen badge overflow risk. Task #180 added scoped CSS wrapping guards and a mobile full-width badge layout.

No blocking visual issues found.

未發現阻塞性的視覺問題。

## Decision

Task #180 visual QA passed. Plan_ServiceOPS attention reason UI is ready for release note preparation.

Task #180 視覺 QA 通過。Plan_ServiceOPS attention reason UI 可進入 release note 整理。
