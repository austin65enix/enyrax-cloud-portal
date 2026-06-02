# AgentOps Product Family Navigation Design

Navigation and product-family structure for AI Agent Governance modules

## Overview

AgentOps has grown from a single dashboard into a product family for AI Agent Governance. This design defines how AgentOps, Server_AgentOps, Personal_AgentOps, and Team_AgentOps should be positioned, grouped, and navigated inside ENYRAX Portal.

AgentOps 已經從單一 dashboard 成長為 AI Agent Governance 的產品族群。本設計定義 AgentOps、Server_AgentOps、Personal_AgentOps 與 Team_AgentOps 在 ENYRAX Portal 中的定位、分組與導覽方式。

AgentOps 不再只是單一頁面，而應該成為 AI Agent Governance 的入口。Server_AgentOps、Personal_AgentOps 與 Team_AgentOps 分別代表伺服器端、個人與團隊三種不同治理視角。主選單應避免隨著模組增加而越來越擠；navigation 設計應支援未來擴充，但避免一次過度改版。

## Current Navigation Problem

目前主選單已經包含：

```text
Portal / SOC / ServiceOps / ProjectOps / AgentOps / Sync Gateway / Audit Logs / Status
```

* 主選單開始變長。
* AgentOps 相關功能越來越多。
* Team_AgentOps 已經是獨立模組。
* 未來還會有 Server_AgentOps / Personal_AgentOps。
* 如果全部塞在主選單，會降低可讀性。
* 需要一個 AgentOps product family / hub 概念。

現在的問題不是功能不夠，而是產品線開始長大，需要把同類型功能整理成清楚的產品族群。

## AgentOps Product Family

```text
AgentOps
├─ Server_AgentOps
├─ Personal_AgentOps
└─ Team_AgentOps
```

| Module            | 中文                 | Purpose                                                            |
| ----------------- | -------------------- | ------------------------------------------------------------------ |
| AgentOps Hub      | AgentOps 入口         | AI Agent Governance product family entry point                     |
| Server_AgentOps   | 伺服器端 Agent 治理   | Server-side AI / automation run observability and governance       |
| Personal_AgentOps | 個人 Agent 治理       | Personal AI work mode governance with safe metadata boundaries     |
| Team_AgentOps     | 團隊 Agent 治理       | Human-AI team collaboration, project contribution, review workflow |

## Module Positioning

### AgentOps Hub

AgentOps Hub is the entry point for AI Agent Governance inside ENYRAX. It should summarize Server_AgentOps, Personal_AgentOps, and Team_AgentOps, and guide users to the right governance view.

AgentOps Hub 是 ENYRAX 裡 AI Agent Governance 的入口。它負責整理 Server_AgentOps、Personal_AgentOps 與 Team_AgentOps，並引導使用者進入正確的治理視角。

### Server_AgentOps

Server_AgentOps manages server-side AI, Codex, automation, parser, snapshot, backup, deployment, and release-check runs. It focuses on background execution governance.

Server_AgentOps 管理伺服器端 AI、Codex、automation、parser、snapshot、backup、deployment 與 release check 執行紀錄，重點是背景任務治理。

適合包含：

* Codex / automation run logs
* parser execution
* snapshot generation
* backup automation
* deployment verification
* release readiness checks
* scheduled task status
* server-side tool activity

### Personal_AgentOps

Personal_AgentOps manages individual AI-assisted work under enterprise boundaries. It keeps personal AI usage traceable through safe metadata without storing full prompts, responses, or raw sessions.

Personal_AgentOps 管理企業工作模式下的個人 AI 輔助工作。它透過 safe metadata 讓個人 AI 使用可追蹤，但不保存完整 prompt、response 或 raw sessions。

適合包含：

* personal AI worklog
* private mode boundary
* safe metadata
* no prompt / response storage
* personal task summary
* review-needed flag
* policy reminder
* data boundary hints

### Team_AgentOps

Team_AgentOps turns safe agent run metadata into human-AI team delivery records. It connects agent runs to projects, reviews, contribution, scorecards, and delivery accountability.

Team_AgentOps 將 safe agent run metadata 轉換成人機協作交付紀錄，並把 Agent 執行接回專案、審核、貢獻、scorecard 與交付責任。

已完成：

* static dashboard
* safe fixtures
* read-only fixture API
* API DATA / DEMO FALLBACK
* role filtering
* frontend role switcher

## Recommended Navigation Strategy

### Option A: Keep AgentOps as single top nav item

主選單只保留：

```text
Portal / SOC / ServiceOps / ProjectOps / AgentOps / Audit / Status
```

AgentOps 點進去後顯示 hub：

```text
AgentOps Hub
├─ Server_AgentOps
├─ Personal_AgentOps
└─ Team_AgentOps
```

優點：主選單不會變擠、產品族群清楚、未來可擴充更多 AgentOps 子模組，最適合目前階段。

缺點：需要新增 hub 頁或重構現有 AgentOps 入口。

### Option B: Keep current pages but group homepage cards

維持既有 routes：

```text
/agentops/
/team-agentops/
/personal-agentops/
/server-agentops/
```

首頁以 AgentOps Group 方式排列。

優點：改動小、不破壞既有路由、可先做視覺分組。

