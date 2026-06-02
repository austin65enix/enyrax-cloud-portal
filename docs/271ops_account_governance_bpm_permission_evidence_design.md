# 271ops Account Governance and BPM Permission Evidence Design

Access review queue, permission lifecycle, and BPM access request evidence mapping for ISO27001 readiness

ISO27001 readiness 的權限覆核佇列、權限生命週期與 BPM 權限申請單證據勾稽設計

## Overview

This document extends 271ops with Account Governance and BPM permission evidence mapping. The goal is to connect access requests, approvals, provisioning records, access reviews, and revocation evidence into a traceable governance chain for ISO27001 readiness.

本文件將 271ops 延伸到 Account Governance 與 BPM 權限申請證據勾稽。目標是把權限申請、核准、開通、覆核與停用證據串成可追蹤的治理鏈，支援 ISO27001 readiness。

* Account Governance is an important governance area in 271ops.
* Access Review Queue is not a simple account list. It is a periodic permission review work queue.
* BPM IT equipment permission request forms can provide access approval and change evidence.
* 271ops does not replace BPM. It references BPM requests as evidence.
* 271ops does not directly manage AD / LDAP / SaaS permissions. It organizes access governance evidence.
* Formal access changes remain in IAM / AD / LDAP / SaaS admin / IT operation processes.

## Product Positioning

271ops Account Governance 把 BPM 權限申請單、IT 執行紀錄、帳號狀態與定期覆核結果串成可稽核的權限治理證據。

271ops Account Governance connects BPM access requests, IT execution records, account status, and periodic access reviews into audit-ready access governance evidence.

它回答的問題不是「誰現在有權限」而已，而是「這個權限當初誰申請、誰核准、誰開通、是否仍需要、何時覆核、是否已回收」。

It does not only answer who currently has access. It also answers who requested the access, who approved it, who provisioned it, whether it is still needed, when it was reviewed, and whether it has been revoked.

## Permission Lifecycle

```text
Request → Approval → Provisioning → Usage / Ownership → Periodic Review → Change / Exception → Revocation → Evidence Retention
```

```text
申請 → 核准 → 開通 → 使用 / 保管 → 定期覆核 → 異動 / 例外 → 停用 / 回收 → 證據留存
```

| Stage | 中文 | Evidence |
| --- | --- | --- |
| Request | 申請 | BPM IT設備權限申請單 |
| Approval | 核准 | 主管 / 系統 owner / 資安核准紀錄 |
| Provisioning | 開通 | ServiceOps ticket、IT 執行紀錄、AD / LDAP / SaaS 變更紀錄 |
| Usage / Ownership | 使用 / 保管 | account owner、department、system owner |
| Periodic Review | 定期覆核 | Access Review Queue、覆核結果 |
| Change / Exception | 異動 / 例外 | 變更單、例外核准、期限 |
| Revocation | 停用 / 回收 | 離職、調職、職務變更、回收工單 |
| Evidence Retention | 證據留存 | 271ops evidence reference、Audit Logs |

## BPM Permission Request Evidence

A BPM IT equipment permission request should become a safe evidence reference in 271ops.

| Field | 中文 | Meaning |
| --- | --- | --- |
| bpm_request_ref | BPM申請單編號 | Safe request reference |
| requester_ref | 申請人代號 | Safe alias, not raw personal data |
| department_ref | 部門代號 | Department alias |
| system_ref | 系統代號 | Target system |
| permission_type | 權限類型 | AD group / Linux sudo / SaaS admin / VPN / DB / folder |
| requested_role | 申請角色 | Requested access role |
| business_reason | 申請理由 | Short business reason |
| approver_role | 核准角色 | Manager / system owner / security |
| approval_status | 核准狀態 | pending / approved / rejected / expired |
| approved_at | 核准時間 | Timestamp |
| expiry_date | 權限期限 | Optional expiration date |
| linked_ticket_ref | 關聯工單 | ServiceOps / provisioning ticket |
| linked_access_review_ref | 關聯覆核 | Access review record |
| evidence_status | 證據狀態 | ready / partial / missing |

Safety boundary:

* Do not store the full BPM form.
* Do not store raw attachments.
* Do not store national ID numbers, private phone numbers, addresses, or other sensitive personal data.
* Do not store passwords, keys, or tokens.
* Use safe reference + short summary.

## Access Review Queue

Access Review Queue / 權限覆核佇列 is a recurring governance work queue. It supports:

* Periodic verification that accounts are still required.
* Verification that permissions still match job responsibilities.
* Revocation checks after departure, role change, or project completion.
* Verification that privileged accounts have BPM request evidence.
* Expiration checks for exception access.
* Owner checks for shared accounts.
* Custodian and purpose checks for AI / automation / service accounts.

| Field | 中文 | Meaning |
| --- | --- | --- |
| review_uid | 覆核項目ID | Unique review item |
| period | 期間 | 2026-06 |
| system_ref | 系統 | AD / LDAP / Linux / SaaS / VPN / DB |
| account_ref | 帳號代號 | Safe account alias |
| account_type | 帳號類型 | user / admin / service / shared / automation |
| current_permission | 目前權限 | Safe role / group label |
| owner_ref | 保管人 | Safe owner alias or role |
| department_ref | 部門 | Department alias |
| bpm_request_ref | BPM申請單 | Linked request evidence |
| provisioning_ticket_ref | 開通工單 | Linked IT execution evidence |
| last_reviewed_at | 上次覆核 | Timestamp |
| review_status | 覆核狀態 | pending / approved / revoke_needed / revoked / exception |
| decision | 決議 | keep / revoke / reduce / exception / needs_owner |
| reviewer | 覆核者 | Role label |
| due_date | 到期日 | Due date |
| evidence_status | 證據狀態 | ready / partial / missing |
| attention_reason | 卡關原因 | missing_bpm_request / waiting_owner / waiting_approval / missing_reviewer / none |

## Access Review Status Model

### review_status

```text
pending
approved
revoke_needed
revoked
exception
needs_update
```

### decision

```text
keep
revoke
reduce
exception
needs_owner
not_applicable
```

### account_type

```text
user
admin
service
shared
automation
vendor
```

### evidence_status

```text
ready
partial
missing
```

### attention_reason

```text
missing_bpm_request
waiting_owner
waiting_approval
missing_reviewer
missing_provisioning_ticket
expired_exception
role_mismatch
none
```

Access Review Queue 的重點不是懲罰個人，而是確認權限是否仍有業務依據、是否有核准證據、是否應保留或回收。

Access Review Queue is not for blaming individuals. It verifies whether access still has a business basis, approval evidence, and a valid reason to remain active or be revoked.

## BPM / ServiceOps / IAM Mapping

```text
BPM Access Request
→ Approval Evidence
→ ServiceOps Provisioning Ticket
→ IAM / AD / LDAP / SaaS Account State
→ 271ops Access Review Queue
→ Revocation or Exception Evidence
→ Audit Logs
```

```text
BPM 權限申請單
→ 核准證據
→ ServiceOps 開通工單
→ IAM / AD / LDAP / SaaS 帳號狀態
→ 271ops 權限覆核佇列
→ 回收或例外證據
→ Audit Logs
```

| Source | Role in 271ops |
| --- | --- |
| BPM | Original access request and approval evidence |
| ServiceOps | Provisioning / change / revocation execution evidence |
| IAM / AD / LDAP | Account state and group membership source |
| SaaS Admin Console | SaaS role / admin permission source |
| Audit Logs | Operation trail and review decision history |
| Plan_ServiceOPS | Attention reason when approval, owner, vendor, or schedule is blocking |
| ProjectOps | Remediation project if access governance requires improvement |

## Data Model Concept

### `ops271_bpm_permission_requests`

