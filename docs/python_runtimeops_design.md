# Python_RuntimeOps Design

Python runtime diagnosis and RCA evidence governance submodule for RuntimeOps

## Purpose

Python_RuntimeOps is the Python / FastAPI / worker diagnosis submodule under RuntimeOps.

Python_RuntimeOps 的目標是把 Python production troubleshooting 轉成可追蹤、可驗證、可復盤、可留證據的治理流程。它聚焦 FastAPI endpoint latency、Uvicorn / Gunicorn worker behavior、background job timeout、sync job failure、memory growth、CPU profile、exception rate、external dependency latency, and DB latency symptoms.

The first stage is read-only diagnostics design. It does not implement restart, kill process, config change, database write, or any production diagnostic command.

## Product context

RuntimeOps is the overall ENYRAX production runtime diagnostics and RCA evidence governance concept.

Python_RuntimeOps is the first concrete runtime family. It can use the ENYRAX FastAPI backend as a self-diagnosis demo because ENYRAX already has a Python backend, read-only API patterns, ServiceOps references, 271ops governance evidence, and AgentOps-style summary concepts.

Potential integrations:

* ServiceOps ticket: runtime diagnosis ticket, remediation reference, closure workflow.
* Evidence Package: diagnosis summary and verification result retained as evidence.
* AgentOps RCA summary: AI-assisted RCA summary with human review.
* RuntimeOps dashboard: Python service health, diagnosis runs, evidence, RCA findings, and verification results.

## Core Python runtime problems

Python_RuntimeOps should cover these common production symptoms:

* FastAPI endpoint latency spike
* Uvicorn / Gunicorn worker timeout
* background job timeout
* sync job failure
* Wazuh / Graylog ingestion delay
* memory growth / memory leak suspected
* CPU spike
* exception rate increase
* dependency / import failure
* slow external API call
* DB query latency symptom
* event loop blocking
* queue backlog
* log not enough to reproduce issue

The module should preserve safe context around these symptoms so teams can explain what happened and how it was verified without exposing secrets, raw dumps, raw command output, or customer data.

## Python_RuntimeOps governance flow

Text flow:

```text
ServiceOps Ticket / Runtime Alert
-> Python Runtime Diagnosis Run
-> Metrics Snapshot
-> Trace / Profile Evidence
-> RCA Finding
-> Remediation Reference
-> Verification Result
-> Closure
```

Flow description:

1. ServiceOps Ticket / Runtime Alert: A runtime symptom enters through a ticket, alert, SOC event, dashboard warning, or manual escalation.
2. Python Runtime Diagnosis Run: The service, runtime, process reference, endpoint, worker, job, symptom, severity, and diagnosis type are recorded.
3. Metrics Snapshot: Safe metric summary is attached, such as latency percentiles, error rate, memory summary, CPU summary, queue length, or timeout count.
4. Trace / Profile Evidence: Safe trace, profile, memory, or endpoint evidence references are linked.
5. RCA Finding: A finding records likely cause, confidence, related evidence, and unresolved questions.
6. Remediation Reference: Remediation is linked to ServiceOps or ProjectOps.
7. Verification Result: Before/after summaries and evidence references confirm whether the issue was resolved.
8. Closure: The runtime event is closed with ticket, evidence, RCA, remediation, and verification trail.

## Diagnostic categories

Initial categories:

| Category | Purpose |
| --- | --- |
| API Latency Diagnosis | Investigate FastAPI slow endpoint, timeout, p95/p99 latency, and user impact. |
| Worker / Process Diagnosis | Review Uvicorn / Gunicorn worker status, timeout suspicion, crash loop, or process health. |
| Background Job Diagnosis | Track sync jobs, scheduled jobs, delayed runs, failed runs, and timeout symptoms. |
| Memory Diagnosis | Review memory growth, RSS changes, suspected leak area, and memory evidence reference. |
| CPU Profile Diagnosis | Attach safe CPU profile or py-spy flamegraph evidence reference. |
| Exception / Error Rate Diagnosis | Track exception count changes, fixture warnings, dependency failure, or error bursts. |
| External Dependency Diagnosis | Track slow external API calls, dependency timeout, and safe dependency references. |
| DB Latency Symptom Diagnosis | Track DB query latency symptoms without storing sensitive SQL values. |
| Queue / Scheduler Diagnosis | Track queue backlog, scheduler delay, delayed processing, and worker capacity symptoms. |

