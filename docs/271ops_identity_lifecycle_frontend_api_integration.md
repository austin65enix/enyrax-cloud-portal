# 271Ops Identity Lifecycle Frontend API Integration

## Task summary

Task #218 adds Identity Lifecycle Governance frontend integration to `/271ops/`. The section consumes the Task #217 read-only fixture APIs and renders Access Verify / Identity Governance Readiness data for JML, review, exception, and evidence package governance.

## Frontend section added

`271ops/index.html` now includes `Identity Lifecycle Governance / 身分生命週期治理` with:

* Identity Lifecycle Summary Cards
* Lifecycle Breakdown
* Risk Breakdown
* Top Attention Items
* Recent Lifecycle Events
* Evidence Package Preview
* Safety Boundary

## APIs consumed

```text
GET /api/271ops/identity-lifecycle/dashboard
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
```

All frontend fetch calls use `method: "GET"`.

## API DATA / DEMO FALLBACK behavior

When all Identity Lifecycle APIs return valid read-only fixture responses, the badge displays:

```text
IDENTITY LIFECYCLE API DATA / 身分生命週期 API 資料
```

When an API fails, returns invalid schema, or returns empty records for list endpoints, the frontend renders local fallback data and displays:

```text
IDENTITY LIFECYCLE DEMO FALLBACK / 身分生命週期 DEMO 備援
```

The section remains nonblank and avoids JavaScript crash behavior.

## UI coverage

The UI covers:

* Total Events
* Open Queue
* Critical Findings
* High Risk Findings
* Overdue Reviews
* Expiring Exceptions
* Completed Evidence Packages
* Joiner / Mover / Leaver / Reviewer / Exception breakdown
* Critical / High / Medium / Low risk breakdown
* Attention items for failed, mismatched, overdue, review-required, critical, and high-risk records
* Recent lifecycle event metadata
* Evidence package preview metadata

## Safety boundary

The section displays:

* Read-only Access Verify layer
* No AD mutation
* No LDAP mutation
* No IAM mutation
* No SaaS permission mutation
* No approve / reject action
* No upload control
* No edit / delete action
* No password / credential / API key / private key
* No raw logs / raw BPM form body / raw attachment content
* Safe metadata only

## No-mutation guarantee

The frontend integration does not add approve / reject buttons, upload inputs, edit / delete buttons, localStorage writes, sessionStorage writes, write API calls, or POST / PUT / PATCH / DELETE fetch calls.

## Validation performed

Validation should include:

* `node --check` style JavaScript parse validation if extracted or available.
* `git diff --check`.
* `grep -R "fetch(" -n 271ops/index.html`.
* `grep -R "localStorage\|sessionStorage" -n 271ops/index.html`.
* `grep -R "POST\|PUT\|PATCH\|DELETE" -n 271ops/index.html`.
* API DATA manual/API route validation after Task #217.
* Visual QA in Task #219.

## Limitations

* Frontend integration only.
* Fixture-backed demo data only.
* No DB schema changes.
* No write API.
* No live IAM, AD, LDAP, HRM, BPM, or SaaS connector.
* Browser screenshot QA is deferred to Task #219.

## Recommended next task

* Task #219: 271Ops Identity Lifecycle Frontend Visual QA
