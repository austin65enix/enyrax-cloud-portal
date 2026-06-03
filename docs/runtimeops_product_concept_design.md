# RuntimeOps Product Concept Design

Runtime diagnosis and RCA evidence governance module for ENYRAX

## Purpose

RuntimeOps is the formal production runtime diagnosis and RCA evidence governance module in ENYRAX.

RuntimeOps 是 ENYRAX 的正式環境執行期診斷與 RCA 證據治理模組。它的目標是把 production troubleshooting 從臨時排障，轉成可追蹤、可驗證、可復盤、可留證據的治理流程。

RuntimeOps is not only a monitoring dashboard. It is a governance chain that connects:

```text
Runtime Diagnosis + ServiceOps Ticket + Evidence + RCA + Verification
```

RuntimeOps focuses on the point where production symptoms, technical diagnosis, remediation tracking, and closure evidence need to be connected. It helps teams preserve enough safe context to understand what happened, why it happened, what was changed, and how the fix was verified.

## Product positioning

RuntimeOps is ENYRAX's technical depth module for technical managers, development managers, SRE leads, and infrastructure leads.

相較 AgentOps 偏 AI 時代前瞻治理，RuntimeOps 更泛用。任何企業只要有正式環境系統，都會遇到 runtime 問題：API 變慢、背景任務卡住、記憶體成長、查詢變慢、服務 timeout、正式環境難以重現。

RuntimeOps sits at the intersection of:

* Infra
* Dev
* SRE
* ServiceOps
* Audit Evidence

It is designed to show that ENYRAX can support deep technical operations, not only workflow dashboards. The product position is practical: production troubleshooting should become an auditable and reviewable operational discipline.

## Core problem

Enterprises often have monitoring, logs, tickets, and dashboards, but the actual runtime investigation is still fragmented. Teams see symptoms, restart services, inspect logs, exchange screenshots, and close tickets without preserving enough diagnosis evidence.

Common pain points:

* API becomes slow but the team cannot identify where the latency is.
* Production timeout appears under real traffic only.
* Background worker gets stuck.
* Queue backlog grows and no one knows whether the cause is worker capacity, dependency latency, or query delay.
* Memory leak is suspected but not proven.
* CPU spike affects users but no profile evidence is retained.
* GC pressure is visible but not tied to incident evidence.
* Thread pool starvation is hard to explain after the incident.
* Slow query impacts an API path but Dev, Infra, and DBA disagree on ownership.
* Logs are insufficient or too noisy.
* Test environment cannot reproduce the problem.
* The issue disappears after restart.
* Dev / Infra / DBA teams blame each other because evidence is not structured.

RuntimeOps addresses the evidence gap between "we saw a production symptom" and "we can explain, remediate, verify, and review it."

## RuntimeOps governance flow

Text flow:

```text
Incident / Ticket
-> Runtime Diagnosis
-> Trace / Dump / Profile / Metrics
-> Evidence Collection
-> RCA Summary
-> ServiceOps Remediation
-> Verification
-> Closure
```

Flow description:

1. Incident / Ticket: A runtime symptom is reported through alert, user impact, ServiceOps ticket, SOC event, or manual escalation.
2. Runtime Diagnosis: The team records the service, runtime, environment, suspected symptom, severity, and diagnosis type.
3. Trace / Dump / Profile / Metrics: Safe references are collected for traces, profiles, dumps, metrics snapshots, process status, exception rates, or slow endpoint summaries.
4. Evidence Collection: RuntimeOps stores safe metadata and evidence references, not raw sensitive payloads.
5. RCA Summary: The team records the likely root cause, contributing signals, unresolved questions, and confidence level.
6. ServiceOps Remediation: Remediation work is linked to a ServiceOps ticket or project task.
7. Verification: The team records whether the issue was fixed, what metric improved, and what evidence proves it.
8. Closure: The runtime incident is closed with traceable RCA, remediation, and verification evidence.

## First supported runtime families

### Python_RuntimeOps

Python_RuntimeOps covers Python production services, especially FastAPI, Uvicorn, Gunicorn, scheduled sync jobs, background workers, and Python diagnostic tooling.

Initial coverage:

* FastAPI latency
* Uvicorn / Gunicorn process status
* background worker timeout
* Wazuh / Graylog sync job failure
* memory growth
* CPU profile
* py-spy flamegraph
* exception rate
* slow endpoint summary

Example evidence references:

* FastAPI slow endpoint summary
* Uvicorn worker status snapshot
* process RSS / CPU metrics snapshot
* background job timeout metadata
* py-spy profile reference
* safe exception count summary
* ServiceOps ticket remediation link

### .NET_RuntimeOps

.NET_RuntimeOps covers enterprise .NET production workloads, especially ASP.NET Core APIs, IIS-hosted apps, Windows Services, EF Core, SQL Server integrations, and Windows diagnostic evidence.

