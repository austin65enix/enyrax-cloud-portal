# RuntimeOps Lab Environment Setup Plan

## 1. Purpose

The RuntimeOps Lab Environment Setup Plan defines a controlled, isolated, and repeatable runtime diagnostics lab for future validation of real runtime evidence in Python_RuntimeOps and .NET_RuntimeOps.

This task is setup planning only. It does not create a VM, install packages, start services, execute diagnostics, inspect processes, modify production settings, or collect runtime evidence.

## 2. Relationship to Task #319

Task #319 defines the RuntimeOps lab verification goals and diagnostic scenarios. It describes what the lab must prove, including Python and .NET runtime evidence, ServiceOps linkage, RCA summaries, and safe evidence handling.

Task #320 defines the lab environment needed to support those goals: VM specification, network exposure rules, directory layout, demo services, future tools, evidence output locations, service design, RuntimeOps fixture mapping, and safety boundaries.

## 3. Lab Scope

First phase lab scope:

* Ubuntu 24.04 VM
* Python Demo FastAPI Service
* .NET Demo ASP.NET Core Service
* Safe evidence output directory
* RuntimeOps fixture mapping workflow

Out of scope for the first phase:

* Windows Server VM
* IIS
* AD
* DNS / DHCP
* M365
* SQL Server production-like environment

## 4. Recommended VM Specification

| Item | Recommendation |
| --- | --- |
| OS | Ubuntu 24.04 LTS |
| CPU | 2 vCPU minimum, 4 vCPU recommended |
| RAM | 4 GB minimum, 8 GB recommended |
| Disk | 40 GB minimum |
| Network | Private / lab-only access preferred |
| User | Non-root operator account |
| Firewall | Allow SSH only from trusted source; optional HTTP local-only |

## 5. Lab Topology

Planned directory topology:

```text
RuntimeOps Lab VM
+-- /opt/runtimeops-lab/python-demo
+-- /opt/runtimeops-lab/dotnet-demo
+-- /opt/runtimeops-lab/evidence
+-- /opt/runtimeops-lab/scripts
+-- /opt/runtimeops-lab/logs
+-- /opt/runtimeops-lab/reports
```

Planned demo services:

* `python-demo-fastapi.service`
* `dotnet-demo-api.service`

These services are lab demo services only. They must not use production data, customer data, production databases, production credentials, or production service integrations.

## 6. Network and Exposure Rules

Default network policy:

* Allow localhost testing by default.
* Optionally expose lab demo routes through Nginx reverse proxy.
* Do not expose lab services to the public internet unless the route is explicitly marked demo-only.
* Do not connect to production DB.
* Do not connect to customer systems.
* Do not connect to real AD, IAM, or M365.
* Do not connect to real Windows, IIS, or SQL Server environments.

The lab should be treated as an isolated environment. Any external access should be intentional, temporary, and documented as demo-only.

## 7. Package Plan

This section lists future packages that may be needed. This task does not install them.

Python side:

* python3
* python3-venv
* pip
* fastapi
* uvicorn
* psutil
* py-spy
* stress-ng optional

.NET side:

* dotnet-sdk-8.0 or dotnet-sdk-9.0
* aspnetcore-runtime
* dotnet-counters
* dotnet-trace
* dotnet-dump metadata-only usage

System side:

* curl
* jq
* nginx optional
* systemd
* journalctl
* pidstat / sysstat optional

## 8. Directory Plan

Planned lab filesystem layout:

```text
/opt/runtimeops-lab/
+-- python-demo/
|   +-- app/
|   +-- venv/
|   +-- logs/
|   +-- README.md
+-- dotnet-demo/
|   +-- src/
|   +-- logs/
|   +-- README.md
+-- evidence/
|   +-- python/
|   +-- dotnet/
|   +-- safe-summaries/
+-- scripts/
|   +-- generate-python-symptoms/
|   +-- generate-dotnet-symptoms/
|   +-- summarize-evidence/
+-- reports/
+-- README.md
```

