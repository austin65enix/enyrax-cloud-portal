# 271ops Product Concept Design

ISO27001 readiness and security governance preparation module for ENYRAX

## Overview

271ops is the ISO27001 readiness and security governance preparation module in ENYRAX. It helps organizations collect, organize, and review security governance evidence before or during ISMS preparation, without claiming to replace formal consulting, certification, or audit processes.

271ops 是 ENYRAX 裡的 ISO27001 readiness 與資安治理準備模組。它協助企業在申辦或導入 ISMS 前後，收集、整理與檢視資安治理證據，但不宣稱取代正式顧問、驗證或稽核流程。

* 271ops 不是 ISO27001 認證工具。
* 271ops 不是法律或稽核保證。
* 271ops 不是取代顧問。
* 271ops 是申辦前準備、制度落地、證據整理與治理追蹤工具。
* 271ops 的價值在於把分散在 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps、Server_AgentOps、Audit / Status 的紀錄整理成資安治理證據層。

## Product Positioning

271ops 是 ENYRAX 的 ISO27001 準備與資安治理落地模組，協助企業把日常維運、事件處理、權限管理、備份驗證與 AI Agent 治理轉換成可追蹤、可審核、可改善的治理證據。

271ops is the ISO27001 readiness and security governance module in ENYRAX, helping organizations turn daily operations, incident handling, access management, backup verification, and AI Agent governance into traceable, reviewable, and improvable governance evidence.

Short version:

```text
271ops turns daily IT operations into security governance evidence.
```

中文短版：

```text
271ops 把日常 IT 維運轉成資安治理證據。
```

## Naming Rationale

The previous display style `271Ops` is treated as a legacy spelling. The primary UI brand is `271ops`.

`271Ops` 視為舊顯示寫法，主要 UI 品牌統一為 `271ops`。`271Ops` 在部分字體中容易被誤讀成 `2710ps`，因此 UI 品牌顯示統一使用小寫 `271ops`。

`271ops` 取自 ISO27001 的語感，但避免直接命名為認證工具。外部展示時應搭配副標，清楚說明用途。`271ops` 有品牌感，但不能讓使用者誤解為正式認證、稽核或顧問服務。

建議英文顯示：

```text
271ops
ISO27001 Readiness & Security Governance
```

建議中文顯示：

```text
271ops
ISO27001 準備與資安治理落地
```

## Problem Statement

企業準備 ISO27001 或 ISMS 時，治理證據通常分散在不同系統。SOC 事件、工單、專案、備份、帳號權限、廠商處理與稽核紀錄常常各自獨立，很多證據仍在 Email、Teams、Excel、截圖、口頭紀錄或個人電腦裡。

常見落差包括：

* 事件處理有做，但不一定能證明。
* 權限有回收，但不一定有完整紀錄。
* 備份有跑，但還原演練與驗證證據不一定整理好。
* 廠商協作、維護時段、預算或核准流程有執行，但責任邊界不明確。
* AI Agent 協作開始出現，但治理紀錄不明確。

271ops 要解決的不是「企業完全沒有做資安」，而是「企業做了很多事情，但證據、流程與責任邊界沒有被整理成可稽核的治理紀錄」。

271ops does not assume that organizations have no security practices. It addresses the gap where many security-related activities are performed, but evidence, workflow, and responsibility boundaries are not organized into audit-ready governance records.

## Core Modules

| Module                     | 中文             | Purpose                                                  |
| -------------------------- | ---------------- | -------------------------------------------------------- |
| Governance Overview        | 治理總覽         | Overall readiness, gaps, evidence coverage               |
| Asset Inventory            | 資產盤點         | Servers, systems, services, cloud assets, owners         |
| Account & Access Review    | 帳號與權限覆核   | AD / LDAP / Linux / SaaS account review                  |
| Incident Evidence          | 事件處理證據     | SOC incidents, ServiceOps tickets, remediation proof     |
| Backup & Restore Evidence  | 備份與還原證據   | Backup jobs, restore drill, R2 / local backup evidence   |
| Vendor & Approval Evidence | 廠商與核准證據   | Vendor response, approval, maintenance window, budget    |
| Risk Register              | 風險登錄         | Risk items, owner, impact, mitigation, status            |
| Audit Checklist            | 稽核準備清單     | Readiness checklist and missing evidence                 |
| Policy Mapping             | 政策與控制項對應 | Map evidence to internal policy / control areas          |
| AI Governance Evidence     | AI 治理證據      | AgentOps / Team_AgentOps / Server_AgentOps safe metadata |

## Integration With Existing ENYRAX Modules

