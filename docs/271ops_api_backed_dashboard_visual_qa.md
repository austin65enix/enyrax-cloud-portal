# 271ops API-backed Dashboard Visual QA

## Overview

This document records the Task #202 visual QA for the 271ops API-backed read-only dashboard after the frontend API switch.

本文件記錄 Task #202：271ops frontend API switch 後的 API-backed read-only dashboard 視覺 QA。

## Reviewed Page

* `/271ops/`
* `GET /api/271ops/dashboard`

## API DATA QA

* `/271ops/` returned HTTP 200.
* The dashboard API returned `source=fixture`, `mode=read_only`, `product=271ops`, `display_name=271ops`, `production_data=false`, and `certification_claim=false`.
* Readiness score is `68`.
* Record counts are risks `4`, evidence queue `9`, access reviews `4`, AI governance evidence `4`, and audit checklist `6`.
* Boundary flags are `readiness_preparation_only=true`, `not_certification_score=true`, `not_legal_assurance=true`, `not_audit_approval=true`, and `safe_references_only=true`.
* API warnings are `[]`.
* API success renders `API DATA / API 資料`, KPI cards, all six main data arrays, and the Safety / Compliance Boundary.
* API success does not display `DEMO FALLBACK / DEMO 備援`.

## DEMO FALLBACK QA

A temporary DOM / JS harness validated these failure paths:

* fetch throws an error
* HTTP response is non-200
* JSON parsing fails
* schema has an invalid product
* schema has an invalid mode
* schema has `certification_claim=true`
* schema is missing `summary.readiness_score`
* schema is missing a required array

All failure paths render `DEMO FALLBACK / DEMO 備援` and show this fallback note:

```text
Using local demo fallback because the 271ops API is unavailable or returned invalid data.
因 271ops API 無法使用或資料格式不完整，目前使用本機 Demo 備援資料。
```

The harness confirmed that fallback KPI cards, all six main data arrays, and the Safety / Compliance Boundary remain populated. The page does not become blank and no uncaught error is produced.

## Responsive QA

Browser screenshot tooling was not available, so this QA used static HTML/CSS responsive checks, HTTP validation, and JS harness checks.

執行環境沒有可用的瀏覽器截圖工具，因此本次 QA 以 HTML/CSS responsive 檢查、HTTP 驗證與 JS harness 檢查為主。

Static responsive checks covered the requested viewport classes:

| Device | Width x Height | Static responsive result |
| --- | ---: | --- |
| Desktop | 1440 x 1200 | Four-column KPI grid and two-column dashboard layout apply. |
| Laptop | 1366 x 900 | Four-column KPI grid and two-column dashboard layout apply. |
| Tablet | 820 x 1180 | KPI cards wrap to two columns; hero and dashboard layout become one column. |
| Tablet narrow | 768 x 1024 | KPI cards wrap to two columns; hero and dashboard layout remain one column. |
| Mobile | 390 x 844 | KPI cards, overview, sources, and checklist become one column. |
| Mobile wide | 430 x 932 | KPI cards, overview, sources, and checklist become one column. |

The CSS retains `max-width:100%`, `overflow-x:hidden`, `min-width:0`, `overflow-wrap:anywhere`, a scrollable evidence matrix wrapper, and mobile `word-break:break-word`. Long labels, the mode badge, and the ISO27001 subtitle can wrap without forcing horizontal page scroll.

## Copy and Certification Boundary QA

* The page states: `Demo readiness estimate only. Not an ISO27001 certification score.`
* The page states: `僅為 Demo 準備度估算，不代表 ISO27001 認證分數。`
* The Safety / Compliance Boundary states that 271ops does not claim ISO27001 certification, legal assurance, or audit approval.
* The hero boundary states that 271ops does not replace consultants, auditors, certification bodies, or formal compliance decisions.
* API metadata keeps `production_data=false` and `certification_claim=false`.
* The page retains `No secrets`, `No raw logs by default`, `No raw prompt / response`, and `Safe references only` boundaries.

## Accessibility QA

* The page has one `<h1>` and a viewport meta tag.
* `Back to Portal` links to `/`; no empty links were found.
* KPI cards have text labels and values.
* Ready, Partial, Missing, API DATA, and DEMO FALLBACK states include text and do not rely only on color.
* Mixed Chinese and English copy can wrap.
* Existing foreground colors, bordered badges, and panel backgrounds provide reasonable visual contrast for this prototype.

## No API Mutation QA

* Frontend uses only implicit `GET /api/271ops/dashboard` through `fetch('/api/271ops/dashboard')`.
* It does not call individual fixture endpoints.
* It does not call POST, PUT, PATCH, or DELETE.
* It does not write `localStorage` or `sessionStorage`.
* It does not upload files.
* It does not add create, update, approve, or reject buttons.
* It does not load a shared shell script that performs storage writes.

## Issues Found

* Issue: dynamic API and fallback rendering replaced the static Safety / Compliance Boundary without preserving `No secrets` and `No raw logs by default`.
* Fix: restored both safety statements in the dynamically rendered boundary.
* File: `271ops/index.html`

* Issue: non-empty API warnings had no visible dashboard strip.
* Fix: added a warnings strip that remains hidden for `warnings=[]` and displays safe warning text when warnings are present.
* File: `271ops/index.html`

No blocking visual, copy, or API-backed rendering issues found.

未發現阻塞性的視覺、文案或 API-backed render 問題。

## Decision

Task #202 visual QA passed. 271ops API-backed dashboard is ready for release note preparation.

Task #202 視覺 QA 通過。271ops API-backed dashboard 可進入 release note 整理。
