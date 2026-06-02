# ENYRAX 3-minute Demo Rehearsal Notes

Timing, pacing, transition lines, and key messages for interview demo delivery

## Demo Goal

這份演練筆記的目標，是把 ENYRAX 從完整產品文件濃縮成 3 分鐘內可以講清楚的展示節奏。

面試時不需要把每個功能講完，而是要讓對方快速理解：ENYRAX 是一套 enterprise operations command center，能把 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps、Team_AgentOps 與 Audit / Status 串成可追蹤、可審核、可交付的流程。

The goal of this rehearsal note is to compress the full ENYRAX product story into a clear 3-minute interview demo flow.

The purpose is not to explain every feature. The purpose is to help the interviewer quickly understand that ENYRAX is an enterprise operations command center that connects SOC, ServiceOps, ProjectOps, Plan_ServiceOPS, AgentOps, Team_AgentOps, and Audit / Status into one traceable, reviewable, and deliverable workflow.

## 3-minute Timing Plan

|      Time | Page / Section           | Goal                                      |
| --------: | ------------------------ | ----------------------------------------- |
| 0:00–0:25 | Portal Home              | 建立 ENYRAX 是 operations command center  |
| 0:25–0:50 | SOC                      | 說明資安事件如何進入處理流程              |
| 0:50–1:15 | ServiceOps               | 說明工單如何有狀態、有紀錄、有結案        |
| 1:15–1:40 | ProjectOps               | 說明工單如何接回專案進度                  |
| 1:40–2:00 | Plan_ServiceOPS          | 說明每天打開先知道要做什麼                |
| 2:00–2:30 | AgentOps                 | 說明 AI Agent 執行紀錄如何可觀察、可治理  |
| 2:30–2:50 | Team_AgentOps            | 說明 AI Agent 如何成為團隊可管理資源      |
| 2:50–3:00 | Audit / Status + Closing | 收束成可追蹤、可審核、可交付              |

如果時間不足，可以把 ProjectOps 與 Plan_ServiceOPS 合併講，把 Audit / Status 放在 closing 一句帶過。

## 3-minute Spoken Script

### Opening / Portal Home

**切換提示：先從首頁看整體模組入口。**

這是 ENYRAX Portal 首頁。我把它定位成企業營運戰情中心，不是單一工單系統，也不是單一 Dashboard。

這裡把 SOC、ServiceOps、ProjectOps、Plan_ServiceOPS、AgentOps、Team_AgentOps 都放在同一個入口，目標是把分散的事件、工單、專案與 AI Agent 工作紀錄，整理成一條可追蹤流程。

### SOC

**切換提示：接著看事件從哪裡進來。**

先看 SOC。這一層處理資安事件與風險。

我的想法是，資安告警不應該只停在 log 或 dashboard，而是要轉成可以指派、追蹤、驗證與結案的 incident。後面可以再接到 ServiceOps 的處理工單。

### ServiceOps

**切換提示：事件後面要能變成處理工單。**

接著是 ServiceOps。這裡管理維運工單與服務請求。

很多 IT 工作會散在訊息、Email 或口頭交辦裡，ServiceOps 的價值是把工作變成有狀態、有進度、有紀錄、有結案的流程。

### ProjectOps

**切換提示：工單也要接回專案與交付。**

再來是 ProjectOps。工單不應該只是零散任務，很多工單其實會影響專案時程或基礎設施交付。

所以 ProjectOps 把工作接回專案、里程碑、起訖時間與交付狀態，讓主管可以看整體進度。

### Plan_ServiceOPS

**切換提示：對個人來說，最重要是今天先做什麼。**

Plan_ServiceOPS 是比較貼近使用者每天會打開的頁面。

它回答的是：今天我應該先處理什麼？它把今日待辦、團隊待辦與專案截止日整理在一起，讓維運人員不用到處翻頁面。

### AgentOps