| Source Module   | 271ops Usage                                                    |
| --------------- | --------------------------------------------------------------- |
| SOC             | Security incident evidence, severity, response status           |
| ServiceOps      | Ticket handling evidence, worklog, closure record               |
| ProjectOps      | Security improvement projects and remediation roadmap           |
| Plan_ServiceOPS | Attention reasons, blocked-flow explanations, pending approvals |
| AgentOps        | AI Agent execution governance and snapshot evidence             |
| Team_AgentOps   | Human-AI team review and contribution evidence                  |
| Server_AgentOps | Backup, deployment, parser, snapshot, release-check evidence    |
| Audit Logs      | Operation history and change trace                              |
| Status          | Platform health and availability reference                      |
| Sync Gateway    | External data ingestion / integration evidence                  |

271ops 不取代上述模組，而是把上述模組產生的紀錄整理成治理證據視角。

271ops does not replace these modules. It reorganizes their records into a security governance evidence view.

## Dashboard Concept

### KPI Cards

| KPI                       | Meaning                                             |
| ------------------------- | --------------------------------------------------- |
| Readiness Score           | Overall readiness estimate                          |
| Open Risks                | Active risk items                                   |
| Missing Evidence          | Required evidence not yet attached                  |
| Access Review Pending     | Accounts or permissions awaiting review             |
| Backup Evidence           | Backup / restore evidence coverage                  |
| Incident Evidence         | Incident remediation evidence coverage              |
| Vendor / Approval Pending | Waiting approval, vendor, budget, or schedule items |
| AI Governance Coverage    | AgentOps safe metadata / review coverage            |

### Main Sections

1. Readiness Overview
2. Evidence Coverage Matrix
3. Open Risk Register
4. Account & Access Review
5. Incident / Ticket Evidence
6. Backup / Restore Evidence
7. Vendor / Approval Queue
8. AI Governance Evidence
9. Audit Checklist
10. Missing Evidence List

## Readiness Score Concept

Readiness Score 是 demo / internal estimate，不是正式認證分數，也不代表通過 ISO27001。它可以用於粗略判斷準備程度，協助企業知道哪些證據、風險與流程還需要補齊。正式稽核仍需顧問、稽核員與組織正式流程。

概念公式：

```text
Readiness Score = evidence coverage + risk closure + access review completion + backup verification + incident closure evidence + audit trail coverage
```

Readiness Score 只是準備度估算，不能代表認證結果。它用來協助企業知道哪些證據、風險與流程還需要補齊。

## Data Model Concept

以下資料表僅為概念設計，不代表本任務會建立 DB migration、API 或正式 schema。

### `ops271_controls`

| Field          | Meaning                                                      |
| -------------- | ------------------------------------------------------------ |
| control_uid    | Unique control ID                                            |
| control_group  | Policy / access / incident / backup / vendor / AI governance |
| title          | Control title                                                |
| description    | Control description                                          |
| owner          | Control owner                                                |
| status         | ready / partial / missing / not_applicable                   |
| evidence_count | Linked evidence count                                        |
| risk_level     | low / medium / high / critical                               |

### `ops271_evidence`

| Field         | Meaning                                                                |
| ------------- | ---------------------------------------------------------------------- |
| evidence_uid  | Unique evidence ID                                                     |
| source_module | SOC / ServiceOps / ProjectOps / AgentOps / Server_AgentOps / Audit     |
| source_ref    | Safe reference to original record                                      |
| evidence_type | incident / ticket / backup / access_review / approval / policy / audit |
| title         | Evidence title                                                         |
| summary       | Safe short summary                                                     |
| owner         | Evidence owner                                                         |
| collected_at  | Timestamp                                                              |
| review_status | pending / accepted / rejected / needs_update                           |

### `ops271_risks`

| Field           | Meaning                                                     |
| --------------- | ----------------------------------------------------------- |
| risk_uid        | Unique risk ID                                              |
| title           | Risk title                                                  |
| category        | access / incident / backup / vendor / system / AI / process |
| impact          | low / medium / high / critical                              |
| likelihood      | low / medium / high                                         |
| treatment       | accept / mitigate / transfer / avoid                        |
| owner           | Risk owner                                                  |
| status          | open / in_progress / mitigated / accepted / closed          |
| linked_evidence | Evidence references                                         |

### `ops271_access_reviews`

| Field         | Meaning                                                  |
| ------------- | -------------------------------------------------------- |
| review_uid    | Unique access review ID                                  |
| account_ref   | Safe account reference                                   |
| system        | AD / LDAP / Linux / SaaS / Database                      |
| owner         | Account owner or reviewer                                |
| status        | pending / approved / revoke_needed / revoked / exception |
| last_login_at | Optional timestamp                                       |
| evidence_ref  | Evidence reference                                       |

## Allowed Values

### control_status

```text
ready
partial
missing
not_applicable
```

