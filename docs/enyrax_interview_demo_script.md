# ENYRAX Interview Demo Script

3–5 minute product demo script for ENYRAX operations command center

## Opening Positioning

### 中文

我目前把 ENYRAX 定位成一套企業營運戰情中心。它不是單一工單系統，也不是單一 Dashboard，而是把 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps 與 Team_AgentOps 串成一條完整的營運流程。

它的核心價值是把原本分散的資安事件、維運工單、專案進度、AI Agent 執行紀錄與人工審核流程，整理成可追蹤、可審核、可交付的平台。

### English

I position ENYRAX as an enterprise operations command center. It is not just a ticketing system or a single dashboard. It connects SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, and Team_AgentOps into one operational workflow.

The core value is turning scattered security incidents, service tickets, project progress, AI agent execution records, and human review workflows into a traceable, reviewable, and deliverable platform.

## 30-second Short Version

### 中文

ENYRAX 是我做的一套企業營運戰情中心，核心是把資安事件、維運工單、專案進度與 AI Agent 工作紀錄串成一條可追蹤流程。

傳統企業裡 SOC 看 SOC、工單看工單、專案看專案，AI Agent 又常常變成個人私下使用的工具。ENYRAX 則把這些東西拉回同一個平台，讓事件可以轉成工單，工單可以連到專案，AI Agent 的產出可以被審核，最後回到交付與稽核紀錄。

### English

ENYRAX is an enterprise operations command center that connects security incidents, service tickets, project progress, and AI agent work into one traceable workflow.

In many companies, SOC, ticketing, and project management are separated, while AI agents are often used privately by individuals. ENYRAX brings these activities back into one platform, where incidents can become tickets, tickets can link to projects, AI outputs can be reviewed, and delivery can be traced and audited.

## 3-minute Demo Script

### 1. Portal Home

**中文話術**

這是 ENYRAX Portal 的首頁。我的設計不是把每個功能做成孤立頁面，而是把企業營運裡常見的資安事件、維運工單、專案進度、個人待辦與 AI Agent 管理，整理成一個入口。

所以從這裡可以進入 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps、Team_AgentOps，以及 Audit / Status。

**English Talk Track**

This is the ENYRAX Portal home. The idea is not to build isolated pages, but to bring common enterprise operations activities into one entry point: security incidents, service tickets, project progress, personal work queues, and AI agent governance.

From here, we can enter SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Team_AgentOps, and Audit / Status.

### 2. SOC

**中文話術**

SOC 這一層負責資安事件與風險。它的價值不是只顯示告警，而是把原始 security alert 轉成可以被指派、追蹤、驗證與結案的 incident。

例如一個 SSH brute force 或異常登入事件，不應該只停在 log 裡，而是要能進入處理流程，後續可以連到 ServiceOps 工單、修復紀錄與驗證證據。

**English Talk Track**

The SOC layer handles security incidents and risk. Its value is not simply displaying alerts, but turning raw security alerts into incidents that can be assigned, tracked, verified, and closed.

For example, an SSH brute force or suspicious login event should not remain only in logs. It should enter an operational workflow and later connect to ServiceOps tickets, remediation records, and verification evidence.

### 3. ServiceOps

**中文話術**

ServiceOps 負責維運工單與服務請求。很多公司日常 IT 工作會散在 Teams、Email、口頭交辦或 Excel 裡，最後很難知道誰處理了什麼、目前狀態如何、是否真的完成。

ServiceOps 把這些工作整理成有狀態、有進度、有工時與結案紀錄的流程。

**English Talk Track**

ServiceOps manages operational tickets and service requests. In many companies, daily IT work is scattered across Teams, email, verbal requests, or spreadsheets, making it hard to know who handled what, what the current status is, and whether the work was actually completed.

ServiceOps turns that work into a structured workflow with status, progress, worklogs, and closure records.

### 4. ProjectOps

**中文話術**

ProjectOps 則把工單與維運工作接回專案。因為工單不應該只是零散任務，很多工單其實會影響專案時程、基礎設施調整或交付進度。

所以 ProjectOps 管理的是專案組合、起訖時間、里程碑、狀態與風險，讓主管可以從專案角度看整體交付。

**English Talk Track**

ProjectOps connects tickets and operational work back to projects. Tickets should not remain isolated tasks, because many of them affect project timelines, infrastructure changes, or delivery progress.

ProjectOps manages project portfolios, start and end dates, milestones, status, and risk, giving managers a delivery-level view.

