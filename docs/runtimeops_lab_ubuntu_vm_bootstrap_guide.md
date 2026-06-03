# RuntimeOps Lab Ubuntu VM Bootstrap Guide

## 1. Purpose

The RuntimeOps Lab Ubuntu VM Bootstrap Guide is a future operation blueprint for creating an isolated Ubuntu lab VM that can support Python_RuntimeOps and .NET_RuntimeOps real runtime evidence demos.

This task creates the guide only. It does not provision a VM, install packages, start services, run diagnostics, inspect processes, or collect evidence.

## 2. Dependency

Task #319: RuntimeOps Lab Verification Plan is completed.

Task #320: RuntimeOps Lab Environment Setup Plan defines the lab environment, VM specification, network design, directory plan, services, tools, and safety boundaries. If Task #320 is not completed before execution, this bootstrap guide can still be used as an initial blueprint, but the environment design should be completed or recalibrated before any lab VM build begins.

This guide does not handle the production host and must not be used to install anything on `portal.soc-monitoring.dev`.

## 3. Lab VM Assumptions

Recommended lab VM assumptions:

| Item | Recommendation |
| --- | --- |
| OS | Ubuntu 24.04 LTS |
| CPU | 2 vCPU minimum, 4 vCPU recommended |
| RAM | 4 GB minimum, 8 GB recommended |
| Disk | 40 GB minimum |
| Isolation | Isolated lab VM |
| User | Non-root operator user |
| SSH | Restricted to trusted source |
| Data | No production data and no customer data |

## 4. Safety Boundary

This guide must preserve these boundaries:

* Guide only.
* Do not run on production ENYRAX host.
* Do not inspect production process.
* Do not install diagnostic tools on production as part of this guide.
* No production DB connection.
* No customer data.
* No secrets.
* No raw dump stored.
* No raw trace stored.
* No raw command output stored.
* No automated remediation.
* No restart / kill / config change against production.

## 5. Bootstrap Phases

Planned phases, not executed in this task:

| Phase | Name | Purpose |
| --- | --- | --- |
| Phase 0 | Prepare isolated VM | Create or select a lab-only Ubuntu VM with restricted network access. |
| Phase 1 | Create lab directory structure | Prepare `/opt/runtimeops-lab` and subdirectories. |
| Phase 2 | Install base packages | Install future lab dependencies on the isolated VM only. |
| Phase 3 | Prepare Python demo service | Create the FastAPI demo application and bounded symptom endpoints. |
| Phase 4 | Prepare .NET demo service | Create the ASP.NET Core demo application and bounded symptom endpoints. |
| Phase 5 | Prepare evidence directories | Create safe evidence output locations for Python, .NET, and summaries. |
| Phase 6 | Prepare systemd unit templates | Draft lab-only service units for demo services. |
| Phase 7 | Run controlled symptoms | Trigger lab-only symptoms against demo services. |
| Phase 8 | Generate safe evidence summaries | Convert observations into redacted summary JSON. |
| Phase 9 | Map evidence to RuntimeOps fixture schema | Import reviewed safe summaries into RuntimeOps fixture-style data. |

## 6. Suggested Directory Structure

Planned directory structure:

```text
/opt/runtimeops-lab/
+-- python-demo/
+-- dotnet-demo/
+-- evidence/
|   +-- python/
|   +-- dotnet/
|   +-- safe-summaries/
+-- scripts/
+-- logs/
+-- reports/
+-- README.md
```

## 7. Future Bootstrap Commands

The following commands are future lab VM commands only.

DO NOT RUN ON PRODUCTION HOST.

DO NOT RUN THESE COMMANDS AS PART OF THIS TASK.

