# 271ops API-backed Dashboard Release Note

Version: `v0.6.30-271ops-api-backed-dashboard`

ISO27001 readiness dashboard with safe fixture API, demo fallback, and certification boundary

ISO27001 準備度看板，支援 safe fixture API、Demo 備援與認證邊界聲明。

## Overview

271ops API-backed Dashboard upgrades the 271ops static readiness dashboard into a fixture-backed, read-only API dashboard. It presents ISO27001 readiness, governance evidence, risk register, access review, backup evidence, incident evidence, AI governance evidence, and audit checklist data while keeping a clear boundary that it does not claim certification, legal assurance, or audit approval.

271ops API-backed Dashboard 將 271ops static readiness dashboard 升級為 fixture-backed、read-only API dashboard。它呈現 ISO27001 準備度、治理證據、風險登錄、權限覆核、備份證據、事件證據、AI 治理證據與稽核清單，同時清楚保留不宣稱認證、法律保證或稽核通過的邊界。

* Product display name is normalized to lowercase `271ops`.
* `271Ops` is a legacy spelling and is not the primary UI brand.
* 271ops is a readiness / governance preparation module.
* 271ops is not an ISO27001 certification tool.
* 271ops does not replace consultants, auditors, certification bodies, or formal compliance decisions.

## Completed Scope

* Task #195：271ops Product Concept Design
* Task #196：271ops Static Dashboard Prototype
* Task #197：271ops Visual QA and Product Copy Review
* Task #198：AgentOps Snapshot Generated Data Review for 2026-06-02
* Task #199：271ops Demo Data Fixture Design
* Task #200：271ops Read-only Fixture API Prototype
* Task #201：271ops Frontend API Switch with Demo Fallback
* Task #202：271ops API-backed Dashboard Visual QA
* Task #203：271ops API-backed Dashboard Release Note

## Key Features

### 1. Lowercase 271ops Naming

* Primary UI brand is lowercase `271ops`.
* This avoids visual confusion where `271Ops` can be misread as `2710ps`.
* Route is `/271ops/`.
* Product subtitle is `ISO27001 Readiness & Security Governance`.
* 中文副標是 `ISO27001 準備與資安治理落地`。

### 2. Static Dashboard Prototype

Dashboard sections:

* Readiness Overview
* Evidence Coverage Matrix
* Open Risk Register
* Access Review Queue
* Evidence Queue
* AI Governance Evidence
* Audit Checklist
* Evidence Sources
* Safety / Compliance Boundary

### 3. Safe Demo Fixtures

* `data/271ops/demo_readiness_summary.json`
* `data/271ops/demo_evidence_coverage.json`
* `data/271ops/demo_risk_register.json`
* `data/271ops/demo_access_reviews.json`
* `data/271ops/demo_evidence_queue.json`
* `data/271ops/demo_ai_governance_evidence.json`
* `data/271ops/demo_audit_checklist.json`

Fixtures use safe references and short summaries only. They do not represent ISO27001 certification status. They do not store secrets, raw logs, raw prompt / response, credentials, private keys, full home paths, or sensitive personal data.

### 4. Read-only Fixture API

```text
GET /api/271ops/dashboard
GET /api/271ops/readiness-summary
GET /api/271ops/evidence-coverage
GET /api/271ops/risk-register
GET /api/271ops/access-reviews
GET /api/271ops/evidence-queue
GET /api/271ops/ai-governance-evidence
GET /api/271ops/audit-checklist
```

Shared response metadata:

* `source = fixture`
* `mode = read_only`
* `product = 271ops`
* `display_name = 271ops`
* `production_data = false`
* `certification_claim = false`

### 5. Frontend API DATA / DEMO FALLBACK

* `/271ops/` first fetches `GET /api/271ops/dashboard`.
* API success renders `API DATA / API 資料`.
* Fetch error, HTTP non-200, invalid JSON, or invalid schema renders `DEMO FALLBACK / DEMO 備援`.
* Fallback keeps the dashboard visible and avoids a blank page.
* The boundary remains visible in both modes.

### 6. Visual QA

* API DATA QA passed.
* DEMO FALLBACK QA passed.
* Responsive QA passed via static HTML/CSS checks and JS harness.
* Accessibility QA passed.
* No API mutation QA passed.
* No blocking visual, copy, or API-backed rendering issues found.

## Current Verification

Verified against the public portal during Task #203:

* `/271ops/` returns HTTP 200.
* `source = fixture`
* `mode = read_only`
* `product = 271ops`
* `display_name = 271ops`
* `production_data = false`
* `certification_claim = false`
* `readiness_score = 68`
* `risks = 4`
* `evidence = 9`
* `access_reviews = 4`
* `ai_evidence = 4`
* `checklist = 6`
* `warnings = []`
* High risk filter returns `2` records with `risk_level = high`.

## Product Value

### For IT Managers

* Gives a governance overview of readiness, evidence gaps, risks, access reviews, backup evidence, incident evidence, and AI governance.
* Helps turn daily operations into security governance evidence.
* Provides a readiness cockpit before formal ISO27001 / ISMS preparation.

### For Security / Governance Teams

* Shows missing evidence, open risks, and access review status.
* Connects SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Server_AgentOps, Audit Logs, and Status into a governance evidence view.
* Helps prepare evidence before consultant or audit review.

### For Engineers / Operators

* Makes operational work visible as evidence.
* Shows that incident handling, remediation tickets, backup verification, deployment checks, and AI review records contribute to governance readiness.
* Protects operators by using safe references and short summaries rather than raw logs or sensitive content.

### For Interviews / Demo

* Demonstrates that ENYRAX is not only a ticketing or dashboard system.
* Shows a higher-level governance layer over daily IT operations.
* Connects operations, security, audit, AI governance, and readiness preparation into one story.

## Before / After

| Before | After |
| --- | --- |
| Static 271ops dashboard only | API-backed dashboard with demo fallback |
| Hardcoded data only | Safe JSON fixtures + read-only API |
| Readiness concept only | Queryable readiness summary, risks, evidence, access reviews, AI governance, audit checklist |
| No fallback mode indicator | API DATA / DEMO FALLBACK mode badge |
| Potential ambiguity around ISO27001 | Clear no certification / no legal assurance / no audit approval boundary |
| Evidence in narrative form | Evidence organized as safe references and short summaries |

這一版的重點不是宣稱系統能讓企業通過 ISO27001，而是把日常 IT 維運與資安治理活動整理成可檢視、可追蹤、可補強的 readiness evidence。

## Scope Boundary

This release does not include:

* no production DB schema
* no DB migration
* no write API
* no live AD / LDAP integration
* no live SIEM integration
* no automatic ISO27001 control mapping engine
* no consultant replacement
* no certification guarantee
* no legal assurance
* no audit approval
* no e-signature workflow
* no document management system
* no release tag yet
* no deployment config change

This release is a fixture-backed demo dashboard. It is suitable for product demo and interview storytelling. Formal compliance decisions remain with management, consultants, auditors, certification bodies, and the organization's official process.

## Safety Boundary

* safe references only
* short summaries only
* no secrets
* no raw logs by default
* no raw prompt / response
* no raw session
* no credentials
* no private keys
* no `DATABASE_URL`
* no rclone config
* no sensitive personal data
* token / cost / readiness values are operational or demo estimates only
* `certification_claim = false`
* `production_data = false`

271ops 預設只使用 safe references 與短摘要，不保存 secrets、raw logs、raw prompt / response、credentials、private keys 或敏感個資。Readiness Score 是 demo estimate，不是認證分數。

## Known Limitations

* Fixture-backed demo only.
* No production DB.
* No live identity integration.
* No live SIEM / Wazuh / ServiceOps production evidence ingestion yet.
* Demo data is curated and not production compliance evidence.
* Readiness Score is a demo estimate.
* API has read-only fixture filtering only.
* Frontend fallback uses local demo data.
* Browser screenshot tooling was not available in the environment; QA used static responsive checks and JS harness.

## Recommended Next Steps

* Task #204：271ops API-backed Dashboard Release Tag
* Task #205：271ops Screenshot Baseline
* Task #206：271ops Role-based Governance View Design
* Task #207：271ops Evidence Control Mapping Design
* Task #208：271ops Access Review Workflow Design
* Task #209：271ops Backup / Restore Evidence Integration Design
* Task #210：271ops Release Package for Interview Demo


## Task #205 Evidence Collection Queue and Audit Calendar Design

* Task #205 defines Collection Queue, Evidence Queue, Audit Calendar, and Monthly Control Tasks for 271ops.
* Collection Queue tracks missing or pending evidence collection work.
* Evidence Queue tracks collected evidence waiting for review or acceptance.
* Audit Calendar organizes monthly, quarterly, semiannual, and annual governance tasks.
* The design supports continuous ISO27001 readiness preparation without claiming certification, legal assurance, or audit approval.
* No frontend, backend, DB, API, fixtures, release, deployment, or tag changes were made.
* It prepares Task #206 and Task #207 demo fixture design.
