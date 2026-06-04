# RuntimeOps End-to-End Demo Scenario Design

## 1. Purpose

RuntimeOps End-to-End Demo Scenario connects runtime symptom, safe evidence, RCA finding, ServiceOps remediation, verification result, and closure into one complete demonstration story.

This demo is intended for:

* Interview demonstration
* Technical manager explanation
* ENYRAX product walkthrough
* RuntimeOps roadmap validation

## 2. Product Context

RuntimeOps currently has:

* Python_RuntimeOps
* .NET_RuntimeOps
* RuntimeOps Portal
* Safe Evidence Schema
* Evidence Validator + CI
* RCA Workflow
* ServiceOps Integration
* Verification Workflow

Verification Workflow is available as of `bd1c6f4 docs: design runtimeops verification workflow`.

## 3. Demo Storyline

Primary storyline:

```text
A production-like API becomes slow.
RuntimeOps captures safe runtime evidence.
RCA finding is drafted.
ServiceOps remediation ticket is linked.
After remediation, RuntimeOps verifies before / after metrics.
RCA is closed with evidence.
```

Chinese storyline:

正式環境類似的 API 變慢，不再只是看 log 猜原因，而是透過 RuntimeOps 建立診斷、證據、RCA、工單、驗證與結案鏈。

## 4. Primary Demo Scenario: Python FastAPI Latency RCA

### Step 1: Symptom Detected

* Symptom: FastAPI endpoint latency spike.
* `service_name`: `runtimeops-python-demo` or `enyrax-api` demo reference.
* `endpoint_ref`: `/demo/slow` or `/api/271ops/identity-lifecycle/dashboard`.
* `risk_level`: High.

### Step 2: Runtime Diagnosis Run

* `diagnosis_type`: API Latency Diagnosis.
* `diagnosis_run_id`: `PY-DIAG-E2E-001`.
* Safe metrics collected:
  * `p95_ms`
  * `p99_ms`
  * `timeout_count`
  * `error_rate_percent`

### Step 3: Safe Evidence Created

* `evidence_ref`: `EVD-RUNTIME-E2E-PY-001`.
* `raw_output_exposed`: false.
* `raw_trace_exposed`: false.
* `raw_profile_exposed`: false.
* `secrets_exposed`: false.

The evidence stores only safe summary fields and references.

### Step 4: Evidence Validator PASS

* `validator_status`: PASS.
* CI safe evidence guardrail concept: unsafe evidence should fail before entering fixture mapping or dashboard previews.

### Step 5: RCA Draft

* `rca_finding_id`: `RCA-RUNTIME-E2E-PY-001`.
* `root_cause_category`: Code Path Latency / Dependency Latency.
* `confidence`: Medium / High.
* `human_review_required`: true.

RuntimeOps may draft the RCA, but human review is required before confirmation.

### Step 6: ServiceOps Remediation Link

* `serviceops_ticket_ref`: `SVC-RUNTIME-E2E-PY-001`.
* `remediation_type`: Code Fix Required / Dependency Review Required.
* `owner_team`: Platform Team.

RuntimeOps links remediation as a ServiceOps reference. It does not execute remediation directly.

### Step 7: Verification

* `before_evidence_ref`: `EVD-RUNTIME-E2E-PY-001`.
* `after_evidence_ref`: `EVD-RUNTIME-E2E-PY-002`.
* `latency_delta_percent`: improvement percentage based on safe summary metrics.
* `verification_status`: Verified or ImprovedButWatch.

Verification compares safe before / after evidence and records residual risk.

### Step 8: Closure

* RCA closed after review.
* ServiceOps ticket moved to Done / closed state.
* Postmortem candidate created.
* Knowledge base candidate created for recurring latency patterns.

## 5. Secondary Demo Scenario: .NET ThreadPool Starvation RCA

Short flow:

* ASP.NET Core endpoint becomes slow.
* dotnet counter evidence summary is captured as safe metadata.
* ThreadPool starvation is suspected.
* RCA finding is linked.
* ServiceOps remediation ticket is linked.
* Verification confirms queue wait improves.
* Raw trace, raw counter output, and raw dump content are not exposed.

Suggested references:

* `diagnosis_run_id`: `DOTNET-DIAG-E2E-001`
* `evidence_ref`: `EVD-RUNTIME-E2E-DOTNET-001`
* `rca_finding_id`: `RCA-RUNTIME-E2E-DOTNET-001`
* `serviceops_ticket_ref`: `SVC-RUNTIME-E2E-DOTNET-001`
* `verification_ref`: `VER-RUNTIME-E2E-DOTNET-001`

