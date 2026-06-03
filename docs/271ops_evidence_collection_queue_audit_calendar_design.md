# 271ops Evidence Collection Queue and Audit Calendar Design

Monthly evidence collection, audit calendar, and recurring control task design for ISO27001 readiness

ISO27001 readiness 的每月證據收集、稽核行事曆與例行查核任務設計

## Overview

This document extends 271ops from a readiness dashboard into an evidence collection and audit calendar workflow. The goal is to help organizations collect governance evidence continuously through monthly control tasks instead of waiting until audit preparation time.

本文件將 271ops 從 readiness dashboard 延伸為證據收集與稽核行事曆工作流。目標是協助企業透過每月例行查核事項持續收集治理證據，而不是等到稽核前才集中補資料。

* 271ops is not only a dashboard. It should also support an ongoing governance rhythm.
* ISO27001 / ISMS practice includes annual calendars and recurring control reviews.
* Collection Queue represents evidence work items that are not yet complete.
* Evidence Queue represents governance evidence that exists and awaits organization or review.
* Audit Calendar represents annual, quarterly, monthly, and recurring governance cadence.
* This design does not claim ISO27001 certification, legal assurance, or audit approval.

## Terminology

| Term | 中文 | Meaning |
| --- | --- | --- |
| Collection Queue | 證據收集佇列 | Items that still need evidence to be collected, attached, verified, or followed up |
| Evidence Queue | 證據整理佇列 | Evidence records that already exist and need review, acceptance, or update |
| Audit Calendar | 稽核年度行事曆 | Annual, quarterly, monthly, or recurring governance schedule |
| Monthly Control Task | 每月例行查核事項 | Recurring task that produces governance evidence |
| Evidence Requirement | 證據需求 | The expected proof, document, ticket, review, screenshot, or system record |
| Evidence Owner | 證據負責人 | Person or role responsible for collecting or confirming evidence |
| Reviewer | 審核者 | Person or role responsible for accepting or rejecting evidence |

Collection Queue 偏「還沒收齊」，Evidence Queue 偏「已形成證據、等待整理或審核」。

Collection Queue focuses on missing or pending evidence work. Evidence Queue focuses on existing evidence records waiting for review or acceptance.

## Collection Queue vs Evidence Queue

| Aspect | Collection Queue | Evidence Queue |
| --- | --- | --- |
| 中文 | 證據收集佇列 | 證據整理佇列 |
| Primary Question | What evidence still needs to be collected? | What evidence has been collected and needs review? |
| Typical Status | pending / collecting / blocked / overdue | pending_review / accepted / needs_update / rejected |
| Owner | Collector / operator / control owner | Reviewer / governance owner |
| Source | Audit calendar, monthly task, missing evidence, risk item | SOC, ServiceOps, BackupOps, AgentOps, Server_AgentOps, uploaded evidence |
| Output | Evidence request or collection task | Accepted evidence record |
| Example | Need March backup restore drill proof | Backup restore drill evidence accepted |

Collection Queue 讓團隊知道「缺什麼證據、誰要補、何時到期」；Evidence Queue 讓治理人員知道「哪些證據已收齊、哪些需要審核或退回更新」。

## Audit Calendar Concept

Audit Calendar should support:

* annual schedule
* quarterly schedule
* monthly recurring tasks
* evidence due dates
* control owner
* reviewer
* evidence requirement
* linked collection queue items
* linked accepted evidence
* overdue status
* reminder concept

| Frequency | Example Control Task |
| --- | --- |
| Monthly | Disabled account check, backup success review, incident closure review |
| Quarterly | Privileged access review, risk register update, vulnerability remediation review |
| Semiannual | Restore drill, vendor service review, policy awareness review |
| Annual | Internal audit preparation, ISMS management review, policy document review |

