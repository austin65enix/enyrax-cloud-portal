# .NET_RuntimeOps Read-only Fixture API Design

## Purpose

This document designs the .NET_RuntimeOps read-only fixture API.

The API is intended to demonstrate ASP.NET Core / IIS / Windows Service runtime diagnosis, endpoint metrics, App Pool snapshots, Windows Service snapshots, counter evidence, trace evidence, dump evidence, RCA findings, verification results, and dashboard summary.

This task is design only. It does not implement backend routes, frontend pages, live collectors, Windows / IIS / SQL Server connections, production diagnostic commands, or mutation workflows.

## Fixture source

The proposed API reads from the safe demo fixtures created by Task #310:

* `data/runtimeops/dotnet/demo_dotnet_runtime_services.json`
* `data/runtimeops/dotnet/demo_dotnet_diagnosis_runs.json`
* `data/runtimeops/dotnet/demo_dotnet_endpoint_metrics.json`
* `data/runtimeops/dotnet/demo_dotnet_app_pool_snapshots.json`
* `data/runtimeops/dotnet/demo_dotnet_windows_service_snapshots.json`
* `data/runtimeops/dotnet/demo_dotnet_counter_evidence.json`
* `data/runtimeops/dotnet/demo_dotnet_trace_evidence.json`
* `data/runtimeops/dotnet/demo_dotnet_dump_evidence.json`
* `data/runtimeops/dotnet/demo_dotnet_rca_findings.json`
* `data/runtimeops/dotnet/demo_dotnet_verification_results.json`
* `data/runtimeops/dotnet/demo_dotnet_runtime_dashboard.json`

## Proposed read-only endpoints

```text
GET /api/runtimeops/dotnet/services
GET /api/runtimeops/dotnet/diagnosis-runs
GET /api/runtimeops/dotnet/diagnosis-runs/{diagnosis_run_id}
GET /api/runtimeops/dotnet/slow-endpoints
GET /api/runtimeops/dotnet/app-pools
GET /api/runtimeops/dotnet/windows-services
GET /api/runtimeops/dotnet/counter-evidence
GET /api/runtimeops/dotnet/trace-evidence
GET /api/runtimeops/dotnet/dump-evidence
GET /api/runtimeops/dotnet/rca-findings
GET /api/runtimeops/dotnet/verification-results
GET /api/runtimeops/dotnet/dashboard
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
  "message": ".NET_RuntimeOps fixture is unavailable; safe fallback response returned."
}
```

## Diagnosis detail endpoint contract

`GET /api/runtimeops/dotnet/diagnosis-runs/{diagnosis_run_id}` returns a diagnosis-centered bundle:

| Field | Meaning |
| --- | --- |
| `diagnosis_run` | Matching diagnosis run record or `null` if not found. |
| `endpoint_metrics` | Endpoint metric records related by `endpoint_ref` or `evidence_ref`. |
| `app_pool_snapshots` | App Pool snapshot records related by `app_pool_ref`, `event_log_ref`, or `evidence_ref`. |
| `windows_service_snapshots` | Windows Service snapshot records related by `windows_service_ref`, `event_log_ref`, or `evidence_ref`. |
| `counter_evidence` | Counter evidence records related by `diagnosis_run_id` or `counter_ref`. |
| `trace_evidence` | Trace evidence records related by `diagnosis_run_id` or `trace_ref`. |
| `dump_evidence` | Dump metadata records related by `diagnosis_run_id` or `dump_ref`. |
| `rca_findings` | RCA finding records related by `diagnosis_run_id`. |
| `verification_results` | Verification records related by `diagnosis_run_id`. |
| `summary` | Safe counts for related evidence. |
| `warnings` | Safe warnings. |
| `safety_boundary` | Read-only safety summary. |

If `diagnosis_run_id` does not exist:

* Return HTTP 200 with `source=safe_fallback`.
* Return `diagnosis_run: null`.
* Return empty related arrays and a warning with code `diagnosis_run_not_found`.
* Do not expose raw paths, raw stack traces, raw command output, raw Event Log content, SQL values, or internal exception details.

## Dashboard endpoint contract

`GET /api/runtimeops/dotnet/dashboard` should aggregate or pass through:

* `total_services`
* `active_diagnosis_runs`
* `high_risk_findings`
* `slow_endpoints`
* `app_pool_warnings`
* `windows_service_warnings`
* `counter_evidence_count`
* `trace_evidence_count`
* `dump_evidence_count`
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
* `app-pools`: Return App Pool snapshots with statuses such as `Recycled`, `Warning`, `CrashLoop`, or `Stopped`.
* `windows-services`: Return Windows Service snapshots with statuses such as `Stuck`, `NotResponding`, `Stopped`, or `CrashLoop`.
* `counter-evidence`: Return dotnet-counters / PerfMon summary fixture records.
* `trace-evidence`: Return dotnet-trace metadata fixture records.
* `dump-evidence`: Return dotnet-dump metadata fixture records. `raw_dump_exposed` must be `false`.
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
* No dynamic path input.
* No user-provided file path.
* No production diagnostic command execution.
* No Windows / IIS / SQL Server connection.

## API safety boundary

The API safety boundary must include:

* GET only
* no POST / PUT / PATCH / DELETE
* no IIS App Pool recycle action
* no Windows Service restart action
* no kill process action
* no config change action
* no database write action
* no production diagnostic command execution
* no Windows / IIS / SQL Server connection
* no raw command output
* no raw dump content
* no raw trace content
* no raw counter output
* no raw Event Log full content
* no raw SQL with sensitive values
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
* app pool filter test
* Windows service filter test
* counter evidence response test
* trace evidence response test
* dump evidence response test
* dump evidence `raw_dump_exposed=false` test
* RCA findings response test
* verification results response test
* GET-only test
* no mutation route test
* no credential string scan
* no raw command output scan
* no raw path exposure
* warning response test

## Product positioning

.NET_RuntimeOps API is a read-only production runtime diagnostics / RCA evidence governance layer.

It supports ASP.NET Core diagnostics, IIS / App Pool observation, Windows Service observation, counter evidence, trace evidence, dump evidence metadata, RCA findings, and ServiceOps-linked remediation tracking.

It does not replace APM, observability platforms, IIS Manager, Windows Event Viewer, dotnet-counters, dotnet-trace, dotnet-dump, SQL Server tools, or incident management tools. It wraps diagnostic evidence into the ENYRAX governance flow.

## Limitations

* Design only
* No API implementation
* No backend route changes
* No frontend changes
* No live diagnostic collector
* No dotnet-counters integration
* No dotnet-trace integration
* No dotnet-dump integration
* No IIS integration
* No Windows Service integration
* No SQL Server integration
* No production command execution
* No mutation workflow

## Recommended next task

Task #312: .NET_RuntimeOps Read-only Fixture API Prototype