## Possible tools / evidence sources

Design-only possible sources:

* FastAPI access log summary
* Uvicorn / Gunicorn process metadata
* systemd service status reference
* ps / top / pidstat summary
* py-spy profile evidence reference
* tracemalloc summary reference
* cProfile / pstats summary reference
* Prometheus / metrics endpoint if available
* structured application logs
* queue length summary
* database query duration summary
* external API timing summary

Safety handling:

* Raw command output is not directly displayed.
* Raw memory dump is not directly displayed.
* Raw environment dump is not directly displayed.
* Raw profile content is not directly displayed.
* The product stores safe summaries and evidence references only.

## Core entities

| Entity | Meaning |
| --- | --- |
| Python Runtime Service | A Python service under RuntimeOps governance, such as FastAPI backend or worker. |
| Python Diagnosis Run | One structured diagnosis attempt for a Python runtime symptom. |
| Python Endpoint Metric | Safe endpoint latency, request, timeout, and error summary. |
| Python Worker Snapshot | Safe worker or process metadata snapshot. |
| Python Background Job Event | Safe scheduled job, sync job, queue, or worker job event. |
| Python Profile Evidence | Safe reference to CPU profile, py-spy, cProfile, or pstats evidence. |
| Python Memory Evidence | Safe reference to memory growth, tracemalloc, RSS, or leak suspicion summary. |
| Python RCA Finding | Evidence-linked root cause or contributing factor. |
| Python Verification Result | Before/after validation for a diagnosis or remediation. |

## Python diagnosis run fields

Suggested fields:

| Field | Meaning |
| --- | --- |
| `diagnosis_run_id` | Unique Python diagnosis run ID. |
| `runtime_event_id` | Runtime event ID for cross-runtime linkage. |
| `service_name` | Service name, such as `enyrax-api`. |
| `service_type` | FastAPI backend, worker, sync job, scheduler, or queue worker. |
| `language_runtime` | Python runtime label. |
| `python_version_label` | Safe Python version label. |
| `framework` | FastAPI, Uvicorn, Gunicorn, Celery, APScheduler, or custom worker. |
| `environment` | Production, staging, demo, or development. |
| `host_ref` | Safe host reference. |
| `process_ref` | Safe process reference. |
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
| `worker_ref` | Safe worker reference. |
| `job_ref` | Safe job reference. |
| `metric_summary` | Safe metric summary only. |
| `trace_ref` | Safe trace evidence reference. |
| `profile_ref` | Safe profile evidence reference. |
| `memory_ref` | Safe memory evidence reference. |
| `evidence_ref` | Primary evidence reference. |
| `rca_summary` | Safe RCA summary. |
| `remediation_ref` | Remediation reference. |
| `verification_status` | Pending, ReviewRequired, EvidenceCaptured, RemediationQueued, Verified, or FalseAlarm. |
| `notes` | Safe notes. |

## Dashboard views

Future dashboard views:

* Python Runtime Health Summary
* Slow FastAPI Endpoints
* Worker Timeout Watch
* Background Job Failure Queue
* Memory Growth Watch
* CPU Profile Evidence
* Exception Rate Trend
* External Dependency Latency
* Queue / Scheduler Backlog
* RCA Findings
* ServiceOps Linked Tickets
* Verification Results
* Safety Boundary

## Risk scoring

Suggested scoring:

| Condition | Risk level |
| --- | --- |
| API unavailable | Critical |
| Repeated endpoint timeout | High |
| Worker crash loop | High |
| Memory growth suspected | High |
| Event loop blocking suspected | High |
| Background job delayed | Medium |
| External API slow | Medium |
| Exception rate elevated | Medium |
| Profile captured and verified | Low |
| False alarm | Low |

Risk scoring should preserve the symptom, impacted service, diagnosis type, evidence reference, remediation status, and verification status.

## ENYRAX self-diagnosis demo plan

Demo service:

| Field | Value |
| --- | --- |
| `service_name` | `enyrax-api` |
| `framework` | `FastAPI` |
| `runtime` | `Python` |
| `systemd unit` | `enyrax-api.service` |

Demo symptoms:

* `/api/271ops` endpoint latency spike
* fixture loader warning
* background sync delay
* high exception count
* slow JSON response generation

Demo evidence:

* safe route latency summary
* service status reference
* profile evidence reference
* ServiceOps ticket reference
* RCA summary

The demo must not run live diagnostic commands. It should use fixture data, safe references, and summaries.

## Integration model

| Module | Integration |
| --- | --- |
| ServiceOps | Create runtime diagnosis ticket and remediation workflow. |
| SOC / AlertOps | Convert alert into runtime investigation. |
| AgentOps | AI assists RCA summary but does not directly execute high-risk operations. |
| ProjectOps | Major remediation escalates into project. |
| Evidence Package | Preserve diagnosis summary and verification result. |
| 271Ops | Link to governance evidence if runtime issue involves account, permission, or access review context. |

## Safety boundary

Safety boundary:

* Design only
* Read-only diagnostics first
* No restart action
* No kill process action
* No config change action
* No database write action
* No raw memory dump exposed
* No raw environment variables
* No raw command output
* No full stack trace exposure by default
* No password / credential / API key / private key
* No customer raw data
* Safe metadata and evidence references only

## Demo scenarios

Initial demo scenarios:

| Scenario | Diagnosis type | Expected demo output |
| --- | --- | --- |
| FastAPI endpoint latency spike | API Latency Diagnosis | Endpoint metric, trace reference, evidence reference, RCA note. |
| Uvicorn worker timeout suspected | Worker / Process Diagnosis | Worker snapshot and ReviewRequired verification status. |
| Background sync job timeout | Background Job Diagnosis | Job event, ServiceOps ticket reference, remediation reference. |
| Fixture loader warning creates runtime diagnosis | Exception / Error Rate Diagnosis | Warning evidence reference and Medium risk RCA finding. |
| Python memory growth suspected | Memory Diagnosis | Memory evidence reference and ReviewRequired status. |
| py-spy profile evidence captured | CPU Profile Diagnosis | Profile evidence reference and EvidenceCaptured or Verified status. |
| External API latency causing timeout | External Dependency Diagnosis | Safe dependency reference and linked ServiceOps ticket. |
| Runtime diagnosis creates ServiceOps remediation reference | Cross-category | RemediationQueued or Verified result with ServiceOps reference. |

## API design preview

Future read-only API design only. Not implemented in this task.

```text
GET /api/runtimeops/python/services
GET /api/runtimeops/python/diagnosis-runs
GET /api/runtimeops/python/diagnosis-runs/{diagnosis_run_id}
GET /api/runtimeops/python/slow-endpoints
GET /api/runtimeops/python/background-jobs
GET /api/runtimeops/python/profile-evidence
GET /api/runtimeops/python/memory-evidence
GET /api/runtimeops/python/rca-findings
GET /api/runtimeops/python/dashboard
```

## Product roadmap

Suggested phases:

| Phase | Scope |
| --- | --- |
| Phase 1 | Design |
| Phase 2 | Demo fixtures |
| Phase 3 | Read-only fixture API |
| Phase 4 | Frontend dashboard |
| Phase 5 | ENYRAX FastAPI self-diagnosis demo |
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
* No py-spy integration
* No tracemalloc integration
* No production command execution

## Recommended next task

Task #302: Python_RuntimeOps Demo Fixture Design