Directory intent:

| Directory | Purpose |
| --- | --- |
| `/opt/runtimeops-lab/python-demo` | Future FastAPI demo service source, virtual environment, and local logs. |
| `/opt/runtimeops-lab/dotnet-demo` | Future ASP.NET Core demo service source and local logs. |
| `/opt/runtimeops-lab/evidence/python` | Python lab evidence staging area for safe summaries only. |
| `/opt/runtimeops-lab/evidence/dotnet` | .NET lab evidence staging area for safe summaries only. |
| `/opt/runtimeops-lab/evidence/safe-summaries` | Final redacted summary output for RuntimeOps fixture mapping. |
| `/opt/runtimeops-lab/scripts` | Future lab-only symptom generation and summarization helpers. |
| `/opt/runtimeops-lab/reports` | Human-readable lab validation reports. |

## 9. Python Demo Service Plan

Future FastAPI endpoints:

| Endpoint | Purpose | RuntimeOps scenario mapping |
| --- | --- | --- |
| `/health` | Basic service reachability check. | Lab readiness and service health reference. |
| `/demo/slow` | Inject controlled endpoint latency. | `PY-LAB-001`, slow endpoint diagnosis. |
| `/demo/error` | Generate controlled exception bursts. | `PY-LAB-002`, exception burst diagnosis. |
| `/demo/memory-growth` | Allocate bounded memory growth for trend evidence. | `PY-LAB-004`, memory growth suspected. |
| `/demo/cpu-spike` | Run bounded CPU work for profile evidence. | `PY-LAB-005`, CPU spike / profile capture. |
| `/demo/external-timeout` | Simulate a delayed dependency timeout. | `PY-LAB-006`, external dependency timeout simulation. |
| `/demo/background-job-status` | Report controlled background job state and timeout status. | `PY-LAB-003`, background job timeout. |

The service should use demo-only data, structured logs, bounded resource usage, and explicit safeguards for symptom endpoints.

## 10. .NET Demo Service Plan

Future ASP.NET Core endpoints:

| Endpoint | Purpose | RuntimeOps scenario mapping |
| --- | --- | --- |
| `/health` | Basic service reachability check. | Lab readiness and service health reference. |
| `/demo/slow` | Inject controlled endpoint latency. | `DOTNET-LAB-001`, ASP.NET Core slow endpoint. |
| `/demo/error` | Generate controlled exception bursts. | `DOTNET-LAB-002`, ASP.NET Core exception burst. |
| `/demo/gc-pressure` | Allocate bounded memory pressure for GC counters. | `DOTNET-LAB-003`, GC allocation / memory pressure. |
| `/demo/threadpool-starvation` | Simulate bounded worker blocking. | `DOTNET-LAB-004`, ThreadPool starvation simulation. |
| `/demo/external-timeout` | Simulate a delayed dependency timeout. | `DOTNET-LAB-005`, external dependency timeout simulation. |
| `/demo/background-job-status` | Report controlled background job state. | Support future worker and timeout evidence references. |

The service should run only in lab mode, with bounded symptoms and no production integrations.

## 11. Evidence Output Plan

The lab should save safe summaries only.

Required evidence fields:

* `evidence_ref`
* `runtime_family`
* `service_name`
* `scenario_id`
* `diagnosis_type`
* `captured_at`
* `metric_summary`
* `duration_summary`
* `hotspot_summary`
* `before_summary`
* `after_summary`
* `raw_output_exposed: false`
* `raw_dump_exposed: false`
* `raw_trace_exposed: false`
* `safety_notes`

The lab must not save raw dump files, raw trace files, raw profile files, raw command output, customer data, request payloads, response payloads, secrets, or full sensitive paths.

## 12. Systemd Service Plan

This is a future service design only. This task does not create systemd units or start services.