缺點：主選單仍需決定要顯示哪一個 AgentOps 入口。

### Option C: All AgentOps submodules in top nav

主選單直接顯示：

```text
AgentOps / Server_AgentOps / Personal_AgentOps / Team_AgentOps
```

不建議，因為主選單會過度擁擠。

Recommended: Option A first, with Option B as an incremental transition.

建議先採 Option A，把 AgentOps 作為主選單入口；短期可用 Option B 方式，在首頁先做 AgentOps Group 視覺分組。

## Route Recommendation

| Route                 | Purpose                                                    |
| --------------------- | ---------------------------------------------------------- |
| `/agentops/`          | Existing AgentOps dashboard, later may become AgentOps Hub |
| `/agentops-hub/`      | Optional transitional hub route                            |
| `/server-agentops/`   | Server-side AI / automation governance                     |
| `/personal-agentops/` | Personal AI work mode governance                           |
| `/team-agentops/`     | Team AI collaboration governance                           |

### Phase 1: No-breaking transition

* 保留 `/agentops/` 既有 dashboard。
* 保留 `/team-agentops/`。
* 新增文件設計 `/server-agentops/` 與 `/personal-agentops/`。
* 未來可新增 `/agentops-hub/` 作為 hub，不破壞現有 `/agentops/`。

### Phase 2: AgentOps Hub consolidation

* `/agentops/` 可改為 AgentOps Hub。
* 既有 AgentOps dashboard 可移至 `/server-agentops/` 或 `/agentops/server/`。
* 需要 release note 與 redirect strategy。

## Top Navigation Recommendation

建議主選單：

```text
Portal
SOC
ServiceOps
ProjectOps
AgentOps
Audit
Status
```

可考慮把 `Sync Gateway` 改成 Portal card 或 Ops Integration group，而不是長期停在 top nav。

Top nav 應放最高頻或最高層級產品。子產品應進入 hub 或 group。AgentOps top nav 應代表整個 AI Agent Governance family，而不是單一頁面。

## AgentOps Hub Card Design

| Card title        | Subtitle                                      | 中文                       | Status          |
| ----------------- | --------------------------------------------- | -------------------------- | --------------- |
| Server_AgentOps   | Server-side AI and automation run governance  | 伺服器端 AI 與自動化執行治理 | PLANNED         |
| Personal_AgentOps | Personal AI work mode governance              | 個人 AI 工作模式治理         | PLANNED         |
| Team_AgentOps     | Human-AI team collaboration governance        | 人機團隊協作治理             | API-BACKED DEMO |

## Product Story

AgentOps 的產品故事可以從「AI 工具使用變多，但執行紀錄散落在 chat history」開始。Server_AgentOps 處理伺服器端自動化與背景 Agent，Personal_AgentOps 處理個人工作模式下的 AI 使用邊界，Team_AgentOps 則把 Agent 的成果接回團隊、專案與審核。

The AgentOps product story starts from the problem that AI tool usage is growing, but execution records are often scattered in invisible chat history. Server_AgentOps governs server-side automation and background agents. Personal_AgentOps governs individual AI-assisted work under enterprise boundaries. Team_AgentOps connects agent outputs back to teams, projects, and human review.

## Safety Boundary

* AgentOps family stores safe metadata only by default.
* No module should store full prompt / response by default.
* No raw session storage by default.
* No credentials / secrets / API keys.
* Personal_AgentOps must be especially careful with private mode and enterprise data boundary.
* Team_AgentOps must remain governance and protection, not employee surveillance.
* Server_AgentOps must avoid logging secrets from automation outputs.
* Token / cost values remain operational estimates, not billing-grade data.

AgentOps family 的目標是讓 AI Agent 使用可觀察、可審核、可治理，而不是收集完整對話內容或監控個人。

## Future Tasks

* Task #186：AgentOps Hub Static Prototype
* Task #187：Server_AgentOps Product Concept Design
* Task #188：Personal_AgentOps Product Concept Design
* Task #189：AgentOps Top Navigation Refinement
* Task #190：AgentOps Product Family Release Note
* Task #191：AgentOps Hub Release Tag

## Appendix: Task #184 API Restart Verification

Verified against the public deployment on 2026-06-02 after the `enyrax-api` restart:

* `HEAD /plan-serviceops/` returned `HTTP 200`.
* `viewer` returned `team_count=0`, retained `attention_reason_distribution`, and exposed no ticket details.
* `unknown` correctly fell back to `viewer` with `role_source=fallback` and `team_count=0`.
* `operator` returned `team_count=6`.
* `supervisor` returned the current team scope of `team_count=9`.
* `admin` returned `team_count=9`, equal to the supervisor count.
* Returned ticket statuses were `in_progress` and `pending`; no `blocked` status was exposed.
* `warnings=[]` for viewer, operator, supervisor, admin, and unknown fallback.

## Task #186 AgentOps Hub Static Prototype

* Task #186 adds `/agentops-hub/` static prototype.
* The Hub groups Server_AgentOps, Personal_AgentOps, Team_AgentOps, and existing AgentOps Dashboard.
* It keeps existing `/agentops/` and `/team-agentops/` routes intact.
* It updates Portal homepage entry.
* It remains static frontend only.
* No backend, DB, API, fixtures, release, or deployment changes were made.
