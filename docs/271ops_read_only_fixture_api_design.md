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