Initial coverage:

* ASP.NET Core API slow
* IIS App Pool recycle
* Windows Service stuck
* EF Core / SQL Server slow query
* ThreadPool starvation
* GC memory pressure
* application exception rate
* Windows Event Log reference

Example evidence references:

* ASP.NET Core slow response summary
* IIS App Pool recycle event reference
* Windows Service state snapshot
* EF Core slow query reference
* SQL Server wait / query summary reference
* ThreadPool starvation indicator
* GC pressure metrics snapshot
* Windows Event Log safe reference

## Future runtime families

Future runtime families:

* Java_RuntimeOps
* Node_RuntimeOps
* Go_RuntimeOps
* Database_RuntimeOps
* Worker_RuntimeOps
* Container_RuntimeOps

Future families should follow the same governance model: read-only diagnosis first, safe metadata only, evidence references, RCA summary, remediation link, verification result, and closure.

## Core entities

Main data concepts:

| Entity | Meaning |
| --- | --- |
| Runtime Service | A production or staging service under runtime governance. |
| Runtime Incident | A runtime symptom or incident requiring diagnosis and follow-up. |
| Diagnosis Run | A structured diagnostic attempt for one runtime symptom. |
| Trace Evidence | Safe reference to trace, request path, span, or latency evidence. |
| Profile Evidence | Safe reference to CPU profile, flamegraph, or runtime profile summary. |
| Dump Evidence | Safe reference to dump metadata without exposing raw dump content. |
| Metrics Snapshot | Point-in-time summary of CPU, memory, GC, queue, latency, or error rate. |
| RCA Finding | Root cause or contributing factor recorded with confidence and evidence links. |
| ServiceOps Remediation Link | Link from runtime finding to remediation ticket or operational task. |
| Verification Result | Evidence-backed result proving whether remediation worked. |

## Runtime event fields

Suggested runtime event fields:

| Field | Meaning |
| --- | --- |
| `runtime_event_id` | Unique runtime event ID. |
| `service_name` | Service name or application label. |
| `service_type` | API, worker, Windows Service, batch job, sync job, database, or container. |
| `language_runtime` | Python, .NET, Java, Node, Go, database, or other runtime family. |
| `environment` | Production, staging, development, DR, or test. |
| `host_ref` | Safe host, node, app pool, pod, VM, or service reference. |
| `incident_ref` | Incident or alert reference. |
| `serviceops_ticket_ref` | Linked ServiceOps ticket reference. |
| `diagnosis_type` | Latency, timeout, memory, CPU, GC, queue, threadpool, slow query, exception, or process status. |
| `symptom` | Short human-readable symptom. |
| `started_at` | Diagnosis or incident start timestamp. |
| `ended_at` | Diagnosis or incident end timestamp. |
| `duration_ms` | Duration in milliseconds. |
| `severity` | Operational severity. |
| `risk_level` | Governance risk level. |
| `metric_summary` | Safe summarized metrics. |
| `evidence_ref` | Primary evidence package reference. |
| `trace_ref` | Trace evidence reference. |
| `profile_ref` | Profile or flamegraph evidence reference. |
| `dump_ref` | Dump metadata reference. |
| `rca_summary` | Root cause or current RCA summary. |
| `remediation_ref` | Remediation work reference. |
| `verification_status` | Pending, verified, failed, inconclusive, false_alarm, or not_required. |
| `notes` | Safe notes for reviewer context. |

## Dashboard views

Future dashboard views:

* Runtime Health Summary
* Slow API / Timeout Queue
* Background Job Failures
* Memory / CPU Hotspots
* Runtime Diagnosis Runs
* Trace Evidence
* Profile / Flame Graph Evidence
* Dump Evidence
* RCA Queue
* ServiceOps Linked Tickets
* Verification Results
* Safety Boundary

Dashboard intent:

* Show current runtime risk without exposing secrets or raw dumps.
* Help technical leads see which services are repeatedly failing.
* Help SRE and Infra teams prioritize diagnosis and remediation.
* Help Dev leads connect runtime symptoms to code, queries, capacity, or dependency issues.
* Help audit and internal control teams see evidence-backed closure.

## Risk scoring

Suggested risk scoring:

| Runtime condition | Risk level |
| --- | --- |
| Production service down | Critical |
| Recurring timeout | High |
| Memory leak suspected | High |
| CPU spike with user impact | High |
| Background job delayed | Medium |
| Slow endpoint without outage | Medium |
| Diagnosis completed and verified | Low |
| False alarm | Low |

Risk scoring should be explainable. The dashboard should show the symptom, impacted service, evidence references, remediation link, and verification status so reviewers can understand why the item has its current level.

## Integration model

RuntimeOps connects with existing ENYRAX modules:

