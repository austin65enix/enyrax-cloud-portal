# RuntimeOps Verification Workflow Design

## 1. Purpose

RuntimeOps Verification Workflow confirms whether a runtime symptom improved after RCA / ServiceOps remediation, whether residual risk remains, and whether the RCA and ServiceOps ticket can be closed.

Verification is the closure gate in the RuntimeOps governance chain:

```text
Runtime Symptom
-> Safe Evidence
-> RCA Finding
-> ServiceOps Remediation
-> Verification Evidence
-> Closure Decision
```

## 2. Product Context

RuntimeOps currently has:

* Python_RuntimeOps
* .NET_RuntimeOps
* Safe Evidence Schema
* Evidence Validator
* CI Guardrail
* RCA Workflow Design
* ServiceOps Integration Design

ServiceOps Integration Design is available as of `41a65f6 docs: design runtimeops serviceops integration`.

Verification Workflow is the required closure stage for RCA findings and ServiceOps-linked remediation.

## 3. Verification Flow

Recommended verification flow:

```text
Remediation Completed / Ready for Verification
-> Capture Before Summary
-> Capture After Summary
-> Compare Metrics
-> Validate Evidence Safety
-> Human Review
-> Verification Decision
-> RCA Closure / Reopen
-> ServiceOps Ticket Closure / Follow-up
```

The first implementation should be read-only and evidence-reference based.

## 4. Verification States

Recommended verification states:

* Pending
* EvidenceCaptured
* ComparisonReady
* Improved
* NoChange
* Failed
* Verified
* Reopened
* WaivedWithRiskAcceptance
* Closed

State transitions should preserve reviewer, evidence refs, timestamps, and closure decision context.

## 5. Verification Fields

Recommended verification fields:

| Field | Purpose |
| --- | --- |
| `verification_ref` | Stable verification identifier. |
| `rca_finding_id` | Linked RCA finding. |
| `diagnosis_run_id` | Linked diagnosis run. |
| `service_name` | Affected service. |
| `runtime_family` | Runtime family such as Python or .NET. |
| `serviceops_ticket_ref` | Linked ServiceOps ticket. |
| `remediation_ref` | Linked remediation reference. |
| `verification_status` | Current verification status. |
| `verification_type` | Verification category. |
| `before_evidence_ref` | Evidence before remediation. |
| `after_evidence_ref` | Evidence after remediation. |
| `before_summary` | Safe before-state summary. |
| `after_summary` | Safe after-state summary. |
| `metric_delta_summary` | Safe metric comparison. |
| `improvement_summary` | Human-readable improvement summary. |
| `residual_risk` | Remaining risk after remediation. |
| `risk_level_before` | Risk before remediation. |
| `risk_level_after` | Risk after remediation. |
| `verified_by` | Human reviewer reference. |
| `verified_at` | Verification timestamp. |
| `review_required` | Whether human review is required. |
| `closure_decision` | Close, reopen, hold, or waive decision. |
| `reopen_reason` | Reason for reopening, if applicable. |
| `watch_period_start` | Watch period start. |
| `watch_period_end` | Watch period end. |
| `recurrence_detected` | Whether the symptom recurred. |
| `notes` | Safe reviewer notes. |

## 6. Verification Types

Recommended verification types:

* Endpoint Latency Verification
* Error Rate Verification
* Background Job Recovery Verification
* Memory Growth Verification
* CPU Hotspot Verification
* ThreadPool Recovery Verification
* GC Pressure Verification
* Dependency Latency Verification
* Queue Backlog Verification
* Availability Verification

## 7. Before / After Metric Model

`before_summary` should include:

* `observed_window`
* `symptom`
* `metric_summary`
* `risk_level`
* `evidence_ref`

`after_summary` should include:

* `observed_window`
* `symptom_status`
* `metric_summary`
* `risk_level`
* `evidence_ref`

`metric_delta_summary` should include:

* `latency_delta_percent`
* `error_rate_delta_percent`
* `timeout_count_delta`
* `memory_growth_delta`
* `cpu_delta`
* `queue_backlog_delta`
* `availability_change`
* `evidence_quality`

All metric comparisons should use safe summaries only.

## 8. Verification Decision Model

Reviewer decisions:

* Mark Verified
* Mark Improved but Watch
* Mark No Change
* Mark Failed
* Reopen RCA
* Request More Evidence
* Accept Residual Risk
* Close with Waiver

RuntimeOps must not automatically close high-risk RCA findings. Critical and High risk findings require a human reviewer before verification or closure.

## 9. Evidence Safety Validation

Verification evidence must pass:

