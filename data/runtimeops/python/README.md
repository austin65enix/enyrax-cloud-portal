# Python_RuntimeOps Demo Fixtures

## Purpose

These fixtures define safe demo data for Python_RuntimeOps, the first RuntimeOps runtime family. The data demonstrates Python / FastAPI / worker runtime diagnosis, endpoint metrics, worker snapshots, background job evidence, profile evidence, memory evidence, RCA findings, verification results, and dashboard summary.

The first demo target is the ENYRAX FastAPI backend as a self-diagnosis scenario. All records are safe metadata only.

## Fixture files

* `demo_python_runtime_services.json`
* `demo_python_diagnosis_runs.json`
* `demo_python_endpoint_metrics.json`
* `demo_python_worker_snapshots.json`
* `demo_python_background_jobs.json`
* `demo_python_profile_evidence.json`
* `demo_python_memory_evidence.json`
* `demo_python_rca_findings.json`
* `demo_python_verification_results.json`
* `demo_python_runtime_dashboard.json`

## Demo scenarios

1. FastAPI endpoint latency spike for `/api/271ops/identity-lifecycle/dashboard`.
2. Uvicorn worker timeout suspected.
3. Background sync job timeout.
4. Fixture loader warning creates runtime diagnosis.
5. Python memory growth suspected.
6. py-spy profile evidence captured.
7. External API latency causing timeout.
8. Runtime diagnosis creates ServiceOps remediation reference.

## Field contract

Runtime service records include service identity, runtime family, framework, environment, safe host reference, safe systemd unit reference, owner team, status, risk level, and notes.

Diagnosis run records include diagnosis IDs, runtime event IDs, safe service/process/worker/job references, ServiceOps ticket references, diagnosis type, symptom, timestamps, duration, severity, risk level, endpoint reference, metric summary, evidence references, RCA summary, remediation reference, verification status, and notes.

Evidence records store safe summaries and references only. They do not store raw profile content, raw dumps, raw command output, raw environment variables, full stack traces, credentials, or customer raw data.

## Safety boundary

* Safe metadata only.
* Demo data only.
* No production diagnostic command execution.
* No restart action.
* No kill process action.
* No config change action.
* No database write action.
* No raw command output.
* No raw memory dump.
* No raw profile content.
* No raw stack trace.
* No raw environment dump.
* No password / credential / API key / private key / token.
* No customer raw data.
* No full SQL query with sensitive values.

## What is intentionally excluded

These fixtures intentionally exclude real IPs, real host paths, user home paths, environment dumps, raw command output, memory dump content, profile content, stack traces, secrets, customer payloads, and sensitive SQL values.

Allowed examples include:

* `HOST-DEMO-TOKYO-001`
* `PROC-DEMO-UVICORN-001`
* `/api/271ops/identity-lifecycle/dashboard`
* `EVD-RUNTIME-PY-001`
* `SVC-RUNTIME-PY-001`
* `PROF-RUNTIME-PY-001`
* `MEM-RUNTIME-PY-001`

## Future API mapping

Future read-only API mapping:

```text
GET /api/runtimeops/python/services
GET /api/runtimeops/python/diagnosis-runs
GET /api/runtimeops/python/diagnosis-runs/{diagnosis_run_id}
GET /api/runtimeops/python/slow-endpoints
GET /api/runtimeops/python/background-jobs
GET /api/runtimeops/python/profile-evidence
GET /api/runtimeops/python/memory-evidence
GET /api/runtimeops/python/rca-findings
GET /api/runtimeops/python/verification-results
GET /api/runtimeops/python/dashboard
```

## Limitations

* Demo fixture design only.
* No frontend.
* No backend.
* No API implementation.
* No scripts.
* No live diagnostic collector.
* No py-spy integration.
* No tracemalloc integration.
* No production action.

## Recommended next task

Task #303: Python_RuntimeOps Read-only Fixture API Design
