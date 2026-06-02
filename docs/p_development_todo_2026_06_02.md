# P_開發待辦事項 0602

Plan_ServiceOPS development backlog captured from the 2026-06-02 work stream.

## Context

0602 的主線是把 Plan_ServiceOPS 從單純個人工作佇列，推進到更清楚的 daily operations planning dashboard：

* 已完成 API-backed read-only dashboard。
* 已完成 `status + attention_reason` 顯示語意。
* 已完成 Team Attention Queue 不再以 `Blocked` 作為主要使用者 badge。
* 已完成 visual QA 與 release note。
* 下一步應補上 release tag、角色可視規則落地、API refinement、approval / evidence flow 設計與 screenshot baseline。

## Completed on 0602

| Task | Status | Output |
| ---- | ------ | ------ |
| Task #177 | Done | Plan_ServiceOPS Status and Attention Reason Design |
| Task #178 | Done | Attention Reason Demo Data Update |
| Task #179 | Done | Frontend Attention Reason UI Update |
| Task #180 | Done | Attention Reason Visual QA |
| Task #181 | Done | Attention Reason Release Note |

Release package:

```text
v0.6.29-plan-serviceops-attention-reason-ui
```

## Priority Development Backlog

### P0 - Release Tag

Task #182：Plan_ServiceOPS Attention Reason Release Tag

Acceptance criteria:

* Create git tag `v0.6.29-plan-serviceops-attention-reason-ui`.
* Confirm tag points to the commit containing Tasks #177-#181.
* Update release tracking if required.
* Do not change production behavior.

Command:

```bash
git tag v0.6.29-plan-serviceops-attention-reason-ui
```

### P1 - Role-based Attention Queue API Refinement

Task #183 / #184 follow-up：Role-based visibility implementation hardening

Acceptance criteria:

* Keep `X-Demo-Role` limited to demo / development.
* Confirm viewer receives aggregate-only Team Attention data.
* Confirm operator receives personal / assigned scope only.
* Confirm supervisor receives team attention details.
* Confirm admin receives cross-team safe metadata.
* Keep API read-only.
* Do not add DB migration or write endpoints.

Fields to verify:

* `viewer`
* `visibility_note`
* `attention_reason_distribution`
* `team_tickets`
* `display_badge`
* `display_badge_zh`
* `source_status`

### P1 - Frontend Role Views

Task：Plan_ServiceOPS role-aware frontend display refinement

Acceptance criteria:

* Viewer shows empty Team Attention Queue details plus aggregate distribution.
* Operator copy makes clear the queue is personal / assigned.
* Supervisor copy makes clear the queue is team coordination, not personal ranking.
* Admin view stays governance-oriented.
* No individual score / ranking UI is introduced.
* Empty states avoid `undefined`, `null`, or `NaN`.

### P2 - Approval Workflow Design

Task #185：Plan_ServiceOPS Approval Workflow Design

Acceptance criteria:

* Define how approval-related tickets are surfaced in Plan_ServiceOPS.
* Keep mutations in ServiceOps / Audit flow, not directly in Plan_ServiceOPS.
* Define required audit evidence for approve / reject actions.
* Define read-only Plan_ServiceOPS behavior before write workflow exists.
* Include security and role boundaries.

### P2 - Evidence / Closure Integration Design

Task #186：Plan_ServiceOPS Evidence / Closure Integration Design

Acceptance criteria:

* Define how waiting evidence appears in My Today Queue and Team Attention Queue.
* Define closure evidence states.
* Define relationship to ServiceOps worklog / closure records.
* Avoid duplicating ticket source data.
* Keep Plan_ServiceOPS as aggregation and planning layer.

### P2 - Screenshot Baseline

Task #187：Plan_ServiceOPS Screenshot Baseline

Acceptance criteria:

* Capture desktop, laptop, tablet, and mobile baselines.
* Cover API DATA supervisor state.
* Cover viewer empty state.
* Cover DEMO FALLBACK state.
* Verify attention badges wrap correctly on mobile.
* Verify no primary `BLOCKED` badge appears.

## Verification Checklist

Use these checks before closing the 0602 backlog:

```text
/plan-serviceops/ returns HTTP 200
GET /api/plan-serviceops/dashboard returns dashboard JSON
viewer role returns no team ticket details
supervisor role returns team attention tickets
display_badge uses Status · Attention Reason
display_badge_zh uses 中文狀態 · 中文原因
source_status is weak trace metadata only
dashboard remains read-only
no create / update / approve / reject button is added
no DB migration is added
no ServiceOps / ProjectOps source behavior is changed
```

## Demo Talking Point

中文：

```text
Plan_ServiceOPS 現在不只顯示工單是否卡住，而是把「目前處理狀態」和「需要注意的原因」分開。主管可以看出是等待核准、等待廠商、等待使用者、等待證據或風險注意；工程師也不會被單純的 Blocked 標籤誤解。
```

English:

```text
Plan_ServiceOPS now separates progress status from attention reason. Instead of showing Blocked as the main badge, it explains whether the item is waiting for approval, vendor response, user reply, evidence, schedule, budget, or risk coordination.
```

## Scope Boundary

This backlog does not include:

* production authorization replacement
* write API
* ticket mutation
* approval / reject implementation
* DB migration
* ServiceOps source workflow change
* ProjectOps source workflow change
