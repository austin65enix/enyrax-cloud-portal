# 271Ops Exception Governance Design

## Purpose

Exception Governance is the exception access governance module for 271Ops.

The goal is to manage temporary access, emergency access, privileged exceptions, policy exceptions, and expiry review as a traceable governance workflow.

The module is positioned as a read-only Access Verify / Identity Governance Readiness layer.

It does not replace AD, LDAP, IAM, HRM, BPM, or SaaS Admin Console. Those systems remain responsible for identity records, access administration, HR events, workflow approvals, and SaaS permission changes.

## Product Context

Exception Governance extends the governance chain:

```text
Account Governance
→ Identity Lifecycle
→ Access Review Campaign
→ Exception Governance
→ Audit Evidence
```

## Core Exception Types

| Exception type | Purpose |
| --- | --- |
| Temporary Access Exception | Time-bound access granted for a specific business window. |
| Emergency Access Exception | Urgent access granted for incident response or emergency recovery. |
| Privileged Access Exception | Elevated access retained outside the standard access baseline. |
| Segregation of Duties Exception | Access that conflicts with normal role separation but is temporarily accepted. |
| Leaver Delay Exception | Delayed revocation or cleanup after departure, suspension, or role exit. |
| Review Extension Exception | Extension for a review item or campaign that cannot be completed by due date. |
| Policy Exception | Documented exception to an access governance or security policy. |

## Exception Lifecycle

```text
Exception Request
→ Risk Review
→ Owner Approval Reference
→ Temporary Grant Reference
→ Expiry Watch
→ Review / Renew / Revoke Decision
→ ServiceOps Remediation
→ Evidence Package
→ Exception Closed
```

## Exception Fields

Suggested fields:

| Field | Meaning |
| --- | --- |
| exception_id | Stable exception identifier |
| exception_type | Exception category |
| exception_title | Human-readable exception title |
| employee_ref | Safe employee alias or reference |
| user_display_name | Demo-safe display label |
| department | Department label or safe department reference |
| system_ref | Target system reference |
| access_type | Access category |
| privilege_level | Standard / Elevated / High / Admin |
| exception_reason | Short exception reason |
| business_justification | Short safe business justification |
| owner | Exception owner role or safe owner alias |
| reviewer | Reviewer role or safe reviewer alias |
| request_ref | Safe request reference |
| approval_ref | Safe approval reference |
| serviceops_ticket_ref | Linked ServiceOps ticket reference |
| evidence_ref | Safe evidence reference |
| start_date | Exception start date |
| expiry_date | Exception expiry date |
| review_due_date | Review due date |
| status | Active / ExpiringSoon / OverSLA / ReviewOverdue / ExpiredActive / Closed |
| risk_level | Low / Medium / High / Critical |
| renewal_count | Number of renewals |
| decision | Future decision label |
| decision_reason | Short decision reason |
| notes | Short safe summary only |

## Decision Model

Future reviewer or owner decisions:

* Renew Exception
* Revoke Access
* Convert to Standard Access
* Escalate
* Need More Evidence
* Close as Resolved

This task is design only. These options describe a future workflow model and do not implement mutation, approval, rejection, permission changes, or write actions.

## Risk Scoring

| Condition | Risk level |
| --- | --- |
| Expired exception still active | Critical |
| Privileged exception without review | High |
| Emergency access over SLA | High |
| Leaver delay exception | Critical / High |
| Repeated renewal count > 2 | High |
| Missing approval reference | Medium / High |
| Expiring within 7 days | Medium / High |
| Closed with evidence | Low |

## Exception Views

Future frontend views may include:

* Exception Summary
* Active Exceptions
* Expiring Soon
* Expired Exceptions
* Privileged Exceptions
* Emergency Access Watch
* Renewal Review Queue
* ServiceOps Remediation Queue
* Evidence Package Preview
* Audit Trail Preview

## API Design Preview

Future read-only API design only. Not implemented in this task.

Potential endpoints:

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

## Demo Scenarios

| Scenario | Expected governance behavior | Risk level |
| --- | --- | --- |
| Temporary access expiring soon | Exception requires renewal or revocation decision before expiry. | Medium / High |
| Emergency access over SLA | Emergency access exceeded allowed review window and requires escalation. | High |
| Privileged exception missing review | Privileged exception has no current review decision. | High |
| Expired exception still active | Expired exception remains active and requires urgent remediation. | Critical |
| Leaver delay exception with remediation ticket | Delayed leaver cleanup links to ServiceOps remediation. | Critical / High |
| Review extension exception | Review extension is granted or requires additional review. | Medium / High |
| Exception closed with evidence package | Exception is closed with decision and evidence references. | Low |

## Integration Model

* Account Governance provides account and permission baseline data.
* Identity Lifecycle provides Joiner / Mover / Leaver context.
* Access Review Campaign creates exception review items.
* ServiceOps tracks remediation tickets.
* Evidence Package stores safe evidence references.
* Audit Readiness aggregates audit output.

## Safety Boundary

Exception Governance follows these boundaries:

* Design only
* Read-only verification first
* No direct AD mutation
* No direct LDAP mutation
* No direct IAM mutation
* No SaaS permission mutation
* No approve / reject action implemented
* No upload control
* No edit / delete
* No password / credential / API key / private key
* No full HR personal data
* No raw BPM form body
* No raw attachment content
* No raw logs
* Safe metadata only

## Product Positioning

Exception Governance extends 271Ops into:

* Identity Governance Readiness Platform
* Exception Governance layer
* Access Verify layer
* Audit Evidence layer
* ServiceOps-linked remediation governance

## Limitations

* Design only
* No frontend
* No backend
* No fixture
* No API
* No mutation workflow
* No live connector

## Recommended Next Task

* Task #232: 271Ops Exception Governance Demo Fixture Design
