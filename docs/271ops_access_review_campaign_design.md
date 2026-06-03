# 271Ops Access Review Campaign Design

## Purpose

Access Review Campaign is the periodic access review governance module for 271Ops.

The goal is to extend Account Governance and Identity Lifecycle into scheduled, traceable, and audit-ready review campaigns. It turns access review from an ad hoc queue into a campaign model with scope, reviewers, due dates, decisions, remediation references, and evidence packages.

The module is positioned as a read-only Access Verify / Identity Governance Readiness layer.

It does not replace AD, LDAP, IAM, HRM, BPM, or SaaS Admin Console. Those systems remain the source systems for identity records, access administration, HR events, workflow approvals, and SaaS permission changes.

## Product Context

271Ops currently includes:

* Account Governance
* Identity Lifecycle Governance
* Access Verify
* Exception Tracking
* Evidence Package
* Audit Readiness

Access Review Campaign is the next governance layer:

```text
Account Governance
→ Identity Lifecycle
→ Access Review Campaign
→ Audit Evidence
```

## Core Campaign Model

| Campaign model | Purpose | Typical scope |
| --- | --- | --- |
| Quarterly Access Review | Periodic access review across key systems and departments. | Standard user access, business roles, department owners, evidence completeness. |
| Privileged Access Review | Focused review for elevated or administrative permissions. | Admin accounts, privileged groups, sudo roles, break-glass access, production operators. |
| Department Access Review | Department-specific review for role alignment and access ownership. | Department users, transferred employees, shared resources, department-owned SaaS tools. |
| SaaS Access Review | Review for cloud application roles, licenses, and administrative access. | SaaS users, SaaS admins, paid licenses, external collaborators, inactive users. |
| Exception Access Review | Review of temporary or exception access before expiry. | Exception approvals, expiry dates, renewal reasons, revocation evidence. |
| Leaver Follow-up Review | Follow-up review for departed or suspended users. | Disabled accounts, removed groups, SaaS access cleanup, evidence of revocation. |

## Campaign Lifecycle

```text
Campaign Draft
→ Scope Selection
→ Reviewer Assignment
→ Review Open
→ Reminder / Escalation
→ Decision Capture
→ ServiceOps Remediation
→ Evidence Package
→ Campaign Closed
→ Audit Report
```

Lifecycle meaning:

| Stage | Meaning |
| --- | --- |
| Campaign Draft | Define campaign intent, period, owner, risk level, and target review type. |
| Scope Selection | Select systems, departments, users, access types, exceptions, or lifecycle events to review. |
| Reviewer Assignment | Assign reviewers by department, system owner, security owner, or governance owner. |
| Review Open | Reviewers can inspect safe metadata and record future decisions in the campaign workflow design. |
| Reminder / Escalation | Overdue reviewers or high-risk items become attention items. |
| Decision Capture | Reviewer decision, reason, evidence reference, exception reference, or remediation need is captured. |
| ServiceOps Remediation | Remove or change decisions create ServiceOps remediation references instead of direct permission changes. |
| Evidence Package | Campaign records, decisions, exceptions, remediation tickets, and verification evidence are bundled. |
| Campaign Closed | Campaign is closed after review items are completed, accepted as exceptions, or linked to remediation. |
| Audit Report | Safe campaign summary, coverage, gaps, risk, and evidence references are prepared for audit readiness. |

## Campaign Fields

Suggested campaign fields:

| Field | Meaning |
| --- | --- |
| campaign_id | Stable campaign identifier |
| campaign_name | Human-readable campaign name |
| campaign_type | quarterly / privileged / department / saas / exception / leaver_follow_up |
| period | Campaign period, such as 2026-Q3 or 2026-06 |
| scope | Safe summary of selected systems, departments, access types, or lifecycle records |
| owner | Campaign owner role or safe owner alias |
| status | draft / scoping / assigned / open / escalated / remediation / evidence_packaging / closed |
| start_date | Campaign start date |
| due_date | Campaign due date |
| closed_date | Campaign close date, if closed |
| reviewer_count | Number of assigned reviewers |
| item_count | Number of review items |
| completed_count | Number of completed review items |
| overdue_count | Number of overdue review items |
| exception_count | Number of exception review items |
| remediation_ticket_count | Number of linked ServiceOps remediation tickets |
| evidence_package_ref | Safe evidence package reference |
| audit_report_ref | Safe audit report reference |
| risk_level | low / medium / high / critical |
| notes | Short safe summary only |

## Review Item Fields

Suggested review item fields:

| Field | Meaning |
| --- | --- |
| review_item_id | Stable review item identifier |
| campaign_id | Parent campaign identifier |
| employee_ref | Safe employee alias or reference |
| user_display_name | Display label suitable for demo or safe operational view |
| department | Department label or safe department reference |
| system_ref | Target system reference |
| access_type | AD group / LDAP group / SaaS role / IAM role / VPN / DB / folder / service account |
| role_name | Role, group, license, or permission label |
| privilege_level | standard / elevated / privileged / admin / break_glass |
| reviewer | Reviewer role or safe reviewer alias |
| review_decision | keep_access / remove_access / change_access / mark_exception / need_more_evidence / escalate |
| decision_reason | Short safe reason for the review decision |
| decision_date | Decision date, if captured |
| remediation_required | Boolean remediation indicator |
| serviceops_ticket_ref | Linked ServiceOps remediation ticket reference |
| evidence_ref | Safe evidence reference |
| exception_ref | Linked exception reference |
| risk_level | low / medium / high / critical |
| status | pending / in_review / decided / overdue / remediation_open / exception / verified / closed |
| notes | Short safe summary only |

