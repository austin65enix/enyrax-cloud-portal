# 271Ops Identity Lifecycle Read-only Fixture API Design

## Purpose

This document designs the 271Ops Identity Lifecycle read-only fixture API. The API is intended to present safe demo governance data for Joiner / Mover / Leaver lifecycle verification, periodic reviews, exception tracking, and evidence package readiness.

The API is an Access Verify / Identity Governance Readiness surface. It helps show whether lifecycle events, ServiceOps execution references, BPM request references, review metadata, exception expiry, and audit evidence package status can be presented as safe governance metadata.

This task is design only. It does not implement backend routes, frontend views, database schema, write APIs, connectors, or production configuration.

## Fixture source

The proposed endpoints read only from the fixture files created by Task #215:

| Fixture purpose | Fixture path |
| --- | --- |
| Lifecycle events | `data/271ops/identity-lifecycle/demo_identity_lifecycle_events.json` |
| Lifecycle queue | `data/271ops/identity-lifecycle/demo_identity_lifecycle_queue.json` |
| Exceptions | `data/271ops/identity-lifecycle/demo_identity_lifecycle_exceptions.json` |
| Reviews | `data/271ops/identity-lifecycle/demo_identity_lifecycle_reviews.json` |
| Evidence packages | `data/271ops/identity-lifecycle/demo_identity_lifecycle_evidence_packages.json` |

The loader should use an internal allowlist. It must not accept a user-provided file path, directory, filename, or dynamic path segment.

## Proposed read-only endpoints

```text
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
GET /api/271ops/identity-lifecycle/dashboard
```

All endpoints are GET-only and fixture-backed.

## Response contracts

Shared list endpoint shape:

```json
{
  "source": "fixture",
  "count": 0,
  "warnings": [],
  "records": [],
  "generated_at": "2026-06-03T00:00:00+00:00",
  "safety_boundary": {
    "read_only": true,
    "mutation_allowed": false,
    "safe_metadata_only": true,
    "excludes": [
      "passwords",
      "credentials",
      "api_keys",
      "private_keys",
      "raw_logs",
      "raw_bpm_form_body",
      "raw_attachment_content",
      "full_hr_personal_data"
    ]
  }
}
```

`GET /api/271ops/identity-lifecycle/events` returns safe JML + review + exception lifecycle records from the events fixture.

`GET /api/271ops/identity-lifecycle/queue` returns open attention items from the lifecycle queue fixture. The response may use `records` or `items`; the recommended prototype should use `records` for consistency.

`GET /api/271ops/identity-lifecycle/exceptions` returns temporary access exception and retained privileged access records.

`GET /api/271ops/identity-lifecycle/reviews` returns reviewer-oriented lifecycle review records, including overdue quarterly review examples.

`GET /api/271ops/identity-lifecycle/evidence-packages` returns evidence package readiness records for completed and incomplete package examples.

Each response should include:

* `source`
* `count`
* `warnings`
* `records`
* `generated_at` or fixture `period` where available
* `safety_boundary`

## Dashboard endpoint contract

`GET /api/271ops/identity-lifecycle/dashboard` aggregates all identity lifecycle fixtures and returns:

```json
{
  "source": "fixture",
  "warnings": [],
  "summary": {
    "total_events": 0,
    "queue_open": 0,
    "critical_findings": 0,
    "high_risk_findings": 0,
    "overdue_reviews": 0,
    "expiring_exceptions": 0,
    "completed_evidence_packages": 0
  },
  "lifecycle_breakdown": {},
  "risk_breakdown": {},
  "recent_events": [],
  "top_attention_items": [],
  "safety_boundary": {}
}
```

Aggregation rules:

* `total_events`: count of records in the events fixture.
* `queue_open`: count of records in the queue fixture.
* `critical_findings`: count of event or queue records with `risk_level = Critical`.
* `high_risk_findings`: count of event or queue records with `risk_level = High`.
* `overdue_reviews`: count of review records with `verification_status = Overdue`.
* `expiring_exceptions`: count of exception records with `verification_status = ReviewRequired` and a non-empty `exception_expiry_date`.
* `completed_evidence_packages`: count of evidence package records with `verification_status = Verified`.
* `lifecycle_breakdown`: counts by `event_type` across lifecycle events.
* `risk_breakdown`: counts by `risk_level` across lifecycle events.
* `recent_events`: most recent lifecycle events sorted by `effective_date` descending.
* `top_attention_items`: critical, high-risk, failed, mismatched, overdue, or review-required items from queue and exception fixtures.

## Loader behavior

The backend loader should:

* Use allowlisted fixture keys and paths only.
* Load files in read-only mode.
* Return a safe default response if a fixture is missing.
* Validate that decoded fixture JSON is an object.
* Validate that `records` is an array when present.
* Add warnings for missing fixtures, invalid JSON, invalid schema, empty records, or partial fixture unavailability.
* Never return raw stack traces to the frontend.
* Avoid dynamic path input.
* Avoid user-provided file paths.

## API safety boundary

The API boundary is:

* GET only.
* No POST / PUT / PATCH / DELETE.
* No AD mutation.
* No LDAP mutation.
* No IAM mutation.
* No SaaS permission mutation.
* No approve / reject action.
* No upload.
* No edit / delete.
* No credential exposure.
* No raw logs.
* No raw BPM body.
* No attachment raw content.
* Safe metadata only.

## Error / fallback design

Fallback responses should remain nonblank and safe.

Missing fixture:

* Return HTTP 200.
* Return `records: []`.
* Return `count: 0`.
* Add warning `fixture_unavailable`.

Invalid JSON:

* Return HTTP 200.
* Return safe fallback response.
* Add warning `fixture_invalid_json`.
* Do not return raw parser errors or stack traces.

Invalid schema:

* Return HTTP 200.
* Return safe fallback response.
* Add warning `fixture_invalid_schema`.

Empty records:

* Return HTTP 200.
* Return `records: []`.
* Add warning `fixture_empty`.

Partial fixture unavailable:

* Dashboard still returns available fixture data.
* Dashboard warning array names the unavailable fixture key.
* Frontend can display `DEMO FALLBACK` when warnings are present.

## Validation checklist

Prototype validation should include:

* JSON parse test for all five identity lifecycle fixtures.
* Endpoint response contract test for all list endpoints.
* GET-only test.
* No mutation route test.
* No credential string scan.
* No raw path exposure test.
* Warning response test.
* Dashboard aggregation test.

## Product positioning

271Ops Identity Lifecycle API is an Access Verify / Identity Governance Readiness API layer. It supports audit evidence preparation and ServiceOps-linked remediation governance by organizing safe lifecycle metadata, review status, exception status, risk level, and evidence references.

It does not replace IAM, AD, LDAP, BPM, HRM, or SaaS admin consoles. Source systems remain responsible for identity records, permission administration, workflow approval, HR lifecycle events, and actual access changes.

## Limitations

* Design only.
* No API implementation.
* No backend route changes.
* No frontend changes.
* No live connector.
* No mutation workflow.
* No production compliance claim.
* No direct identity administration.

## Recommended next task

* Task #217: 271Ops Identity Lifecycle Read-only Fixture API Prototype
