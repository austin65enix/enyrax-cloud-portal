# Python_RuntimeOps Read-only Fixture API Design

## Purpose

This document designs the Python_RuntimeOps read-only fixture API.

The API is intended to demonstrate Python / FastAPI / worker runtime diagnosis, endpoint metrics, worker snapshots, background jobs, profile evidence, memory evidence, RCA findings, verification results, and dashboard summary.

This task is design only. It does not implement backend routes, frontend pages, live collectors, production diagnostic commands, or mutation workflows.

## Fixture source

The proposed API reads from the safe demo fixtures created by Task #302:

* `data/runtimeops/python/demo_python_runtime_services.json`
* `data/runtimeops/python/demo_python_diagnosis_runs.json`
* `data/runtimeops/python/demo_python_endpoint_metrics.json`
* `data/runtimeops/python/demo_python_worker_snapshots.json`
* `data/runtimeops/python/demo_python_background_jobs.json`
* `data/runtimeops/python/demo_python_profile_evidence.json`
* `data/runtimeops/python/demo_python_memory_evidence.json`
* `data/runtimeops/python/demo_python_rca_findings.json`
* `data/runtimeops/python/demo_python_verification_results.json`
* `data/runtimeops/python/demo_python_runtime_dashboard.json`

## Proposed read-only endpoints

```text
GET /api/runtimeops/python/services
GET /api/runtimeops/python/diagnosis-runs
GET /api/runtimeops/python/diagnosis-runs/{diagnosis_run_id}
GET /api/runtimeops/python/slow-endpoints
GET /api/runtimeops/python/worker-snapshots
GET /api/runtimeops/python/background-jobs
GET /api/runtimeops/python/profile-evidence
GET /api/runtimeops/python/memory-evidence
GET /api/runtimeops/python/rca-findings
GET /api/runtimeops/python/verification-results
GET /api/runtimeops/python/dashboard
```

No write endpoints are proposed.

## Response contracts

Every list endpoint should return:

| Field | Meaning |
| --- | --- |
| `source` | `fixture` for normal fixture-backed responses, or `safe_fallback` for fallback responses. |
| `mode` | `read_only`. |
| `product` | `RuntimeOps`. |
| `display_name` | Human-readable endpoint label. |
| `production_data` | Always `false` for demo fixture responses. |
| `generated_at` | Fixture generation timestamp or fallback response timestamp. |
| `warnings` | Safe warning objects or strings. |
| `count` | Number of returned records. |
| `records` | Returned safe metadata records. |
| `safety_boundary` | Read-only safety summary. |

Suggested warning shape:

```json
{
  "code": "fixture_missing",
  "message": "Python_RuntimeOps fixture is unavailable; safe fallback response returned."
}
```

## Diagnosis detail endpoint contract

`GET /api/runtimeops/python/diagnosis-runs/{diagnosis_run_id}` returns a diagnosis-centered bundle:

| Field | Meaning |
| --- | --- |
| `diagnosis_run` | Matching diagnosis run record or `null` if not found. |
| `endpoint_metrics` | Endpoint metric records related by `endpoint_ref` or `evidence_ref`. |
| `worker_snapshots` | Worker snapshot records related by `worker_ref`, `process_ref`, or `evidence_ref`. |
| `background_jobs` | Background job records related by `job_ref`, `serviceops_ticket_ref`, or `evidence_ref`. |
| `profile_evidence` | Profile evidence records related by `diagnosis_run_id`. |
| `memory_evidence` | Memory evidence records related by `diagnosis_run_id`. |
| `rca_findings` | RCA finding records related by `diagnosis_run_id`. |
| `verification_results` | Verification records related by `diagnosis_run_id`. |
| `summary` | Safe counts for related evidence. |
| `warnings` | Safe warnings. |
| `safety_boundary` | Read-only safety summary. |

If `diagnosis_run_id` does not exist:

* Return HTTP 200 with `source=safe_fallback`.
* Return `diagnosis_run: null`.
* Return empty related arrays and a warning with code `diagnosis_run_not_found`.
* Do not expose raw paths, raw stack traces, raw command output, or internal exception details.