### 5. Plan_ServiceOPS

**中文話術**

Plan_ServiceOPS 是比較貼近使用者每天打開會看到的個人工作中控台。它回答的是一個很實際的問題：今天我應該先處理什麼？

它會整理今日待辦、團隊待辦與專案截止日。這樣維運人員不用到處翻工單或專案頁面，一打開就知道優先順序。

**English Talk Track**

Plan_ServiceOPS is closer to what an operator would open every morning. It answers a very practical question: what should I handle first today?

It brings together today’s tickets, team queue, and project deadlines, so operators do not need to jump across multiple ticket and project pages just to understand priorities.

### 6. AgentOps

**中文話術**

AgentOps 是 AI Agent 治理層。AI 工具在企業裡很容易變成看不見的 chat history，大家都有用，但主管不知道 AI 做了什麼，工程師也很難證明 AI 產出是否有經過審核。

AgentOps 把 AI Agent 的執行紀錄、token estimate、review status、snapshot、risk 與 release readiness 轉成可觀察、可審核、可治理的營運資料。

**English Talk Track**

AgentOps is the AI agent governance layer. In enterprises, AI tools can easily become invisible chat history. People may use AI, but managers do not know what AI actually did, and engineers may not be able to prove whether AI outputs were reviewed.

AgentOps turns AI agent execution records, token estimates, review status, snapshots, risk indicators, and release readiness into observable, reviewable, and governable operational data.

### 7. Team_AgentOps

**中文話術**

Team_AgentOps 則是 AgentOps 的上一層。AgentOps 偏向觀測 Agent 執行；Team_AgentOps 則把這些執行紀錄接回人類團隊、專案進度、人工審核與交付責任。

這裡可以看到 Active Agents、Pending Review、Project Impact、Agent Activity Timeline、Project Contribution、Team Scorecard，以及 Shadow AI Risk。

重點是，Team_AgentOps 不是員工監控工具。它的目標是讓 AI Agent 從個人私下使用的工具，變成企業可管理、可稽核、可衡量貢獻的團隊資源。它只保存 safe metadata，不保存完整 prompt、response 或 raw sessions。

**English Talk Track**

Team_AgentOps sits one layer above AgentOps. AgentOps observes agent execution, while Team_AgentOps connects those records back to human teams, project progress, human review, and delivery accountability.

Here we can see Active Agents, Pending Review, Project Impact, Agent Activity Timeline, Project Contribution, Team Scorecard, and Shadow AI Risk.

The key point is that Team_AgentOps is not an employee surveillance tool. Its purpose is to turn AI agents from privately used individual tools into manageable, auditable, and measurable team resources. It stores safe metadata only and does not store full prompts, responses, or raw sessions.

### 8. Audit / Status

**中文話術**

最後是 Audit 與 Status。當系統開始串接 SOC、工單、專案與 AI Agent，就一定要有操作紀錄與健康狀態。

Audit 提供操作軌跡，Status 提供平台健康檢查。這讓系統不是只有畫面，而是有基本的信任基礎。

**English Talk Track**

Finally, Audit and Status provide the trust layer. Once a system connects SOC, tickets, projects, and AI agents, it needs operation trails and health visibility.

Audit provides operation history, while Status provides platform health checks. This makes the system more than just a dashboard. It gives it a basic trust foundation.

### 9. Closing

**中文話術**

所以 ENYRAX 的重點不是只有做 Dashboard，而是把事件、工單、專案、AI Agent 產出與人工審核流程，整理成一條可追蹤、可審核、可交付的營運流程。

對主管來說，可以看到進度與風險。對工程師來說，可以留下處理證據與審核紀錄。對企業來說，AI Agent 不再是 shadow AI，而是可以被治理的正式協作資源。

**English Talk Track**

So the key point of ENYRAX is not just building dashboards. It is about turning incidents, tickets, projects, AI agent outputs, and human review workflows into one traceable, reviewable, and deliverable operations process.

For managers, it provides visibility into progress and risk. For engineers, it preserves evidence and review records. For enterprises, AI agents no longer remain shadow AI, but become governed collaboration resources.

## 5-minute Extended Demo Script

### Opening

**中文話術**

我不是想做一個取代所有系統的大型 ERP，而是先做一個 operations command center，把原本分散的流程拉回同一個脈絡。它可以跟既有工具並存，但把事件、工單、專案與 AI Agent 產出串成可追蹤流程。

**English Talk Track**

