# RuntimeOps ServiceOps Integration Design

## 1. Purpose

RuntimeOps ServiceOps Integration connects RuntimeOps runtime diagnosis, safe evidence, RCA findings, remediation references, and verification results back into the ServiceOps ticket governance flow.

RuntimeOps does not directly change production. It converts diagnosis results into traceable ServiceOps remediation tickets and preserves the evidence chain needed for review and closure.

## 2. Product Context

RuntimeOps currently has:

* Python_RuntimeOps
* .NET_RuntimeOps
* Safe Evidence Schema
* Evidence Validator
* RCA Workflow Design
* RuntimeOps Dashboard

ServiceOps is the ENYRAX foundation for ticket, remediation, worklog, and close flow governance.

This integration turns RuntimeOps into:

```text
Runtime Symptom
-> Runtime Diagnosis
-> Safe Evidence
-> RCA Finding
-> ServiceOps Remediation Ticket
-> Verification Evidence
-> Closure
```

## 3. Integration Principles

* RuntimeOps diagnoses, ServiceOps executes.
* RuntimeOps never directly restarts, kills, patches, or changes config.
* ServiceOps owns remediation workflow.
* Evidence refs connect RuntimeOps and ServiceOps.
* RCA closure requires verification evidence.
* High-risk remediation requires human approval.
* AgentOps may summarize, not execute.

## 4. Integration Flow

Recommended integration flow:

```text
Runtime Alert / RuntimeOps Finding
-> RCA Draft
-> Human Review
-> Create / Link ServiceOps Ticket
-> Assign Owner Team
-> Remediation Worklog
-> Runtime Verification
-> Evidence Package
-> Close ServiceOps Ticket
-> Close RCA
```

The first implementation should be read-only and reference-based. Future write workflows should require explicit approval and audit logging.

## 5. ServiceOps Ticket Mapping

RuntimeOps can map RCA and evidence data into ServiceOps ticket fields:

| ServiceOps ticket field | RuntimeOps source |
| --- | --- |
| `ticket_id` | ServiceOps ticket identifier. |
| `source_module` | `RuntimeOps`. |
| `source_ref` | RuntimeOps finding or diagnosis reference. |
| `runtime_family` | Python, .NET, or future runtime family. |
| `service_name` | Affected service. |
| `diagnosis_run_id` | RuntimeOps diagnosis run. |
| `rca_finding_id` | RuntimeOps RCA finding. |
| `symptom` | Runtime symptom summary. |
| `risk_level` | RuntimeOps risk level. |
| `severity` | RuntimeOps severity. |
| `remediation_type` | Controlled remediation category. |
| `requested_action` | Safe action request summary. |
| `owner_team` | Responsible team. |
| `due_date` | Remediation due date. |
| `evidence_refs` | Safe evidence references. |
| `verification_required` | Whether closure requires verification evidence. |
| `verification_ref` | RuntimeOps verification reference. |
| `status` | ServiceOps ticket status. |
| `notes` | Safe notes only. |

## 6. Remediation Types

Recommended remediation categories:

* Code Fix Required
* Config Review Required
* Capacity Review Required
* Dependency Review Required
* Worker / Queue Review Required
* Database Query Review Required
* Memory Leak Investigation
* ThreadPool / GC Investigation
* Restart Review Required
* Rollback Review Required
* Monitoring Rule Update
* Knowledge Base Update

The remediation type should describe the review or work category, not an automatic action.

## 7. No Direct Mutation Rule

RuntimeOps only proposes remediation references. It must not directly execute:

* Restart service
* Kill process
* Deploy code
* Edit config
* Modify DB
* Recycle IIS App Pool
* Change firewall
* Change IAM / AD / LDAP
* Modify cloud resource

If any of these actions are required, they must go through ServiceOps, ChangeOps, or a human-approved operational process.

## 8. Worklog Model

ServiceOps worklogs can record safe operational progress:

* `diagnosis_summary`
* `evidence_reviewed`
* `action_taken`
* `command_not_recorded_raw`
* `safe_action_summary`
* `owner_note`
* `verification_step`
* `rollback_plan_ref`
* `risk_acceptance_ref`

Worklogs must not record raw command output, secrets, customer data, raw dumps, raw traces, raw stack traces, or sensitive paths.

## 9. Verification Model