| 週期 | 例行查核事項 |
| --- | --- |
| 每月 | 離職帳號檢查、備份成功率檢查、事件結案證據檢查 |
| 每季 | 特權帳號覆核、風險清單更新、弱點改善追蹤 |
| 半年 | 還原演練、供應商服務檢討、政策宣導檢查 |
| 每年 | 內部稽核準備、ISMS 管理審查、政策文件覆核 |

## Monthly Control Tasks

| Task | 中文 | Evidence Requirement |
| --- | --- | --- |
| Disabled Account Review | 停用帳號檢查 | List of disabled / terminated accounts reviewed |
| Privileged Account Review | 特權帳號覆核 | Admin / sudo / privileged group review evidence |
| Backup Success Review | 備份成功率檢查 | Backup job summary and exception list |
| Restore Drill Evidence Check | 還原演練證據檢查 | Restore drill result or scheduled exception |
| Incident Closure Evidence Review | 事件結案證據檢查 | SOC / ServiceOps incident closure proof |
| Vendor Follow-up Review | 廠商追蹤檢查 | Vendor response or pending issue record |
| Risk Register Update | 風險清單更新 | Risk status updated and owner confirmed |
| AI Governance Review | AI 治理紀錄檢查 | AgentOps / Team_AgentOps / Server_AgentOps safe metadata review |

Not every task needs a large body of evidence every month. A task may use `not_applicable` or `no_event_this_month`. The important outcome is a governance record that the review occurred.

## Status Model

### Collection status

```text
pending
collecting
blocked
submitted
overdue
cancelled
not_applicable
no_event_this_month
```

| Status | 中文 | Meaning |
| --- | --- | --- |
| pending | 待收集 | 尚未開始收集 |
| collecting | 收集中 | 正在補資料或確認 |
| blocked | 卡關 | 等主管、廠商、使用者、系統或預算 |
| submitted | 已提交 | 已提交待 review |
| overdue | 已逾期 | 超過到期日 |
| cancelled | 已取消 | 不再需要 |
| not_applicable | 不適用 | 本期不適用 |
| no_event_this_month | 本月無事件 | 已檢查但本月無相關事件 |

### Evidence review status

```text
pending_review
accepted
needs_update
rejected
expired
```

### Calendar task status

```text
scheduled
due_soon
in_progress
completed
overdue
skipped
```

## Data Model Concept

### `ops271_collection_items`

| Field | Meaning |
| --- | --- |
| collection_uid | Unique collection item ID |
| calendar_task_uid | Related calendar task |
| control_area | access / backup / incident / vendor / risk / ai / policy |
| title | Collection item title |
| title_zh | Chinese title |
| evidence_requirement | Expected evidence |
| owner | Collection owner role |
| reviewer | Review owner role |
| due_date | Due date |
| frequency | monthly / quarterly / semiannual / annual / ad_hoc |
| status | pending / collecting / blocked / submitted / overdue / not_applicable |
| attention_reason | waiting_approval / waiting_vendor / waiting_user / waiting_schedule / missing_source / none |
| source_module | Optional source module |
| source_ref | Optional safe source reference |
| evidence_refs | Linked accepted or submitted evidence |
| notes | Safe short note |

### `ops271_audit_calendar_tasks`

| Field | Meaning |
| --- | --- |
| calendar_task_uid | Unique task ID |
| period | 2026-06 |
| frequency | monthly / quarterly / semiannual / annual |
| control_area | access / backup / incident / vendor / risk / ai / policy |
| task_name | Task name |
| task_name_zh | Chinese task name |
| owner | Task owner role |
| reviewer | Reviewer role |
| due_date | Due date |
| status | scheduled / due_soon / in_progress / completed / overdue / skipped |
| collection_count | Related collection items count |
| accepted_evidence_count | Accepted evidence count |
| missing_evidence_count | Missing evidence count |

### `ops271_evidence_requirements`