**切換提示：AI Agent 的工作也需要治理。**

AgentOps 是 AI Agent 治理層。企業開始使用 AI 之後，很容易變成大家都有用，但執行紀錄留在看不見的 chat history 裡。

AgentOps 把 Agent 執行、review 狀態、snapshot、risk 與 release readiness 轉成可觀察、可審核的營運資料。

### Team_AgentOps

**切換提示：再往上看團隊如何管理 AI Agent。**

Team_AgentOps 則是 AgentOps 的上一層。AgentOps 偏向觀測單次 Agent 執行，Team_AgentOps 則把這些執行接回團隊、專案進度、人工審核與交付責任。

重點是它不是員工監控工具。它只保存 safe metadata，不保存完整 prompt、response 或 raw session，目標是讓 AI Agent 從個人工具變成企業可管理、可稽核的團隊資源。

### Closing

**切換提示：最後看平台信任基礎。**

所以 ENYRAX 的重點不是只有做 Dashboard，而是把資安事件、工單、專案、AI Agent 產出與人工審核流程，串成一條可追蹤、可審核、可交付的營運流程。

對主管來說可以看見進度與風險；對工程師來說，可以留下處理證據與責任邊界；對企業來說，AI Agent 不再是 shadow AI，而是可以治理的協作資源。

## 30-second Emergency Version

### 中文

ENYRAX 是我做的一套企業營運戰情中心，核心是把資安事件、維運工單、專案進度與 AI Agent 工作紀錄串成一條可追蹤流程。

傳統企業常常是 SOC 看 SOC、工單看工單、專案看專案，AI Agent 又變成個人私下使用的工具。ENYRAX 把這些東西拉回同一個平台，讓事件可以轉成工單，工單可以連到專案，AI Agent 產出可以被審核，最後回到交付與稽核紀錄。

### English

ENYRAX is an enterprise operations command center that connects security incidents, service tickets, project progress, and AI agent work into one traceable workflow.

In many companies, SOC, ticketing, and project management are separated, while AI agents are often used privately by individuals. ENYRAX brings these activities back into one platform, where incidents become tickets, tickets link to projects, AI outputs are reviewed, and delivery can be traced and audited.

## 5-minute Expansion Points

### 1. 為什麼不是單純 ticketing system？

工單只是流程裡的一段。ENYRAX 想處理的是事件從哪裡來、工單影響哪個專案、AI Agent 做了什麼、最後如何留下交付與稽核證據。

### 2. 為什麼 SOC / ServiceOps / ProjectOps 要串起來？

資安告警如果只停在 log 裡，就沒有後續責任。串起來之後，可以從 incident 一路追到處理工單、專案影響與結案證據。

### 3. 為什麼 Plan_ServiceOPS 很重要？

平台不只要給主管看，也要讓第一線人員每天真的能用。Plan_ServiceOPS 直接回答今天先做什麼，降低使用者在不同頁面來回切換的成本。

### 4. 為什麼 AgentOps 是 AI 時代的新治理層？

AI 工具很容易只留下個人的 chat history。AgentOps 把執行狀態、review、snapshot 與 risk 整理成營運資料，讓 AI-assisted work 可以被觀察與審核。

### 5. 為什麼 Team_AgentOps 不是員工監控？

它關注的是 AI 協作流程，不是對員工做績效監控。留下 review 狀態、專案關聯與責任邊界，反而能在出現問題時保護工程師與團隊。

### 6. safe metadata 為什麼重要？

治理不代表要保存所有敏感內容。只保留執行狀態、專案關聯、review 狀態與 output reference，就能追蹤流程，同時避免保存完整 prompt、response 或 raw session。

### 7. 這套作品展示了什麼能力？

它展示的是把維運、資安、專案與 AI 工具拆成可操作模組，再串回同一條責任流程的能力。也展示了我能定義資料邊界、做出可展示原型，並保留後續演進方向。

## Strongest Lines

