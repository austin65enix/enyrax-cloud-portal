# AgentOps Dashboard Preview Release Note

## Overview

This release moves AgentOps from preview parser / review pipeline work into a Dashboard Preview presentation release.

AgentOps Dashboard Preview provides operational visibility into AI agent / Codex work records, token usage estimates, preview review quality, safe metadata classification, trend snapshot, release readiness, and rule-based risk indicators.

## Completed Scope

* Dashboard Metrics Design
* AgentOps Preview Dashboard UI
* Visual QA / responsive pass
* Explainability Demo Notes
* Trend Snapshot
* Release Quality Score
* Risk & Anomaly Detection

## Dashboard Features

* KPI cards
* Project Distribution
* Task Distribution
* Token Normalization Summary
* Review Health Summary
* Metric Semantics
* Trend Snapshot
* Release Quality Score
* Risk & Anomaly Detection

## Current Metrics

* records: 50
* review status: passed
* total_tokens: 50,078,459
* original total_tokens: 1,058,156,153
* token normalization reduction: approx. 95.3%
* project coverage: 100%
* task coverage: 100%
* unknown models: 0
* zero token records: 0
* forbidden hits: 0
* extra fields: 0
* Release Quality Score: 98 / 100
* Overall Risk Level: Low
* Blocking Risks: 0
* Caution Items: 3

## Safety and Semantic Boundaries

* AgentOps does not inspect prompt / response content.
* Content-based inference remains prohibited.
* Token values are operational estimates, not billing-grade cost data.
* Project / task values may be pipeline-level metadata classifications.
* Trend data is dashboard preview sample data, not full historical telemetry.
* Release Quality Score is not AI answer quality.
* Risk indicators are not session-content-level correctness.

## Known Cautions

* Token estimate caution
* Classification semantics caution
* Trend sample data caution

The current overall risk level is Low, but it is not no risk.

## AgentOps Historical Snapshots Schema Design

Task #130 defines the historical snapshot schema for future real Trend Chart data.

Snapshot v1 stores aggregate dashboard-level operational metrics. Snapshot v1 does not store prompt / response, shell output, command text, diff, file contents, raw JSONL, credentials, or full home paths.

Recommended MVP storage is JSON files under `data/agentops/snapshots/`. Token values remain operational estimates, not billing-grade cost data. Project / task values may remain pipeline-level metadata classifications.

Future work should implement snapshot generation in Task #131.

## Review Result

* review status: passed
* forbidden_hits: {}
* extra_fields: {}
* unknown_project_count: 0
* unknown_task_count: 0

## Non-goals

* no parser changes
* no schema changes
* no backend API changes
* no preview JSON regeneration
* no historical telemetry storage
* no billing-grade cost reporting
* no AI answer quality scoring
* no session-content-level project/task correctness claim

## Recommended Next Steps

* Historical snapshots schema design
* Real trend data generation
* pipeline_project / session_project schema split
* pipeline_task / session_task schema split
* future AgentOps audit export
* future risk rule configuration

## AgentOps Snapshot Generation

Task #131 implements the first snapshot generator.

Generator reads `review_agentops_preview.py --json` aggregate review output.

Generator does not read raw session files or prompt / response content.

Generated snapshots are stored under `data/agentops/snapshots/`.

First generated snapshots:

* `data/agentops/snapshots/daily/2026-05-31.json`
* `data/agentops/snapshots/releases/v0.6.22-agentops-dashboard-preview.json`

Snapshot values remain operational estimates and dashboard-level indicators.

## AgentOps Snapshot Trend Integration

Task #132 connects Trend Snapshot UI to historical snapshot index data.

Trend UI uses `data/agentops/snapshots/index.json` when available.

If snapshot index is unavailable, UI falls back to static sample data.

Snapshot index contains aggregate dashboard-level metrics only.

Snapshot trend values remain operational indicators.

Token values are not billing-grade cost data.

Project / task coverage does not imply content-level classification accuracy.

No prompt / response content is used.


## AgentOps Snapshot Index Publish Path

Task #133 documents how `/data/agentops/snapshots/index.json` should be served by nginx.

Only `/data/agentops/snapshots/` should be exposed, not the entire `/data/` tree. Snapshot files contain aggregate operational metrics only. The restricted publish path must not expose preview fixtures or other present or future files under `/data/`.

The nginx rule should use `root /var/www/enyrax-portal`, add `Cache-Control: no-store` for preview dashboard freshness, and return `404` for the remaining `/data/` tree. Trend UI falls back to clearly labeled sample data if the snapshot index is unavailable.