| Field | Meaning |
| --- | --- |
| requirement_uid | Unique requirement ID |
| control_area | Control area |
| requirement_name | Requirement name |
| requirement_name_zh | Chinese name |
| required_frequency | monthly / quarterly / semiannual / annual / ad_hoc |
| accepted_source_modules | SOC / ServiceOps / AgentOps / Server_AgentOps / Audit Logs |
| expected_evidence_type | ticket / incident / backup / access_review / audit / ai_governance |
| minimum_review_status | accepted / pending_review |
| retention_note | Safe retention note |

## Attention Reasons for Collection Queue

| Reason | 中文 | Meaning |
| --- | --- | --- |
| waiting_approval | 等待核准 | 等主管或流程核准 |
| waiting_vendor | 等待廠商 | 等廠商回覆或報告 |
| waiting_user | 等待使用者 | 等系統 owner / 使用單位確認 |
| waiting_schedule | 等待排程 | 等維護或查核時段 |
| missing_source | 缺少來源 | 找不到來源紀錄或證據 |
| missing_reviewer | 缺少審核者 | 尚未指派 reviewer |
| policy_unclear | 政策不明 | 控制項或證據要求尚未定義 |
| none | 無 | 無卡關原因 |

Collection Queue attention reasons can align conceptually with Plan_ServiceOPS attention reasons. Collection Queue focuses on evidence collection rather than ticket processing status. `blocked` can remain an internal semantic, but UI should display the explicit reason.

## Dashboard Concept

Future 271ops dashboard additions:

### KPI Cards

| KPI | Meaning |
| --- | --- |
| Collection Items Due | This month's evidence collection items |
| Overdue Collections | Overdue evidence collection tasks |
| Submitted Evidence | Evidence submitted and waiting review |
| Accepted Evidence | Evidence accepted this period |
| Monthly Control Completion | Completion rate of monthly control tasks |
| Calendar Tasks Due Soon | Upcoming audit calendar tasks |

### Main Sections

1. Collection Queue
2. Audit Calendar
3. Monthly Control Tasks
4. Overdue Evidence
5. Submitted Evidence Pending Review
6. Evidence Requirement Matrix
7. Control Area Calendar
8. Missing Evidence by Owner

## Role Behavior

### viewer

* Can see aggregate readiness and collection counts.
* Does not see owner-level collection detail.

### operator

* Can see assigned collection items.
* Can submit evidence references.
* Can see due dates and attention reasons.

### supervisor

* Can see team collection queue.
* Can see overdue items and blockers.
* Can coordinate owners and reviewers.

### governance_admin

* Can manage calendar definitions.
* Can review cross-team evidence collection status.
* Can see policy / control mapping readiness.

### auditor_viewer

* Future read-only role for audit review.
* Can see accepted evidence and audit calendar completion.
* Cannot mutate data.

## Integration With Existing Modules

| Module | Integration |
| --- | --- |
| SOC | Incident closure evidence can satisfy monthly incident review tasks |
| ServiceOps | Remediation ticket evidence can be collected or reviewed |
| Plan_ServiceOPS | Attention reasons can identify blocked collection items |
| ProjectOps | Remediation projects can link to risk treatment evidence |
| AgentOps | AI execution governance records can become AI governance evidence |
| Team_AgentOps | Human review records can support AI governance collection |
| Server_AgentOps | Backup, deployment, snapshot, and release evidence can be collected |
| Audit Logs | Operation trail supports evidence integrity |
| Status | Platform health reference for availability-related checks |
| Sync Gateway | Imported external records can become collection sources |

## Example Records

### Collection Item

```json
{
  "collection_uid": "271-collection-202606-001",
  "calendar_task_uid": "271-calendar-202606-access-001",
  "control_area": "access",
  "title": "Privileged account review evidence",
  "title_zh": "特權帳號覆核證據",
  "evidence_requirement": "Monthly review of admin / sudo / privileged groups.",
  "owner": "infra-operator",
  "reviewer": "governance-owner",
  "due_date": "2026-06-10",
  "frequency": "monthly",
  "status": "collecting",
  "attention_reason": "none",
  "source_module": "271ops",
  "source_ref": "access-review-demo-001",
  "evidence_refs": [],
  "notes": "Demo safe metadata only."
}
```

