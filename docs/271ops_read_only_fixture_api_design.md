# 271ops Read-only Fixture API Design

## Task #200 271ops Read-only Fixture API Prototype

Task #200 adds a fixture-backed, read-only API prototype for lowercase `271ops`. The API reads safe demo fixtures from `data/271ops/` and prepares a future frontend API switch with fallback. It does not add DB, migration, write API, production auth, release, or deployment changes.

## Endpoints

* `GET /api/271ops/dashboard`
* `GET /api/271ops/readiness-summary`
* `GET /api/271ops/evidence-coverage`
* `GET /api/271ops/risk-register`
* `GET /api/271ops/access-reviews`
* `GET /api/271ops/evidence-queue`
* `GET /api/271ops/ai-governance-evidence`
* `GET /api/271ops/audit-checklist`

## Response Shape

Every endpoint returns shared metadata: `source: fixture`, `mode: read_only`, `product: 271ops`, `display_name: 271ops`, `production_data: false`, `certification_claim: false`, and `warnings`. The dashboard aggregates the readiness summary and all fixture record lists, and adds `generated_at`, summary metrics, and a boundary object. Individual list endpoints return `records`.

If an allowlisted fixture is missing, unreadable, invalid JSON, or structurally invalid, the endpoint returns an empty safe response with a `fixture_unavailable` warning instead of crashing. The loader maps fixed internal keys to fixed filenames and does not accept arbitrary paths or filenames.

## Exact Filters

The prototype supports exact-match filters only. It does not perform fuzzy search, full-text search, or content inference.

* `risk-register`: `status`, `risk_level`, `category`
* `access-reviews`: `status`, `system`, `evidence_status`
* `evidence-queue`: `review_status`, `evidence_type`, `source_module`
* `audit-checklist`: `status`, `control_area`

## Safety Boundary

271ops is for ISO27001 readiness preparation and security governance evidence organization only. It does not represent ISO27001 certification status, provide legal assurance, indicate audit approval, or replace consultants, auditors, certification bodies, or formal compliance decisions.

The API returns safe references and short summaries only. It does not store or return secrets, raw logs, raw prompt / response, raw session, credentials, private keys, or sensitive personal data.

## Checks

* Run `python3 -m py_compile backend/main.py`.
* Confirm dashboard metadata, metrics, record counts, boundary, and empty warnings.
* Confirm individual endpoint record counts and exact-match filter behavior.
* Run the Task #200 grep, safety scan, and `git diff --check` commands.


## Task #203 271ops API-backed Dashboard Release Note

* Task #203 packages Tasks #195-#202 as `v0.6.30-271ops-api-backed-dashboard`.
* Release covers product concept, static dashboard, visual QA, demo fixtures, read-only fixture API, frontend API switch, fallback behavior, and API-backed visual QA.
* 271ops remains lowercase in UI.
* It remains fixture-backed and read-only.
* It does not claim ISO27001 certification, legal assurance, or audit approval.
* No frontend, backend, DB, API, fixtures, deployment, or tag changes were made in this release note task.
* Prepares Task #204 release tag.


## Task #205 Evidence Collection Queue and Audit Calendar Design

* Task #205 defines Collection Queue, Evidence Queue, Audit Calendar, and Monthly Control Tasks for 271ops.
* Collection Queue tracks missing or pending evidence collection work.
* Evidence Queue tracks collected evidence waiting for review or acceptance.
* Audit Calendar organizes monthly, quarterly, semiannual, and annual governance tasks.
* The design supports continuous ISO27001 readiness preparation without claiming certification, legal assurance, or audit approval.
* No frontend, backend, DB, API, fixtures, release, deployment, or tag changes were made.
* It prepares Task #206 and Task #207 demo fixture design.