| Module | RuntimeOps integration |
| --- | --- |
| SOC / AlertOps | Runtime symptom can be converted from alert to incident. |
| ServiceOps | Runtime diagnosis links to ticket, remediation work, closure, and verification. |
| ProjectOps | Major remediation can become a project or improvement roadmap item. |
| AgentOps | AI can assist with RCA summary, but must not directly execute high-risk operations. |
| 271Ops | Access or account-related runtime abnormality can be linked to access governance. |
| Evidence Package | Diagnosis result and verification result can be retained as evidence. |

RuntimeOps should not replace these modules. It provides the runtime technical diagnosis layer and preserves safe evidence references for cross-module governance.

## Safety boundary

RuntimeOps safety boundary:

* Design only
* Read-only diagnostics first
* No production mutation in early stage
* No restart action
* No kill process action
* No config change action
* No database write action
* No raw memory dump exposed
* No raw environment dump
* No raw command output
* No password / credential / API key / private key
* No customer raw data
* Safe metadata and evidence references only

RuntimeOps may reference diagnostic artifacts, but the product should expose only safe metadata, controlled summaries, and evidence references. Raw dumps, raw environment output, raw command output, secrets, keys, credentials, customer data, and private payloads must not be displayed in the product UI.

## Demo scenarios

Initial demo scenarios:

| Scenario | Runtime family | Demo outcome |
| --- | --- | --- |
| FastAPI endpoint latency spike | Python_RuntimeOps | Slow endpoint summary links latency metrics, trace reference, RCA note, and ServiceOps ticket. |
| Background sync job timeout | Python_RuntimeOps | Wazuh / Graylog sync job timeout creates diagnosis run and remediation reference. |
| Python memory growth suspected | Python_RuntimeOps | Memory metrics snapshot and process status indicate suspected leak for review. |
| py-spy flamegraph evidence captured | Python_RuntimeOps | Profile evidence reference is attached to an RCA finding. |
| ASP.NET Core API slow response | .NET_RuntimeOps | API slow response links request path, exception rate, and metrics snapshot. |
| IIS App Pool recycle observed | .NET_RuntimeOps | Windows Event Log reference and recycle timing are preserved as evidence. |
| SQL slow query suspected from .NET service | .NET_RuntimeOps | EF Core / SQL Server slow query reference links runtime symptom to DBA review. |
| Runtime diagnosis creates ServiceOps remediation reference | Cross-runtime | RCA finding creates a ServiceOps remediation link and later verification result. |

Additional future demo scenarios:

* ThreadPool starvation suspected in .NET service.
* GC memory pressure affects API response time.
* Queue backlog grows after dependency timeout.
* Restart clears symptom but RuntimeOps records missing evidence and unresolved RCA.

## Product roadmap

Suggested phases:

| Phase | Scope |
| --- | --- |
| Phase 1 | Concept + safe fixture data |
| Phase 2 | Read-only fixture API + dashboard |
| Phase 3 | Python_RuntimeOps self-diagnosis demo for ENYRAX FastAPI |
| Phase 4 | .NET_RuntimeOps enterprise scenario demo |
| Phase 5 | Agent-assisted RCA summary |
| Phase 6 | Controlled remediation workflow, still human-approved |

Roadmap notes:

* Phase 1 and Phase 2 should avoid live collection and use safe fixture data.
* Phase 3 can demonstrate ENYRAX FastAPI self-diagnosis, but should remain read-only.
* Phase 4 makes the product more enterprise-relevant by showing .NET / IIS / SQL Server scenarios.
* Phase 5 can use AgentOps-style assisted summaries while preserving human review.
* Phase 6 must remain controlled and human-approved; early RuntimeOps should not perform production mutation.

## Product value

Value by role:

| Role | Value |
| --- | --- |
| 技術主管 | Sees production troubleshooting depth, recurring runtime risks, RCA quality, and verification status. |
| Infra / SRE | Brings runtime diagnosis into operational workflow instead of ad hoc terminal sessions. |
| 開發主管 | Makes RCA evidence-backed with trace, profile, dump metadata, metrics, and slow endpoint summaries. |
| 稽核 / 內控 | Each runtime incident has ticket, evidence, remediation link, verification, and closure trail. |
| 面試展示 | Demonstrates cross Infra, App, Ops, and Evidence capability with practical technical depth. |

RuntimeOps gives ENYRAX a strong technical narrative: the platform is not only tracking work, but also organizing production diagnosis into a repeatable governance flow.

## Limitations

This task is design only.

No implementation was added:

* No frontend
* No backend
* No fixture
* No API
* No live diagnostic collector
* No runtime adapter
* No production action

RuntimeOps currently defines product scope and concepts only. It does not collect live diagnostics, inspect production processes, read dumps, execute commands, restart services, kill processes, change config, or write to databases.

## Recommended next task

Task #301: Python_RuntimeOps Design
