# 271Ops Identity Lifecycle Release Note

## Release summary

This release note covers Task #214 through Task #219. 271Ops now includes Identity Lifecycle Governance / 身分生命週期治理 capability.

The work extends 271Ops from Account Governance into a broader JML + Review + Exception + Evidence Package governance model. It is a read-only Access Verify / Identity Governance Readiness layer. It is not an IAM mutation system and does not directly change AD, LDAP, IAM, HRM, BPM, SaaS, or ServiceOps records.

## Task coverage

* Task #214: Identity Lifecycle Governance Design
* Task #215: Identity Lifecycle Demo Fixture Design
* Task #216: Identity Lifecycle Read-only Fixture API Design
* Task #217: Identity Lifecycle Read-only Fixture API Prototype
* Task #218: Identity Lifecycle Frontend API Integration
* Task #219: Identity Lifecycle Frontend Visual QA

## Feature coverage

* Identity Lifecycle Summary Cards
* Lifecycle Breakdown
* Risk Breakdown
* Top Attention Items
* Recent Lifecycle Events
* Evidence Package Preview
* Safety Boundary

## Lifecycle model

* Joiner: 入職帳號建立與權限開通驗證
* Mover: 調職、部門異動、角色變更、權限調整驗證
* Leaver: 離職、停權、帳號回收、群組移除驗證
* Reviewer: 定期權限覆核
* Exception: 例外保留與到期追蹤
* Evidence Package: 稽核證據包

## Fixture coverage

* `data/271ops/identity-lifecycle/demo_identity_lifecycle_events.json`
* `data/271ops/identity-lifecycle/demo_identity_lifecycle_queue.json`
* `data/271ops/identity-lifecycle/demo_identity_lifecycle_exceptions.json`
* `data/271ops/identity-lifecycle/demo_identity_lifecycle_reviews.json`
* `data/271ops/identity-lifecycle/demo_identity_lifecycle_evidence_packages.json`

## API coverage

```text
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
GET /api/271ops/identity-lifecycle/dashboard
```

The API is fixture-backed and read-only. It uses an allowlisted fixture loader and returns safe warnings instead of raw stack traces for missing or invalid fixture states.

## Frontend behavior

When the Identity Lifecycle APIs succeed and return valid schema, `/271ops/` displays:

```text
IDENTITY LIFECYCLE API DATA / 身分生命週期 API 資料
```

When API calls fail, schema is invalid, or list records are empty, `/271ops/` displays:

```text
IDENTITY LIFECYCLE DEMO FALLBACK / 身分生命週期 DEMO 備援
```

The section must not render as a blank area and must not crash JavaScript. Local fallback data keeps the Identity Lifecycle Governance section visible when the API is unavailable.

## QA summary from Task #219

* Public `/271ops/` route check: HTTP 200.
* Identity Lifecycle API DATA check: local Task #217 API returned valid dashboard summary, lifecycle_breakdown, risk_breakdown, recent_events, top_attention_items, and list records.
* DEMO FALLBACK check: API DATA and DEMO FALLBACK strings were present; frontend fallback path is triggered for API failure, invalid schema, or empty records.
* UI coverage check: Summary Cards, Lifecycle Breakdown, Risk Breakdown, Top Attention Items, Recent Lifecycle Events, Evidence Package Preview, and Safety Boundary were present.
* Responsive QA check: static review confirmed reuse of existing responsive grid/card classes and media queries.
* Safety boundary check: required no-mutation and safe metadata copy was present.
* No-mutation scan: no `localStorage`, `sessionStorage`, `POST`, `PUT`, `PATCH`, or `DELETE` strings were found in `271ops/index.html`; Identity Lifecycle fetch helper uses `method: "GET"`.
* JS / DOM harness result: `identity lifecycle DOM/static harness ok`.
* Browser screenshot QA result: not run because no Chromium/Chrome binary was available in the environment.
* Public API limitation: public backend returned `{"detail":"Not Found"}` for the new identity lifecycle API path during QA, so backend service reload/deploy verification remains required for public API DATA rendering.

## Safety boundary

* Read-only Access Verify layer
* No AD mutation
* No LDAP mutation
* No IAM mutation
* No SaaS permission mutation
* No approve / reject action
* No upload control
* No edit / delete action
* No localStorage write
* No sessionStorage write
* No write API call
* No password / credential / API key / private key
* No raw logs
* No raw BPM form body
* No raw attachment content
* Safe metadata only

## Product positioning

271Ops now covers:

* Account Governance
* Identity Lifecycle Governance
* Access Review
* Exception Tracking
* Evidence Package
* ServiceOps-linked remediation governance

This strengthens 271Ops as:

* Identity Governance Readiness Platform
* Access Verify layer
* Audit Evidence layer

271Ops does not replace AD, LDAP, IAM, HRM, BPM, or SaaS admin consoles. Source systems remain responsible for identity records, permission administration, HR events, workflow approval, and actual access changes.

## Limitations

* Fixture-backed read-only demo.
* No live IAM connector.
* No HRM connector.
* No BPM connector.
* No mutation workflow.
* No production identity write path.
* Public backend API route required reload/deploy verification during Task #219 QA.
* Browser screenshot QA was not run because no Chromium/Chrome binary was available in this environment.

## Recommended next task

* Task #221: 271Ops Identity Lifecycle Release QA and Backlog Review
