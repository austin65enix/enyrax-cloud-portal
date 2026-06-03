# 271ops Identity Lifecycle Demo Fixtures

## Purpose

These files provide safe demo fixtures for the 271ops Identity Lifecycle Governance design. They model Joiner / Mover / Leaver lifecycle verification, exception tracking, access review follow-up, and audit evidence package grouping.

The fixtures are read-only demo data. They do not represent real HR, BPM, IAM, AD, LDAP, SaaS, ServiceOps, or audit records.

## Fixture files

* `demo_identity_lifecycle_events.json`
* `demo_identity_lifecycle_queue.json`
* `demo_identity_lifecycle_exceptions.json`
* `demo_identity_lifecycle_reviews.json`
* `demo_identity_lifecycle_evidence_packages.json`

Each file uses safe references, role labels, department labels, lifecycle status, risk level, reviewer aliases, evidence references, ticket references, BPM request references, and short summary notes only.

## Demo scenarios

The fixture set includes these demo scenarios:

* Joiner verified: new hire account provisioned and verified, `risk_level` = `Low`, `verification_status` = `Verified`.
* Mover mismatch: department transfer where the old role is still retained, `risk_level` = `High`, `verification_status` = `Mismatch`.
* Leaver active account: leaver account remains active after effective date, `risk_level` = `Critical`, `verification_status` = `Failed`.
* Privileged access retained: sudo / admin group retained after transfer, `risk_level` = `High`, `verification_status` = `ReviewRequired`.
* Exception expiring soon: temporary access exception is close to expiry, `risk_level` = `High`, `verification_status` = `ReviewRequired`.
* Quarterly review overdue: reviewer has not completed access review, `risk_level` = `High`, `verification_status` = `Overdue`.
* Evidence package completed: access removal verified with ServiceOps ticket and evidence reference, `risk_level` = `Low`, `verification_status` = `Verified`.

## Field contract

Lifecycle records should use this safe metadata contract:

| Field | Meaning |
| --- | --- |
| `lifecycle_event_id` | Stable demo lifecycle event identifier |
| `employee_ref` | Fake employee alias, such as `EMP-DEMO-001` |
| `user_display_name` | Safe demo display label, such as `Demo User A` |
| `department` | Department label or safe department reference |
| `role_before` | Previous role, group, or responsibility label |
| `role_after` | New role, group, or responsibility label |
| `event_type` | `Joiner`, `Mover`, `Leaver`, `Reviewer`, or `Exception` |
| `event_source` | Safe source label such as `HRM`, `BPM`, `ServiceOps`, `IAM`, `AD`, `LDAP`, `SaaS`, or `271ops` |
| `effective_date` | Date the lifecycle event should take effect |
| `expected_action` | Expected account or permission action summary |
| `actual_action` | Observed action or execution summary |
| `verification_status` | Demo status such as `Verified`, `Mismatch`, `Failed`, `ReviewRequired`, or `Overdue` |
| `evidence_ref` | Safe evidence reference, such as `EVD-271OPS-LC-001` |
| `serviceops_ticket_ref` | Safe ServiceOps ticket reference, such as `SVC-DEMO-001` |
| `bpm_request_ref` | Safe BPM request reference, such as `BPM-DEMO-001` |
| `reviewer` | Reviewer role or safe reviewer alias |
| `review_due_date` | Due date for lifecycle review |
| `exception_reason` | Short safe reason for exception retention |
| `exception_expiry_date` | Expiry date for exception access |
| `risk_level` | `Low`, `Medium`, `High`, or `Critical` |
| `notes` | Short safe summary only |

Future APIs may normalize enum casing if needed. These fixture values prioritize demo readability and the Task #215 scenario labels.

## Safety boundary

These fixtures are safe metadata only. They may include:

* Fake employee references, such as `EMP-DEMO-001`
* Fake user display labels, such as `Demo User A`
* Safe evidence references, such as `EVD-271OPS-LC-001`
* Safe ServiceOps ticket references, such as `SVC-DEMO-001`
* Safe BPM request references, such as `BPM-DEMO-001`
* Department, role, reviewer, lifecycle, and risk labels
* Short summary notes

They must not include secrets, credentials, passwords, API keys, private keys, tokens, SSH keys, real names, real employee numbers, real email addresses, sensitive HR personal data, raw BPM form bodies, raw attachment content, raw logs, full home paths, or raw command output.

## What is intentionally excluded

These files intentionally exclude:

* Frontend implementation
* Backend implementation
* Database schema or migrations
* API routes
* Production configuration
* Identity system connectors
* Direct AD / LDAP / IAM / SaaS mutation
* Raw HR records
* Raw BPM forms
* Raw ServiceOps ticket bodies
* Raw evidence attachments
* Raw verification logs

## Future API mapping

Future read-only fixture API design may map these files to:

```text
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
```

The future API should return safe references, lifecycle status, risk levels, review metadata, evidence references, warning summaries, and short notes. It should not mutate identity systems or expose raw sensitive records.

## Limitations

* Demo fixture only
* Read-only intent only
* No live HRM, BPM, AD, LDAP, IAM, SaaS, or ServiceOps connector
* No production compliance claim
* No proof of actual access removal
* No raw evidence storage
* No frontend or API implementation in this task

## Recommended next task

* Task #216: 271Ops Identity Lifecycle Read-only Fixture API Design
