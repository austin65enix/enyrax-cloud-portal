# 271Ops Access Review Campaign Read-only Fixture API Prototype

## Task Summary

Task #226 adds a read-only fixture API prototype for 271Ops Access Review Campaign data.

The prototype exposes safe demo campaign metadata, review items, active campaigns, overdue items, remediation queue records, evidence packages, campaign detail bundles, and dashboard aggregation. It does not add write APIs, database schema, frontend changes, production configuration, connectors, or mutation workflows.

## Endpoints Added

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

## Fixture Source

The prototype reads from allowlisted fixture paths only:

* `data/271ops/access-review-campaigns/demo_access_review_campaigns.json`
* `data/271ops/access-review-campaigns/demo_access_review_items.json`
* `data/271ops/access-review-campaigns/demo_access_review_remediation_queue.json`
* `data/271ops/access-review-campaigns/demo_access_review_evidence_packages.json`
* `data/271ops/access-review-campaigns/demo_access_review_dashboard.json`

No endpoint accepts a user-provided fixture path.

## Response Contract

List endpoints return:

* `source`
* `mode`
* `product`
* `display_name`
* `production_data`
* `generated_at`
* `warnings`
* `count`
* `records`
* `safety_boundary`

The shared safety boundary reports `read_only: true`, `mutation_allowed: false`, and `safe_metadata_only: true`.

## Dashboard Aggregation

`GET /api/271ops/access-review-campaigns/dashboard` returns:

* `summary.total_campaigns`
* `summary.active_campaigns`
* `summary.overdue_items`
* `summary.high_risk_items`
* `summary.exception_items`
* `summary.remediation_open`
* `summary.evidence_packages_completed`
* `campaign_breakdown`
* `risk_breakdown`
* `reviewer_progress`
* `top_attention_items`
* `recent_campaigns`
* `safety_boundary`

The endpoint computes summary counts from the campaign, item, remediation, and evidence package fixtures, while using dashboard fixture arrays for demo-ready presentation lists when present.

## Filter Behavior

`/active` returns campaigns with active-style statuses such as `Review Open`, `Overdue`, or `ReviewRequired`.

`/overdue-items` returns review items where `status = Overdue`.

`/remediation-queue` returns the remediation queue fixture.

`/evidence-packages` returns the evidence package fixture.

`/{campaign_id}/items` returns only review items matching the requested campaign identifier.

## Campaign Detail Behavior

`GET /api/271ops/access-review-campaigns/{campaign_id}` returns:

* `campaign`
* `review_items`
* `remediation_queue`
* `evidence_packages`
* `summary`
* `warnings`
* `safety_boundary`

If `campaign_id` is not found, the endpoint returns a safe nonblank response with `campaign: null`, empty related arrays, zero summary counts, and a `campaign_not_found` warning. It does not expose raw fixture paths or stack traces.

## Safety Boundary

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

## Validation Performed

Validation expected for this task:

* JSON fixture parse checks for all five access review campaign fixtures.
* Backend Python syntax check.
* Endpoint response contract checks for all campaign endpoints.
* Dashboard aggregation check.
* Campaign detail response check.
* Campaign ID not found safe behavior check.
* Active campaign filter check.
* Overdue item filter check.
* Remediation queue check.
* Evidence packages endpoint check.
* No mutation route scan.
* No POST / PUT / PATCH / DELETE route added for the access review campaign API.

## Limitations

* Fixture-backed demo API only
* No frontend changes in this task
* No database schema changes
* No production connector
* No write API
* No mutation workflow
* No live AD, LDAP, IAM, HRM, BPM, SaaS, or ServiceOps connector

## Recommended Next Task

* Task #227: 271Ops Access Review Campaign Frontend API Integration
