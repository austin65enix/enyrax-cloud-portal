# 271Ops Identity Lifecycle Read-only Fixture API Prototype

## Task summary

Task #217 implements the 271Ops Identity Lifecycle read-only fixture API prototype. The API exposes safe demo metadata for Joiner / Mover / Leaver lifecycle verification, review follow-up, exception tracking, and evidence package readiness.

The prototype is fixture-backed and GET-only. It does not add database schema, write APIs, identity connectors, frontend changes, or production configuration changes.

## Endpoints added

```text
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
GET /api/271ops/identity-lifecycle/dashboard
```

## Fixture source

The backend reads only allowlisted fixtures:

| Endpoint | Fixture |
| --- | --- |
| `/api/271ops/identity-lifecycle/events` | `data/271ops/identity-lifecycle/demo_identity_lifecycle_events.json` |
| `/api/271ops/identity-lifecycle/queue` | `data/271ops/identity-lifecycle/demo_identity_lifecycle_queue.json` |
| `/api/271ops/identity-lifecycle/exceptions` | `data/271ops/identity-lifecycle/demo_identity_lifecycle_exceptions.json` |
| `/api/271ops/identity-lifecycle/reviews` | `data/271ops/identity-lifecycle/demo_identity_lifecycle_reviews.json` |
| `/api/271ops/identity-lifecycle/evidence-packages` | `data/271ops/identity-lifecycle/demo_identity_lifecycle_evidence_packages.json` |

The loader does not accept user-provided file paths, dynamic filenames, or path query parameters.

## Response contract

List endpoints return:

```json
{
  "source": "fixture",
  "mode": "read_only",
  "product": "271ops",
  "display_name": "271ops Identity Lifecycle",
  "production_data": false,
  "generated_at": "ISO-8601 timestamp",
  "warnings": [],
  "count": 0,
  "records": [],
  "safety_boundary": {}
}
```

Missing fixtures, invalid JSON, invalid schema, and empty records return a safe nonblank response with warnings instead of raw stack traces.

## Dashboard aggregation

`GET /api/271ops/identity-lifecycle/dashboard` returns:

* `summary.total_events`
* `summary.queue_open`
* `summary.critical_findings`
* `summary.high_risk_findings`
* `summary.overdue_reviews`
* `summary.expiring_exceptions`
* `summary.completed_evidence_packages`
* `lifecycle_breakdown`
* `risk_breakdown`
* `recent_events`
* `top_attention_items`
* `safety_boundary`

Aggregation is computed from the safe fixture records only.

## Safety boundary

The API response includes:

* `read_only: true`
* `mutation_allowed: false`
* `safe_metadata_only: true`
* no AD mutation
* no LDAP mutation
* no IAM mutation
* no SaaS permission mutation
* no approve / reject action
* no upload
* no edit / delete
* excludes passwords, credentials, API keys, private keys, raw logs, raw BPM form body, raw attachment content, and full HR personal data

## Validation performed

Validation for this task should include:

* JSON fixture parse checks for all five identity lifecycle fixture files.
* `python3 -m py_compile backend/main.py`.
* HTTP 200 checks for all six GET endpoints.
* Dashboard aggregation check for summary and breakdown fields.
* Route scan confirming no POST / PUT / PATCH / DELETE identity lifecycle routes.
* Safety scan confirming no credential strings or raw path exposure were introduced.

## Limitations

* Prototype only.
* Fixture-backed only.
* No frontend integration in this task.
* No DB schema changes.
* No live HRM, BPM, AD, LDAP, IAM, SaaS, or ServiceOps connector.
* No mutation workflow.
* No production compliance claim.

## Recommended next task

* Task #218: 271Ops Identity Lifecycle Frontend API Integration
