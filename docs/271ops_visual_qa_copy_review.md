# 271ops Visual QA and Product Copy Review

## Overview

This document records the Task #197 visual QA and product copy review for the 271ops static dashboard.

本文件記錄 Task #197 的 271ops static dashboard 視覺 QA 與產品文案檢查。

## Reviewed Page

* `/271ops/`
* `/`

## Naming QA

* Primary UI brand is lowercase `271ops`.
* `271Ops` is treated as legacy spelling only.
* `/271ops/` route confirmed.
* The Portal homepage card uses lowercase `271ops`.

## Visual QA

Browser screenshot tooling was not available, so this QA used static HTML/CSS responsive checks and HTTP validation.

執行環境沒有可用的瀏覽器截圖工具，因此本次 QA 以 HTML/CSS responsive 檢查與 HTTP 驗證為主。

* Desktop checks cover the 1440 x 1200 and 1366 x 900 target layouts. The hero uses a bounded two-column grid, the subtitle can wrap, KPI cards use four columns, and detailed sections use balanced columns.
* Tablet checks cover the 820 x 1180 and 768 x 1024 target layouts. The `980px` breakpoint changes the hero and detail layout to one column and KPI cards to two columns.
* Mobile checks cover the 390 x 844 and 430 x 932 target layouts. The `600px` breakpoint changes KPI, overview, evidence source, and checklist grids to one column. Tables wrap long text and remain contained by `.table-wrap`.
* The Safety / Compliance Boundary is visible once beside the hero and again as a full-width section near the end of the dashboard.

## Copy Review

* `Readiness Score` is presented as a demo estimate, not an ISO27001 certification score.
* The readiness boundary states that 271ops does not replace consultants, auditors, certification bodies, or formal compliance decisions.
* Evidence Sources now states that the dashboard organizes safe references and summaries, not raw sensitive data.
* AI Governance Evidence now states that only safe metadata references are organized and raw prompt / response content is not stored.
* Dashboard labels remain readable for management and IT users without implying certification, legal assurance, or audit approval.

## Homepage Entry QA

* The Portal homepage card uses `271ops`.
* The card includes `ISO27001 Readiness & Security Governance`.
* The Chinese description explains that daily operations, incidents, access reviews, backup verification, and AI Agent governance are organized into security governance evidence.
* The card route is `/271ops/`.
* The card badge is `STATIC DEMO`.
* Existing AgentOps Hub, AgentOps, Team_AgentOps, and Plan_ServiceOPS entries remain present.

## Safety and Compliance Boundary QA

* The dashboard clearly states readiness preparation and evidence organization only.
* It makes no ISO27001 certification claim, legal assurance claim, or audit approval claim.
* It states: no secrets, no raw logs by default, no raw prompt / response, and safe references only.
* Formal decisions remain with management, auditors, consultants, and certified professionals.

## Accessibility and Responsive QA

* Status pills include text labels and do not rely on color alone.
* KPI cards have text labels.
* The page has one `<h1>` and a viewport meta tag.
* Navigation links are non-empty and the `Back to Portal` link points to `/`.
* Responsive grids, `min-width: 0`, overflow containment, and word wrapping prevent horizontal page overflow in the reviewed static CSS.
* English and Traditional Chinese copy can wrap without forcing narrow cards wider than the viewport.

## No API / No Mutation QA

* `/271ops/` is a static demo page.
* The dashboard does not fetch backend APIs.
* The dashboard does not write to localStorage or sessionStorage.
* The dashboard does not create, update, or upload data.
* The dashboard does not claim to show production data.

## Issues Found

* Issue: shared shell scripts could issue auth or status API requests and access browser storage on an otherwise static dashboard.
* Fix: removed shared shell script references from `/271ops/`.
* File: `271ops/index.html`
* Issue: safe-reference boundaries were clear in the final boundary block but less explicit near Evidence Sources and AI Governance Evidence.
* Fix: added concise bilingual safe-reference copy near those sections.
* File: `271ops/index.html`

No blocking visual or copy issues found.

未發現阻塞性的視覺或文案問題。

## Decision

Task #197 visual QA and product copy review passed. 271ops static dashboard is ready for demo data fixture design.

Task #197 視覺 QA 與產品文案檢查通過。271ops static dashboard 可進入 demo data fixture design。

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
