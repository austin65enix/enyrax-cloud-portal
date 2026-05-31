# Plan_ServiceOPS Personal Work Queue Release Note

Version: `v0.6.25-plan-serviceops-personal-work-queue`

## Overview

Plan_ServiceOPS Personal Work Queue is the first static demo release of a personal daily operations cockpit for IT operators. It brings today’s personal tickets, blocked team tickets, and upcoming project deadlines into one focused dashboard.

Plan_ServiceOPS Personal Work Queue 是給維運人員每天打開使用的個人工作中控台。它把今日個人待辦、團隊卡住的工單、以及專案截止日集中到同一個畫面，讓使用者不用進多個系統查詢，也能知道今天優先處理什麼。

* 它不是取代 ServiceOps。
* 它不是取代 ProjectOps。
* 它是 ServiceOps + ProjectOps 的個人入口層。
* 它把傳統工單系統從 passive query tool，推進成 proactive daily operations cockpit。

## Completed Scope

* Task #147：Plan_ServiceOPS Personal Work Queue Design
* Task #148：Plan_ServiceOPS Personal Work Queue UI Prototype
* Task #149：Plan_ServiceOPS Visual QA and Interaction Review

## Key Features

### Personal Work Queue Dashboard

* 新增 `/plan-serviceops/` static page。
* 顯示 Plan_ServiceOPS / Personal Work Queue Dashboard / 個人每日工作中控台。
* 使用 dark glass ENYRAX visual style。
* 使用 static demo data。

### Summary Cards

包含：

* Today Tickets: 5
* Doing: 2
* Overdue: 1
* Nearest Deadline: D-14
* Blocked Team Tickets: 3

中文：

* 今日待辦：5
* 進行中：2
* 逾期：1
* 最近專案截止：D-14
* 團隊卡住：3

### Today Tickets

顯示個人今日待辦：

* ERP Test VM Request
* AD Account Unlock
* Wazuh Agent Install Check

特性：

* 依 High → Medium → Low 排序。
* priority badge 可讀。
* status badge 可讀。
* status button 可切換 Pending → Doing → Done → Pending。
* refresh 後恢復 demo data。

### Team Queue

顯示團隊待辦：

* Firewall Rule Change
* Suspicious SSH Alert
* Shared Printer Issue

特性：

* 包含 Blocked / Pending / Doing。
* 顯示 waiting reason。
* 顯示 SLA。
* 不做互動切換。

### Project Deadlines

顯示專案截止日：

* ERP Upgrade：D-14
* Wazuh Rollout：D-19
* AD Permission Review：D-29

特性：

* 顯示 owner。
* 顯示 deadline。
* 顯示 remaining days。
* 顯示 related ticket count。

### Portal Homepage Entry

首頁已新增 Portal card：

* Title: Plan_ServiceOPS
* Subtitle: Personal Work Queue
* Route: `/plan-serviceops/`
* Status: STATIC DEMO

### Visual QA and Interaction QA

已驗證：

* Desktop 1240 / 1366 / 1440px
* Tablet 768 / 820px
* Mobile 390 / 430 / 520px
* Pending → Doing → Done → Pending
* Team Queue 與 Project Deadlines 保持非互動
* `/plan-serviceops/` 200 OK
* `/` 200 OK

## Product Positioning

| Module          | Purpose          |
| --------------- | ---------------- |
| ServiceOps      | 全部維運工單管理 |
| ProjectOps      | 專案時程與狀態   |
| Plan_ServiceOPS | 個人每日工作中控台 |
| SOC             | 資安事件來源     |
| Audit           | 操作紀錄與證據留存 |

ServiceOps 管全部工單，ProjectOps 管專案時程，Plan_ServiceOPS 則把個人今天需要看的事項集中成每日工作入口。

## Interview Demo Talk Track

中文：

```text
我做了一個 Plan_ServiceOPS 個人版，它不是取代原本的 ServiceOps，而是把維運人員每天最需要看的三件事集中起來：今天待辦 ticket、團隊卡住的 ticket、以及專案截止日。這樣使用者一打開頁面，不用進多個系統查詢，就能知道今天優先處理什麼。
```

英文：

```text
I built Plan_ServiceOPS as a personal work queue dashboard for IT operators. It does not replace the full ServiceOps module. Instead, it brings together the three things operators need to see every day: today’s tickets, blocked team tickets, and upcoming project deadlines. The goal is to help users know what to prioritize as soon as they open the page.
```

產品價值：

中文：

```text
它把傳統工單系統從被動查詢，改成每日主動工作中控台。
```

英文：

```text
It turns a traditional ticketing system from a passive query tool into a proactive daily operations cockpit.
```

## Scope Boundary

本 release 不包含：

* no backend implementation
* no DB migration
* no new API
* no ServiceOps behavior change
* no ProjectOps behavior change
* no auth behavior change
* no production data integration
* no deployment config change

## Known Limitations

* 第一版使用 demo data。
* Status toggle 只存在前端 local state。
* refresh 後恢復 demo data。
* 尚未接 ServiceOps / ProjectOps API aggregation。
* 尚未接 DB。
* 尚未接 role-based filtered data。
* 尚未產生真正 workload report。

## Recommended Next Steps

* Task #151：Plan_ServiceOPS Release Tag
* Task #152：Plan_ServiceOPS API Aggregation Design
* Task #153：Plan_ServiceOPS Read-only API Prototype
* Task #154：Plan_ServiceOPS Role-based View Design
* Task #155：Plan_ServiceOPS Snapshot / Daily Summary Design