### evidence_type

```text
incident
ticket
backup
restore_drill
access_review
approval
vendor_response
policy
audit
ai_governance
```

### review_status

```text
pending
accepted
rejected
needs_update
```

### risk_status

```text
open
in_progress
mitigated
accepted
closed
```

### risk_category

```text
access
incident
backup
vendor
system
ai
process
compliance
```

## Evidence Examples

### Incident Evidence

```json
{
  "evidence_uid": "271-evidence-20260602-001",
  "source_module": "SOC",
  "source_ref": "SOC-INC-20260602-001",
  "evidence_type": "incident",
  "title": "Suspicious SSH brute force remediation",
  "summary": "Incident reviewed, ticket created, remediation tracked, verification evidence attached.",
  "review_status": "accepted"
}
```

### Backup Evidence

```json
{
  "evidence_uid": "271-evidence-20260602-002",
  "source_module": "Server_AgentOps",
  "source_ref": "srv-agent-run-20260602-003",
  "evidence_type": "backup",
  "title": "PostgreSQL backup uploaded to R2",
  "summary": "Backup job completed and upload destination verified without exposing credentials.",
  "review_status": "accepted"
}
```

### Access Review Evidence

```json
{
  "evidence_uid": "271-evidence-20260602-003",
  "source_module": "271ops",
  "source_ref": "access-review-20260602-001",
  "evidence_type": "access_review",
  "title": "Linux sudo group review",
  "summary": "Privileged account list reviewed. One account marked for revocation.",
  "review_status": "pending"
}
```

### AI Governance Evidence

```json
{
  "evidence_uid": "271-evidence-20260602-004",
  "source_module": "Team_AgentOps",
  "source_ref": "tagent-run-20260601-001",
  "evidence_type": "ai_governance",
  "title": "AI-assisted release note reviewed by human",
  "summary": "Agent output linked to project contribution and reviewed before release packaging.",
  "review_status": "accepted"
}
```

## MVP Scope

第一版 MVP：

* static dashboard prototype
* readiness score mock
* evidence coverage matrix
* risk register demo data
* access review demo data
* backup evidence demo data
* incident evidence demo data
* AI governance evidence demo data
* audit checklist
* missing evidence list
* interview demo talk track

不包含：

* formal ISO certification workflow
* legal guarantee
* consultant replacement
* production DB migration
* live AD / LDAP integration
* live SIEM integration
* automatic control mapping engine
* document management system
* e-signature workflow

## Safety and Compliance Boundary

* 271ops supports readiness preparation, not certification guarantee.
* It should not claim ISO27001 certification by itself.
* It should not store secrets, passwords, private keys, raw logs, or sensitive personal data by default.
* Evidence should use safe references and short summaries.
* Access review data must be handled carefully.
* AI governance evidence must not contain raw prompt / response unless explicitly approved by policy.
* Formal compliance decisions remain with management, auditors, and certified professionals.

271ops 的定位是準備度、證據整理與治理追蹤，不是正式認證保證。正式合規判斷仍需要管理階層、稽核員、顧問與組織正式流程。

## Dashboard Copy

中文短句：

```text
271ops 協助企業把日常維運、資安事件、權限覆核、備份驗證與 AI Agent 治理整理成可稽核的資安治理證據。
```

英文短句：

```text
271ops helps organizations turn daily operations, security incidents, access reviews, backup verification, and AI Agent governance into audit-ready security governance evidence.
```

Card subtitle：

```text
ISO27001 Readiness & Security Governance
```

中文：

```text
ISO27001 準備與資安治理落地
```

## Interview Talk Track

### 中文

271ops 是我在 ENYRAX 裡規劃的資安治理與 ISO27001 readiness 模組。很多企業不是完全沒有做資安，而是事件處理、帳號權限、備份、廠商處理、核准流程與 AI 使用紀錄分散在不同地方，等到要申辦或稽核時，才發現證據不好整理。

所以 271ops 的定位不是取代顧問或認證流程，而是把 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps、Server_AgentOps、Audit Logs 這些模組產生的紀錄，整理成治理證據視角。它可以協助企業知道目前哪些證據已有、哪些缺漏、哪些風險還沒關閉，以及哪些權限或備份項目需要覆核。

### English

271ops is the security governance and ISO27001 readiness module I plan inside ENYRAX. Many companies do have security practices, but incident handling, access control, backups, vendor responses, approvals, and AI usage records are often scattered across different places. When they start preparing for certification or audit, the evidence becomes hard to organize.

So 271ops does not replace consultants or certification processes. It reorganizes records from SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Server_AgentOps, and Audit Logs into a governance evidence view. It helps organizations understand what evidence exists, what is missing, which risks remain open, and which access or backup items need review.

