# 271ops Identity Lifecycle Governance Design

## Purpose

271ops Identity Lifecycle Governance is the account and permission lifecycle governance design for 271ops. It extends Account Governance from access request evidence and access review queues into Joiner / Mover / Leaver lifecycle verification.

The module is positioned as an Access Verify / Identity Governance Readiness layer. It helps teams verify whether account creation, role changes, access retention, revocation, exceptions, and review evidence are traceable and audit-ready.

It does not replace AD, LDAP, IAM, HRM, BPM, or SaaS Admin Console. Those systems remain the source systems for identity records, access administration, HR events, workflow approvals, and SaaS permission changes.

## Core Lifecycle Model

271ops Identity Lifecycle Governance uses a JML + Review + Exception model.

| Lifecycle area | Purpose | Governance question |
| --- | --- | --- |
| Joiner | New hire account creation and permission provisioning verification | Was the account created from an approved HR / BPM event, provisioned through the right ticket, and verified after activation? |
| Mover | Transfer, department change, role change, and permission adjustment verification | Were old permissions removed, new permissions approved, and role mismatches reviewed? |
| Leaver | Departure, suspension, account revocation, and group removal verification | Was the account disabled or removed on time, and is revocation evidence available? |
| Reviewer | Periodic access review | Does each active permission still have a business reason, owner, approval evidence, and review decision? |
| Exception | Exception retention and expiry tracking | Is the exception approved, time-bound, reviewed before expiry, and remediated when it expires? |

## Lifecycle Event Fields

Future lifecycle records should use safe references and short summaries. Suggested fields:

| Field | Meaning |
| --- | --- |
| lifecycle_event_id | Stable event identifier |
| employee_ref | Safe employee alias or reference |
| user_display_name | Display label suitable for demo or safe operational view |
| department | Department label or safe department reference |
| role_before | Previous role, group, or responsibility label |
| role_after | New role, group, or responsibility label |
| event_type | joiner / mover / leaver / reviewer / exception |
| event_source | HRM / BPM / ServiceOps / IAM / AD / LDAP / SaaS / 271ops |
| effective_date | Date the lifecycle event should take effect |
| expected_action | Expected account or permission action |
| actual_action | Observed action or execution summary |
| verification_status | verified / pending / mismatch / overdue / exception / revoked |
| evidence_ref | Safe evidence reference |
| serviceops_ticket_ref | Linked ServiceOps ticket reference |
| bpm_request_ref | Linked BPM request reference |
| reviewer | Reviewer role or safe reviewer alias |
| review_due_date | Due date for lifecycle review |
| exception_reason | Short reason for exception retention |
| exception_expiry_date | Expiry date for exception access |
| risk_level | low / medium / high / critical |
| notes | Short safe summary only |

## Governance Flow

```text
HR / BPM event
-> 271ops lifecycle queue
-> ServiceOps execution evidence
-> AD / LDAP / IAM / SaaS status verification
-> Access Review Queue
-> Exception or Remediation
-> Audit evidence package
```

The lifecycle queue receives or references HR / BPM lifecycle events. ServiceOps evidence shows whether work was executed. AD / LDAP / IAM / SaaS status verification confirms whether the account state and permission state match the expected lifecycle action. Access Review Queue records periodic decisions. Exceptions and remediation track unresolved mismatches. Audit evidence packages group the safe references for review.

## Governance Views

Future frontend views may include:

### Identity Lifecycle Queue

Shows all lifecycle events waiting for verification, including joiner, mover, leaver, reviewer, and exception items.

### Joiner Verification

Shows new hire account creation, initial permission provisioning, BPM approval evidence, ServiceOps execution reference, and post-provisioning verification status.

### Mover Role Change Review

Shows department transfer or role change events, compares `role_before` and `role_after`, highlights stale permissions, and links required adjustment evidence.

### Leaver Revoke Verification

Shows departure or suspension events, expected revocation actions, actual account status, group removal checks, and overdue disablement risk.

### Exception Expiry Watch

Tracks temporary or exception access, expiry dates, exception reasons, review owners, and upcoming or expired exceptions.

### Quarterly Access Review

Groups periodic access review items by period, system, reviewer, account type, evidence status, and decision.

### Evidence Package

Collects safe references for HR / BPM events, ServiceOps tickets, IAM status checks, access review decisions, exceptions, remediation tickets, and audit logs.

## Risk Scoring

Simple initial risk scoring:

| Condition | Risk level | Reason |
| --- | --- | --- |
| Leaver not disabled | Critical | Former or suspended user still has active access. |
| Privileged access retained | High | Elevated access remains after transfer, role change, or expiry. |
| Department mismatch | Medium | Current permission does not match department or role context. |
| Missing evidence | Medium | Approval, execution, or verification evidence is incomplete. |
| Review overdue | Medium / High | Overdue review risk depends on account type and permission level. |
| Exception expired | High | Exception access passed expiry without revocation or renewal evidence. |
| Normal verified | Low | Lifecycle event and evidence are aligned. |

## Safety Boundary

271ops Identity Lifecycle Governance should follow these boundaries:

- Read-only verification first
- No direct AD mutation
- No direct LDAP mutation
- No direct IAM mutation
- No SaaS permission mutation
- No password / credential / API key / private key
- No full HR personal data
- No raw BPM form body
- No raw attachment content
- No raw logs
- Only safe references and short summaries

## API Design Preview

Future read-only API design only. Not implemented in this task.

Potential endpoints:

```text
GET /api/271ops/identity-lifecycle/events
GET /api/271ops/identity-lifecycle/queue
GET /api/271ops/identity-lifecycle/exceptions
GET /api/271ops/identity-lifecycle/reviews
GET /api/271ops/identity-lifecycle/evidence-packages
```

These future APIs should remain GET-only by default and should return safe references, lifecycle status, risk levels, review metadata, evidence references, warnings, and summaries. They should not mutate identity systems or store raw sensitive records.

## Demo Scenario

| Scenario | Event type | Expected governance behavior | Risk level |
| --- | --- | --- | --- |
| New hire account provisioned and verified | Joiner | HR / BPM event links to ServiceOps provisioning ticket and verified account status. | Low |
| Department transfer role mismatch | Mover | Old department permission remains after transfer and requires review. | Medium |
| Leaver account still active | Leaver | Account remains active after departure effective date and requires urgent remediation. | Critical |
| Privileged sudo group retained after transfer | Mover | Privileged group remains after role change and needs owner review or revocation. | High |
| Exception access expiring soon | Exception | Temporary exception is near expiry and needs renewal review or revocation evidence. | High |

## Product Positioning

Identity Lifecycle Governance extends 271ops from an Account Governance dashboard into:

- Identity Governance Readiness
- Access Verify
- Audit Evidence Layer
- ServiceOps-linked remediation governance

The value is not direct identity administration. The value is traceable governance: connecting lifecycle events, approval references, execution evidence, access state verification, exception tracking, and audit-ready evidence packages.

## Limitations

- Design only
- No frontend
- No backend
- No fixture
- No API
- No mutation
- No live connector

## Recommended Next Task

- Task #215: 271ops Identity Lifecycle Demo Fixture Design