## Reviewer Workflow

Future reviewer decision options:

* Keep Access
* Remove Access
* Change Access
* Mark as Exception
* Need More Evidence
* Escalate

This task is design only. These options describe a future workflow model and do not implement mutation, approval, rejection, permission changes, or write actions.

## Decision and Remediation Model

Review decisions do not directly change permissions.

Remove Access and Change Access decisions only create or reference ServiceOps remediation records. The actual AD, LDAP, IAM, or SaaS permission change remains in the existing administration system or manual operations workflow.

271Ops is responsible for tracking:

* Review decision
* Decision reason
* ServiceOps remediation ticket
* Verification evidence
* Exception reference
* Evidence package
* Audit report reference

This keeps 271Ops as an Access Verify and Identity Governance Readiness layer rather than an identity mutation system.

## Risk Scoring

Initial risk scoring model:

| Condition | Risk level | Reason |
| --- | --- | --- |
| Privileged access unreviewed | High | Elevated access remains without current reviewer confirmation. |
| Leaver account in review scope | Critical | Departed or suspended user access requires urgent verification. |
| Review overdue | Medium / High | Overdue review risk increases with account type, system sensitivity, and privilege level. |
| Exception expired | High | Temporary or exception access passed expiry without renewal or revocation evidence. |
| Missing reviewer decision | Medium | Access remains unresolved because ownership decision is missing. |
| Missing evidence | Medium | Review, approval, provisioning, exception, or remediation evidence is incomplete. |
| All reviewed and verified | Low | Review decision and verification evidence are aligned. |

## Campaign Views

Future frontend view blocks:

| View | Purpose |
| --- | --- |
| Campaign Summary | Shows campaign status, coverage, completion, overdue items, risk, and evidence readiness. |
| Active Campaigns | Lists active campaigns by owner, type, period, status, due date, and risk level. |
| Reviewer Progress | Shows reviewer assignment, completion percentage, overdue count, and escalation state. |
| Overdue Review Items | Highlights review items past due date by reviewer, department, system, and risk. |
| High Risk Access Items | Shows privileged, critical, stale, or leaver-related access items requiring attention. |
| Exception Review Queue | Tracks expiring, expired, renewed, or unresolved exception access. |
| Remediation Queue | Links remove or change decisions to ServiceOps remediation ticket references. |
| Evidence Package Preview | Previews safe evidence references collected for the campaign. |
| Audit Report Preview | Summarizes campaign scope, decisions, exceptions, remediation, and remaining gaps. |

## API Design Preview

Future read-only API design only. Not implemented in this task.

Potential endpoints:

```text
GET /api/271ops/access-review-campaigns
GET /api/271ops/access-review-campaigns/{campaign_id}
GET /api/271ops/access-review-campaigns/{campaign_id}/items
GET /api/271ops/access-review-campaigns/active
GET /api/271ops/access-review-campaigns/overdue-items
GET /api/271ops/access-review-campaigns/remediation-queue
GET /api/271ops/access-review-campaigns/evidence-packages
```

These endpoints should remain GET-only by default and should return safe campaign metadata, review item summaries, risk levels, remediation references, exception references, evidence package references, warnings, and audit-ready summaries.

## Demo Scenarios

| Scenario | Campaign type | Expected governance behavior | Risk level |
| --- | --- | --- | --- |
| Quarterly access review campaign in progress | Quarterly Access Review | Department reviewers are assigned, review items are open, and campaign progress is tracked by completion and overdue count. | Medium |
| Privileged admin access review overdue | Privileged Access Review | Admin roles remain unreviewed after due date and are escalated as high-risk attention items. | High |
| Department transfer stale access review | Department Access Review | A mover still has old department access and requires reviewer decision plus remediation reference. | Medium / High |
| SaaS license access review | SaaS Access Review | Inactive or unneeded SaaS licenses are reviewed for retention, removal, or evidence gaps. | Medium |
| Exception access review expiring soon | Exception Access Review | Temporary access is near expiry and requires renewal justification or revocation evidence. | High |
| Review decision creates ServiceOps remediation reference | Quarterly Access Review | Remove or change decision creates a linked ServiceOps remediation reference without direct permission mutation. | Medium |

## Safety Boundary

Access Review Campaign follows these boundaries:

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

Access Review Campaign extends 271Ops into:

* Identity Governance Readiness Platform
* Access Review Campaign layer
* Access Verify layer
* Audit Evidence layer
* ServiceOps-linked remediation governance

The value is not direct identity administration. The value is scheduled, traceable, and audit-ready access governance: campaign scope, reviewer assignment, decision capture, remediation references, exception tracking, verification evidence, and audit packages.

## Limitations

* Design only
* No frontend
* No backend
* No fixture
* No API
* No mutation workflow
* No live connector

## Recommended Next Task

* Task #224: 271Ops Access Review Campaign Demo Fixture Design