The goal is not to replace every existing system like a large ERP. The goal is to build an operations command center that brings scattered workflows back into one context. It can coexist with existing tools while connecting incidents, tickets, projects, and AI agent outputs into a traceable workflow.

### 1. Portal Home

**中文話術**

這是 ENYRAX Portal 首頁。企業通常已經有很多工具，問題往往不是完全沒有工具，而是每個工具只看到一小段流程。ENYRAX 先用同一個入口整理 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps、Team_AgentOps 與 Audit / Status，讓操作人員與主管都能看見完整脈絡。

**English Talk Track**

This is the ENYRAX Portal home. Enterprises often already have many tools. The problem is that each tool sees only part of the workflow. ENYRAX provides one entry point for SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Team_AgentOps, and Audit / Status, so operators and managers can see the broader context.

### 2. SOC

**中文話術**

先從 SOC 開始。資安告警如果只停留在 log 或告警列表，很容易缺少責任人、修復進度與驗證證據。ENYRAX 把 alert 轉成 incident，再接到後續工單。這也是為什麼 SOC 與 ServiceOps 要接在一起：偵測之後必須有人執行、追蹤與結案。

**English Talk Track**

Starting with SOC, a security alert that stays only in logs or an alert list can easily lose ownership, remediation progress, and verification evidence. ENYRAX turns alerts into incidents and connects them to follow-up tickets. This is why SOC and ServiceOps belong together: detection must lead to execution, tracking, and closure.

### 3. ServiceOps

**中文話術**

ServiceOps 將日常維運整理成有狀態、有工作紀錄、有結案的流程。現成 ticketing system 很適合管理工單，但 ENYRAX 想補上的不是另一套孤立工單工具，而是事件來源、專案影響、AI 協作與稽核證據之間的連結。

**English Talk Track**

ServiceOps turns daily operations into a workflow with status, worklogs, and closure records. Existing ticketing systems are useful for ticket management. ENYRAX is not trying to create another isolated ticketing tool. It adds the context between event sources, project impact, AI collaboration, and audit evidence.

### 4. ProjectOps

**中文話術**

ProjectOps 再把零散工單接回交付層。維運工作可能影響基礎設施調整、里程碑與專案期限。把 SOC、ServiceOps 與 ProjectOps 串起來，主管才能從風險一路看到執行進度與交付影響。

**English Talk Track**

ProjectOps connects individual tickets back to delivery. Operational work can affect infrastructure changes, milestones, and project deadlines. Connecting SOC, ServiceOps, and ProjectOps lets managers follow risk through execution and see delivery impact.

### 5. Plan_ServiceOPS

**中文話術**

Plan_ServiceOPS 把平台收斂到使用者每天真正需要的工作畫面：今天有哪些優先項目、團隊有哪些待辦、哪些專案快到期。它不是增加另一個頁面，而是降低操作人員在不同模組間切換的成本。

**English Talk Track**

Plan_ServiceOPS focuses the platform on the operator’s daily view: today’s priorities, team queue items, and approaching project deadlines. It is not just another page. It reduces the cost of switching across modules to understand what matters today.

### 6. AgentOps

**中文話術**

接著是 AgentOps。AI Agent 可以加速分析、開發與文件工作，但如果執行紀錄只存在個人 chat history，企業無法知道產出是否經過 review，也無法建立責任邊界。AgentOps 保存執行狀態、token estimate、snapshot、risk 與 release readiness，讓 AI 協作可觀察、可審核。

**English Talk Track**

Next is AgentOps. AI agents can accelerate analysis, development, and documentation, but if execution records remain only in personal chat history, the enterprise cannot tell whether outputs were reviewed or establish responsibility boundaries. AgentOps records execution status, token estimates, snapshots, risk, and release readiness so AI-assisted work becomes observable and reviewable.

### 7. Team_AgentOps

**中文話術**

Team_AgentOps 把 AgentOps 再接回團隊、專案與人工審核。這裡特別重要的是 safe metadata：平台只保存執行狀態、專案關聯、review 狀態與 output reference，不保存完整 prompt、response 或 raw sessions。這樣既能治理 AI 使用，也避免蒐集不必要的敏感內容。

這不是員工監控。對工程師來說，留下 safe metadata、review 與責任邊界反而是一種保護。當 AI-assisted work 出現問題時，團隊有可核對的紀錄，不需要依賴口頭回憶，也不會把責任模糊地推回個人。

**English Talk Track**

