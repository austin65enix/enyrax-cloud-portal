# .NET_RuntimeOps Design

.NET runtime diagnosis and RCA evidence governance submodule for RuntimeOps

## Purpose

.NET_RuntimeOps is the .NET / ASP.NET Core / IIS / Windows Service diagnosis submodule under RuntimeOps.

Its goal is to turn enterprise .NET production troubleshooting into a traceable, verifiable, reviewable, and evidence-backed governance workflow. This is especially relevant for internal enterprise systems, manufacturing systems, ERP / MES / BPM services, and SQL Server-backed application layers where runtime incidents often cross application, infrastructure, DBA, and operations boundaries.

The first stage is read-only diagnostics design. It does not implement restart, kill process, IIS App Pool recycle, config change, database write, or any production diagnostic command.

## Product context

RuntimeOps is ENYRAX's production runtime diagnosis governance module. It connects runtime symptoms, diagnosis evidence, RCA findings, ServiceOps remediation, verification, and closure.

Python_RuntimeOps is the first RuntimeOps runtime family. .NET_RuntimeOps extends the same model to common enterprise .NET environments:

* ASP.NET Core API
* IIS hosted applications
* Windows Service
* ERP / MES / BPM surrounding services
* EF Core / SQL Server application layer

.NET_RuntimeOps can connect with:

* ServiceOps ticket for diagnosis and remediation workflow.
* Evidence Package for diagnosis summary and verification evidence.
* AgentOps RCA summary for AI-assisted RCA drafting with human review.

## Core .NET runtime problems

.NET_RuntimeOps should cover these common enterprise runtime symptoms:

* ASP.NET Core API slow response
* IIS App Pool recycle
* IIS 500 / 502 / 503 symptom
* Windows Service stuck
* Windows Service crash loop
* ThreadPool starvation
* GC memory pressure
* high exception rate
* EF Core slow query symptom
* SQL Server latency symptom from application layer
* external API latency
* queue / background worker backlog
* Windows Event Log warning / error reference
* log not enough to reproduce issue

The module is designed for evidence governance, not direct system control. It should preserve safe summaries and evidence references so teams can explain symptoms, assign ownership, plan remediation, and verify results without exposing sensitive runtime content.

## .NET_RuntimeOps governance flow

Text flow:

```text
ServiceOps Ticket / Runtime Alert
-> .NET Runtime Diagnosis Run
-> Metrics Snapshot
-> Event Log / Trace / Profile Evidence
-> RCA Finding
-> Remediation Reference
-> Verification Result
-> Closure
```

Flow description:

1. ServiceOps Ticket / Runtime Alert: A symptom enters through ServiceOps, SOC / AlertOps, monitoring, user impact, or manual escalation.
2. .NET Runtime Diagnosis Run: The service, runtime, hosting model, app pool, Windows Service, process reference, endpoint, and symptom are recorded.
3. Metrics Snapshot: Safe counters and summaries are attached, such as request latency, exception rate, GC pressure, ThreadPool indicators, SQL timeout count, queue length, or service status.
4. Event Log / Trace / Profile Evidence: Safe references are linked for IIS logs, Windows Event Log events, dotnet-counters summaries, dotnet-trace evidence, dump metadata, or OpenTelemetry traces.
5. RCA Finding: The likely root cause or contributing factor is recorded with confidence and related evidence refs.
6. Remediation Reference: Remediation is linked to ServiceOps or ProjectOps.
7. Verification Result: Before/after summaries and evidence refs prove whether remediation worked.
8. Closure: The incident is closed with traceable diagnosis, RCA, remediation, and verification evidence.

## Diagnostic categories

Initial categories:

| Category | Purpose |
| --- | --- |
| ASP.NET API Latency Diagnosis | Investigate slow ASP.NET Core endpoints, repeated timeout, 500 / 502 / 503 symptoms, and user impact. |
| IIS / App Pool Diagnosis | Review App Pool recycle, crash loop, unhealthy worker process, and IIS hosting metadata. |
| Windows Service Diagnosis | Review service stuck, stopped, crash loop, delayed processing, or service state warnings. |
| ThreadPool Diagnosis | Track ThreadPool starvation suspicion, queued work item growth, and request delay symptoms. |
| GC / Memory Diagnosis | Track GC pressure, heap growth symptoms, memory pressure, and dump metadata references. |
| Exception / Error Rate Diagnosis | Track elevated application exception rate and safe error summaries. |
| EF Core / SQL Latency Symptom Diagnosis | Track EF Core query duration symptoms and SQL Server latency indicators without sensitive SQL text. |
| External Dependency Diagnosis | Track slow external API calls, dependency timeout, and safe dependency references. |
| Queue / Background Worker Diagnosis | Track queue backlog, scheduler delay, delayed workers, and service capacity symptoms. |
| Windows Event Log Diagnosis | Track safe Windows Event Log warning/error references without raw full event content. |

