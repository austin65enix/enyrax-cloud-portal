# 271Ops Access Review Campaign Read-only Fixture API Design

## Purpose

This document designs the 271Ops Access Review Campaign read-only fixture API.

The API is intended to display scheduled access review campaigns, review items, remediation queue records, evidence packages, and dashboard summary data from safe demo fixtures.

This task is design only. It does not implement backend routes, frontend views, database schema, write APIs, connectors, or production configuration.

## Fixture Source

The proposed endpoints read only from the fixture files created by Task #224:

| Fixture purpose | Fixture path |
| --- | --- |
| Campaigns | `data/271ops/access-review-campaigns/demo_access_review_campaigns.json` |
| Review items | `data/271ops/access-review-campaigns/demo_access_review_items.json` |
| Remediation queue | `data/271ops/access-review-campaigns/demo_access_review_remediation_queue.json` |
| Evidence packages | `data/271ops/access-review-campaigns/demo_access_review_evidence_packages.json` |
| Dashboard | `data/271ops/access-review-campaigns/demo_access_review_dashboard.json` |

The loader should use an internal allowlist. It must not accept a user-provided file path, directory, filename, or dynamic path segment.

## Proposed Read-only Endpoints

```text
GET /api/271ops/access-review-campaigns
GET /api/271ops/access-review-campaigns/{campaign_id}
GET /api/271ops/access-review-campaigns/{campaign_id}/items
GET /api/271ops/access-review-campaigns/active
GET /api/271ops/access-review-campaigns/overdue-items
GET /api/271ops/access-review-campaigns/remediation-queue
GET /api/271ops/access-review-campaigns/evidence-packages
GET /api/271ops/access-review-campaigns/dashboard
```

All endpoints are GET-only and fixture-backed.

## Response Contracts

Shared list endpoint shape:

```json
{
  "source": "fixture",
  "mode": "read_only",
  "product": "271ops",
  "display_name": "271Ops Access Review Campaign",
  "production_data": false,
  "generated_at": "2026-06-03T00:00:00+00:00",
  "warnings": [],
  "count": 0,
  "records": [],
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

Endpoint-specific contracts:

| Endpoint | Response content |
| --- | --- |
| `GET /api/271ops/access-review-campaigns` | Returns campaign records from `demo_access_review_campaigns.json`. |
| `GET /api/271ops/access-review-campaigns/{campaign_id}` | Returns one campaign detail bundle with related review items, remediation queue records, evidence packages, summary, warnings, and safety boundary. |
| `GET /api/271ops/access-review-campaigns/{campaign_id}/items` | Returns review items filtered by `campaign_id`. |
| `GET /api/271ops/access-review-campaigns/active` | Returns campaigns with active statuses such as `Review Open`, `Overdue`, or `ReviewRequired`. |
| `GET /api/271ops/access-review-campaigns/overdue-items` | Returns review items with `status = Overdue` or campaign overdue context. |
| `GET /api/271ops/access-review-campaigns/remediation-queue` | Returns remediation records from `demo_access_review_remediation_queue.json`. |
| `GET /api/271ops/access-review-campaigns/evidence-packages` | Returns evidence package records from `demo_access_review_evidence_packages.json`. |
| `GET /api/271ops/access-review-campaigns/dashboard` | Returns dashboard fixture data plus any future aggregate fields. |

Each response should include:

* `source`
* `mode`
* `product`
* `display_name`
* `production_data`
* `generated_at`
* `warnings`
* `count`
* `records` or `items`
* `safety_boundary`

## Campaign Detail Endpoint Contract

`GET /api/271ops/access-review-campaigns/{campaign_id}` returns a campaign-centered bundle:

```json
{
  "source": "fixture",
  "mode": "read_only",
  "product": "271ops",
  "display_name": "271Ops Access Review Campaign",
  "production_data": false,
  "generated_at": "2026-06-03T00:00:00+00:00",
  "campaign_id": "ARC-DEMO-2026Q2-001",
  "campaign": {},
  "review_items": [],
  "remediation_queue": [],
  "evidence_packages": [],
  "summary": {
    "item_count": 0,
    "completed_count": 0,
    "overdue_count": 0,
    "high_risk_count": 0,
    "exception_count": 0,
    "remediation_open": 0,
    "evidence_packages_completed": 0
  },
  "warnings": [],
  "safety_boundary": {
    "read_only": true,
    "mutation_allowed": false,
    "safe_metadata_only": true
  }
}
```

Detail aggregation rules:

* `campaign`: matching campaign record by `campaign_id`.
* `review_items`: review item records where `campaign_id` matches.
* `remediation_queue`: remediation records where `campaign_id` matches.
* `evidence_packages`: evidence package records where `campaign_id` matches.
* `summary.item_count`: count of matching review items.
* `summary.completed_count`: count of matching review items with `status = Completed`.
* `summary.overdue_count`: count of matching review items with `status = Overdue`.
* `summary.high_risk_count`: count of matching review items with `risk_level = High` or `Critical`.
* `summary.exception_count`: count of matching review items with non-empty `exception_ref`.
* `summary.remediation_open`: count of matching remediation records with `status = Open`.
* `summary.evidence_packages_completed`: count of matching evidence packages with `package_status = Completed`.

If `campaign_id` is not found, return a nonblank safe fallback with `campaign: null`, empty arrays, zero summary values, and warning `campaign_not_found`.

## Dashboard Endpoint Contract

`GET /api/271ops/access-review-campaigns/dashboard` aggregates:

* `total_campaigns`
* `active_campaigns`
* `overdue_items`
* `high_risk_items`
* `exception_items`
* `remediation_open`
* `evidence_packages_completed`
* `campaign_breakdown`
* `risk_breakdown`
* `reviewer_progress`
* `top_attention_items`
* `recent_campaigns`

Recommended dashboard response shape:

```json
{
  "source": "fixture",
  "mode": "read_only",
  "product": "271ops",
  "display_name": "271Ops Access Review Campaign",
  "production_data": false,
  "generated_at": "2026-06-03T00:00:00+00:00",
  "warnings": [],
  "summary": {
    "total_campaigns": 0,
    "active_campaigns": 0,
    "overdue_items": 0,
    "high_risk_items": 0,
    "exception_items": 0,
    "remediation_open": 0,
    "evidence_packages_completed": 0
  },
  "campaign_breakdown": [],
  "risk_breakdown": [],
  "reviewer_progress": [],
  "top_attention_items": [],
  "recent_campaigns": [],
  "safety_boundary": {
    "read_only": true,
    "mutation_allowed": false,
    "safe_metadata_only": true
  }
}
```

Aggregation rules:

* `total_campaigns`: count of campaign records.
* `active_campaigns`: count of campaigns with active statuses such as `Review Open`, `Overdue`, or `ReviewRequired`.
* `overdue_items`: count of review items with `status = Overdue`.
* `high_risk_items`: count of review items with `risk_level = High` or `Critical`.
* `exception_items`: count of review items with non-empty `exception_ref`.
* `remediation_open`: count of remediation records with `status = Open`.
* `evidence_packages_completed`: count of evidence packages with `package_status = Completed`.
* `campaign_breakdown`: counts by campaign type and status.
* `risk_breakdown`: counts by review item risk level.
* `reviewer_progress`: grouped reviewer assignment, completion, overdue, and review-required state.
* `top_attention_items`: high-risk, overdue, remediation-open, or review-required review items.
* `recent_campaigns`: recent campaign records sorted by `start_date` or `due_date` descending.

## Loader Behavior

The backend loader should:

* Use allowlisted fixture paths only.
* Load files in read-only mode.
* Return a safe default response if a fixture is missing.
* Return warnings for invalid JSON.
* Return warnings for invalid schema.
* Return a nonblank safe response when records are empty.
* Never throw raw stack traces to the frontend.
* Avoid dynamic path input.
* Avoid user-provided file paths.

Suggested allowlist keys:

| Key | Fixture path |
| --- | --- |
| `campaigns` | `data/271ops/access-review-campaigns/demo_access_review_campaigns.json` |
| `items` | `data/271ops/access-review-campaigns/demo_access_review_items.json` |
| `remediation_queue` | `data/271ops/access-review-campaigns/demo_access_review_remediation_queue.json` |
| `evidence_packages` | `data/271ops/access-review-campaigns/demo_access_review_evidence_packages.json` |
| `dashboard` | `data/271ops/access-review-campaigns/demo_access_review_dashboard.json` |

The loader should validate that decoded fixture JSON is an object and that `records` is an array for list fixtures. The dashboard fixture should validate that `summary`, `campaign_breakdown`, `risk_breakdown`, `reviewer_progress`, `top_attention_items`, `recent_campaigns`, and `safety_boundary` are present with safe object or array shapes.

## API Safety Boundary

The API boundary is:

* GET only
* No POST / PUT / PATCH / DELETE
* No AD mutation
* No LDAP mutation
* No IAM mutation
* No SaaS permission mutation
* No approve / reject action
* No upload
* No edit / delete
* No credential exposure
* No raw logs
* No raw BPM body
* No attachment raw content
* No full HR personal data
* Safe metadata only

## Error / Fallback Design

Fallback responses should remain nonblank and safe.

Missing fixture:

* Return HTTP 200.
* Return `records: []` or endpoint-specific empty arrays.
* Return `count: 0` where relevant.
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

Campaign ID not found:

* Return HTTP 200.
* Return `campaign: null`.
* Return empty `review_items`, `remediation_queue`, and `evidence_packages` arrays.
* Add warning `campaign_not_found`.

Partial fixture unavailable:

* Return available fixture data.
* Add warning naming the unavailable fixture key.
* Dashboard and detail endpoints still return a nonblank safe fallback.

Frontend fallback:

* Frontend can display `DEMO FALLBACK` when warnings are present, fixture records are empty, schemas are invalid, or required dashboard fields are missing.

## Validation Checklist

Prototype validation should include:

* JSON parse test for all five access review campaign fixtures.
* Endpoint response contract test.
* Campaign detail response test.
* Dashboard aggregation test.
* Active campaign filter test.
* Overdue item filter test.
* Remediation queue filter test.
* GET-only test.
* No mutation route test.
* No credential string scan.
* No raw path exposure.
* Warning response test.

## Product Positioning

271Ops Access Review Campaign API is an Access Verify / Identity Governance Readiness API layer.

It supports reviewer progress, overdue tracking, exception tracking, remediation linkage, and audit evidence. It helps turn periodic access review campaigns into safe, traceable governance metadata for audit readiness.

It does not replace IAM, AD, LDAP, BPM, HRM, or SaaS admin consoles. Source systems remain responsible for identity records, permission administration, workflow approval, HR lifecycle events, SaaS roles, and actual access changes.

## Limitations

* Design only
* No API implementation
* No backend route changes
* No frontend changes
* No live connector
* No mutation workflow

## Recommended Next Task

* Task #226: 271Ops Access Review Campaign Read-only Fixture API Prototype
