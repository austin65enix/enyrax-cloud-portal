# RuntimeOps RCA Workflow Design

## 1. Purpose

RuntimeOps RCA Workflow turns runtime diagnosis evidence into a Root Cause Analysis governance process that is traceable, reviewable, repeatable, and verifiable.

RuntimeOps is not only a dashboard. It should preserve the full diagnosis and closure chain:

```text
Runtime Symptom
-> Safe Evidence
-> RCA Finding
-> ServiceOps Remediation
-> Verification Result
-> Closure
```

## 2. Product Context

RuntimeOps currently has the foundation for runtime evidence governance:

* Python_RuntimeOps
* .NET_RuntimeOps
* Safe Evidence Schema
* Evidence Validator
* CI guardrail
* RuntimeOps dashboard
* Portal entry

RCA Workflow is the next governance layer. It connects safe runtime evidence to findings, review, remediation references, verification, and knowledge capture.

## 3. Core RCA Flow

Recommended RCA flow:

```text
Runtime Alert / ServiceOps Ticket
-> Runtime Diagnosis Run
-> Safe Evidence Collection
-> Evidence Validation
-> RCA Draft
-> Human Review
-> RCA Finding Confirmed
-> Remediation Plan
-> ServiceOps Ticket Link
-> Verification Evidence
-> RCA Closure
-> Postmortem / Knowledge Base
```

The flow is evidence-first and human-reviewed. RuntimeOps should not mutate production systems as part of RCA confirmation.

## 4. RCA Workflow States

Recommended RCA states:

* New Symptom
* Evidence Collected
* Evidence Validated
* RCA Drafted
* Review Required
* RCA Confirmed
* Remediation Queued
* Remediation In Progress
* Verification Pending
* Verified
* Closed
* Reopened

State transitions should preserve timestamps, reviewer references, and evidence references.

## 5. RCA Finding Fields

Recommended RCA finding fields:

| Field | Purpose |
| --- | --- |
| `rca_finding_id` | Stable RCA finding identifier. |
| `runtime_event_id` | Runtime symptom or event reference. |
| `diagnosis_run_id` | RuntimeOps diagnosis run reference. |
| `service_name` | Affected service name. |
| `runtime_family` | Runtime family such as Python or .NET. |
| `symptom` | Human-readable symptom summary. |
| `finding_type` | RCA finding type. |
| `finding_summary` | Concise RCA finding. |
| `root_cause_category` | Controlled category label. |
| `confidence` | Confidence level with evidence basis. |
| `evidence_refs` | Safe evidence references. |
| `validator_status` | Evidence validation status. |
| `reviewer` | Human reviewer reference. |
| `review_status` | Review state. |
| `serviceops_ticket_ref` | Linked ServiceOps ticket reference. |
| `remediation_ref` | Linked remediation reference. |
| `verification_ref` | Linked verification evidence reference. |
| `postmortem_ref` | Linked postmortem reference. |
| `knowledge_base_ref` | Linked knowledge base reference. |
| `risk_level` | Risk level. |
| `severity` | Severity label. |
| `status` | RCA workflow status. |
| `created_at` | Creation timestamp. |
| `updated_at` | Last update timestamp. |
| `closed_at` | Closure timestamp. |
| `notes` | Safe reviewer notes. |

## 6. Root Cause Categories

Recommended root cause categories:

* Code Path Latency
* Dependency Latency
* Worker Timeout
* Memory Growth
* CPU Hotspot
* ThreadPool Starvation
* GC Pressure
* Queue Backlog
* Configuration Drift
* Capacity Constraint
* Network / DNS Symptom
* Database Latency Symptom
* External Service Degradation
* Unknown / Needs More Evidence

## 7. Evidence-to-RCA Mapping

Safe evidence should map to RCA categories through explicit rules and human review.

| Evidence type | Possible RCA category |
| --- | --- |
| `endpoint_latency_summary` | Code Path Latency / Dependency Latency |
| `profile_summary` | CPU Hotspot |
| `memory_summary` | Memory Growth |
| `counter_summary` | ThreadPool Starvation / GC Pressure |
| `background_job_summary` | Queue Backlog / Worker Timeout |
| `dependency_latency_summary` | External Service Degradation |
| `verification_summary` | Closure Evidence |

Mapping should create an RCA draft first. Confirmation requires human review.

## 8. Human Review Model

AI can assist by drafting RCA summaries, classifying candidate root cause categories, and identifying related evidence. RuntimeOps should not automatically confirm RCA findings.

RCA Confirmed requires a human reviewer. High-risk events must be reviewed by a human before they can move to remediation or closure.

AI-generated RCA drafts must include:

* Confidence
* Evidence references
* Assumptions
* Missing evidence, if any
* Suggested next review action

Reviewer actions:

* Confirm
* Request more evidence
* Reject finding
* Link remediation
* Close after verification

## 9. ServiceOps Integration Model

RCA does not directly execute remediation.

Actions such as remove, fix, restart, config change, scale, rollback, or other operational changes should become ServiceOps-tracked work:

* `serviceops_ticket_ref`
* `remediation_ref`
* `owner_team`
* `due_date`
* `verification_required`