| Service | Purpose | Working directory | Execution user | Environment file policy | Log handling | Restart policy | Safety note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `python-demo-fastapi.service` | Run the FastAPI lab demo service for Python_RuntimeOps scenarios. | `/opt/runtimeops-lab/python-demo` | Non-root lab service user. | Use a demo-only env file if needed; no production secrets. | Write structured demo logs to lab logs and journal summary only. | Conservative restart such as on-failure for lab availability. | Demo service only; no production data or production integrations. |
| `dotnet-demo-api.service` | Run the ASP.NET Core lab demo service for .NET_RuntimeOps scenarios. | `/opt/runtimeops-lab/dotnet-demo` | Non-root lab service user. | Use a demo-only env file if needed; no production secrets. | Write structured demo logs to lab logs and journal summary only. | Conservative restart such as on-failure for lab availability. | Demo service only; no production data or production integrations. |

## 13. RuntimeOps Mapping Plan

Lab evidence should be summarized first, reviewed, and only then mapped into existing RuntimeOps fixture-style schema files.

Python fixture mapping targets:

* `demo_python_diagnosis_runs.json`
* `demo_python_endpoint_metrics.json`
* `demo_python_profile_evidence.json`
* `demo_python_memory_evidence.json`
* `demo_python_rca_findings.json`
* `demo_python_verification_results.json`

.NET fixture mapping targets:

* `demo_dotnet_diagnosis_runs.json`
* `demo_dotnet_endpoint_metrics.json`
* `demo_dotnet_counter_evidence.json`
* `demo_dotnet_trace_evidence.json`
* `demo_dotnet_dump_evidence.json`
* `demo_dotnet_rca_findings.json`
* `demo_dotnet_verification_results.json`

Mapping workflow:

1. Trigger lab-only scenario.
2. Capture raw diagnostic material only in a controlled lab staging context when future tasks explicitly allow it.
3. Redact and summarize into safe evidence fields.
4. Review safe summary before import.
5. Map safe summaries into RuntimeOps fixture schema.
6. Display only safe evidence in the RuntimeOps dashboard.
7. Link ServiceOps ticket references by `evidence_ref`, without exposing raw artifacts.

## 14. Validation Plan

Future validation steps:

* VM created.
* Demo services reachable on localhost.
* Python scenarios can be triggered.
* .NET scenarios can be triggered.
* Safe evidence summaries generated.
* No raw output stored.
* RuntimeOps fixture schema updated from safe summaries.
* Dashboard can show lab-derived evidence.
* ServiceOps ticket references can be linked.

## 15. Safety Boundary

This task and the future first-phase lab must preserve these boundaries:

* Plan only.
* No VM created in this task.
* No package installed in this task.
* No service started in this task.
* No diagnostic command executed in this task.
* No production data.
* No customer data.
* No secrets.
* No production DB.
* No production process inspection.
* No raw dump stored.
* No raw trace stored.
* No raw command output stored.
* No automated remediation.
* No restart / kill / config change.

## 16. Risk Controls

Required risk controls:

* Use demo services only.
* Use isolated lab VM.
* Use non-root service user.
* Use localhost-first access.
* Use safe evidence summaries.
* Review evidence before importing into fixtures.
* Keep production ENYRAX portal separate from lab collector.
* Avoid automatic remediation.

## 17. Limitations

* Plan only.
* No implementation.
* No scripts.
* No VM provisioning.
* No collector.
* No live runtime data.
* No Windows lab.
* No IIS lab.
* No AD lab.

## 18. Recommended Next Task

Task #321: RuntimeOps Lab Ubuntu VM Bootstrap Guide

#320 RuntimeOps Lab Environment Setup Plan ✅

RuntimeOps Lab VM 已建立並完成第一筆 OS baseline evidence。

Evidence:
- runtimeops_verify_20260604_014139.txt

驗證內容:
- Hostname: atn
- Uptime: PASS
- Memory: 3.8GiB available 3.3GiB
- Disk: root volume 9.8G, used 35%
- IP: 192.168.23.156/24
- Workspace: ~/runtimeops-lab
