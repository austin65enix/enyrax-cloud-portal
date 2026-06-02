# Server_AgentOps Product Concept Design

Server-side AI, automation, parser, backup, deployment, and release run governance

## Overview

Server_AgentOps is the server-side execution governance module in the AgentOps product family. It tracks safe metadata for AI agents, Codex sessions, automation scripts, parsers, snapshot jobs, backup jobs, deployment checks, release readiness checks, and scheduled server-side operations.

Server_AgentOps 是 AgentOps 產品族群中的伺服器端執行治理模組。它負責追蹤 AI Agent、Codex session、自動化腳本、parser、snapshot job、backup job、deployment check、release readiness check 與伺服器端排程任務的 safe metadata。

Server_AgentOps is not general server monitoring. It does not replace Status or healthcheck. It focuses on governance records for server-side AI, automation, and job execution.

Server_AgentOps 不是一般 server monitoring，也不是取代 Status / healthcheck。它關注的是「伺服器端 AI / automation / job execution 的治理紀錄」。

It answers:

* Which server-side agent or automation runs were executed?
* Who triggered them?
* Which task, release, or module were they related to?
* Did they succeed?
* Do they need review?
* Is there an artifact or evidence reference?
* Were there any safety boundary issues?

它回答：

* 哪些 server-side agent / automation run 執行過？
* 是誰觸發？
* 跟哪個 task / release / module 有關？
* 是否成功？
* 是否需要 review？
* 是否有 artifact / evidence reference？
* 是否有安全邊界問題？

Server_AgentOps stores safe metadata only. It does not store full prompts, responses, raw sessions, credentials, secrets, or full command output.

## Product Positioning

Server_AgentOps 讓伺服器端 AI 與自動化任務從黑箱背景執行，變成可觀察、可審核、可追蹤的治理紀錄。

Server_AgentOps turns server-side AI and automation runs from background black boxes into observable, reviewable, and traceable governance records.

It is the operations-side counterpart of Team_AgentOps.

它可以視為 Team_AgentOps 在伺服器端與背景任務場景下的對應模組。

## Core Use Cases

### 1. Codex / Server Agent Run Log

記錄 Codex 或 server-side agent 執行任務，例如：

* release note generation
* API prototype implementation
* parser review
* visual QA harness
* deployment verification

保存 safe metadata：

* `run_uid`
* `task_id`
* `module`
* `status`
* `started_at` / `ended_at`
* `trigger_source`
* `actor`
* artifact references
* review status

### 2. Parser / Snapshot Job Governance

追蹤 AgentOps parser、snapshot generation、retention dry-run 與 generated data review，例如：

* `parse_codex_sessions.py`
* daily snapshot generation
* retention report
* snapshot review decision

不保存 raw session。

### 3. Backup / Restore Job Governance

追蹤 backup scripts 執行情況，例如：

* PostgreSQL dump
* app archive
* R2 upload
* restore drill

保存結果：

* success / failed
* backup artifact reference
* size
* destination label
* verification status

不保存 `DATABASE_URL`、rclone config 或 credentials。

### 4. Deployment / Release Verification

記錄 deploy、restart、curl、healthcheck 與 release tag 驗證，例如：

* `systemctl restart enyrax-api`
* `/plan-serviceops/ HTTP 200`
* API role check
* tag push result

只保存 safe verification result。

### 5. Scheduled Task / Cron Governance

記錄排程任務狀態，例如：

* certbot renew
* backup schedule
* snapshot schedule
* healthcheck schedule

不取代 systemd / cron，而是提供治理摘要。

## What Server_AgentOps Is Not

* It is not general CPU / RAM / disk monitoring.
* It is not a full observability platform.
* It is not a replacement for Status page.
* It is not a secrets vault.
* It does not store raw prompts or raw command output.
* It does not replace AuditOps.
* It does not automatically approve deployment or release.
* It does not mutate production systems in MVP.

Server_AgentOps 不是要取代監控系統，而是補上「伺服器端 AI / 自動化執行是否有紀錄、是否可審核、是否有交付證據」這一層。

## Dashboard Concept

### KPI Cards

| KPI            | Meaning                                  |
| -------------- | ---------------------------------------- |
| Active Runs    | Currently running server-side jobs       |
| Failed Runs    | Failed automation / agent runs           |
| Pending Review | Runs waiting human review                |
| Backup Jobs    | Recent backup / upload jobs              |
| Release Checks | Recent deployment / release verification |
| Snapshot Jobs  | Parser / snapshot / retention jobs       |

### Main Sections