## Possible tools / evidence sources

Design-only possible sources:

* ASP.NET Core access log summary
* IIS log summary
* IIS App Pool metadata
* Windows Service status reference
* Windows Event Log reference
* dotnet-counters summary reference
* dotnet-trace evidence reference
* dotnet-dump metadata reference
* PerfMon counter summary
* Application Insights / OpenTelemetry if available
* EF Core query duration summary
* SQL timeout summary
* queue length summary
* external API timing summary

Safety handling:

* Raw command output is not directly displayed.
* Raw dump content is not directly displayed.
* Raw trace content is not directly displayed.
* Raw Event Log full content is not directly displayed.
* Raw SQL with sensitive values is not directly displayed.
* The product stores safe summaries and evidence references only.

## Core entities

| Entity | Meaning |
| --- | --- |
| .NET Runtime Service | A .NET service under RuntimeOps governance, such as ASP.NET Core API, IIS app, or Windows Service. |
| .NET Diagnosis Run | One structured diagnosis attempt for a .NET runtime symptom. |
| ASP.NET Endpoint Metric | Safe endpoint latency, response code, timeout, and error summary. |
| IIS App Pool Snapshot | Safe app pool status, recycle, crash loop, or worker health metadata. |
| Windows Service Snapshot | Safe Windows Service status and lifecycle metadata. |
| .NET Counter Snapshot | Safe dotnet-counters, PerfMon, GC, ThreadPool, exception, or request metrics summary. |
| .NET Trace Evidence | Safe reference to trace evidence, not raw trace content. |
| .NET Dump Evidence | Safe reference to dump metadata, not raw dump content. |
| .NET RCA Finding | Evidence-linked root cause or contributing factor. |
| .NET Verification Result | Before/after validation for a diagnosis or remediation. |

## .NET diagnosis run fields

Suggested fields:

| Field | Meaning |
| --- | --- |
| `diagnosis_run_id` | Unique .NET diagnosis run ID. |
| `runtime_event_id` | Runtime event ID for cross-runtime linkage. |
| `service_name` | Service name, such as `demo-erp-api`. |
| `service_type` | ASP.NET Core API, IIS hosted application, Windows Service, worker, or scheduler. |
| `language_runtime` | `.NET`. |
| `dotnet_version_label` | Safe .NET version label. |
| `framework` | ASP.NET Core, .NET Worker Service, .NET Framework, or mixed enterprise component. |
| `hosting_model` | IIS, Kestrel, Windows Service, container, or scheduled worker. |
| `environment` | Production, staging, demo, or development. |
| `host_ref` | Safe host reference. |
| `process_ref` | Safe process reference. |
| `app_pool_ref` | Safe IIS App Pool reference. |
| `windows_service_ref` | Safe Windows Service reference. |
| `incident_ref` | Runtime alert or incident reference. |
| `serviceops_ticket_ref` | Linked ServiceOps ticket reference. |
| `diagnosis_type` | Diagnosis category. |
| `symptom` | Short safe symptom summary. |
| `started_at` | Diagnosis start timestamp. |
| `ended_at` | Diagnosis end timestamp. |
| `duration_ms` | Duration in milliseconds. |
| `severity` | Operational severity. |
| `risk_level` | Governance risk level. |
| `endpoint_ref` | Safe endpoint reference. |
| `app_pool_status` | Safe app pool status summary. |
| `windows_service_status` | Safe Windows Service status summary. |
| `metric_summary` | Safe metric summary only. |
| `event_log_ref` | Safe Windows Event Log evidence reference. |
| `trace_ref` | Safe trace evidence reference. |
| `counter_ref` | Safe counter evidence reference. |
| `dump_ref` | Safe dump metadata reference. |
| `evidence_ref` | Primary evidence reference. |
| `rca_summary` | Safe RCA summary. |
| `remediation_ref` | Remediation reference. |
| `verification_status` | Pending, ReviewRequired, EvidenceCaptured, RemediationQueued, Verified, or FalseAlarm. |
| `notes` | Safe notes. |

## Dashboard views

Future dashboard views:

* .NET Runtime Health Summary
* Slow ASP.NET Endpoints
* IIS / App Pool Watch
* Windows Service Watch
* ThreadPool / GC Watch
* Exception Rate Trend
* EF Core / SQL Latency Symptoms
* External Dependency Latency
* Queue / Background Worker Backlog
* Event Log Evidence
* Trace / Counter Evidence
* Dump Evidence
* RCA Findings
* ServiceOps Linked Tickets
* Verification Results
* Safety Boundary