Base package preparation:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
sudo apt install -y curl jq
sudo apt install -y sysstat
sudo apt install -y stress-ng
```

The `sysstat` and `stress-ng` packages are optional and should be used only in the isolated lab VM.

Microsoft package repository setup for .NET:

```bash
wget https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
sudo apt update
```

.NET SDK installation:

```bash
sudo apt install -y dotnet-sdk-8.0
```

If the lab design chooses .NET 9 instead of .NET 8, the future install command can be adjusted:

```bash
sudo apt install -y dotnet-sdk-9.0
```

.NET diagnostic tool installation:

```bash
dotnet tool install --global dotnet-counters
dotnet tool install --global dotnet-trace
dotnet tool install --global dotnet-dump
```

These commands are future lab VM commands only. They must not be run on the production ENYRAX host, and raw diagnostic outputs must not be exposed in RuntimeOps.

## 8. Python Demo Service Bootstrap Plan

Future Python demo bootstrap steps:

* Create `/opt/runtimeops-lab/python-demo`.
* Create a Python virtual environment.
* Install FastAPI, Uvicorn, and psutil inside the lab virtual environment.
* Create a demo FastAPI app with bounded symptom endpoints.
* Keep demo logs local to the lab.
* Ensure endpoints use demo-only data and safe synthetic payloads.

Planned endpoints:

| Endpoint | Purpose |
| --- | --- |
| `/health` | Basic service readiness and localhost reachability check. |
| `/demo/slow` | Controlled slow endpoint for latency diagnosis. |
| `/demo/error` | Controlled exception burst for error diagnosis. |
| `/demo/memory-growth` | Bounded memory growth for memory evidence. |
| `/demo/cpu-spike` | Bounded CPU work for CPU profile evidence. |
| `/demo/external-timeout` | Simulated dependency timeout without real external systems. |
| `/demo/background-job-status` | Demo background job status and timeout state. |

This guide describes the demo service only. It does not implement the application.

## 9. .NET Demo Service Bootstrap Plan

Future .NET demo bootstrap steps:

* Create `/opt/runtimeops-lab/dotnet-demo`.
* Use `dotnet new webapi` for an ASP.NET Core demo service.
* Add bounded symptom endpoints for RuntimeOps scenarios.
* Keep demo logs local to the lab.
* Ensure the service uses demo-only data and no production integrations.

Planned endpoints:

| Endpoint | Purpose |
| --- | --- |
| `/health` | Basic service readiness and localhost reachability check. |
| `/demo/slow` | Controlled slow endpoint for ASP.NET Core latency diagnosis. |
| `/demo/error` | Controlled exception burst for .NET exception evidence. |
| `/demo/gc-pressure` | Bounded allocation pressure for GC evidence. |
| `/demo/threadpool-starvation` | Bounded ThreadPool starvation simulation. |
| `/demo/external-timeout` | Simulated dependency timeout without real external systems. |
| `/demo/background-job-status` | Demo background job status and timeout state. |

This guide describes the demo service only. It does not implement the application.

## 10. Systemd Unit Template Plan

The following unit examples are templates only. Do not create these files in `/etc/systemd/system` as part of this task.

Future `python-demo-fastapi.service` template:

```ini
[Unit]
Description=RuntimeOps Lab Python Demo FastAPI Service
After=network.target

[Service]
Type=simple
User=runtimeops-lab
WorkingDirectory=/opt/runtimeops-lab/python-demo
EnvironmentFile=-/opt/runtimeops-lab/python-demo/runtimeops-lab.env
ExecStart=/opt/runtimeops-lab/python-demo/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8101
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Future `dotnet-demo-api.service` template:

```ini
[Unit]
Description=RuntimeOps Lab .NET Demo API Service
After=network.target

[Service]
Type=simple
User=runtimeops-lab
WorkingDirectory=/opt/runtimeops-lab/dotnet-demo/src
EnvironmentFile=-/opt/runtimeops-lab/dotnet-demo/runtimeops-lab.env
ExecStart=/usr/bin/dotnet /opt/runtimeops-lab/dotnet-demo/src/DotnetDemoApi.dll --urls http://127.0.0.1:8102
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Template safety notes:

* Use a non-root lab service user.
* Bind demo services to localhost by default.
* Use demo-only environment files.
* Do not store secrets in environment files.
* Do not point these services at production systems.

## 11. Evidence Summary Plan

Safe evidence summary JSON should use this shape:

```json
{
  "evidence_ref": "rtops-lab-example-001",
  "runtime_family": "python",
  "scenario_id": "PY-LAB-001",
  "service_name": "python-demo-fastapi",
  "diagnosis_type": "slow_endpoint",
  "captured_at": "2026-06-03T00:00:00Z",
  "metric_summary": {},
  "duration_summary": "Controlled lab capture window.",
  "hotspot_summary": "No raw profile exposed.",
  "before_summary": "Baseline summary only.",
  "after_summary": "Post-symptom summary only.",
  "raw_output_exposed": false,
  "raw_dump_exposed": false,
  "raw_trace_exposed": false,
  "safety_notes": "Safe summary only; no raw command output, raw dump, or raw trace stored."
}
```

Required fields:

* `evidence_ref`
* `runtime_family`
* `scenario_id`
* `service_name`
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

## 12. Lab Validation Checklist

Future validation checklist:

* VM isolated.
* No production data.
* Demo services only.
* Python demo service reachable locally.
* .NET demo service reachable locally.
* Controlled symptoms reproducible.
* Safe evidence summaries generated.
* Raw dump / trace / command output excluded.
* Evidence can map to RuntimeOps fixture schema.

## 13. Rollback / Cleanup Plan

Future cleanup steps:

* Stop demo services.
* Remove lab systemd units.
* Remove lab directories.
* Remove .NET global tools if needed.
* Confirm no production service affected.
* Preserve only sanitized reports if needed.

Cleanup must remain limited to the isolated lab VM and must not target the production ENYRAX host.

## 14. Known Limitations

* Guide only.
* No VM provisioning.
* No package installation.
* No demo app implementation.
* No collector implementation.
* No production validation.
* No live runtime evidence yet.

## 15. Recommended Next Task

Task #322: RuntimeOps Python Demo Service Design
