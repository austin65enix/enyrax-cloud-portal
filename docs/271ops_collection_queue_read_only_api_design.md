# 271ops Collection Queue Read-only API Design

## Overview

Task #209 adds read-only fixture API endpoints for the 271ops Collection Queue, Audit Calendar Tasks, and Evidence Requirements. These endpoints extend the 271ops readiness dashboard API surface so future frontend work can render monthly evidence collection work, recurring governance tasks, and expected evidence requirements without adding DB schema, migrations, write APIs, or production compliance claims.

The APIs read safe demo fixtures from `data/271ops/` through a fixed backend allowlist. They return safe references, role labels, due dates, statuses, short summaries, shared metadata, computed summaries, and warnings. They do not represent ISO27001 certification status, legal assurance, audit approval, production compliance evidence, or formal control mapping.

## Endpoints

```text
GET /api/271ops/collection-queue
GET /api/271ops/audit-calendar-tasks
GET /api/271ops/evidence-requirements
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
| `/api/271ops/collection-queue` | `data/271ops/demo_collection_queue.json` |
| `/api/271ops/audit-calendar-tasks` | `data/271ops/demo_audit_calendar_tasks.json` |
| `/api/271ops/evidence-requirements` | `data/271ops/demo_evidence_requirements.json` |

## Response Shape

### Collection Queue

`GET /api/271ops/collection-queue` returns shared metadata, `records`, computed `summary`, and `warnings`.

Summary fields:

```text
total
pending
collecting
blocked
submitted
overdue
not_applicable
no_event_this_month
```

### Audit Calendar Tasks

`GET /api/271ops/audit-calendar-tasks` returns shared metadata, fixture `period`, `records`, computed `summary`, and `warnings`.

Summary fields:

```text
total
monthly
quarterly
semiannual
annual
scheduled
due_soon
in_progress
completed
overdue
skipped
```

### Evidence Requirements

`GET /api/271ops/evidence-requirements` returns shared metadata, `records`, computed `summary`, and `warnings`.

Summary fields:

```text
total
monthly
quarterly
semiannual
annual
ad_hoc
```

If a fixture is missing or invalid, the endpoint returns a safe warning response with empty records instead of crashing.

## Optional Exact Filters

Filters are exact-match only. The API does not perform fuzzy search, full-text search, content inference, path lookup, or filename lookup from query values. Unknown filters are ignored by the implemented endpoint signatures.

Collection Queue filters:

```text
status
control_area
attention_reason
frequency
owner
reviewer
```

Audit Calendar filters:

```text
status
frequency
control_area
period
owner
reviewer
```

Evidence Requirements filters:

```text
control_area
required_frequency
expected_evidence_type
minimum_review_status
```

## Safety Boundary

Collection Queue API is fixture-backed and read-only. Audit Calendar API is readiness planning support, not certification proof. Evidence Requirements API defines expected proof, not formal legal control mapping.

The APIs do not represent ISO27001 certification status, provide legal assurance, replace consultants, replace auditors, replace certification bodies, or make formal compliance decisions. They do not write DB records, write files, create audit logs, read secrets, read raw logs, read raw prompt / response, read raw session data, read credentials, read private keys, read raw command output, read full home paths, or return sensitive personal data.

The intended response content is safe references, role labels, due dates, statuses, and short summaries only.

## Current Verification

Verification for Task #209 checks:

* `python3 -m py_compile backend/main.py`
* JSON validation for Collection Queue, Audit Calendar Tasks, and Evidence Requirements fixtures.
* Public API checks for unfiltered and filtered endpoints.
* POST check confirms the Collection Queue endpoint remains GET-only.
* grep checks confirm endpoint names, fixture allowlist keys, `read_only`, `production_data`, `certification_claim`, Task #209, and Task #210 references.
* Safety scan confirms no real sensitive material is introduced by this task.

Expected public API values:

* `source = fixture`
* `mode = read_only`
* `product = 271ops`
* `display_name = 271ops`
* `production_data = false`
* `certification_claim = false`
* collection queue count = 8
* audit calendar task count = 10
* evidence requirement count = 8
* warnings = []

## Future Tasks

* Task #210: 271ops Access Review Queue Read-only API Prototype
* Task #211: 271ops Audit Calendar Frontend Prototype
* Task #212: 271ops Role-based Governance View Design
* Task #213: 271ops Evidence Control Mapping Design
* Task #214: 271ops Account Governance Release Note
* Task #215: 271ops Account Governance Release Tag
