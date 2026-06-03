# 271Ops Access Review Campaign Demo Fixtures

## Purpose

These files provide safe demo fixtures for the 271Ops Access Review Campaign design. They model scheduled access review campaigns, reviewer progress, overdue review items, exception review, remediation references, evidence packages, and dashboard summary data.

The fixtures are read-only demo data. They do not represent real HR, BPM, IAM, AD, LDAP, SaaS, ServiceOps, audit, or production records.

## Fixture Files

* `demo_access_review_campaigns.json`
* `demo_access_review_items.json`
* `demo_access_review_remediation_queue.json`
* `demo_access_review_evidence_packages.json`
* `demo_access_review_dashboard.json`

Each file uses safe references, campaign labels, reviewer aliases, department labels, system references, review status, risk levels, evidence references, ticket references, and short summary notes only.

## Demo Scenarios

The fixture set includes these demo scenarios:

* Quarterly access review campaign in progress: `campaign_type` = `Quarterly Access Review`, `status` = `Review Open`, `risk_level` = `Medium`.
* Privileged admin access review overdue: admin / privileged access remains pending and overdue with `risk_level` = `High`.
* Department transfer stale access review: mover stale access requires remediation and has `risk_level` = `High`.
* SaaS license access review: SaaS ERP / CRM access is reviewed for retention or removal with `risk_level` = `Low` or `Medium`.
* Exception access review expiring soon: exception reference is present, status is `ReviewRequired`, and `risk_level` = `High`.
* Review decision creates ServiceOps remediation reference: remove or change decision links to a ServiceOps remediation reference and evidence reference.
* Evidence package completed: evidence package and audit report references are present, status is `Completed`, and `risk_level` = `Low`.

## Field Contract

### Campaign Fields

| Field | Meaning |
| --- | --- |
| `campaign_id` | Stable demo campaign identifier |
| `campaign_name` | Human-readable campaign name |
| `campaign_type` | Campaign type such as `Quarterly Access Review` or `Privileged Access Review` |
| `period` | Review period, such as `2026-Q2` |
| `scope` | Safe summary of selected departments, systems, access types, or lifecycle records |
| `owner` | Campaign owner role or safe owner alias |
| `status` | Demo campaign status |
| `start_date` | Campaign start date |
| `due_date` | Campaign due date |
| `closed_date` | Campaign close date, if closed |
| `reviewer_count` | Number of assigned reviewers |
| `item_count` | Number of review items |
| `completed_count` | Number of completed review items |
| `overdue_count` | Number of overdue review items |
| `exception_count` | Number of exception review items |
| `remediation_ticket_count` | Number of linked ServiceOps remediation references |
| `evidence_package_ref` | Safe evidence package reference |
| `audit_report_ref` | Safe audit report reference |
| `risk_level` | `Low`, `Medium`, `High`, or `Critical` |
| `notes` | Short safe summary only |

### Review Item Fields

| Field | Meaning |
| --- | --- |
| `review_item_id` | Stable demo review item identifier |
| `campaign_id` | Parent campaign identifier |
| `employee_ref` | Fake employee alias, such as `EMP-DEMO-101` |
| `user_display_name` | Safe demo display label, such as `Demo User A` |
| `department` | Department label or safe department reference |
| `system_ref` | Target system reference |
| `access_type` | Safe access category such as `Admin / Privileged` or `SaaS License` |
| `role_name` | Role, group, license, or permission label |
| `privilege_level` | Demo privilege level |
| `reviewer` | Reviewer role or safe reviewer alias |
| `review_decision` | Demo review decision |
| `decision_reason` | Short safe decision reason |
| `decision_date` | Decision date, if captured |
| `remediation_required` | Boolean remediation indicator |
| `serviceops_ticket_ref` | Safe ServiceOps remediation reference |
| `evidence_ref` | Safe evidence reference |
| `exception_ref` | Safe exception reference |
| `risk_level` | `Low`, `Medium`, `High`, or `Critical` |
| `status` | Demo review item status |
| `notes` | Short safe summary only |

## Safety Boundary

These fixtures are safe metadata only. They may include:

* Fake employee references, such as `EMP-DEMO-101`
* Fake user display labels, such as `Demo User A`
* Safe campaign identifiers, such as `ARC-DEMO-2026Q2-001`
* Safe review item identifiers, such as `ARI-DEMO-001`
* Safe evidence package references, such as `EVD-271OPS-ARC-001`
* Safe ServiceOps ticket references, such as `SVC-DEMO-ARC-001`
* Department, role, system, reviewer, campaign, lifecycle, status, and risk labels
* Short summary notes

## What Is Intentionally Excluded

These fixtures intentionally exclude:

* Real names
* Real employee numbers
* Real email addresses
* Passwords
* Credentials
* API keys
* Private keys
* Full HR personal data
* Raw BPM form bodies
* Raw attachment content
* Raw logs
* Full home paths
* Raw command output
* Frontend implementation
* Backend implementation
* Database schema or migrations
* API routes
* Production configuration
* Direct AD / LDAP / IAM / SaaS mutation

## Future API Mapping

Future read-only fixture API design may map these files to:

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

The future API should return safe campaign metadata, review item summaries, reviewer progress, remediation references, exception references, evidence package references, dashboard counts, warnings, and audit-ready summaries. It should not mutate identity systems or expose raw sensitive records.

## Limitations

* Demo fixture only
* Read-only intent only
* No frontend in this task
* No backend in this task
* No API in this task
* No live HRM, BPM, AD, LDAP, IAM, SaaS, or ServiceOps connector
* No production compliance claim
* No proof of actual access removal
* No raw evidence storage
* No mutation workflow

## Recommended Next Task

* Task #225: 271Ops Access Review Campaign Read-only Fixture API Design