## Dashboard endpoint contract

`GET /api/runtimeops/python/dashboard` should aggregate or pass through:

* `total_services`
* `active_diagnosis_runs`
* `high_risk_findings`
* `slow_endpoints`
* `worker_warnings`
* `background_job_failures`
* `profile_evidence_count`
* `memory_watch_items`
* `remediation_open`
* `verified_results`
* `diagnosis_breakdown`
* `risk_breakdown`
* `service_health`
* `top_attention_items`
* `recent_diagnosis_runs`

The dashboard response should also include `source`, `mode`, `product`, `display_name`, `production_data`, `generated_at`, `warnings`, and `safety_boundary`.

## Filter behavior

* `slow-endpoints`: Return endpoint metrics where `p95_ms` or `p99_ms` exceeds a demo threshold, or `timeout_count > 0`.
* `background-jobs`: Return jobs with status values such as `Timeout`, `Delayed`, `Failed`, or `Warning`.
* `profile-evidence`: Return profile evidence fixture records.
* `memory-evidence`: Return memory evidence fixture records.
* `rca-findings`: Return RCA finding fixture records.
* `verification-results`: Return verification result fixture records.
* `diagnosis-runs/{diagnosis_run_id}`: Aggregate related evidence by `diagnosis_run_id` and safe refs.

Suggested demo thresholds:

```text
p95_ms > 750
p99_ms > 1000
timeout_count > 0
```

## Loader behavior

The loader should use:

* Allowlisted fixture paths only.
* Read-only file loading.
* Safe default response if a fixture is missing.
* Safe warnings for invalid JSON.
* Safe warnings for invalid schema.
* Nonblank safe response for empty records.
* No raw stack traces returned to frontend.
* No raw path exposure.
* No dynamic path input.
* No user-provided file path.
* No production diagnostic command execution.

## API safety boundary

The API safety boundary must include:

* GET only
* no POST / PUT / PATCH / DELETE
* no restart action
* no kill process action
* no config change action
* no database write action
* no production diagnostic command execution
* no raw command output
* no raw memory dump
* no raw profile content
* no raw stack trace by default
* no raw environment variables
* no credential exposure
* no customer raw data
* safe metadata only

## Error / fallback design

Fallback cases:

| Case | Response behavior |
| --- | --- |
| Missing fixture | Return safe fallback with warning `fixture_missing`. |
| Invalid JSON | Return safe fallback with warning `fixture_invalid_json`. |
| Invalid schema | Return safe fallback with warning `fixture_invalid_schema`. |
| Empty records | Return nonblank safe response with `count=0`, `records=[]`, warning optional. |
| Diagnosis run not found | Return safe detail response with `diagnosis_run=null` and warning `diagnosis_run_not_found`. |
| Partial fixture unavailable | Return available related records and warnings for unavailable fixture groups. |

Frontend should be able to display DEMO FALLBACK for invalid, missing, or empty responses without rendering a blank page.

## Validation checklist

Recommended validation:

* JSON parse test
* endpoint response contract test
* diagnosis detail response test
* dashboard aggregation test
* slow endpoint filter test
* background job filter test
* profile evidence response test
* memory evidence response test
* RCA findings response test
* verification results response test
* GET-only test
* no mutation route test
* no credential string scan
* no raw command output scan
* no raw path exposure
* warning response test

## Product positioning

Python_RuntimeOps API is a read-only production runtime diagnostics / RCA evidence governance layer.

It supports FastAPI diagnostics, worker monitoring, background job evidence, profile evidence, memory evidence, RCA findings, and ServiceOps-linked remediation tracking.

It does not replace APM, observability platforms, systemd, py-spy, tracemalloc, logging systems, or incident management tools. It wraps diagnostic evidence into the ENYRAX governance flow.

## Limitations

* Design only
* No API implementation
* No backend route changes
* No frontend changes
* No live diagnostic collector
* No py-spy integration
* No tracemalloc integration
* No production command execution
* No mutation workflow

## Recommended next task

Task #304: Python_RuntimeOps Read-only Fixture API Prototype
