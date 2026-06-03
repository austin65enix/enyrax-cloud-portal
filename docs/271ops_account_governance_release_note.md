# 271ops Account Governance Release Note

## Release Summary

This release note records Task #211 and Task #212 for 271ops Account Governance / 帳號與權限治理.

Account Governance has been added to the 271ops dashboard as a read-only governance view. It helps present access request evidence, approval evidence, access review queue status, and lifecycle metadata for governance readiness.

This is a read-only governance view. It is not an actual IAM mutation system and does not directly change permissions.

## Feature Coverage

- `/271ops/` now includes an Account Governance section.
- The section supports three types of read-only governance evidence:
  - BPM Permission Requests
  - Access Review Queue
  - Access Lifecycle Events
- Account Governance presents KPI cards, data cards, BPM / ServiceOps / IAM mapping, warnings, and a safety boundary.
- Account Governance keeps the page nonblank when active API data is unavailable or invalid.

## API Coverage

Account Governance reads these GET-only endpoints:

```text
GET /api/271ops/bpm-permission-requests
GET /api/271ops/access-review-items
GET /api/271ops/access-lifecycle-events
```

The endpoints are fixture-backed, read-only, and expose safe references, role labels, status metadata, short summaries, computed summaries, and warnings.

## Frontend Behavior

- Account Governance displays `ACCOUNT API DATA / 帳號治理 API 資料` when the three read-only APIs are valid.
- API success uses fixture API data.
- API failure or schema invalid data uses `ACCOUNT DEMO FALLBACK / 帳號治理 DEMO 備援`.
- Empty or unusable record payloads must not blank the page; if records are considered unavailable by release policy, Account Governance should use `ACCOUNT DEMO FALLBACK / 帳號治理 DEMO 備援`.
- Empty valid `records` arrays are handled without blanking the page; Task #212 verified zero KPI rendering for valid empty arrays.
- The page must not go blank when Account Governance APIs are unavailable, invalid, or empty.
- Account Governance fallback is independent from the main 271ops dashboard fallback.

## QA Summary From Task #212

- Public `/271ops/` returned `HTTP/1.1 200 OK`.
- BPM Permission Requests: `count=6`, `warnings=[]`.
- Access Review Items: `count=8`, `period=2026-06`, `warnings=[]`.
- Access Lifecycle Events: `count=12`, `warnings=[]`.
- Inline JS `node --check` passed.
- DOM harness passed.
- Static no-mutation scan passed.
- Existing `upload` text is read-only backup evidence copy, not an upload control.
- Browser screenshot QA was not run because no Chromium / Chrome binary is available in this environment.

## Safety Boundary

Account Governance keeps these boundaries explicit:

- No AD modification
- No LDAP modification
- No IAM modification
- No SaaS permission mutation
- No approve / reject action
- No upload control
- No edit / delete action
- No localStorage write
- No write API call
- No password / credential / API key / private key
- No BPM form full content
- No attachment raw content
- No raw logs
- No sensitive personal data

## Product Positioning

Account Governance strengthens 271ops as an Identity Governance Readiness / Access Verify layer.

It connects BPM permission request evidence, access review queue records, lifecycle events, ServiceOps execution evidence, and audit readiness into a traceable governance view.

It does not replace AD, LDAP, IAM, HRM, BPM, or SaaS admin consoles.

## Limitations

- Fixture-backed read-only demo.
- No live IAM connector.
- No BPM connector.
- No HRM connector.
- No mutation workflow.
- No browser screenshot QA in this environment.

## Recommended Next Task

- Task #214: 271ops Identity Lifecycle Governance Design
