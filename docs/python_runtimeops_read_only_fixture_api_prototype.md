# Python_RuntimeOps Read-only Fixture API Prototype

## Scope

Task #304-R recovers the Python_RuntimeOps read-only fixture API routes in `backend/main.py`.

The prototype is fixture-backed only and reads allowlisted JSON files from `data/runtimeops/python/`:

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

## Implemented GET routes

```text
GET /api/runtimeops/python/services
GET /api/runtimeops/python/diagnosis-runs
GET /api/runtimeops/python/diagnosis-runs/{diagnosis_run_id}
GET /api/runtimeops/python/slow-endpoints
GET /api/runtimeops/python/worker-snapshots
GET /api/runtimeops/python/background-jobs
GET /api/runtimeops/python/profile-evidence
GET /api/runtimeops/python/memory-evidence
GET /api/runtimeops/python/rca-findings
GET /api/runtimeops/python/verification-results
GET /api/runtimeops/python/dashboard
```

No POST, PUT, PATCH, or DELETE routes are implemented for Python_RuntimeOps.

## Response model

List endpoints return safe metadata only:

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

The diagnosis detail endpoint returns a diagnosis-centered safe bundle with related endpoint metrics, worker snapshots, background jobs, profile evidence, memory evidence, RCA findings, verification results, summary counts, warnings, and safety boundary.

The dashboard endpoint returns fixture dashboard sections when available and can safely aggregate from fixtures if the dashboard fixture is unavailable.

## Filtering

* `slow-endpoints` includes records with `p95_ms > 750`, `p99_ms > 1000`, or `timeout_count > 0`.
* `worker-snapshots` includes warning/risk snapshots only.
* `background-jobs` includes `Timeout`, `Delayed`, `Failed`, or `Warning` status records.
* `profile-evidence` excludes records unless `raw_profile_exposed` is `false`.
* `memory-evidence` excludes records unless `raw_dump_exposed` is `false`.

## Safety boundary

The API is read-only and fixture-backed. It does not:

* execute production diagnostic commands
* restart workers or services
* kill processes
* mutate configuration
* write to a database
* expose raw command output
* expose raw memory dumps
* expose raw profile content
* expose raw stack traces by default
* expose raw environment variables
* expose credentials or customer raw data

Only safe metadata records from allowlisted fixtures are returned.

## Fallback behavior

Missing, invalid, or malformed fixtures return safe fallback metadata with warnings. Missing diagnosis run detail returns HTTP 200 with `source=safe_fallback`, `diagnosis_run=null`, empty related arrays, summary counts of zero, and a `diagnosis_run_not_found` warning.

## Validation

Recommended validation commands:

```bash
python3 -m json.tool data/runtimeops/python/demo_python_runtime_dashboard.json >/dev/null
curl -s http://127.0.0.1:<local-port>/api/runtimeops/python/dashboard | jq .
curl -s http://127.0.0.1:<local-port>/api/runtimeops/python/services | jq .
curl -s http://127.0.0.1:<local-port>/api/runtimeops/python/diagnosis-runs | jq .
git diff --check
git status --short
```