1. Server Agent Run Timeline
2. Job Type Breakdown
3. Failed / Warning Runs
4. Backup and Restore Evidence
5. Snapshot / Parser Governance
6. Deployment Verification
7. Release Readiness
8. Safety Boundary

## Data Model Concept

### `server_agent_runs`

| Field            | Meaning                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------- |
| run_uid          | Unique run identifier                                                                     |
| task_id          | Optional task number, e.g. Task #184                                                      |
| module           | AgentOps / Plan_ServiceOPS / Team_AgentOps / BackupOps                                    |
| job_type         | codex / parser / snapshot / backup / deployment / release_check / healthcheck / scheduled |
| job_name         | Human-readable job name                                                                   |
| trigger_source   | manual / codex / cron / systemd / script / release                                        |
| actor            | Safe actor label, not credential                                                          |
| status           | running / success / failed / warning / review_needed                                      |
| started_at       | Start time                                                                                |
| ended_at         | End time                                                                                  |
| duration_seconds | Duration                                                                                  |
| artifact_ref     | Safe artifact reference                                                                   |
| evidence_ref     | Safe evidence reference                                                                   |
| review_status    | not_required / pending / approved / rework                                                |
| risk_level       | low / medium / high / critical                                                            |
| warning_code     | Optional safe warning code                                                                |
| notes            | Safe short note                                                                           |

### `server_agent_artifacts`

| Field         | Meaning                                                                       |
| ------------- | ----------------------------------------------------------------------------- |
| artifact_uid  | Unique artifact ID                                                            |
| run_uid       | Related run                                                                   |
| artifact_type | log_summary / backup_file / snapshot_json / release_note / healthcheck_report |
| artifact_ref  | Safe path or label                                                            |
| checksum      | Optional checksum                                                             |
| size_bytes    | Optional size                                                                 |
| created_at    | Timestamp                                                                     |

### `server_agent_reviews`

| Field           | Meaning                                      |
| --------------- | -------------------------------------------- |
| review_uid      | Unique review ID                             |
| run_uid         | Related run                                  |
| reviewer        | Human reviewer                               |
| decision        | approved / rejected / rework / accepted_risk |
| comment_summary | Safe review summary                          |
| reviewed_at     | Timestamp                                    |

## Allowed Values

### `job_type`

```text
codex
parser
snapshot
backup
deployment
release_check
healthcheck
scheduled
automation
```

### `status`

```text
running
success
failed
warning
review_needed
skipped
```

### `review_status`

```text
not_required
pending
approved
rework
accepted_risk
```

### `risk_level`

```text
low
medium
high
critical
```

### `trigger_source`

```text
manual
codex
cron
systemd
script
release
api
```

## Safe Metadata Boundary

Server_AgentOps may store:

* task id
* module
* job type
* job name
* status
* duration
* safe artifact reference
* safe evidence reference
* review status
* warning code
* aggregate token / cost estimate if needed

Server_AgentOps must not store:

* full prompt
* full response
* raw session logs
* raw command output
* credentials
* secrets
* API keys
* private keys
* `DATABASE_URL`
* rclone config
* full home paths
* sensitive backup contents
* unredacted environment variables

Server_AgentOps 預設只保存 safe metadata。它可以記錄任務、模組、狀態、時間、artifact reference 與 review status，但不能保存完整 prompt、response、raw session、raw command output、credentials、secrets 或未遮蔽環境變數。

## Integration With ENYRAX Modules

| Module          | Integration                                                                       |
| --------------- | --------------------------------------------------------------------------------- |
| AgentOps        | Server_AgentOps can feed server-side run metadata into AgentOps family governance |
| Team_AgentOps   | Server runs may later be linked to team delivery records                          |
| Plan_ServiceOPS | Server automation failures can create attention items or support evidence         |
| ServiceOps      | Failed backup / deployment / sync jobs can become tickets                         |
| ProjectOps      | Release / deployment checks can link to project milestones                        |
| BackupOps       | Backup job records and restore drill evidence                                     |
| AuditOps        | Human review, approval, deployment, and exception evidence                        |
| Status          | Healthcheck result references, but not replacement for Status                     |

## Example Run Records

### Codex Task Run

```json
{
  "run_uid": "srv-agent-run-20260602-001",
  "task_id": "Task #184",
  "module": "Plan_ServiceOPS",
  "job_type": "codex",
  "job_name": "Role-based Attention Queue API Prototype",
  "trigger_source": "codex",
  "actor": "operator@enyrax.local",
  "status": "success",
  "review_status": "approved",
  "artifact_ref": "commit:440a16c",
  "risk_level": "low"
}
```

