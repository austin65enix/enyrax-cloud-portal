# 271Ops Access Review Campaign Frontend Visual QA

## Task summary

Task #228 reviews the `/271ops/` Access Review Campaign frontend section integrated in Task #227. The QA focuses on public route availability, API DATA behavior, DEMO FALLBACK behavior, UI coverage, responsive/static layout risks, safety boundary copy, no-mutation guarantees, and DOM harness coverage.

No backend, DB, API, fixture, script, release, deployment, nginx, cron, systemd, production setting, or tag changes were made.

## Scope

Reviewed file:

* `271ops/index.html`

Reviewed frontend area:

* `/271ops/` Access Review Campaign / 權限覆核活動 section
* Access Review Campaign Summary Cards
* Campaign Breakdown
* Risk Breakdown
* Reviewer Progress
* Top Attention Items
* Recent Campaigns
* Remediation Queue Preview
* Evidence Package Preview
* Safety Boundary

## Public route check

`curl -I https://portal.soc-monitoring.dev/271ops/` returned HTTP 200.

Observed headers included:

```text
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 83070
```

## API DATA check

Public API validation was attempted against `https://portal.soc-monitoring.dev`.

Validated endpoints:

```text
GET /api/271ops/access-review-campaigns/dashboard
GET /api/271ops/access-review-campaigns
GET /api/271ops/access-review-campaigns/active
GET /api/271ops/access-review-campaigns/overdue-items
GET /api/271ops/access-review-campaigns/remediation-queue
GET /api/271ops/access-review-campaigns/evidence-packages
```

Public API result:

* All six public endpoints returned `{"detail":"Not Found"}` during QA.
* The public HTML route is live, but the public backend service had not loaded the Access Review Campaign API routes at QA time.
* Because public API DATA is unavailable, production browser rendering should use DEMO FALLBACK for this section until the backend service is reloaded or deployed with Task #226 routes.

Repo implementation validation was performed directly against the read-only helper functions in `backend/main.py` without changing or restarting services.

Repo helper results:

* `dashboard`: `product=271ops`, `mode=read_only`, `source=fixture`, `warnings=[]`
* `campaigns`: `count=4`, `product=271ops`, `mode=read_only`, `source=fixture`, `warnings=[]`
* `active`: `count=3`, `product=271ops`, `mode=read_only`, `source=fixture`, `warnings=[]`
* `overdue`: `count=1`, `product=271ops`, `mode=read_only`, `source=fixture`, `warnings=[]`
* `remediation`: `count=3`, `product=271ops`, `mode=read_only`, `source=fixture`, `warnings=[]`
* `evidence`: `count=4`, `product=271ops`, `mode=read_only`, `source=fixture`, `warnings=[]`

Confirmed dashboard fields available for frontend rendering:

* `summary`
* `campaign_breakdown`
* `risk_breakdown`
* `reviewer_progress`
* `top_attention_items`
* `recent_campaigns`

## DEMO FALLBACK check

Static/DOM harness confirmed both display strings exist and render correctly:

* `ACCESS REVIEW CAMPAIGN API DATA / 權限覆核活動 API 資料`
* `ACCESS REVIEW CAMPAIGN DEMO FALLBACK / 權限覆核活動 DEMO 備援`

The frontend validates dashboard shape and list endpoint records. If any campaign API fails, returns invalid schema, or returns empty records, it renders `campaignFallback`, displays the DEMO FALLBACK badge, and keeps the section nonblank.

## UI coverage checklist

| Check | Result | Evidence |
| --- | --- | --- |
| Access Review Campaign Summary Cards | Pass | `#campaign-summary-cards` exists and DOM harness rendered nonblank cards. |
| Campaign Breakdown | Pass | `#campaign-breakdown` exists and DOM harness rendered nonblank cards. |
| Risk Breakdown | Pass | `#campaign-risk-breakdown` exists and DOM harness rendered nonblank cards. |
| Reviewer Progress | Pass | `#campaign-reviewer-progress` exists and DOM harness rendered nonblank cards. |
| Top Attention Items | Pass | `#campaign-attention-items` exists and DOM harness rendered nonblank cards. |
| Recent Campaigns | Pass | `#campaign-recent-campaigns` exists and DOM harness rendered nonblank cards. |
| Remediation Queue Preview | Pass | `#campaign-remediation-queue` exists and DOM harness rendered nonblank cards. |
| Evidence Package Preview | Pass | `#campaign-evidence-packages` exists and DOM harness rendered nonblank cards. |
| Safety Boundary | Pass | Access Review Campaign safety boundary copy exists in the section. |

## Responsive QA checklist

Static CSS review result:

* Desktop: campaign summary cards use `.account-kpis` with `auto-fit` and `minmax(170px,1fr)`.
* Desktop: data areas use `.account-grid` with `repeat(3,minmax(0,1fr))`.
* Tablet: `@media(max-width:980px)` collapses `.account-grid` to one column and `.account-kpis` to two columns.
* Mobile: `@media(max-width:600px)` collapses `.account-kpis` and `.field-grid` to one column.
* Long IDs and notes are protected by `overflow-wrap:anywhere` and `word-break:break-word` in `.account-card` and `.field`.
* The page root keeps `max-width:100%` and `overflow-x:hidden`.
* Account Governance and Identity Lifecycle sections remain present and use separate IDs and render targets.

## Safety boundary checklist

Confirmed visible Access Review Campaign safety boundary copy includes:

| Safety item | Result |
| --- | --- |
| Read-only Access Verify layer | Pass |
| No AD mutation | Pass |
| No LDAP mutation | Pass |
| No IAM mutation | Pass |
| No SaaS permission mutation | Pass |
| No approve / reject action implemented | Pass |
| No upload control | Pass |
| No edit / delete action | Pass |
| No password / credential / API key / private key | Pass |
| No raw logs / raw BPM form body / raw attachment content | Pass |
| Safe metadata only | Pass |

## No-mutation checklist

Static scan and DOM harness result:

| Check | Result | Notes |
| --- | --- | --- |
| No approve / reject button | Pass | No `<button>` elements are present. Approval/rejection words appear only as read-only metadata or safety copy. |
| No upload input | Pass | No file input exists. |
| No edit / delete button | Pass | No `<button>` elements are present. Edit/delete words appear only in safety copy. |
| No localStorage write | Pass | No `localStorage` reference found. |
| No sessionStorage write | Pass | No `sessionStorage` reference found. |
| No POST / PUT / PATCH / DELETE fetch | Pass | No write fetch method found. |
| Fetch only uses GET/default GET | Pass | Campaign fetch helper uses `method: "GET"`; main dashboard default fetch is GET. |
| No new write API call | Pass | Access Review Campaign frontend calls only read-only `/api/271ops/access-review-campaigns...` GET endpoints. |

## JS / DOM harness result

One-time Node VM DOM harness result:

```text
api data render: badge=ACCESS REVIEW CAMPAIGN API DATA / 權限覆核活動 API 資料, nonblank=true, methodsOk=true, errors=[]
fetch-error fallback: badge=ACCESS REVIEW CAMPAIGN DEMO FALLBACK / 權限覆核活動 DEMO 備援, nonblank=true, methodsOk=true, errors=[]
invalid-schema fallback: badge=ACCESS REVIEW CAMPAIGN DEMO FALLBACK / 權限覆核活動 DEMO 備援, nonblank=true, methodsOk=true, errors=[]
empty-records fallback: badge=ACCESS REVIEW CAMPAIGN DEMO FALLBACK / 權限覆核活動 DEMO 備援, nonblank=true, methodsOk=true, errors=[]
htmlChecks.safetyBoundary=true
htmlChecks.noStorageWrites=true
htmlChecks.noWriteFetchMethods=true
htmlChecks.noButtons=true
htmlChecks.noUploadInput=true
```

The harness checked:

* API DATA render
* fetch-error fallback
* invalid-schema fallback
* empty records / empty dashboard nonblank fallback
* safety boundary exists
* GET-only fetch methods
* no storage writes
* no blocking console errors

## Browser screenshot QA result or limitation

Browser screenshot QA was not run because no Chromium/Chrome binary is available in this environment.

Checked commands:

```text
command -v chromium-browser
command -v chromium
command -v google-chrome
```

No browser binary was available. QA used public route curl, public API curl, repo helper validation, static CSS review, and Node VM DOM harness validation instead.

## Findings

* Public `/271ops/` route returned HTTP 200.
* Public Access Review Campaign API endpoints returned `Not Found`, so public API DATA cannot render until the backend service is reloaded or deployed with the Task #226 routes.
* Repo implementation returns valid read-only fixture responses for all six campaign endpoints when invoked from the current codebase.
* Frontend DEMO FALLBACK behavior is valid for fetch errors, invalid schema, and empty record responses.
* Empty records / empty dashboard conditions do not blank the section; fallback data renders nonblank campaign cards.
* Required UI sections and safety boundary copy are present and readable by static/DOM review.
* No frontend mutation controls, storage writes, or write API calls were found.
* Account Governance and Identity Lifecycle sections remain present and use separate render targets.

## Limitations

* Browser screenshot QA was not run due missing Chromium/Chrome binary.
* Public API DATA could not be confirmed because the public backend returned `Not Found` for all six Access Review Campaign API paths.
* Local running `127.0.0.1:8000` service also returned `Not Found`, indicating that process was likely stale relative to the repo route definitions.
* DOM behavior was validated with a mock DOM harness rather than a full browser automation run.
* QA did not modify frontend, backend, DB, API, fixtures, scripts, release files, deployment files, nginx, cron, systemd, production settings, or tags.

## Recommended next task

Task #229: 271Ops Access Review Campaign Release Note
