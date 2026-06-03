# 271Ops Exception Governance Demo Fixtures

## Purpose

These files provide safe demo fixtures for the 271Ops Exception Governance design. They model temporary access, emergency access, privileged exceptions, leaver delay exceptions, review extensions, remediation references, evidence packages, and dashboard summary data.

The fixtures are read-only demo data. They do not represent real HR, BPM, IAM, AD, LDAP, SaaS, ServiceOps, audit, or production records.

## Fixture Files

* `demo_exceptions.json`
* `demo_exception_remediation_queue.json`
* `demo_exception_evidence_packages.json`
* `demo_exception_dashboard.json`

## Demo Scenarios

* Temporary access expiring soon: `status` = `ExpiringSoon`, expiry date within seven days, and `risk_level` = `High`.
* Emergency access over SLA: `status` = `OverSLA`, `risk_level` = `High`, and ServiceOps ticket reference is present.
* Privileged exception missing review: `privilege_level` = `High`, review due date is overdue, `status` = `ReviewOverdue`, and `risk_level` = `High`.
* Expired exception still active: `status` = `ExpiredActive`, `risk_level` = `Critical`, and notes state that access is still active in a safe summary.
* Leaver delay exception with remediation ticket: ServiceOps ticket and remediation queue item are present.
* Review extension exception: renewal count is at least one and review remains required.
* Exception closed with evidence package: closed decision, evidence reference, evidence package reference, and low risk.

## Field Contract

Exception records use this safe metadata contract:

| Field | Meaning |
| --- | --- |
| `exception_id` | Stable demo exception identifier |
| `exception_type` | Exception type |
| `exception_title` | Human-readable exception title |
| `employee_ref` | Fake employee alias, such as `EMP-DEMO-201` |
| `user_display_name` | Safe display label, such as `Demo User A` |
| `department` | Department label or safe department reference |
| `system_ref` | Target system reference |
| `access_type` | Access category |
| `privilege_level` | Standard / Elevated / High / Admin |
| `exception_reason` | Short exception reason |
| `business_justification` | Short safe business justification |
| `owner` | Owner role or safe owner alias |
| `reviewer` | Reviewer role or safe reviewer alias |
| `request_ref` | Safe request reference |
| `approval_ref` | Safe approval reference |
| `serviceops_ticket_ref` | Safe ServiceOps ticket reference |
| `evidence_ref` | Safe evidence reference |
| `evidence_package_ref` | Safe evidence package reference |
| `start_date` | Exception start date |
| `expiry_date` | Exception expiry date |
| `review_due_date` | Review due date |
| `status` | Demo status |
| `risk_level` | `Low`, `Medium`, `High`, or `Critical` |
| `renewal_count` | Number of exception renewals |
| `decision` | Demo decision label |
| `decision_reason` | Short decision reason |
| `notes` | Short safe summary only |

## Safety Boundary

These fixtures are safe metadata only. They may include:

* Fake employee references, such as `EMP-DEMO-201`
* Fake user display labels, such as `Demo User A`
* Safe exception identifiers, such as `EXC-DEMO-001`
* Safe evidence package references, such as `EVD-271OPS-EXC-001`
* Safe ServiceOps ticket references, such as `SVC-DEMO-EXC-001`
* Safe request references, such as `REQ-DEMO-EXC-001`
* Safe approval references, such as `APR-DEMO-EXC-001`
* Department, role, system, reviewer, status, and risk labels
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
GET /api/271ops/exceptions
GET /api/271ops/exceptions/{exception_id}
GET /api/271ops/exceptions/active
GET /api/271ops/exceptions/expiring-soon
GET /api/271ops/exceptions/expired
GET /api/271ops/exceptions/privileged
GET /api/271ops/exceptions/remediation-queue
GET /api/271ops/exceptions/evidence-packages
GET /api/271ops/exceptions/dashboard
```

The future API should return safe exception metadata, risk levels, remediation references, evidence package references, warning summaries, and short notes only.

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

* Task #233: 271Ops Exception Governance Read-only Fixture API Design
