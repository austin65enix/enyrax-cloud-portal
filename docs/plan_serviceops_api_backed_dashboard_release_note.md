# Plan_ServiceOPS API-backed Dashboard Release Note

Version: `v0.6.26-plan-serviceops-api-backed-dashboard`

## Overview

Plan_ServiceOPS API-backed Dashboard upgrades the personal work queue from static demo data to API-first read-only aggregation. The page now fetches `/api/plan-serviceops/dashboard` and falls back to local demo data when the API is unavailable.

Plan_ServiceOPS API-backed Dashboard 將個人每日工作中控台從 static demo 推進到 API 優先的唯讀聚合模式。頁面會先讀取 `/api/plan-serviceops/dashboard`，如果 API 暫時不可用，則安全回退到本機 demo data。

## Completed Scope

* Task #152：Plan_ServiceOPS API Aggregation Design
* Task #153：Plan_ServiceOPS Read-only API Prototype
* Task #154：Plan_ServiceOPS Frontend API Switch with Demo Fallback
* Task #155：Plan_ServiceOPS API-backed Frontend QA and Release Note

## Key Features

* API-first dashboard loading
* Demo fallback
* API DATA / DEMO FALLBACK badge
* Read-only API mode
* Demo-only local status toggle
* Viewer empty state
* Role-aware API fetch
* Warnings strip
* No mutation

## Current Verification

* `/plan-serviceops/`: 200 OK
* operator: today=0, team=9, projects=4, warnings=[]
* supervisor: today=1, team=9, projects=4, warnings=[]
* viewer: today=0, team=0, projects=4, warnings=[]

## Scope Boundary

This release does not include:

* no DB migration
* no new table
* no ticket mutation
* no project mutation
* no audit write
* no ServiceOps behavior change
* no ProjectOps behavior change
* no deployment config change

## Known Limitations

* API mode is read-only.
* Status update is disabled in API mode.
* Demo fallback uses local demo data.
* Role handling still uses demo role semantics.
* No production permission model integration yet.

## Recommended Next Steps

* Task #156：Plan_ServiceOPS API-backed Dashboard Release Tag
* Task #157：Plan_ServiceOPS Role-based Filtering Refinement
* Task #158：Plan_ServiceOPS Status Update Design through ServiceOps API
* Task #159：Plan_ServiceOPS Workload Summary Metrics Design
