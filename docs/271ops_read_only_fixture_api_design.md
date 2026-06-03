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


## Task #206 Collection Queue Demo Data Fixture Design

* Task #206 adds safe demo fixtures for Collection Queue, Audit Calendar Tasks, and Evidence Requirements.
* Collection Queue tracks missing or pending evidence collection work.
* Audit Calendar Tasks model monthly, quarterly, semiannual, and annual governance tasks.
* Evidence Requirements define what proof is expected, how often, and which source modules are acceptable.
* Fixtures use safe references and role labels only.
* Fixtures do not contain real personal data, secrets, raw logs, raw prompt / response, raw command output, credentials, private keys, full home paths, or sensitive source content.
* This prepares Task #207 read-only API prototype.
* No frontend, backend, DB, API, release, deployment, or tag changes were made.


## Task #207 Account Governance and BPM Permission Evidence Design

* Task #207 defines Account Governance, Access Review Queue, BPM Permission Request Evidence, and permission lifecycle mapping for 271ops.
* It connects BPM access request evidence, ServiceOps provisioning tickets, IAM / AD / LDAP / SaaS account state, access review decisions, revocation evidence, and Audit Logs.
* It treats BPM forms as safe evidence references, not raw form storage.
* It does not implement live BPM, IAM, AD, LDAP, or SaaS integration.
* It does not add write API or provisioning actions.
* It prepares Task #208 demo fixture design and Task #210 Access Review Queue API design.
* No frontend, backend, DB, API, fixtures, release, deployment, or tag changes were made.


## Task #208 Account Governance Demo Data Fixture Design

* Task #208 adds safe demo fixtures for BPM Permission Requests, Access Review Items, and Access Lifecycle Events.
* BPM Permission Request fixtures model access request and approval evidence using safe references only.
* Access Review Items model periodic access review queue records.
* Access Lifecycle Events model request, approval, provisioning, review, exception, and revocation events.
* Fixtures use safe aliases, role labels, and short summaries only.
* Fixtures do not contain real BPM form content, attachments, raw logs, credentials, passwords, API keys, private keys, tokens, SSH keys, raw prompt / response, full home paths, or sensitive personal data.
* This prepares Account Governance read-only API design.
* No frontend, backend, DB, API, release, deployment, or tag changes were made.


## Task #209 Collection Queue Read-only API Prototype

* Task #209 adds read-only fixture API endpoints for Collection Queue, Audit Calendar Tasks, and Evidence Requirements.
* API reads safe demo fixtures from `data/271ops/`.
* Endpoints return shared metadata, records, summaries, and warnings.
* Exact-match filters are supported for status, control area, attention reason, frequency, owner, reviewer, period, expected evidence type, and minimum review status.
* APIs are fixture-backed, read-only, and do not represent ISO27001 certification, legal assurance, or audit approval.
* No frontend, DB, fixture, release, deployment, or tag changes were made.
* It prepares Task #210 Access Review Queue Read-only API Prototype.

## Task #211 Account Governance Frontend Prototype

* Task #211 adds Account Governance frontend sections to `/271ops/`.
* It fetches BPM Permission Requests, Access Review Items, and Access Lifecycle Events from read-only APIs.
* It renders Account Governance API DATA when all three APIs are valid.
* It falls back to local Account Governance demo data when any API fails, returns non-200, invalid JSON, or invalid schema.
* It displays BPM Permission Requests, Access Review Queue, Access Lifecycle Events, BPM / ServiceOps / IAM mapping, KPI cards, warnings, and safety boundary.
* It remains read-only.
* It does not directly change IAM, AD, LDAP, or SaaS permissions.
* It does not store raw BPM forms, raw attachments, credentials, secrets, keys, raw logs, or sensitive personal data.
* No backend, DB, API, fixture, release, deployment, or tag changes were made.
* It prepares Task #212 visual QA and release note preparation.