### Snapshot Job

```json
{
  "run_uid": "srv-agent-run-20260602-002",
  "module": "AgentOps",
  "job_type": "snapshot",
  "job_name": "Daily snapshot generated data review",
  "trigger_source": "cron",
  "status": "review_needed",
  "review_status": "pending",
  "artifact_ref": "data/agentops/snapshots/daily/2026-06-01.json",
  "risk_level": "medium"
}
```

### Backup Job

```json
{
  "run_uid": "srv-agent-run-20260602-003",
  "module": "BackupOps",
  "job_type": "backup",
  "job_name": "PostgreSQL local dump and R2 upload",
  "trigger_source": "script",
  "status": "success",
  "review_status": "not_required",
  "artifact_ref": "r2://enyrax-soc-backup/enyrax-soc-tokyo/postgres/latest",
  "risk_level": "medium"
}
```

### Deployment Check

```json
{
  "run_uid": "srv-agent-run-20260602-004",
  "module": "Platform",
  "job_type": "deployment",
  "job_name": "Restart FastAPI backend and verify Plan_ServiceOPS API",
  "trigger_source": "manual",
  "status": "success",
  "review_status": "not_required",
  "evidence_ref": "curl:/api/plan-serviceops/dashboard role matrix",
  "risk_level": "low"
}
```

## MVP Scope

第一版 MVP 包含：

* static dashboard prototype
* safe demo run records
* run timeline
* job type breakdown
* failed / warning run list
* review needed queue
* backup / snapshot / deployment evidence references
* safety boundary card
* interview demo talk track

不包含：

* production DB schema
* actual parser ingestion
* live cron integration
* write API
* auto approval
* secret scanning engine
* full observability
* billing-grade cost tracking

## Role Consideration

### viewer

* aggregate status
* recent safe run summaries
* no artifact details

### operator

* own / assigned server runs
* failed jobs requiring action
* evidence references for own work

### supervisor

* team-level server automation health
* failed / warning runs
* review needed queue
* release readiness

### admin

* cross-module server run governance
* configuration visibility
* retention / policy overview
* safe metadata only

## Dashboard Copy

中文短句：

```text
Server_AgentOps 管理伺服器端 AI 與自動化任務的執行治理，讓背景任務不再是黑箱。
```

英文短句：

```text
Server_AgentOps governs server-side AI and automation runs, making background execution traceable and reviewable.
```

Card subtitle：

```text
Server-side AI and automation run governance
```

中文：

```text
伺服器端 AI 與自動化執行治理
```

## Interview Talk Track

### 中文

Server_AgentOps 是 AgentOps family 裡面偏伺服器端與背景任務治理的模組。像 Codex 任務、parser、snapshot、backup、deployment check、release verification，這些都不是一般使用者每天會看到的工單，但它們會影響平台穩定性與交付信任。

所以 Server_AgentOps 不是監控 CPU 或 RAM，而是記錄伺服器端 AI / automation 做了什麼、是否成功、是否需要 review、產生了哪些 evidence。這樣背景任務也可以被治理，而不是執行完就消失在 terminal history 裡。

### English

Server_AgentOps is the server-side and background execution governance module in the AgentOps family. Codex tasks, parsers, snapshots, backups, deployment checks, and release verification may not be daily user tickets, but they directly affect platform stability and delivery trust.

So Server_AgentOps is not about monitoring CPU or RAM. It records what server-side AI or automation did, whether it succeeded, whether it needs review, and what evidence was produced. This makes background execution governable instead of disappearing into terminal history.

## Future Tasks

* Task #188：Server_AgentOps Static Dashboard Prototype
* Task #189：Server_AgentOps Demo Data Fixture Design
* Task #190：Server_AgentOps Read-only Fixture API Prototype
* Task #191：Server_AgentOps Frontend API Switch with Fallback
* Task #192：Server_AgentOps Visual QA
* Task #193：Server_AgentOps Release Note
* Task #194：Server_AgentOps Release Tag


## Task #195 271Ops Product Concept Design

* Task #195 defines 271Ops as the ISO27001 readiness and security governance preparation module.
* It turns daily operations, incident handling, access review, backup evidence, and AI governance records into audit-ready governance evidence.
* It does not replace consultants, auditors, certification bodies, or formal compliance decisions.
* It integrates SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Team_AgentOps, Server_AgentOps, Audit Logs, Status, and Sync Gateway.
* It prepares Task #196 static dashboard prototype.
* No frontend, backend, DB, API, release, or deployment changes were made.