| Field | Meaning |
| --- | --- |
| bpm_request_uid | Unique BPM request reference |
| bpm_request_ref | Safe BPM request number |
| request_type | new_access / change_access / revoke_access / temporary_access / exception |
| requester_ref | Safe requester alias |
| department_ref | Department alias |
| system_ref | Target system |
| permission_type | ad_group / linux_sudo / saas_admin / vpn / db / folder / service_account |
| requested_role | Requested role / group |
| business_reason_summary | Short reason summary |
| approver_role | manager / system_owner / security / governance |
| approval_status | pending / approved / rejected / expired |
| approved_at | Timestamp |
| expiry_date | Optional expiration |
| linked_ticket_ref | ServiceOps ticket reference |
| evidence_status | ready / partial / missing |
| safe_reference_only | true |
| sensitive_content_stored | false |

### `ops271_access_review_items`

| Field | Meaning |
| --- | --- |
| review_uid | Unique review item |
| period | Review period |
| system_ref | System reference |
| account_ref | Safe account alias |
| account_type | user / admin / service / shared / automation / vendor |
| current_permission | Safe permission label |
| owner_ref | Safe owner alias or role |
| department_ref | Department alias |
| bpm_request_ref | Linked BPM request |
| provisioning_ticket_ref | Linked provisioning ticket |
| last_reviewed_at | Last review timestamp |
| review_status | pending / approved / revoke_needed / revoked / exception / needs_update |
| decision | keep / revoke / reduce / exception / needs_owner / not_applicable |
| reviewer | Reviewer role |
| due_date | Due date |
| evidence_status | ready / partial / missing |
| attention_reason | missing_bpm_request / waiting_owner / waiting_approval / missing_reviewer / none |
| safe_reference_only | true |
| sensitive_content_stored | false |

### `ops271_access_lifecycle_events`

| Field | Meaning |
| --- | --- |
| event_uid | Unique event |
| account_ref | Safe account alias |
| event_type | requested / approved / provisioned / reviewed / exception_granted / revoked |
| event_at | Timestamp |
| source_module | BPM / ServiceOps / IAM / Audit Logs / 271ops |
| source_ref | Safe evidence reference |
| actor_role | Role label |
| summary | Safe short summary |

## Example Records

### BPM Permission Request

```json
{
  "bpm_request_uid": "271-bpm-perm-202606-001",
  "bpm_request_ref": "BPM-ACCESS-DEMO-001",
  "request_type": "new_access",
  "requester_ref": "employee-demo-001",
  "department_ref": "infra-team",
  "system_ref": "linux-admin-hosts",
  "permission_type": "linux_sudo",
  "requested_role": "sudo-maintainer",
  "business_reason_summary": "Temporary maintenance permission for scheduled patch work.",
  "approver_role": "infra-supervisor",
  "approval_status": "approved",
  "approved_at": "2026-06-02T09:30:00+08:00",
  "expiry_date": "2026-06-30",
  "linked_ticket_ref": "SVC-DEMO-ACCESS-001",
  "evidence_status": "ready",
  "safe_reference_only": true,
  "sensitive_content_stored": false
}
```

### Access Review Item

```json
{
  "review_uid": "271-access-review-202606-001",
  "period": "2026-06",
  "system_ref": "linux-admin-hosts",
  "account_ref": "linux-admin-alias-001",
  "account_type": "admin",
  "current_permission": "sudo-maintainer",
  "owner_ref": "infra-operator-role",
  "department_ref": "infra-team",
  "bpm_request_ref": "BPM-ACCESS-DEMO-001",
  "provisioning_ticket_ref": "SVC-DEMO-ACCESS-001",
  "last_reviewed_at": "2026-05-31T16:00:00+08:00",
  "review_status": "pending",
  "decision": "keep",
  "reviewer": "governance-owner",
  "due_date": "2026-06-10",
  "evidence_status": "ready",
  "attention_reason": "none",
  "safe_reference_only": true,
  "sensitive_content_stored": false
}
```

### Lifecycle Event

```json
{
  "event_uid": "271-access-event-202606-001",
  "account_ref": "linux-admin-alias-001",
  "event_type": "approved",
  "event_at": "2026-06-02T09:30:00+08:00",
  "source_module": "BPM",
  "source_ref": "BPM-ACCESS-DEMO-001",
  "actor_role": "infra-supervisor",
  "summary": "Access request approved for scheduled patch work."
}
```

## Dashboard Concept

Future 271ops Account Governance dashboard additions:

### KPI Cards

| KPI | Meaning |
| --- | --- |
| Access Reviews Pending | Pending access review items |
| Missing BPM Evidence | Active permissions without linked BPM request |
| Revoke Needed | Accounts or permissions requiring revocation |
| Exceptions Expiring | Temporary exceptions near expiry |
| Privileged Accounts Reviewed | Privileged accounts reviewed this period |
| Service Accounts With Owner | Service / automation accounts with owner assigned |

### Main Sections

1. Access Review Queue
2. Missing BPM Request Evidence
3. Privileged Account Review
4. Shared / Service Account Ownership
5. Expiring Exceptions
6. Revocation Queue
7. BPM Request Mapping
8. Access Lifecycle Timeline

## Role Behavior

### viewer

* aggregate counts only
* no account-level detail

### operator

* assigned access review items
* can prepare evidence references
* can see linked BPM / ServiceOps references for assigned scope

### supervisor

* team access review queue
* missing BPM evidence
* revoke-needed items
* approval blockers

### governance_admin

* cross-system governance view
* control mapping
* exception tracking
* evidence policy definition

### auditor_viewer

* read-only accepted evidence view
* no mutation
* no raw sensitive content

## Safety and Compliance Boundary

* Account Governance stores safe references and short summaries only.
* Do not store BPM form full content by default.
* Do not store raw attachments.
* Do not store passwords, credentials, API keys, private keys, tokens, SSH keys, or raw logs.
* Do not store sensitive personal data by default.
* Account refs should be aliases, not raw employee identifiers.
* Auditor-facing views should be read-only.
* 271ops does not directly change IAM / AD / LDAP / SaaS permissions.
* Formal authorization decisions remain in BPM / IAM / management process.

Account Governance 的目標是勾稽權限治理證據，不是保存敏感表單全文或直接操作權限。271ops 應保存 safe references、短摘要、狀態與 review decision，而不是保存密碼、金鑰、原始附件或敏感個資。

## MVP Scope

First MVP includes:

* account governance design
* BPM permission request evidence concept
* access review queue design
* access lifecycle event concept
* safe demo fixture design
* dashboard concept
* integration mapping
* interview talk track

Not included:

* live BPM integration
* live AD / LDAP integration
* live SaaS admin integration
* write API
* actual permission provisioning
* password / key vault
* raw BPM form storage
* e-signature
* automatic approval
* formal IAM policy engine

## Interview Talk Track

### 中文

271ops 的 Account Governance 是把權限申請、核准、開通、覆核與回收串成一條治理證據鏈。很多企業有 BPM 權限申請單，也有 AD、Linux、SaaS 權限，但稽核時常常要人工去對：這個權限當初誰申請、誰核准、誰開通、現在是否仍需要、是否已經覆核。

所以我會讓 BPM IT設備權限申請單成為 safe evidence reference，再勾稽 ServiceOps 執行工單、帳號狀態與 Access Review Queue。這樣不是 271ops 直接改權限，而是把權限生命週期整理成可追蹤、可審核、可回收的治理紀錄。

### English

271ops Account Governance connects access requests, approvals, provisioning, access reviews, and revocation into one governance evidence chain. Many organizations have BPM access request forms and separate AD, Linux, or SaaS permissions, but during audits they still need to manually prove who requested access, who approved it, who provisioned it, whether it is still needed, and whether it was reviewed.

The idea is to treat BPM IT permission requests as safe evidence references, then link them with ServiceOps execution tickets, account state, and Access Review Queue. 271ops does not directly change permissions. It organizes the permission lifecycle into traceable, reviewable, and revocable governance records.

## Future Tasks

* Task #208：271ops Account Governance Demo Data Fixture Design
* Task #209：271ops Collection Queue Read-only API Prototype
* Task #210：271ops Access Review Queue Read-only API Prototype
* Task #211：271ops Audit Calendar Frontend Prototype
* Task #212：271ops Role-based Governance View Design
* Task #213：271ops Evidence Control Mapping Design
* Task #214：271ops Account Governance Release Note
* Task #215：271ops Account Governance Release Tag
