# .NET_RuntimeOps Demo Fixtures

## Purpose

These fixtures define safe demo data for .NET_RuntimeOps, the second RuntimeOps runtime family. The data demonstrates ASP.NET Core / IIS / Windows Service runtime diagnosis, endpoint metrics, App Pool snapshots, Windows Service snapshots, counter evidence, trace evidence, dump metadata, RCA findings, verification results, and dashboard summary.

The enterprise demo target is a safe `demo-erp-api` service. All records are safe metadata only.

## Fixture files

* `demo_dotnet_runtime_services.json`
* `demo_dotnet_diagnosis_runs.json`
* `demo_dotnet_endpoint_metrics.json`
* `demo_dotnet_app_pool_snapshots.json`
* `demo_dotnet_windows_service_snapshots.json`
* `demo_dotnet_counter_evidence.json`
* `demo_dotnet_trace_evidence.json`
* `demo_dotnet_dump_evidence.json`
* `demo_dotnet_rca_findings.json`
* `demo_dotnet_verification_results.json`
* `demo_dotnet_runtime_dashboard.json`

## Demo scenarios

1. ASP.NET Core endpoint latency spike.
2. IIS App Pool recycle observed.
3. Windows Service stuck.
4. ThreadPool starvation suspected.
5. GC memory pressure warning.
6. EF Core SQL timeout symptom.
7. External API latency causing timeout.
8. .NET runtime diagnosis creates ServiceOps remediation reference.

## Field contract

Runtime service records include service identity, .NET runtime family, framework, hosting model, environment, safe host reference, safe App Pool reference, safe Windows Service reference, owner team, status, risk level, and notes.

Diagnosis run records include diagnosis IDs, runtime event IDs, safe service/process/App Pool/Windows Service references, ServiceOps ticket references, diagnosis type, symptom, timestamps, duration, severity, risk level, endpoint reference, safe metric summary, Event Log reference, trace reference, counter reference, dump reference, evidence reference, RCA summary, remediation reference, verification status, and notes.

Evidence records store safe summaries and references only. They do not store raw dump content, raw trace content, raw counter output, raw command output, raw Event Log full content, SQL text with sensitive values, credentials, or customer raw data.

## Safety boundary

* Safe metadata only.
* Demo data only.
* No production diagnostic command execution.
* No IIS App Pool recycle action.
* No Windows Service restart action.
* No kill process action.
* No config change action.
* No database write action.
* No raw command output.
* No raw dump content.
* No raw trace content.
* No raw counter output.
* No raw Event Log full content.
* No SQL text with sensitive values.
* No password / credential / API key / private key / token.
* No customer raw data.

## What is intentionally excluded

These fixtures intentionally exclude real IPs, real host paths, Windows paths, user home paths, environment dumps, raw command output, dump content, trace content, counter output, Event Log full content, sensitive SQL values, secrets, and customer payloads.

Allowed examples include:

* `HOST-DEMO-WIN-001`
* `PROC-DEMO-DOTNET-001`
* `APPPOOL-DEMO-ERP-001`
* `WINSVC-DEMO-ERP-001`
* `/api/demo-erp/orders`
* `EVD-RUNTIME-DOTNET-001`
* `SVC-RUNTIME-DOTNET-001`
* `TRACE-RUNTIME-DOTNET-001`
* `COUNTER-RUNTIME-DOTNET-001`
* `DUMP-RUNTIME-DOTNET-001`

## Future API mapping

Future read-only API mapping:

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

## Limitations

* Demo fixture design only.
* No frontend.
* No backend.
* No API implementation.
* No scripts.
* No live diagnostic collector.
* No dotnet-counters integration.
* No dotnet-trace integration.
* No dotnet-dump integration.
* No IIS integration.
* No Windows Service integration.
* No Windows / IIS / SQL Server connection.
* No production action.

## Recommended next task

Task #311: .NET_RuntimeOps Read-only Fixture API Design