## Risk scoring

Suggested scoring:

| Condition | Risk level |
| --- | --- |
| API unavailable / repeated 503 | Critical |
| Windows Service stopped unexpectedly | Critical / High |
| App Pool crash loop | High |
| ThreadPool starvation suspected | High |
| GC memory pressure with user impact | High |
| SQL timeout recurring | High |
| Elevated exception rate | Medium / High |
| Slow endpoint without outage | Medium |
| Trace / counter evidence captured and verified | Low |
| False alarm | Low |

Risk scoring should preserve symptom, impacted service, hosting context, evidence refs, remediation status, and verification status.

## Enterprise demo plan

Demo service:

| Field | Value |
| --- | --- |
| `service_name` | `demo-erp-api` |
| `framework` | `ASP.NET Core` |
| `hosting_model` | `IIS / Windows Service` |
| `runtime` | `.NET` |

Demo symptoms:

* ERP API slow response
* IIS App Pool recycle observed
* Windows Service stuck
* EF Core SQL timeout symptom
* ThreadPool starvation suspected
* GC memory pressure

Demo evidence:

* safe IIS log summary reference
* Windows Event Log reference
* dotnet-counters summary reference
* trace evidence reference
* ServiceOps ticket reference
* RCA summary

The demo should not connect to any Windows, IIS, or SQL Server environment. It should use safe fixture data and evidence references only.

## Integration model

| Module | Integration |
| --- | --- |
| ServiceOps | Create .NET runtime diagnosis ticket and remediation workflow. |
| SOC / AlertOps | Convert runtime alert into investigation. |
| AgentOps | AI assists RCA summary but does not directly execute high-risk operations. |
| ProjectOps | Major remediation escalates into a project. |
| Evidence Package | Preserve diagnosis summary and verification result. |
| 271Ops | Link governance evidence if issue involves account, permission, service account, or access review context. |
| Firewall ChangeOps | Link change evidence if API / DB / external dependency connectivity is involved. |

## Safety boundary

Safety boundary:

* Design only
* Read-only diagnostics first
* No IIS App Pool recycle action
* No Windows Service restart action
* No kill process action
* No config change action
* No database write action
* No raw dump exposed
* No raw trace exposed
* No raw Event Log full content
* No raw command output
* No raw environment variables
* No SQL text with sensitive values
* No password / credential / API key / private key
* No customer raw data
* Safe metadata and evidence references only

## Demo scenarios

Initial demo scenarios:

| Scenario | Diagnosis type | Expected demo output |
| --- | --- | --- |
| ASP.NET Core endpoint latency spike | ASP.NET API Latency Diagnosis | Endpoint metric, trace ref, evidence ref, RCA note. |
| IIS App Pool recycle observed | IIS / App Pool Diagnosis | App Pool snapshot and Windows Event Log reference. |
| Windows Service stuck | Windows Service Diagnosis | Service status reference, ServiceOps ticket, ReviewRequired status. |
| ThreadPool starvation suspected | ThreadPool Diagnosis | dotnet-counters summary ref and RCA finding. |
| GC memory pressure warning | GC / Memory Diagnosis | Counter evidence, dump metadata reference, safe summary. |
| EF Core SQL timeout symptom | EF Core / SQL Latency Symptom Diagnosis | Query duration summary and SQL timeout evidence ref without sensitive SQL values. |
| External API latency causing timeout | External Dependency Diagnosis | Safe dependency reference and ServiceOps ticket. |
| .NET runtime diagnosis creates ServiceOps remediation reference | Cross-category | RemediationQueued or Verified result with ServiceOps reference. |

## API design preview

Future read-only API design only. Not implemented in this task.

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

## Product roadmap

Suggested phases:

| Phase | Scope |
| --- | --- |
| Phase 1 | Design |
| Phase 2 | Demo fixtures |
| Phase 3 | Read-only fixture API |
| Phase 4 | Frontend dashboard |
| Phase 5 | ASP.NET / IIS / Windows Service enterprise demo |
| Phase 6 | Agent-assisted RCA summary |
| Phase 7 | Human-approved controlled remediation workflow |

## Limitations

This task is design only.

No implementation was added:

* No frontend
* No backend
* No fixture
* No API
* No live diagnostic collector
* No dotnet-counters integration
* No dotnet-trace integration
* No dotnet-dump integration
* No IIS integration
* No Windows Service integration
* No production command execution

## Recommended next task

Task #310: .NET_RuntimeOps Demo Fixture Design