## Future Tasks

* Task #196：271ops Static Dashboard Prototype
* Task #197：271ops Visual QA and Product Copy Review
* Task #199：271ops Demo Data Fixture Design
* Task #200：271ops Read-only Fixture API Prototype
* Task #201：271ops Frontend API Switch with Fallback
* Task #202：271ops Visual QA
* Task #203：271ops Release Note
* Task #204：271ops Release Tag


## Task #196 271ops Static Dashboard Prototype

* Task #196 adds `/271ops/` static dashboard prototype.
* UI brand display is normalized to lowercase `271ops`.
* The page presents ISO27001 readiness, governance evidence, risk register, access review, backup evidence, incident evidence, and AI governance evidence.
* It updates Portal homepage entry.
* It remains static frontend only.
* It does not claim ISO27001 certification or audit approval.
* No backend, DB, API, fixtures, release, or deployment changes were made.

## Task #197 271ops Visual QA and Product Copy Review

* Task #197 validates `/271ops/` visual layout, homepage entry, lowercase naming, ISO27001 readiness boundary, safety boundary, responsive behavior, and static-only behavior.
* Primary UI brand remains lowercase `271ops`.
* The dashboard does not claim ISO27001 certification, legal assurance, or audit approval.
* No backend, DB, API, fixtures, release, or deployment changes were made.
* It prepares Task #199 demo data fixture design.

## Task #199 271ops Demo Data Fixture Design

* Task #199 adds safe demo fixtures under `data/271ops/`.
* Fixtures cover readiness summary, evidence coverage, risk register, access reviews, evidence queue, AI governance evidence, and audit checklist.
* Fixtures use safe references and short summaries only.
* Fixtures do not represent ISO27001 certification status.
* Fixtures do not store secrets, raw logs, raw prompt / response, credentials, private keys, full home paths, or sensitive personal data.
* This prepares Task #200 read-only fixture API prototype.
* No frontend, backend, DB, API, release, or deployment changes were made.


## Task #200 271ops Read-only Fixture API Prototype

* Task #200 adds read-only fixture API endpoints for 271ops.
* API reads `data/271ops/` safe demo fixtures.
* It adds a dashboard aggregation endpoint and individual fixture endpoints.
* Product display name remains lowercase `271ops`.
* Responses return safe references and short summaries only.
* It does not add DB, migration, write API, production auth, release, or deployment changes.
* It does not claim ISO27001 certification, legal assurance, or audit approval.
* It prepares a future frontend API switch with fallback.


## Task #201 271ops Frontend API Switch with Demo Fallback

* Task #201 upgrades `/271ops/` from a static dashboard to an API-backed read-only dashboard.
* Frontend fetches only `GET /api/271ops/dashboard` and renders KPI cards, evidence coverage, risk register, access reviews, evidence queue, AI governance evidence, audit checklist, and the safety / compliance boundary from active data.
* Valid API responses display `API DATA / API 資料`.
* HTTP errors, invalid JSON, or invalid schema use local demo fallback and display `DEMO FALLBACK / DEMO 備援` with a fallback note.
* Schema validation requires `product === "271ops"`, `mode === "read_only"`, `certification_claim === false`, numeric `summary.readiness_score`, and all six dashboard arrays.
* Boundary remains readiness preparation only: no ISO27001 certification claim, no legal assurance, no audit approval, and safe references only.
* It adds no mutation API, create / update / approve / reject action, upload, localStorage write, backend change, DB change, script change, release, or deployment change.
* This prepares Task #202 271ops Visual QA.


## Task #202 271ops API-backed Dashboard Visual QA

* Task #202 validates `/271ops/` after the frontend API switch.
* API DATA renders from `GET /api/271ops/dashboard`.
* DEMO FALLBACK renders on fetch, HTTP, JSON, or schema failures.
* Responsive layout, copy boundary, certification boundary, accessibility, and no-mutation behavior were checked.
* Dashboard remains read-only and does not claim ISO27001 certification, legal assurance, or audit approval.
* No backend, DB, API, fixtures, release, or deployment changes were made.
* Prepares Task #203 release note.


## Task #203 271ops API-backed Dashboard Release Note

* Task #203 packages Tasks #195-#202 as `v0.6.30-271ops-api-backed-dashboard`.
* Release covers product concept, static dashboard, visual QA, demo fixtures, read-only fixture API, frontend API switch, fallback behavior, and API-backed visual QA.
* 271ops remains lowercase in UI.
* It remains fixture-backed and read-only.
* It does not claim ISO27001 certification, legal assurance, or audit approval.
* No frontend, backend, DB, API, fixtures, deployment, or tag changes were made in this release note task.
* Prepares Task #204 release tag.