Team_AgentOps connects AgentOps back to teams, projects, and human review. Safe metadata is especially important here: the platform stores execution status, project linkage, review status, and output references, but not full prompts, responses, or raw sessions. This supports governance without collecting unnecessary sensitive content.

This is not employee surveillance. For engineers, safe metadata, review records, and responsibility boundaries are protective. If AI-assisted work causes an issue, the team has records to review instead of relying on verbal memory or pushing ambiguous responsibility back onto an individual.

### 8. Audit / Status

**中文話術**

最後，Audit 與 Status 提供信任基礎。Audit 留下操作軌跡，Status 顯示平台健康。當事件、工單、專案與 AI Agent 都進入同一個營運脈絡時，這些紀錄讓流程可被檢查，也讓後續導入 auth、RBAC 與正式稽核政策有明確方向。

**English Talk Track**

Finally, Audit and Status provide the trust foundation. Audit preserves operation trails, and Status shows platform health. Once incidents, tickets, projects, and AI agents share an operational context, these records make the workflow reviewable and establish a clear path toward auth, RBAC, and formal audit policy.

### 9. Closing

**中文話術**

ENYRAX 展示的不是單一 Dashboard，而是一個可演進的 operations command center。它可以與既有工具並存，先把事件、執行、交付與 AI 協作治理接成一條可追蹤流程。

**English Talk Track**

ENYRAX is not a single dashboard. It is an evolvable operations command center that can coexist with existing tools while connecting incidents, execution, delivery, and AI collaboration governance into one traceable workflow.

## Interviewer Q&A

### 1. 這跟一般 ticketing system 有什麼不同？ / How is this different from a typical ticketing system?

**中文回答**

一般 ticketing system 主要管理工單本身，但 ENYRAX 想處理的是更完整的營運脈絡：事件從哪裡來、是否連到資安風險、是否影響專案、是否有 AI Agent 協助分析或修復、最後有沒有審核與結案證據。

所以它不是單純取代 ticketing system，而是把 ticket 放回 SOC、ProjectOps、AgentOps 與 Audit 的上下文裡。

**English Answer**

A typical ticketing system mainly manages tickets themselves. ENYRAX focuses on the broader operational context: where the event came from, whether it relates to security risk, whether it affects a project, whether an AI agent helped with analysis or remediation, and whether there is review and closure evidence.

So it does not simply replace a ticketing system. It puts tickets back into the context of SOC, ProjectOps, AgentOps, and Audit.

### 2. 這跟 Jira / ServiceNow / Power BI 有什麼不同？ / How is this different from Jira, ServiceNow, or Power BI?

**中文回答**

這些工具各自有成熟定位：Jira 偏任務與專案協作，ServiceNow 偏企業服務管理，Power BI 偏資料視覺化。ENYRAX 不宣稱取代它們。它展示的是 operations command center 的產品方向：把 SOC、工單、專案、每日工作與 AI Agent 治理放進同一個可追蹤脈絡，也可以在未來串接既有工具。

**English Answer**

These tools each have mature roles: Jira focuses on task and project collaboration, ServiceNow on enterprise service management, and Power BI on analytics and visualization. ENYRAX does not claim to replace them. It demonstrates an operations command center direction that connects SOC, tickets, projects, daily work, and AI agent governance in one traceable context and can later integrate with existing tools.

### 3. 為什麼要自己做？ / Why build it yourself?

**中文回答**

我想展示的不只是套用單一工具，而是把實際營運痛點整理成產品流程的能力。從事件、工單、專案到 AI Agent 治理，這個原型讓我可以驗證資訊架構、操作流程與治理邊界，再決定哪些部分適合整合現成系統。

**English Answer**

The goal is to demonstrate more than configuring one tool. It shows how I translate operational pain points into a product workflow. This prototype lets me validate information architecture, operational flow, and governance boundaries across incidents, tickets, projects, and AI agents before deciding which parts should integrate with existing systems.

### 4. AI Agent 的資料怎麼避免變成隱私或監控問題？ / How do you avoid privacy or surveillance issues with AI agent data?

**中文回答**

設計原則是 data minimization 與 safe metadata。平台保存 Agent 執行狀態、專案關聯、人工審核狀態、風險指標與 output reference，不保存完整 prompt、response、raw session、credential 或 secret。正式導入時還需要搭配存取權限、保留政策與稽核政策。

**English Answer**

The design principle is data minimization through safe metadata. The platform stores agent run status, project linkage, human review status, risk indicators, and output references. It does not store full prompts, responses, raw sessions, credentials, or secrets. A production rollout would also require access control, retention policy, and audit policy.

