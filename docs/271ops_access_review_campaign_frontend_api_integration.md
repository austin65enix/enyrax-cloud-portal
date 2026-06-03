# 271Ops Access Review Campaign Frontend API Integration

## Task Summary

Task #227 adds the Access Review Campaign / 權限覆核活動 section to `/271ops/` and connects it to the read-only fixture API from Task #226.

The frontend remains read-only. It does not add approval, rejection, upload, edit, delete, storage writes, or write API calls.

## Frontend Section Added

The new section is `#access-review-campaign-governance` in `271ops/index.html`.

It includes:

* Access Review Campaign Summary Cards
* Campaign Breakdown
* Risk Breakdown
* Reviewer Progress
* Top Attention Items
* Recent Campaigns
* Remediation Queue Preview
* Evidence Package Preview
* Safety Boundary

## APIs Consumed

```text
GET /api/271ops/access-review-campaigns/dashboard
GET /api/271ops/access-review-campaigns
GET /api/271ops/access-review-campaigns/active
GET /api/271ops/access-review-campaigns/overdue-items
GET /api/271ops/access-review-campaigns/remediation-queue
GET /api/271ops/access-review-campaigns/evidence-packages
```

All frontend fetch calls use `method: "GET"`.

## API DATA / DEMO FALLBACK Behavior

When all Access Review Campaign APIs return valid read-only schema, the mode badge shows:

```text
ACCESS REVIEW CAMPAIGN API DATA / 權限覆核活動 API 資料
```

When fetch fails, schema is invalid, or required record lists are empty, the frontend renders local fallback data and shows:

```text
ACCESS REVIEW CAMPAIGN DEMO FALLBACK / 權限覆核活動 DEMO 備援
```

The section should not render blank and should not crash JavaScript.

## UI Coverage

The section renders:

* Summary counts for campaigns, active campaigns, overdue items, high-risk items, exceptions, remediation, and completed evidence packages.
* Campaign type breakdown.
* Risk breakdown.
* Reviewer progress with completion rate.
* Top attention items.
* Recent campaigns.
* Remediation queue preview.
* Evidence package preview.
* Read-only safety boundary.

## Safety Boundary

Visible copy includes:

* Read-only Access Verify layer
* No AD mutation
* No LDAP mutation
* No IAM mutation
* No SaaS permission mutation
* No approve / reject action implemented
* No upload control
* No edit / delete action
* No password / credential / API key / private key
* No raw logs / raw BPM form body / raw attachment content
* Safe metadata only

## No-mutation Guarantee

The frontend integration does not add:

* approve / reject buttons
* upload input
* edit / delete buttons
* localStorage writes
* sessionStorage writes
* POST / PUT / PATCH / DELETE fetch calls
* write API calls

## Validation Performed

Recommended validation:

* `git diff --check`
* `node --check` against the inline script extracted from `271ops/index.html`
* `grep -n "access-review-campaigns" 271ops/index.html`
* `grep -n "ACCESS REVIEW CAMPAIGN API DATA\|ACCESS REVIEW CAMPAIGN DEMO FALLBACK" 271ops/index.html`
* `grep -n "localStorage\|sessionStorage" 271ops/index.html`
* `grep -n "POST\|PUT\|PATCH\|DELETE" 271ops/index.html`

## Limitations

* Frontend integration only.
* No backend changes in this task.
* No DB changes.
* No production deployment changes.
* Browser screenshot QA is deferred to Task #228.

## Recommended Next Task

* Task #228: 271Ops Access Review Campaign Frontend Visual QA