* Safe Evidence Schema
* Evidence Validator
* All `raw_*` flags false
* No production command output
* No dump / trace raw content
* No secret
* No customer data

Unsafe verification evidence should block closure.

## 10. Closure Rules

Closure is allowed when:

* RCA finding exists.
* Remediation ref exists or residual risk is accepted.
* After evidence exists.
* Verification status is `Verified` or `WaivedWithRiskAcceptance`.
* Human reviewer exists.
* No Critical unresolved residual risk exists.
* ServiceOps ticket status is compatible with closure.

Closure is not allowed when:

* After evidence is missing.
* Verification failed.
* Symptom recurrence is detected.
* High risk has no reviewer.
* Unsafe evidence is detected.
* ServiceOps remediation is still open.

## 11. Reopen Rules

Reopen the RCA if:

* Symptom recurs during watch period.
* After metrics degrade again.
* ServiceOps remediation is incomplete.
* Evidence is invalidated.
* New related diagnosis run appears.
* Reviewer rejects closure.

Reopen events should link to the prior RCA, prior verification, and new evidence refs.

## 12. Watch Period Model

Watch period fields:

* `watch_period_start`
* `watch_period_end`
* `recurrence_detected`
* `recurrence_count`
* `monitoring_summary`
* `closure_hold_reason`

Suggested watch periods:

| Risk level | Watch period |
| --- | --- |
| Critical | 24-72 hours |
| High | 1-3 business days |
| Medium | Optional watch |
| Low | No watch or short watch |

## 13. Dashboard Views

Future RuntimeOps Verification dashboard sections:

* Verification Summary Cards
* Pending Verification
* Failed Verification
* Improved but Watch
* Reopened RCA
* Recently Verified
* Residual Risk Accepted
* Before / After Comparison
* Evidence Safety Status
* Closure Candidate Queue

## 14. ServiceOps Integration

ServiceOps ticket `Done` status alone should not mean the technical issue is verified.

RuntimeOps verification should add:

* After evidence
* Metric comparison
* Residual risk
* Closure decision

ServiceOps can display:

* Runtime verification status
* Before / after summary
* Verification evidence ref
* Reopen flag

## 15. AgentOps Integration

AgentOps can assist with:

* Summarizing before / after difference
* Identifying possible recurrence
* Drafting verification note
* Drafting postmortem update

AgentOps must not:

* Mark verified without human review
* Close RCA automatically
* Execute production command
* Restart / kill / config change

## 16. API Design Preview

Future read-only API design only. Not implemented in this task.

Potential future endpoints:

* `GET /api/runtimeops/verifications`
* `GET /api/runtimeops/verifications/{verification_ref}`
* `GET /api/runtimeops/verifications/pending`
* `GET /api/runtimeops/verifications/failed`
* `GET /api/runtimeops/verifications/reopened`
* `GET /api/runtimeops/verifications/closure-candidates`
* `GET /api/runtimeops/verifications/dashboard`

The first implementation should be read-only and fixture-backed.

## 17. Demo Scenarios

| Scenario | Verification outcome | Closure implication |
| --- | --- | --- |
| FastAPI latency improved after remediation | Verified | RCA and ServiceOps ticket can close after review. |
| Python memory growth still failing verification | Failed | RCA remains open and remediation follow-up required. |
| Background job timeout improved but watch required | Improved | Hold closure until watch period completes. |
| .NET ThreadPool starvation verified | Verified | RCA can close with counter evidence summary. |
| .NET GC pressure improved but residual risk accepted | WaivedWithRiskAcceptance | Closure allowed only with reviewer and risk acceptance. |
| External dependency latency no change | NoChange | Reopen or keep remediation open. |
| RCA reopened after recurrence | Reopened | New diagnosis run and evidence refs required. |
| Critical incident closed after human verification | Verified | Postmortem and reviewer required before closure. |

## 18. Safety Boundary

Required safety boundary:

* Design only.
* Read-only verification first.
* No production command execution.
* No restart action.
* No kill process action.
* No config change.
* No database write.
* No automatic closure for high risk.
* No raw dump.
* No raw trace.
* No raw command output.
* No raw stack trace by default.
* No secret exposure.
* No customer raw data.
* AgentOps cannot mark verified without human review.
* ServiceOps closure is reference-only in this design.

## 19. Limitations

* Design only.
* No frontend.
* No backend.
* No fixture.
* No API.
* No verification engine.
* No live collector.
* No ServiceOps write integration.
* No AgentOps automation.

## 20. Recommended Next Task

Task #343: RuntimeOps End-to-End Demo Scenario Design