RuntimeOps verification can be linked back to ServiceOps through:

* `verification_ref`
* `before_summary`
* `after_summary`
* `metric_summary`
* `verification_status`
* `verified_by`
* `verified_at`
* `residual_risk`
* `evidence_ref`

Verification statuses:

* Pending
* EvidenceCaptured
* Improved
* NoChange
* Failed
* Verified
* Reopened

ServiceOps tickets should not close when verification is required but missing.

## 10. Status Mapping

Recommended status mapping:

| RuntimeOps RCA status | ServiceOps ticket status |
| --- | --- |
| RCA Drafted | Open |
| Review Required | Open |
| RCA Confirmed | Open |
| Remediation Queued | Open |
| Remediation In Progress | In Progress |
| Verification Pending | Pending Verification |
| Verified | Done |
| Closed | Archived |
| Reopened | Open |

If evidence is incomplete, ServiceOps can use `Pending Evidence`.

## 11. Dashboard / UI Integration

Future RuntimeOps RCA Detail should show:

* Linked ServiceOps Ticket
* Remediation Status
* Owner Team
* Due Date
* Worklog Summary
* Verification Evidence
* Closure Status

Future ServiceOps Ticket Detail should show:

* RuntimeOps Diagnosis Ref
* RCA Finding Ref
* Evidence Refs
* Before / After Summary
* Runtime Verification Status

Both views should display safe references and summaries only.

## 12. API Design Preview

Future read-only API design only. Not implemented in this task.

RuntimeOps side:

* `GET /api/runtimeops/serviceops-links`
* `GET /api/runtimeops/serviceops-links/{link_id}`
* `GET /api/runtimeops/serviceops-links/open`
* `GET /api/runtimeops/serviceops-links/verification-pending`
* `GET /api/runtimeops/serviceops-links/dashboard`

ServiceOps side:

* `GET /api/serviceops/runtimeops-linked-tickets`
* `GET /api/serviceops/tickets/{ticket_id}/runtimeops-summary`

The first implementation should be read-only and fixture-backed.

## 13. Demo Scenarios

| Scenario | RuntimeOps input | ServiceOps linkage |
| --- | --- | --- |
| FastAPI slow endpoint creates ServiceOps remediation reference | Python endpoint latency evidence and RCA finding. | Code fix or dependency review ticket. |
| Python memory growth requires investigation ticket | Python memory summary evidence. | Memory leak investigation ticket. |
| Python background job timeout links to worker review ticket | Background job timeout RCA. | Worker / queue review ticket. |
| .NET ThreadPool starvation creates remediation ticket | .NET counter evidence and ThreadPool RCA. | ThreadPool / GC investigation ticket. |
| .NET GC pressure creates capacity review ticket | .NET GC pressure counter evidence. | Capacity review or memory investigation ticket. |
| External dependency latency links to dependency review | Dependency latency evidence. | Dependency review ticket with owner team. |
| RCA verified after ServiceOps remediation | Verification evidence captured after remediation. | ServiceOps ticket moves to Done and RCA moves to Verified. |
| RCA reopened because symptom recurs | Recurring timeout during watch period. | ServiceOps ticket reopened or new linked ticket created. |

## 14. Safety Boundary

Required safety boundary:

* Design only.
* Read-only integration first.
* No ServiceOps ticket creation implemented.
* No ServiceOps write API implemented.
* No production command execution.
* No restart action.
* No kill process action.
* No config change.
* No database write.
* No raw command output.
* No raw dump.
* No raw trace.
* No raw stack trace by default.
* No secret exposure.
* No customer raw data.
* Remediation is reference-only in this design.

## 15. Product Value

RuntimeOps ServiceOps integration gives ENYRAX a complete governance chain:

* RuntimeOps is no longer only a diagnosis dashboard.
* ServiceOps is no longer only a manual ticket queue.
* RCA, evidence, remediation, and verification can become one traceable workflow.
* Technical managers can see the full path from runtime symptom to closure.
* Audit and internal control teams can review the evidence package and responsibility trail.

## 16. Limitations

* Design only.
* No frontend.
* No backend.
* No fixture.
* No API.
* No actual ServiceOps ticket creation.
* No workflow engine.
* No live collector.
* No automation.

## 17. Recommended Next Task

Task #342: RuntimeOps Verification Workflow Design
