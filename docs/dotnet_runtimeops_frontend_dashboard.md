# .NET_RuntimeOps Frontend Dashboard

## Task summary

Task #313 adds the RuntimeOps frontend page with .NET_RuntimeOps dashboard coverage. Because no `runtimeops/` page existed, this task creates `runtimeops/index.html` and includes both Python_RuntimeOps and .NET_RuntimeOps sections.

No DB schema, write API, production config, nginx, cron, systemd, Windows / IIS / SQL Server connection, or production diagnostic command was added.

## Frontend page updated

* Added `runtimeops/index.html`

The page keeps Python_RuntimeOps regression coverage and adds a separate .NET_RuntimeOps section below it.

## APIs consumed

.NET_RuntimeOps uses GET-only fetches:

* `GET /api/runtimeops/dotnet/dashboard`
* `GET /api/runtimeops/dotnet/services`
* `GET /api/runtimeops/dotnet/diagnosis-runs`
* `GET /api/runtimeops/dotnet/slow-endpoints`
* `GET /api/runtimeops/dotnet/app-pools`
* `GET /api/runtimeops/dotnet/windows-services`
* `GET /api/runtimeops/dotnet/counter-evidence`
* `GET /api/runtimeops/dotnet/trace-evidence`
* `GET /api/runtimeops/dotnet/dump-evidence`
* `GET /api/runtimeops/dotnet/rca-findings`
* `GET /api/runtimeops/dotnet/verification-results`

Python_RuntimeOps regression fetches remain GET-only.

## API DATA / DEMO FALLBACK behavior

API success badge:

```text
DOTNET RUNTIMEOPS API DATA / .NET RuntimeOps API 資料
```

Fallback badge:

```text
DOTNET RUNTIMEOPS DEMO FALLBACK / .NET RuntimeOps DEMO 備援
```

The frontend falls back to local demo data when APIs fail, return invalid schema, or return empty required records. The UI remains nonblank and should not crash.

## UI coverage

The page includes:

* .NET RuntimeOps Summary Cards
* Diagnosis Breakdown
* Risk Breakdown
* Service Health
* Top Attention Items
* Recent Diagnosis Runs
* Slow Endpoint Preview
* IIS / App Pool Preview
* Windows Service Preview
* Counter / Trace / Dump Evidence Preview
* RCA Findings
* Verification Results
* Safety Boundary

## Safety boundary

The .NET section visibly states:

* Read-only diagnostics first
* No IIS App Pool recycle action
* No Windows Service restart action
* No kill process action
* No config change action
* No database write action
* No production diagnostic command execution
* No Windows / IIS / SQL Server connection
* No raw command output
* No raw dump content
* No raw trace content
* No raw counter output
* No raw Event Log full content
* No raw SQL with sensitive values
* No raw environment variables
* No password / credential / API key / private key
* Safe metadata only

## No-mutation guarantee

The page does not add recycle, restart, kill, run diagnostic, collect dump, upload, edit, or delete controls. It does not write `localStorage` or `sessionStorage`, and all fetch calls use GET.

## Validation performed

* `node --check` was not applicable to raw HTML; syntax will be covered in visual QA DOM harness.
* Static grep confirmed API DATA / DEMO FALLBACK text exists.
* Static grep confirmed `/api/runtimeops/dotnet` fetch paths exist.
* Static grep confirmed Python_RuntimeOps API/fallback text remains present.
* `git diff --check` passed.

## Limitations

* Frontend is fixture/API-backed and read-only.
* No live diagnostic collector.
* No IIS / Windows Service / SQL Server integration.
* No production command execution.
* Browser screenshot QA is deferred to Task #314.

## Recommended next task

Task #314: .NET_RuntimeOps Frontend Visual QA
