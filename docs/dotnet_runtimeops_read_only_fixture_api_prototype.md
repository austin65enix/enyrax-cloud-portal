# .NET_RuntimeOps Read-only Fixture API Prototype

## Task summary

Task #312 adds the .NET_RuntimeOps read-only fixture API prototype for RuntimeOps. The prototype exposes safe fixture-backed GET endpoints for ASP.NET Core / IIS / Windows Service runtime diagnosis, endpoint metrics, App Pool snapshots, Windows Service snapshots, counter evidence, trace evidence, dump metadata, RCA findings, verification results, and dashboard summary.

No frontend, DB schema, write API, production config, nginx, cron, systemd, Windows / IIS / SQL Server connection, or production diagnostic command was added.

## Endpoints added

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

## Fixture source

The API reads only allowlisted fixture files:

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

## Response contract

List endpoints return:

* `source`
* `mode`
* `product`
* `display_name`
* `production_data`
* `generated_at`
* `warnings`
* `count`
* `records`
* `safety_boundary`

## Dashboard aggregation

`GET /api/runtimeops/dotnet/dashboard` returns:

* `summary.total_services`
* `summary.active_diagnosis_runs`
* `summary.high_risk_findings`
* `summary.slow_endpoints`
* `summary.app_pool_warnings`
* `summary.windows_service_warnings`
* `summary.counter_evidence_count`
* `summary.trace_evidence_count`
* `summary.dump_evidence_count`
* `summary.remediation_open`
* `summary.verified_results`
* `diagnosis_breakdown`
* `risk_breakdown`
* `service_health`
* `top_attention_items`
* `recent_diagnosis_runs`
* `safety_boundary`

## Filter behavior

* `slow-endpoints` returns endpoint metrics where `p95_ms > 750`, `p99_ms > 1000`, or `timeout_count > 0`.
* `app-pools` returns App Pool snapshots whose status contains `Recycled`, `Warning`, `CrashLoop`, or `Stopped`.
* `windows-services` returns Windows Service snapshots whose status contains `Stuck`, `NotResponding`, `Stopped`, or `CrashLoop`.
* `counter-evidence`, `trace-evidence`, `rca-findings`, and `verification-results` return their fixture records.
* `dump-evidence` returns dump metadata records only when `raw_dump_exposed` is `false`.

## Diagnosis detail behavior

`GET /api/runtimeops/dotnet/diagnosis-runs/{diagnosis_run_id}` returns:

* `diagnosis_run`
* `endpoint_metrics`
* `app_pool_snapshots`
* `windows_service_snapshots`
* `counter_evidence`
* `trace_evidence`
* `dump_evidence`
* `rca_findings`
* `verification_results`
* `summary`
* `warnings`
* `safety_boundary`

If the ID is not found, the response is safe and nonblank with `diagnosis_run: null`, empty related arrays, and warning code `diagnosis_run_not_found`. It does not expose raw path, stack trace, command output, Event Log content, SQL values, or internal exception details.

## Safety boundary

Every response includes safety metadata:

* `read_only: true`
* `mutation_allowed: false`
* `safe_metadata_only: true`
* `no_iis_app_pool_recycle: true`
* `no_windows_service_restart: true`
* `no_kill_process: true`
* `no_config_change: true`
* `no_database_write: true`
* `no_production_diagnostic_command: true`
* `no_windows_iis_sql_connection: true`
* excludes passwords, credentials, API keys, private keys, raw logs, raw command output, raw dump content, raw trace content, raw counter output, raw Event Log full content, raw SQL with sensitive values, raw environment variables, and customer raw data.

## Validation performed

Validation commands/results:

* `python3 -m py_compile backend/main.py` passed.
* All `.NET_RuntimeOps` JSON fixture parse checks passed with `python3 -m json.tool`.
* Direct backend helper checks confirmed list response contracts.
* Dashboard helper returned the expected summary, breakdown, service health, attention items, and recent diagnosis runs.
* Diagnosis detail helper returned related evidence for `DOTNET-DIAG-DEMO-001`.
* Missing diagnosis ID returned safe `diagnosis_run: null` with warning `diagnosis_run_not_found`.
* Slow endpoint filter returned demo slow endpoints.
* App Pool filter returned warning/recycled App Pool snapshots.
* Windows Service filter returned stuck/not-responding snapshots.
* Counter, trace, dump, RCA, and verification endpoints returned fixture records.
* Dump evidence records keep `raw_dump_exposed=false`.
* Static route scan found no POST / PUT / PATCH / DELETE routes for `/api/runtimeops/dotnet`.

## Limitations

* Fixture-backed read-only prototype only.
* No frontend dashboard in this task.
* No live diagnostic collector.
* No dotnet-counters integration.
* No dotnet-trace integration.
* No dotnet-dump integration.
* No IIS integration.
* No Windows Service integration.
* No SQL Server integration.
* No Windows / IIS / SQL Server connection.
* No production command execution.
* No mutation workflow.

## Recommended next task

Task #313: .NET_RuntimeOps Frontend Dashboard