## 6. Cross-Runtime Comparison

Python_RuntimeOps can demonstrate:

* FastAPI latency
* Worker timeout
* Memory growth
* py-spy / profile metadata

.NET_RuntimeOps can demonstrate:

* ASP.NET latency
* ThreadPool / GC
* Counter / trace / dump metadata
* Enterprise app scenario

Shared governance model:

```text
Runtime Symptom
-> Evidence
-> RCA
-> ServiceOps
-> Verification
-> Closure
```

## 7. Demo Data Model

Recommended demo references:

| Reference | Purpose |
| --- | --- |
| `runtime_event_id` | Runtime symptom or alert reference. |
| `diagnosis_run_id` | Diagnosis run reference. |
| `evidence_ref` | Safe evidence reference. |
| `validator_result_ref` | Validator result reference. |
| `rca_finding_id` | RCA finding reference. |
| `serviceops_ticket_ref` | ServiceOps ticket reference. |
| `remediation_ref` | Remediation reference. |
| `verification_ref` | Verification reference. |
| `postmortem_ref` | Postmortem reference. |
| `knowledge_base_ref` | Knowledge base reference. |

## 8. UI Walkthrough

Suggested walkthrough path:

1. Portal Home
2. RuntimeOps card
3. Python_RuntimeOps dashboard
4. Top Attention Item
5. Diagnosis evidence preview
6. RCA finding preview
7. Linked ServiceOps ticket
8. Verification before / after
9. Closure / knowledge base candidate

Current UI has RuntimeOps entry and runtime-family dashboards. RCA finding preview, linked ServiceOps ticket, generic verification before / after, closure, and knowledge base candidate sections are future UI.

## 9. API Walkthrough

Currently available API surface:

* `GET /api/runtimeops/python/dashboard`
* `GET /api/runtimeops/python/diagnosis-runs`
* `GET /api/runtimeops/python/rca-findings`
* `GET /api/runtimeops/python/verification-results`
* `GET /api/runtimeops/dotnet/dashboard`
* `GET /api/runtimeops/dotnet/rca-findings`
* `GET /api/runtimeops/dotnet/verification-results`

Future API surface needed:

* `GET /api/runtimeops/rca/dashboard`
* `GET /api/runtimeops/serviceops-links`
* `GET /api/runtimeops/verifications/dashboard`

## 10. Demo Script

Three-minute demo script:

| Time | Segment | Script focus |
| --- | --- | --- |
| 30 seconds | RuntimeOps positioning | RuntimeOps turns runtime symptoms into governed evidence, RCA, remediation, verification, and closure. |
| 45 seconds | Python RuntimeOps symptom / evidence | Show a slow FastAPI-style endpoint, safe latency evidence, validator PASS, and no raw artifacts. |
| 45 seconds | RCA + ServiceOps linkage | Show RCA draft, human review requirement, ServiceOps remediation ticket reference, owner team, and due date. |
| 45 seconds | Verification / closure | Show before / after metrics, verification status, residual risk, RCA closure, and knowledge base candidate. |
| 15 seconds | Safety boundary | Emphasize no production command execution, no restart, no raw dump / trace / command output, and human review before closure. |

## 11. Safety Boundary in Demo

Demo safety boundary:

* No production diagnostic command.
* No restart.
* No kill process.
* No config change.
* No database write.
* No raw dump.
* No raw trace.
* No raw command output.
* No secret.
* No customer data.
* Safe evidence only.
* Human review before RCA closure.

## 12. Product Value

Technical managers:

* See the full governance chain from runtime problem to RCA closure.

Infra / SRE:

* Diagnosis is no longer scattered across CLI, logs, and personal notes.

Development managers:

* RCA is evidence-backed instead of based on guesses.

Audit / internal control:

* Event, ticket, evidence, verification, and closure all have a trail.

Interview demonstration:

* Shows integration across Infra, App Runtime, ServiceOps, Evidence, and RCA.

## 13. Demo Limitations

* Current demo is fixture-backed.
* Real lab evidence collection is planned, not complete.
* RCA / ServiceOps / Verification generic APIs are future design.
* No write workflow.
* No automated remediation.
* No production collector.
* No live APM replacement.

## 14. Demo Readiness Checklist

* RuntimeOps portal entry exists.
* Python dashboard API returns 200.
* .NET dashboard API returns 200.
* Safe evidence examples validate PASS.
* CI workflow exists.
* RCA design exists.
* ServiceOps integration design exists.
* Verification workflow design exists.
* Safety boundary visible.
* No mutation action exists.

## 15. Recommended Next Task

Task #344: RuntimeOps End-to-End Demo Fixture Design