### 5. Token 數字是否等於真實成本？ / Do token numbers equal actual cost?

**中文回答**

不等於。現在的 token 數字是 operational estimate，用來觀察趨勢、異常與工作量，不是 billing-grade 成本。若要做正式成本管理，需要接供應商帳務資料、模型定價版本與對帳流程。

**English Answer**

No. Current token values are operational estimates used for trends, anomalies, and workload visibility. They are not billing-grade costs. Formal cost management would require provider billing data, model pricing versions, and a reconciliation process.

### 6. Team_AgentOps 是否會變成員工監控？ / Will Team_AgentOps become employee surveillance?

**中文回答**

不會，我的設計刻意避免這個方向。Team_AgentOps 的定位是 governance and protection，不是 employee surveillance。它保存的是 safe metadata，例如 Agent 執行狀態、專案關聯、審核狀態與產出 reference，不保存完整 prompt、response 或 raw session。

對工程師來說，這反而是一種保護，因為 AI 協作有紀錄、有審核、有責任邊界，而不是出問題時只靠口頭回憶。

**English Answer**

No. The design intentionally avoids that direction. Team_AgentOps is positioned as governance and protection, not employee surveillance. It stores safe metadata such as agent run status, project linkage, review status, and output references. It does not store full prompts, responses, or raw sessions.

For engineers, this is actually protective because AI-assisted work becomes traceable, reviewed, and bounded by responsibility, instead of relying on verbal memory when something goes wrong.

### 7. 目前是 production ready 嗎？ / Is it production ready?

**中文回答**

目前是 working portfolio / prototype platform，不是完整 production ERP。有些模組是 static demo，有些已經 API-backed，也有 fixture-backed 資料。正式導入前需要補 auth、RBAC、audit policy、DB migration、backup / restore drill 與 security review。

**English Answer**

It is currently a working portfolio and prototype platform, not a full production ERP. Some modules are static demos, some are API-backed, and some data is fixture-backed. Production adoption would require auth, RBAC, audit policy, DB migration, backup and restore drills, and security review.

### 8. 如果要導入企業，第一步會怎麼做？ / What would be the first step for enterprise adoption?

**中文回答**

我會先選一條可控的流程做 pilot，例如 SOC incident 到 ServiceOps ticket，再接 Audit evidence。先定義角色、資料邊界、狀態流與成功指標，確認流程有價值後，再逐步加入 ProjectOps 與 AI Agent governance。

**English Answer**

I would start with a controlled pilot workflow, such as SOC incident to ServiceOps ticket to Audit evidence. First define roles, data boundaries, state flow, and success metrics. After proving value, expand into ProjectOps and AI agent governance.

### 9. 這跟你過去 IT 維運經驗有什麼關係？ / How does this relate to your IT operations experience?

**中文回答**

這個作品聚焦在維運現場常見的斷點：告警停在 log、工作散在訊息裡、工單與專案脫節、交付缺少證據、AI 協作缺少治理。我的目標是把這些斷點整理成可操作、可追蹤、可審核的產品流程。

**English Answer**

This work focuses on common operational gaps: alerts staying in logs, work scattered across messages, tickets disconnected from projects, delivery lacking evidence, and AI collaboration lacking governance. My goal is to turn those gaps into an operable, traceable, and reviewable product workflow.

### 10. 你在這個作品裡展示了什麼能力？ / What capabilities does this project demonstrate?

**中文回答**

它展示了我把維運需求轉成產品模組、把不同流程串成資訊架構、設計可展示原型、逐步加入 API-backed dashboard，以及處理 AI Agent 治理、safe metadata、稽核與部署邊界的能力。

**English Answer**

It demonstrates my ability to translate operations needs into product modules, connect workflows through information architecture, build demo-ready prototypes, incrementally add API-backed dashboards, and reason about AI agent governance, safe metadata, auditability, and deployment boundaries.

## Demo Sequence Checklist

| Step | Page            | Key Message                         |
| ---- | --------------- | ----------------------------------- |
| 1    | Portal Home     | ENYRAX 是 operations command center |
| 2    | SOC             | 資安事件轉成可處理 incident         |
| 3    | ServiceOps      | 工單有狀態、有紀錄、有結案          |
| 4    | ProjectOps      | 工單接回專案進度                    |
| 5    | Plan_ServiceOPS | 使用者知道今天先做什麼              |
| 6    | AgentOps        | AI Agent 執行可觀察、可治理         |
| 7    | Team_AgentOps   | AI Agent 成為可管理團隊資源         |
| 8    | Audit / Status  | 操作證據與平台健康                  |

