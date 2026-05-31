# AgentOps Bilingual Demo Dashboard Release Note

## Overview

AgentOps Bilingual Demo Dashboard improves the AgentOps page for interview and product demo scenarios. It adds Chinese / English explanation copy, clarifies the privacy boundary, explains Preview Dashboard metrics, Release Quality Score, Risk & Anomaly Detection, Trend Snapshot, Snapshot Retention Health, and restructures the Preview Dashboard into a full-width layout for better readability.

AgentOps Bilingual Demo Dashboard 將 AgentOps 頁面調整為適合面試展示與產品 demo 的中英雙語儀表板。它補上中文定位、隱私邊界、Preview Dashboard 指標語義、Release Quality Score、Risk & Anomaly Detection、Trend Snapshot、Snapshot Retention Health 與面試展示重點，並修正 Preview Dashboard 被限制在左欄的 layout 問題。

## Release Version

```text
v0.6.24-agentops-bilingual-demo-dashboard
```

## Completed Scope

* Task #143: AgentOps Dashboard Chinese Copy Integration
* Task #144: AgentOps Bilingual Dashboard Layout QA
* Task #144.5: AgentOps Preview Dashboard Full-width Layout Fix

## Key Features

### Bilingual Positioning Copy

* Hero area now includes Chinese / English AgentOps positioning.
* Explains AgentOps as AI Agent workflow observability, governance, and delivery telemetry.
* Adds interview-friendly wording.

### Privacy Boundary Explanation

* Adds Chinese / English explanation that AgentOps does not inspect prompt / response content.
* Clarifies that it only uses safe metadata.
* Reinforces that credentials, API keys, `.env` values, file contents, and raw session data are not stored.

### Preview Dashboard Explanation

* Adds Chinese helper copy for Preview Dashboard.
* Explains preview records, review status, token estimates, project/task coverage, forbidden hits, extra fields, and token normalization.
* Keeps operational-estimate warning.

### Release Quality Score Explanation

* Adds Chinese explanation that Release Quality Score is preview readiness, not AI answer quality.
* Keeps session-content-level correctness warning.

### Risk & Anomaly Explanation

* Adds Chinese labels and explanations for:
  * Review Failure Risk
  * Forbidden Hits Risk
  * Schema Drift Risk
  * Unknown Model Risk
  * Zero Token Records Risk
  * Token Overcounting / Estimate Risk
  * Classification Semantics Risk
  * Trend Sample Data Risk

### Trend Snapshot Explanation

* Adds Chinese explanation for snapshot-backed trend.
* Keeps warning that trend values are aggregate dashboard metrics and not billing-grade cost data.

### Snapshot Retention Health Explanation

* Adds Chinese explanation for dry-run retention health.
* Clarifies:
  * dashboard is read-only
  * no snapshots are deleted
  * index is not modified
  * no auto commit / push
  * release snapshots are never pruned
  * unknown files require manual review

### Interview Demo Notes

* Adds a dedicated interview demo notes section.
* Highlights that AgentOps turns invisible chat history into observable, auditable, replayable, and governable operational data flow.

### Full-width Dashboard Layout

* Fixes missing closing section tag that caused Preview Dashboard to stay inside the left hero column.
* Moves Preview Dashboard below hero + Privacy Boundary row.
* Uses full-width desktop layout.
* Improves KPI and summary card readability.
* Preserves responsive stacking.

## Visual QA Notes

* Desktop layout: Hero + Privacy Boundary on first row; Preview Dashboard full width on second row.
* KPI grid: auto-fit minmax layout, less compressed.
* Summary cards: Project / Task / Token / Review cards use full-width two-column layout.
* Tablet / mobile stacking preserved.
* No horizontal overflow expected on mobile.
* Existing snapshot / retention fetch behavior unchanged.

## Safety and Semantic Boundaries

* AgentOps does not read prompt / response content.
* AgentOps does not store raw sessions.
* Token values remain operational estimates, not billing-grade cost data.
* Project / Task classification may remain pipeline-level metadata classification.
* Release Quality Score is not AI answer quality.
* Retention dashboard is dry-run / read-only only.
* No prune automation is introduced.
* No parser, backend, snapshot JSON, nginx, cron, or systemd changes were made.

## Current Verification

* `/agentops/`: 200 OK
* Inline JS extraction + `node --check`: passed
* `git diff --check`: passed
* HTML section / aside nesting check: balanced
* Mojibake scan: no hits
* Snapshot / retention fetch behavior unchanged

## Non-goals

* no parser changes
* no backend changes
* no snapshot regeneration
* no preview JSON regeneration
* no API change
* no nginx change
* no cron change
* no systemd change
* no retention prune
* no new data schema

## Recommended Next Steps

* Task #146: AgentOps Bilingual Demo Dashboard Release Tag
* Optional desktop / tablet / mobile screenshot archive
* Optional interview demo script page
* Optional short social post / project portfolio description
* Optional formal product one-pager
