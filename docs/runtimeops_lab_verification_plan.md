# RuntimeOps Lab Verification Plan

## 1. Purpose

The RuntimeOps Lab Verification Plan defines a safe, controlled, and repeatable lab for validating whether RuntimeOps can move from a fixture-backed demo toward real runtime evidence.

This stage is plan only. It does not create a VM, install packages, execute diagnostics, inspect production processes, modify production configuration, or implement collectors.

## 2. Current RuntimeOps Status

Current completed RuntimeOps scope:

| Area | Status |
| --- | --- |
| RuntimeOps Portal entry | Completed. |
| Python_RuntimeOps frontend | Completed. |
| Python_RuntimeOps fixture API | Completed. |
| Python_RuntimeOps production route verification | Completed: `GET /api/runtimeops/python/dashboard = 200`, `source = fixture`, `warnings = []`. |
| .NET_RuntimeOps frontend | Completed. |
| .NET_RuntimeOps fixture API | Completed. |
| .NET_RuntimeOps production route verification | Completed: `GET /api/runtimeops/dotnet/dashboard = 200`. |
| Read-only safety boundary | Completed for the current fixture-backed dashboard. |
| No production diagnostic command execution | Preserved. RuntimeOps remains an API-backed demo with fixture-backed read-only evidence. |

## 3. Lab Goals

The lab should validate these RuntimeOps capabilities using controlled demo workloads:

* Verify FastAPI slow endpoint diagnosis.
* Verify Python background job timeout diagnosis.
* Verify Python memory growth evidence.
* Verify Python CPU profile evidence.
* Verify ASP.NET Core slow endpoint diagnosis on Ubuntu.
* Verify .NET GC, ThreadPool, and exception counter evidence on Ubuntu.
* Verify how runtime evidence can become a ServiceOps ticket reference.
* Verify how an RCA summary can be used by AgentOps or a human review process.
* Verify that evidence stores only safe metadata and does not store raw dumps, raw traces, or raw command output.

## 4. Recommended Lab Topology

The first phase should use one isolated Ubuntu VM.

Recommended VM:

* Ubuntu 24.04
* ENYRAX Portal
* FastAPI demo service
* ASP.NET Core demo service
* Nginx reverse proxy if needed
* Python diagnostic tools
* .NET diagnostic tools

Topology:

```text
Ubuntu RuntimeOps Lab VM
+-- ENYRAX Portal
+-- Python Demo FastAPI Service
+-- .NET Demo ASP.NET Core Service
+-- RuntimeOps Evidence Collector Prototype
+-- Safe Evidence Output Directory
```

Windows Server VM is not required for the first lab phase. .NET_RuntimeOps can first validate runtime diagnostics with ASP.NET Core on Ubuntu. IIS, Windows Service, AD, Windows Event Log, and other Windows-specific diagnostics should remain in a later WindowsInfra_RuntimeOps lab.

## 5. Optional Future Lab Topology

The second lab phase can add:

* Windows Server VM
* IIS
* Windows Service
* Event Viewer
* Task Scheduler
* AD, DNS, and DHCP demo roles if needed

This future topology is intended for:

* WindowsInfra_RuntimeOps
* IIS-specific .NET_RuntimeOps
* Windows Service diagnostics

## 6. Python Lab Scenarios

| scenario_id | symptom | trigger method | safe evidence expected | unsafe evidence excluded | expected RuntimeOps mapping | expected ServiceOps linkage |
| --- | --- | --- | --- | --- | --- | --- |
| PY-LAB-001 | FastAPI slow endpoint | Demo endpoint sleeps for a controlled duration such as 2 to 5 seconds. | Endpoint path pattern, percentile latency summary, request count, time window, demo service name, diagnosis label. | Raw request body, raw response body, full headers, raw access log lines. | `diagnosis_type = slow_endpoint`, `runtime_family = python`, endpoint metric summary and RCA candidate. | Reference ticket for slow API triage with evidence_ref and affected demo endpoint. |
| PY-LAB-002 | FastAPI exception burst | Demo endpoint raises controlled exceptions for a fixed request count. | Exception class summary, count, time window, endpoint path pattern, status code distribution. | Stack trace with full paths, request payload, sensitive headers, raw log output. | `diagnosis_type = exception_burst`, Python service exception evidence and RCA finding. | Reference ticket for exception burst review with safe exception summary. |
| PY-LAB-003 | Background job timeout | Demo background task exceeds a configured timeout threshold. | Job name, configured timeout, observed duration band, timeout count, schedule window. | Raw job payload, environment variables, command output, private file paths. | `diagnosis_type = background_job_timeout`, job evidence summary and remediation candidate. | Reference ticket for stuck job investigation with job timeout evidence_ref. |
| PY-LAB-004 | Memory growth suspected | Demo service allocates memory in controlled increments. | RSS trend summary, growth rate, start and end memory bands, process role, capture window. | Raw memory dump, object dump, heap contents, raw profiler file. | `diagnosis_type = memory_growth`, metric_summary and before/after memory evidence. | Reference ticket for suspected leak review with non-sensitive memory trend. |
| PY-LAB-005 | CPU spike / profile capture | Demo CPU-bound endpoint or worker loop runs for a bounded interval. | CPU utilization band, duration, top safe hotspot function names if redacted, profile capture metadata. | Raw profile file, raw flamegraph, full source paths, raw command output. | `diagnosis_type = cpu_profile`, hotspot_summary and bounded CPU evidence. | Reference ticket for CPU hotspot review with safe hotspot summary only. |
| PY-LAB-006 | External dependency timeout simulation | Demo service calls a local delayed dependency endpoint with a low timeout. | Dependency alias, timeout threshold, observed timeout count, affected endpoint, duration summary. | Dependency URL with secrets, raw request/response bodies, tokens, raw logs. | `diagnosis_type = dependency_timeout`, dependency latency evidence and RCA candidate. | Reference ticket for dependency timeout review with safe dependency alias. |