* ENYRAX 不是單一工單系統，也不是單一 Dashboard，而是一套 enterprise operations command center。
* 我想解決的不是單一頁面，而是企業裡事件、工單、專案與 AI Agent 產出彼此斷開的問題。
* AgentOps 把看不見的 AI chat history 轉成可觀察、可審核、可治理的營運資料。
* Team_AgentOps 不是員工監控工具，而是讓 AI 協作有紀錄、有審核、有責任邊界。
* AI Agent 不應該只是個人私下使用的工具，而應該成為企業可管理、可稽核、可衡量貢獻的協作資源。
* 這套作品展示的是我把二十多年 IT 維運、資安、專案與 AI 工具整合成平台的能力。

## Page Switching Cues

| Step | Page            | Cue Sentence                       |
| ---: | --------------- | ---------------------------------- |
|    1 | Portal Home     | 先從首頁看整體模組入口             |
|    2 | SOC             | 接著看事件從哪裡進來               |
|    3 | ServiceOps      | 事件後面要能變成處理工單           |
|    4 | ProjectOps      | 工單也要接回專案與交付             |
|    5 | Plan_ServiceOPS | 對個人來說，最重要是今天先做什麼   |
|    6 | AgentOps        | AI Agent 的工作也需要治理          |
|    7 | Team_AgentOps   | 再往上看團隊如何管理 AI Agent      |
|    8 | Audit / Status  | 最後看平台信任基礎                 |

## Timing Risk Notes

| Risk | Control Suggestion |
| ---- | ------------------ |
| SOC 解釋太久。 | 只講 alert 轉成 incident，再接 ServiceOps 工單；案例最多一句。 |
| ServiceOps 工單細節講太多。 | 聚焦有狀態、有進度、有紀錄、有結案，不逐欄位展示。 |
| AgentOps / Team_AgentOps 太興奮講太久。 | AgentOps / Team_AgentOps 是亮點，但 3 分鐘版只講產品價值，不展開 schema / API / token 細節。 |
| Q&A 提前插入導致主線中斷。 | 先用一句話回答，再說稍後可以展開，立刻回到下一個頁面。 |
| 太快進技術細節，例如 FastAPI、PostgreSQL、Wazuh、snapshot schema。 | 3 分鐘版先講問題、流程與價值；技術選型留到 Q&A 或 5 分鐘延伸版。 |

## If Interviewer Interrupts

### 問：這可以 production 用嗎？

目前我會定位成 working portfolio / prototype platform。它已經有部分 API-backed 模組與部署驗證，但如果要 production 導入，還需要正式 auth、RBAC、audit policy、DB migration、backup / restore drill 與 security review。

### 問：這是不是取代 ServiceNow / Jira？

我不會把它定位成直接取代 ServiceNow 或 Jira，而是 operations command center。它可以跟既有系統並存，把事件、工單、專案與 AI Agent 產出拉回同一個營運脈絡。

### 問：Team_AgentOps 會不會變成監控員工？

這點我刻意避免。Team_AgentOps 是 governance and protection，不是 employee surveillance。它只保存 safe metadata，例如 Agent 執行狀態、專案關聯、review 狀態與 output reference，不保存完整 prompt、response 或 raw session。

## Personal Closing Statement

### 中文

這套作品其實是把我過去二十多年 IT 維運、資安事件處理、專案協作與現在 AI Agent 工具的經驗整合起來。

我不是只想展示會寫程式，而是想展示我能把混亂的企業流程拆成模組、定義資料邊界、設計責任流程，最後把它做成可以操作、可以展示、可以繼續演進的平台。

### English

This project brings together my experience in IT operations, security incident handling, project coordination, and modern AI agent tools.

I am not only trying to show that I can write code. I am trying to show that I can break down complex enterprise workflows into modules, define data boundaries and responsibility flows, and turn them into a platform that can be operated, demonstrated, and continuously improved.

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