### Audit Calendar Task

```json
{
  "calendar_task_uid": "271-calendar-202606-backup-001",
  "period": "2026-06",
  "frequency": "monthly",
  "control_area": "backup",
  "task_name": "Backup success review",
  "task_name_zh": "備份成功率檢查",
  "owner": "infra-operator",
  "reviewer": "governance-owner",
  "due_date": "2026-06-05",
  "status": "completed",
  "collection_count": 2,
  "accepted_evidence_count": 1,
  "missing_evidence_count": 1
}
```

### Evidence Requirement

```json
{
  "requirement_uid": "271-req-backup-monthly-001",
  "control_area": "backup",
  "requirement_name": "Monthly backup evidence",
  "requirement_name_zh": "每月備份證據",
  "required_frequency": "monthly",
  "accepted_source_modules": ["Server_AgentOps", "Audit Logs"],
  "expected_evidence_type": "backup",
  "minimum_review_status": "accepted",
  "retention_note": "Demo retention note only. Production retention must follow policy."
}
```

## Safety and Compliance Boundary

* Collection Queue should use safe references and short summaries.
* It should not store raw logs, screenshots with sensitive content, secrets, credentials, raw prompt / response, raw command output, or sensitive personal data by default.
* Audit Calendar is a readiness planning tool, not a certification guarantee.
* Monthly Control Tasks do not replace formal internal audit, external audit, or management review.
* Auditor-facing views must be read-only by default.
* Formal compliance decisions remain with management, auditors, consultants, certification bodies, and official organizational process.

Collection Queue 是證據收集工作流，不是敏感資料倉庫。它應保存 safe references、短摘要、負責人、到期日與 review 狀態，而不是保存原始敏感內容。

## MVP Scope

First MVP includes:

* static design document
* collection queue demo fixture design
* audit calendar demo fixture design
* monthly control task demo fixture design
* role model
* status model
* dashboard concept
* integration mapping
* interview talk track

Not included:

* production workflow engine
* notification system
* calendar integration
* email reminders
* e-signature
* formal audit workflow
* live AD / SIEM / backup ingestion
* evidence file upload
* document management system

## Interview Talk Track

### 中文

271ops 不只是看目前準備度，也應該幫企業建立每月治理節奏。實務上 ISO27001 或 ISMS 不是稽核前才準備，而是每個月都有帳號覆核、備份檢查、事件結案證據、風險更新、供應商追蹤等例行事項。

所以我把 271ops 延伸成 Collection Queue 與 Audit Calendar。Collection Queue 管「還缺什麼證據、誰要補、何時到期」；Evidence Queue 管「哪些證據已收齊、哪些需要 review」。Audit Calendar 則把每月、每季、半年、年度查核事項排出來，讓資安治理變成持續流程，而不是一次性的補資料。

### English

271ops should not only show readiness. It should help organizations build a monthly governance rhythm. In real ISO27001 or ISMS preparation, evidence is not collected only right before audit time. There are recurring activities such as access reviews, backup checks, incident closure evidence, risk updates, and vendor follow-ups.

That is why I extend 271ops with Collection Queue and Audit Calendar. Collection Queue tracks what evidence is still missing, who needs to collect it, and when it is due. Evidence Queue tracks collected evidence waiting for review. Audit Calendar organizes monthly, quarterly, semiannual, and annual control tasks, turning security governance into a continuous process instead of a last-minute evidence scramble.

## Future Tasks

* Task #206：271ops Collection Queue Demo Data Fixture Design
* Task #207：271ops Audit Calendar Demo Data Fixture Design
* Task #208：271ops Collection Queue Read-only API Prototype
* Task #209：271ops Audit Calendar Frontend Prototype
* Task #210：271ops Role-based Governance View Design
* Task #211：271ops Evidence Control Mapping Design
* Task #212：271ops Monthly Control Task Release Note
* Task #213：271ops Monthly Control Task Release Tag


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
