# 271Ops Identity Lifecycle Frontend Visual QA

## Task summary

Task #219 reviews the `/271ops/` Identity Lifecycle Governance frontend section added by Task #218. The QA focuses on API DATA behavior, DEMO FALLBACK behavior, UI coverage, responsive/static layout risks, safety boundary copy, and no-mutation guarantees.

## Scope

* `271ops/index.html`
* `/271ops/` public route
* Identity Lifecycle Governance / 身分生命週期治理 section
* Task #217 read-only fixture API contract

## Public route check

`curl -I https://portal.soc-monitoring.dev/271ops/` returned HTTP 200.

Observed headers included:

```text
HTTP/1.1 200 OK
Content-Type: text/html
```

## API DATA check

Local API validation was performed against the running backend on `http://127.0.0.1:8021`.

Validated endpoints:

```text
GET /api/271ops/identity-lifecycle/dashboard
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
```

Local API results:

* dashboard summary present
* lifecycle_breakdown present
* risk_breakdown present
* recent_events length = 6
* top_attention_items length = 6
* events count = 7
* queue count = 5
* exceptions count = 2
* reviews count = 4
* evidence packages count = 3
* warnings = []
* safety boundary reports `read_only: true` and `mutation_allowed: false`

Public API check limitation:

`https://portal.soc-monitoring.dev/api/271ops/identity-lifecycle/dashboard` returned `{"detail":"Not Found"}` during QA. This means the public HTML route is live, but the public backend service had not yet loaded the Task #217 identity lifecycle API routes at QA time. The frontend fallback path covers this by rendering DEMO FALLBACK instead of a blank section.

## DEMO FALLBACK check

Static/DOM harness confirmed both display strings exist:

* `IDENTITY LIFECYCLE API DATA / 身分生命週期 API 資料`
* `IDENTITY LIFECYCLE DEMO FALLBACK / 身分生命週期 DEMO 備援`

The frontend validates dashboard shape and list endpoint records. If any identity lifecycle API fails, returns invalid schema, or returns empty records, it renders `identityLifecycleFallback` and shows the fallback badge.

## UI coverage checklist

Confirmed in `271ops/index.html`:

* Identity Lifecycle Summary Cards
* Lifecycle Breakdown
* Risk Breakdown
* Top Attention Items
* Recent Lifecycle Events
* Evidence Package Preview
* Safety Boundary

## Responsive QA checklist

Static review result:

* The section reuses existing `.account-kpis`, `.account-grid`, `.account-card`, `.field-grid`, `.warning-strip`, and `.safety-list` classes.
* Existing media queries collapse `.account-grid` to one column below 980px.
* Existing media queries collapse `.account-kpis` and `.field-grid` to one column below 600px.
* Long metadata fields use `overflow-wrap:anywhere` and `word-break:break-word` through existing account card styles.
* Account Governance markup remains present and separate from Identity Lifecycle markup.

## Safety boundary checklist

Confirmed visible section copy includes:

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

## No-mutation checklist

Static scans confirmed:

* No `localStorage` references.
* No `sessionStorage` references.
* No `POST`, `PUT`, `PATCH`, or `DELETE` strings in `271ops/index.html`.
* Identity Lifecycle fetch helper uses `method: "GET"`.
* No approve / reject buttons were added.
* No upload input was added.
* No edit / delete buttons were added.
* No write API call was added.

## JS / DOM harness result

Node-based static harness result:

```text
identity lifecycle DOM/static harness ok
```

The harness checked required Identity Lifecycle labels, API DATA / DEMO FALLBACK copy, UI section labels, safety boundary copy, inline script syntax, no storage references, and no write method strings.

## Browser screenshot QA result or limitation

Browser screenshot QA was not run because no Chromium/Chrome binary is available in this environment.

Checked commands:

```text
command -v chromium
command -v chromium-browser
command -v google-chrome
```

No browser binary was available. QA used public route curl, local API checks, static CSS/DOM review, and Node script syntax validation instead.

## Findings

* Public `/271ops/` route returned HTTP 200.
* Local Task #217 API returned valid read-only fixture data for all six endpoints.
* Public identity lifecycle API returned `Not Found` during QA, so backend service reload/deploy verification is still needed before public API DATA can render in production.
* Frontend fallback behavior should prevent blank UI while public API is unavailable.
* No frontend mutation pattern was found.
* No blocking JavaScript syntax error was found by static harness.

## Limitations

* Browser screenshot QA was not run due missing Chromium/Chrome binary.
* Public API DATA could not be confirmed because public backend returned `Not Found` for the new identity lifecycle API path.
* DOM behavior was validated statically, not through a full browser automation run.
* QA did not modify frontend, backend, DB, API, fixtures, scripts, release files, deployment files, nginx, cron, or systemd.

## Recommended next task

* Task #220: 271Ops Identity Lifecycle Release Note