ServiceOps tracks execution. RuntimeOps preserves the diagnosis, evidence, RCA, remediation reference, and verification chain.

## 10. Verification Model

Verification should include:

* `before_summary`
* `after_summary`
* `verification_status`
* `verification_evidence_ref`
* `verified_at`
* `verified_by`
* `regression_watch_period`
* `residual_risk`
* `closure_decision`

Verification states:

* Pending
* EvidenceCaptured
* Improved
* NoChange
* Failed
* Verified
* Reopened

RCA should not close until verification evidence is available and reviewed.

## 11. RCA Dashboard Views

Future RuntimeOps RCA dashboard sections:

* RCA Summary Cards
* Open RCA Findings
* High Risk RCA Queue
* Evidence Validation Status
* RCA Draft Queue
* Review Required
* Remediation Linked Items
* Verification Pending
* Recently Verified RCA
* Reopened RCA
* Knowledge Base Candidates

Dashboard views should show safe evidence references, summaries, reviewer state, remediation links, and verification state.

## 12. Risk Scoring

Suggested scoring rules:

| Condition | Risk |
| --- | --- |
| Production service unavailable | Critical |
| Repeated timeout with user impact | High |
| Confirmed memory growth | High |
| Confirmed ThreadPool starvation | High |
| Evidence missing for high risk incident | High |
| RCA pending over SLA | Medium / High |
| Verification pending after remediation | Medium |
| Verified and closed | Low |
| False alarm | Low |

Risk scoring should remain explainable and evidence-linked.

## 13. SLA / Governance Rules

Suggested governance rules:

* Critical RCA draft within 4 hours.
* High RCA draft within 1 business day.
* Medium RCA draft within 3 business days.
* Verification required before closure.
* Reopen if symptom recurs during watch period.
* Postmortem required for Critical.
* Knowledge Base candidate for recurring patterns.

SLA timers should be visible in dashboard queues and review views.

## 14. AgentOps Integration

AgentOps can assist with:

* Summarizing safe evidence
* Drafting RCA findings
* Classifying root cause category
* Suggesting remediation options
* Generating postmortem draft

AgentOps must not:

* Execute production command
* Restart service
* Kill process
* Modify config
* Modify DB
* Confirm RCA without human review

## 15. Knowledge Base / Postmortem Model

Recommended postmortem and knowledge fields:

* `postmortem_ref`
* `incident_summary`
* `timeline_summary`
* `root_cause_summary`
* `contributing_factors`
* `remediation_summary`
* `verification_summary`
* `prevention_actions`
* `knowledge_base_candidate`
* `recurrence_pattern`

Knowledge Base candidates should be generated from recurring verified RCA patterns, not from unreviewed drafts.

## 16. API Design Preview

Future read-only API design only. Not implemented in this task.

Potential future endpoints:

* `GET /api/runtimeops/rca/findings`
* `GET /api/runtimeops/rca/findings/{rca_finding_id}`
* `GET /api/runtimeops/rca/open`
* `GET /api/runtimeops/rca/review-required`
* `GET /api/runtimeops/rca/remediation-linked`
* `GET /api/runtimeops/rca/verification-pending`
* `GET /api/runtimeops/rca/dashboard`
* `GET /api/runtimeops/rca/postmortems`
* `GET /api/runtimeops/rca/knowledge-base-candidates`

The first implementation should be read-only and fixture-backed.

## 17. Demo Scenarios

| Scenario | Runtime family | RCA focus | Expected linkage |
| --- | --- | --- | --- |
| FastAPI slow endpoint RCA | Python | Code Path Latency | Endpoint latency evidence to RCA finding and ServiceOps ticket. |
| Python memory growth RCA | Python | Memory Growth | Memory summary evidence to remediation and verification reference. |
| Python background job timeout RCA | Python | Worker Timeout / Queue Backlog | Background job summary to ServiceOps work item. |
| .NET ThreadPool starvation RCA | .NET | ThreadPool Starvation | Counter evidence to RCA finding and verification evidence. |
| .NET GC pressure RCA | .NET | GC Pressure | Counter evidence and dump metadata reference to RCA finding. |
| External dependency latency RCA | Cross-runtime | External Service Degradation | Dependency latency summary to remediation owner and verification. |
| Recurring timeout reopened RCA | Cross-runtime | Dependency Latency / Worker Timeout | Reopen closed RCA when symptom recurs during watch period. |
| RCA verified and converted to knowledge base candidate | Cross-runtime | Closure Evidence | Verification summary to postmortem and knowledge base candidate. |

## 18. Safety Boundary

Required safety boundary:

* Design only.
* Read-only RCA workflow first.
* No production command execution.
* No restart action.
* No kill process action.
* No config change.
* No database write.
* No raw dump.
* No raw trace.
* No raw command output.
* No raw stack trace by default.
* No secret exposure.
* No customer raw data.
* AI cannot confirm RCA without human review.
* ServiceOps remediation is reference-only in this design.

## 19. Limitations

* Design only.
* No frontend.
* No backend.
* No fixture.
* No API.
* No workflow engine.
* No live collector.
* No AgentOps automation.
* No ServiceOps write integration.

## 20. Recommended Next Task

Task #341: RuntimeOps ServiceOps Integration Design
