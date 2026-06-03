# 271ops Access Review Queue Read-only API Design

## Overview

Task #210 adds read-only fixture API endpoints for 271ops account governance and access review queue data. These endpoints expose safe demo references for BPM permission requests, periodic access review queue items, and access lifecycle events so future frontend work can show permission governance flow without adding database schema, migrations, write APIs, or production compliance claims.

The APIs read safe fixtures from `data/271ops/` through the backend fixture allowlist. They return safe references, role labels, statuses, due dates, short summaries, computed summaries, and warnings. They do not return raw IAM records, raw BPM forms, credentials, secrets, full personal data, raw logs, or production audit evidence.

## Endpoints

```text
GET /api/271ops/bpm-permission-requests
GET /api/271ops/access-review-items
GET /api/271ops/access-lifecycle-events
```

All endpoints are GET-only and fixture-backed.

Shared metadata:

```json
{
  "source": "fixture",
  "mode": "read_only",
  "product": "271ops",
  "display_name": "271ops",
  "production_data": false,
  "certification_claim": false,
  "warnings": []
}
```

Fixture mapping:

| Endpoint | Fixture |
| --- | --- |
| `/api/271ops/bpm-permission-requests` | `data/271ops/demo_bpm_permission_requests.json` |
| `/api/271ops/access-review-items` | `data/271ops/demo_access_review_items.json` |
| `/api/271ops/access-lifecycle-events` | `data/271ops/demo_access_lifecycle_events.json` |

## Response Shape

### BPM Permission Requests

`GET /api/271ops/bpm-permission-requests` returns shared metadata, `records`, computed `summary`, and `warnings`.

Summary fields:

```text
total
approved
pending
rejected
expired
```

### Access Review Items

`GET /api/271ops/access-review-items` returns shared metadata, fixture `period`, `records`, computed review status summary, decision summary, and `warnings`.

Summary fields:

```text
total
pending
approved
exception
needs_update
revoke_needed
revoked
keep
reduce
revoke
needs_owner
not_applicable
```

### Access Lifecycle Events

`GET /api/271ops/access-lifecycle-events` returns shared metadata, `records`, computed `summary`, and `warnings`.

Summary fields:

```text
total
requested
approved
provisioned
reviewed
exception_granted
revoke_requested
revoked
```

If a fixture is missing or invalid, the endpoint returns a safe warning response with empty records instead of crashing.

## Optional Exact Filters

Filters are exact-match only. The API does not perform fuzzy search, full-text search, content inference, path lookup, or filename lookup from query values. Unknown filters are ignored by the implemented endpoint signatures.

BPM Permission Request filters:

```text
request_type
approval_status
evidence_status
system_ref
department_ref
approver_role
```

Access Review Item filters:

```text
period
review_status
decision
evidence_status
attention_reason
account_type
system_ref
department_ref
reviewer
```

Access Lifecycle Event filters:

```text
account_ref
event_type
source_module
source_ref
actor_role
```

## Safety Boundary

Access Review Queue APIs are fixture-backed and read-only. They support governance planning and demo visibility, not production authorization, certification proof, legal assurance, audit approval, or formal access recertification.

The APIs do not write DB records, write files, create audit logs, mutate ServiceOps, mutate IAM, mutate BPM, approve access, revoke access, read secrets, read raw logs, read raw BPM forms, read credentials, read private keys, read raw command output, read full home paths, or return sensitive personal data.

The intended response content is safe references, role labels, approval states, review states, lifecycle event summaries, due dates, evidence status, and short summaries only.

## Current Verification

Verification for Task #210 should check:

* `python3 -m py_compile backend/main.py`
* JSON validation for BPM Permission Requests, Access Review Items, and Access Lifecycle Events fixtures.
* API checks for unfiltered and filtered endpoints.
* POST check confirms endpoints remain GET-only.
* grep checks confirm endpoint names and fixture allowlist keys.
* Safety scan confirms no real sensitive material is introduced by this task.

Expected public API values:

* `source = fixture`
* `mode = read_only`
* `product = 271ops`
* `display_name = 271ops`
* `production_data = false`
* `certification_claim = false`
* BPM permission request count = 6
* access review item count = 8
* access lifecycle event count = 12
* warnings = []

## Future Tasks

* Task #211: 271ops Audit Calendar Frontend Prototype
* Task #212: 271ops Role-based Governance View Design
* Task #213: 271ops Evidence Control Mapping Design
* Task #214: 271ops Account Governance Release Note
* Task #215: 271ops Account Governance Release Tag

## Task #211 Account Governance Frontend Prototype

* Task #211 adds Account Governance frontend sections to `/271ops/`.
* It fetches BPM Permission Requests, Access Review Items, and Access Lifecycle Events from read-only APIs.
* It renders Account Governance API DATA when all three APIs are valid.
* It falls back to local Account Governance demo data when any API fails, returns non-200, invalid JSON, or invalid schema.
* It displays BPM Permission Requests, Access Review Queue, Access Lifecycle Events, BPM / ServiceOps / IAM mapping, KPI cards, warnings, and safety boundary.
* It remains read-only.
* It does not directly change IAM, AD, LDAP, or SaaS permissions.
* It does not store raw BPM forms, raw attachments, credentials, secrets, keys, raw logs, or sensitive personal data.
* No backend, DB, API, fixture, release, deployment, or tag changes were made.
* It prepares Task #212 visual QA and release note preparation.