## Do / Don’t During Demo

### Do

* 強調產品脈絡，不要只講技術。
* 強調可追蹤、可審核、可交付。
* 強調 safe metadata。
* 強調 AI Agent 是協作資源，不是黑箱工具。
* 強調工程師保護與責任邊界。

### Don’t

* 不要說這已經是完整 production ERP。
* 不要誇大成已取代 ServiceNow / Jira。
* 不要說 token estimate 是正式成本。
* 不要說 Team_AgentOps 是員工績效評分。
* 不要展示或宣稱保存 raw prompt / response。

## Current Release Anchors

* `v0.6.24-agentops-bilingual-demo-dashboard`：提供 AgentOps 雙語 Demo dashboard，讓 AI Agent 執行紀錄、review 與風險更容易在面試中說明。
* `v0.6.25-plan-serviceops-personal-work-queue`：提供 Plan_ServiceOPS 個人每日工作佇列，聚合今日待辦、團隊待辦與專案截止日。
* `v0.6.26-plan-serviceops-api-backed-dashboard`：將 Plan_ServiceOPS 推進為 API-backed dashboard，並保留 demo fallback。
* `v0.6.27-team-agentops-static-prototype`：建立 Team_AgentOps static prototype，展示人類團隊與 AI Agent 協作治理概念。
* `v0.6.28-team-agentops-api-backed-dashboard`：將 Team_AgentOps 推進為 API-backed dashboard，支援 role filtering 與 frontend demo role switcher。

## Scope Boundary

目前 ENYRAX 是作品集與原型平台，不是完整 production ERP。它展示的是我如何把企業營運流程、資安事件、維運工單、專案管理與 AI Agent 治理整合成一套可展示、可演進的平台。

* It is a working portfolio / prototype platform.
* Some modules are static demos.
* Some modules are API-backed.
* Some data is fixture-backed.
* It is not a full production ERP.
* It is not a replacement for every enterprise system.
* AI cost values are operational estimates.
* AI governance modules store safe metadata only.
* Production deployment would require auth, RBAC, audit policy, DB migration, backup / restore drill, and security review.


## Related Rehearsal Notes

For timing, pacing, and 3-minute delivery practice, see `docs/enyrax_3min_demo_rehearsal_notes.md`.

若需要 3 分鐘展示節奏、轉場與演練筆記，請參考 `docs/enyrax_3min_demo_rehearsal_notes.md`。

## AgentOps Product Family Navigation

* Task #185 defines AgentOps as an AI Agent Governance product family.
* The family includes Server_AgentOps, Personal_AgentOps, and Team_AgentOps.
* Recommended navigation keeps AgentOps as the top-level entry and groups submodules under an AgentOps Hub.
* This avoids top navigation overload and prepares future Server / Personal AgentOps modules.
* No frontend, backend, DB, API, release, or deployment changes were made.

## Task #186 AgentOps Hub Static Prototype

* Task #186 adds `/agentops-hub/` static prototype.
* The Hub groups Server_AgentOps, Personal_AgentOps, Team_AgentOps, and existing AgentOps Dashboard.
* It keeps existing `/agentops/` and `/team-agentops/` routes intact.
* It updates Portal homepage entry.
* It remains static frontend only.
* No backend, DB, API, fixtures, release, or deployment changes were made.

## Task #187 Server_AgentOps Product Concept Design

* Task #187 defines Server_AgentOps as the server-side AI and automation run governance module.
* It covers Codex runs, parser jobs, snapshot jobs, backup jobs, deployment checks, release checks, and scheduled tasks.
* It stores safe metadata only.
* It does not replace Status, BackupOps, AuditOps, or general observability.
* It prepares Task #188 static dashboard prototype.
* No frontend, backend, DB, API, release, or deployment changes were made.


## Task #195 271ops Product Concept Design

* Task #195 defines 271ops as the ISO27001 readiness and security governance preparation module.
* It turns daily operations, incident handling, access review, backup evidence, and AI governance records into audit-ready governance evidence.
* It does not replace consultants, auditors, certification bodies, or formal compliance decisions.
* It integrates SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Team_AgentOps, Server_AgentOps, Audit Logs, Status, and Sync Gateway.
* It prepares Task #196 static dashboard prototype.
* No frontend, backend, DB, API, release, or deployment changes were made.


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