## 7. .NET on Ubuntu Lab Scenarios

| scenario_id | symptom | trigger method | safe evidence expected | unsafe evidence excluded | expected RuntimeOps mapping | expected ServiceOps linkage |
| --- | --- | --- | --- | --- | --- | --- |
| DOTNET-LAB-001 | ASP.NET Core slow endpoint | Demo controller or minimal API endpoint delays for a controlled duration. | Route pattern, percentile latency summary, request count, time window, demo service name. | Raw request body, raw response body, full headers, raw access log lines. | `diagnosis_type = slow_endpoint`, `runtime_family = dotnet`, endpoint metric summary and RCA candidate. | Reference ticket for slow ASP.NET Core endpoint triage. |
| DOTNET-LAB-002 | ASP.NET Core exception burst | Demo endpoint throws controlled exceptions for a fixed number of requests. | Exception type summary, count, status code distribution, route pattern, time window. | Full stack traces with paths, request payloads, raw structured log output. | `diagnosis_type = exception_burst`, .NET exception counter evidence and RCA finding. | Reference ticket for exception burst review with safe exception summary. |
| DOTNET-LAB-003 | GC allocation / memory pressure | Demo endpoint allocates controlled memory pressure within bounded limits. | GC heap size band, allocation rate band, Gen 0/1/2 count summary, working set trend. | Raw dump, heap dump, object contents, raw trace file. | `diagnosis_type = gc_memory_pressure`, counter summary and before/after evidence. | Reference ticket for memory pressure review with safe GC metrics. |
| DOTNET-LAB-004 | ThreadPool starvation simulation | Demo endpoint blocks worker threads in a bounded test mode. | ThreadPool queue length band, active thread count band, request latency impact, time window. | Raw trace events, raw thread stacks, full command output, sensitive paths. | `diagnosis_type = threadpool_starvation`, ThreadPool metric summary and RCA candidate. | Reference ticket for concurrency starvation review. |
| DOTNET-LAB-005 | External dependency timeout simulation | Demo API calls a local delayed dependency with a short timeout. | Dependency alias, timeout threshold, timeout count, route pattern, duration summary. | Raw URL with secrets, request/response bodies, tokens, full log lines. | `diagnosis_type = dependency_timeout`, dependency timeout evidence and RCA candidate. | Reference ticket for dependency timeout review with safe dependency alias. |
| DOTNET-LAB-006 | dotnet-counters snapshot evidence | Capture a bounded counters snapshot against the demo process only. | Selected counter names, min/max/average bands, capture duration, demo process alias. | Raw `dotnet-counters` output, process command line, raw trace, raw dump. | `diagnosis_type = runtime_counter_snapshot`, safe metric_summary and duration_summary. | Reference ticket for runtime counter review with evidence_ref only. |

## 8. Suggested Tools

This is a planning list only. The task does not install or run these tools.

Python side:

* uvicorn
* FastAPI
* py-spy
* ps
* top
* pidstat
* curl
* structured logs

.NET side:

* dotnet SDK / runtime
* dotnet-counters
* dotnet-trace
* dotnet-dump metadata only
* curl
* structured logs

System side:

* systemd status reference
* journalctl summary reference
* Nginx access log summary if needed

## 9. Safe Evidence Contract

RuntimeOps lab evidence should use this safe metadata contract:

| Field | Description |
| --- | --- |
| `evidence_ref` | Stable reference ID for the summarized evidence. |
| `scenario_id` | Lab scenario that generated the evidence. |
| `service_name` | Demo service alias, not a sensitive production hostname. |
| `runtime_family` | Runtime family such as `python` or `dotnet`. |
| `diagnosis_type` | Diagnosis category such as `slow_endpoint`, `cpu_profile`, or `runtime_counter_snapshot`. |
| `captured_at` | Capture timestamp. |
| `metric_summary` | Redacted aggregate metrics only. |
| `duration_summary` | Time window and duration bands. |
| `hotspot_summary` | Safe hotspot labels or redacted function categories only. |
| `before_summary` | Safe before-state summary. |
| `after_summary` | Safe after-state summary. |
| `raw_output_exposed` | Must be `false`. |
| `raw_dump_exposed` | Must be `false`. |
| `raw_trace_exposed` | Must be `false`. |
| `command_output_ref` | Must be `none` for exposed RuntimeOps dashboard evidence. |
| `safety_notes` | Notes describing redaction, summarization, and excluded data. |

Example shape:

```json
{
  "evidence_ref": "rtops-lab-py-001-001",
  "scenario_id": "PY-LAB-001",
  "service_name": "python-demo-fastapi",
  "runtime_family": "python",
  "diagnosis_type": "slow_endpoint",
  "captured_at": "2026-06-03T00:00:00Z",
  "metric_summary": {
    "request_count": 25,
    "p95_latency_ms": 3100,
    "status_code_summary": {
      "200": 25
    }
  },
  "duration_summary": "Controlled 5 minute lab window.",
  "hotspot_summary": "No raw profile exposed.",
  "before_summary": "Baseline p95 latency below threshold.",
  "after_summary": "Injected slow endpoint exceeded threshold.",
  "raw_output_exposed": false,
  "raw_dump_exposed": false,
  "raw_trace_exposed": false,
  "command_output_ref": "none",
  "safety_notes": "Demo-only aggregate evidence; no raw payloads or command output stored."
}
```

## 10. What Must Not Be Collected

RuntimeOps lab evidence must not collect, store, or expose:

* Raw command output
* Raw memory dump
* Raw trace file
* Raw profile file
* Raw environment variables
* Raw secrets
* Raw request body
* Raw response body
* Customer data
* API key
* Token
* Private key
* Full system path
* Full SQL with sensitive values

## 11. Lab Execution Phases

| Phase | Name | Scope |
| --- | --- | --- |
| Phase 1 | Plan only | Document the lab plan and safety boundaries. No execution. |
| Phase 2 | Create demo Python / .NET services | Build isolated demo services with controlled symptom endpoints. |
| Phase 3 | Generate controlled symptoms | Trigger lab-only symptoms against demo services. |
| Phase 4 | Capture safe metric summaries | Convert diagnostics into aggregate metadata only. |
| Phase 5 | Map evidence to RuntimeOps fixture schema | Align lab evidence with the RuntimeOps read-only data model. |
| Phase 6 | Display evidence in RuntimeOps dashboard | Show safe evidence summaries through existing RuntimeOps dashboard patterns. |
| Phase 7 | Create ServiceOps-linked RCA story | Link evidence_ref to a ServiceOps reference ticket and RCA narrative. |
| Phase 8 | Document production safety boundary | Define what must change before any future real collector is considered. |

## 12. Validation Checklist

* Lab VM isolated from production.
* No production command execution.
* No production process inspection.
* No customer data.
* No secret exposure.
* No raw dump exposure.
* No raw trace exposure.
* Python scenarios reproducible.
* .NET scenarios reproducible.
* Evidence maps to RuntimeOps schema.
* Dashboard can show safe evidence.
* ServiceOps ticket linkage works as reference only.

## 13. Risk and Safety Controls

The lab must run on demo services only.

Diagnostic commands must target only demo process IDs. The first phase must not point any collector at the `enyrax-api` production process or any other production process.

RuntimeOps lab work must not implement automated restart, kill, or remediation behavior. Human review is required before any future real evidence collector is designed, and redaction plus summarization must happen before evidence is stored or displayed.

## 14. Product Value

RuntimeOps Lab gives ENYRAX a path from a fixture-backed demo toward a real evidence demo while preserving a strong safety boundary.

Product value:

* Demonstrates cross-runtime diagnostics across Python and .NET.
* Shows how infrastructure symptoms, application evidence, ServiceOps tickets, and RCA summaries can connect.
* Provides a more convincing technical manager demo than static fixtures alone.
* Creates reusable interview demonstration and productization material.
* Proves that runtime evidence can be summarized safely without exposing raw sensitive artifacts.

## 15. Limitations

* Plan only.
* No VM created.
* No package installed.
* No diagnostic command executed.
* No collector implemented.
* No frontend changes.
* No backend changes.
* No database changes.
* No API changes.
* No fixture changes.
* No script changes.
* No production verification change.

## 16. Recommended Next Task

Task #320: RuntimeOps Lab Environment Setup Plan
