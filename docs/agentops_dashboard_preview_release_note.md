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

## AgentOps Snapshot Auto Update Workflow

Task #134 adds `scripts/update_agentops_snapshots.py`.

The auto update workflow generates daily snapshots and updates the snapshot index from aggregate review JSON only. It does not regenerate preview JSON and does not read raw sessions or prompt / response content.

This keeps snapshot trend data aligned with generated historical snapshots. Release snapshots remain explicit and require `--write-release`.

## AgentOps Snapshot Scheduled Update

Task #135 documents scheduled update deployment. The schedule runs `scripts/update_agentops_snapshots.py` to update the daily snapshot and snapshot index.

The schedule does not regenerate preview JSON and does not read raw sessions or prompt / response content. The first version does not auto commit or auto push generated files.

## AgentOps Snapshot Retention Policy

Task #137 defines retention policy for AgentOps snapshots. Daily snapshots retain the recent 30 days, while release snapshots are kept permanently.

The auto update workflow updates the working tree only and does not auto commit or auto push. This task does not delete snapshots. Future retention automation must start with dry-run reporting.

## AgentOps Snapshot Retention Dry-run Report

Task #138 adds `scripts/report_agentops_snapshot_retention.py`.

The script outputs a retention dry-run report. It does not delete snapshots, modify `index.json`, auto commit, or auto push. It does not read raw sessions or prompt / response content.

The report verifies daily snapshot retention, release snapshot permanence, unknown snapshot files, and index consistency. Future prune automation must build on the dry-run report first.

## AgentOps Retention Report Dashboard Integration

Task #140 adds a read-only retention dry-run summary to the AgentOps Dashboard. The Dashboard fetches `data/agentops/snapshots/retention_report.json` when available and displays daily snapshot retention, release snapshot permanence, unknown files, and index consistency.

The Dashboard does not delete snapshots, modify `index.json`, auto commit, or auto push. The retention report remains dry-run only. If the retention report is unavailable, the Dashboard falls back to a read-only unavailable state.

## AgentOps Historical Snapshot Governance Release

Task #141 packages Tasks #130-#140 as release `v0.6.23-agentops-historical-snapshot-governance`.

The release covers historical snapshots, trend integration, retention dry-run, and the Snapshot Retention Health dashboard summary. It preserves safety boundaries: no prompt / response or raw session content is stored.

This release introduces no automatic prune. Future work must require dry-run reporting and explicit approval before any prune automation.


## AgentOps Chinese Copy Integration

Task #143 adds bilingual Chinese / English copy to AgentOps Dashboard.

Chinese copy explains AgentOps positioning, privacy boundary, preview metrics, Release Quality Score, Risk & Anomaly Detection, Trend Snapshot, Snapshot Retention Health, and interview demo notes.

This task does not modify parser, backend, snapshot JSON, nginx, cron, or systemd. Existing safety boundaries remain unchanged.


## AgentOps Bilingual Layout QA

Task #144 improves layout readability after Chinese copy integration.

KPI cards, Project / Task Distribution, Token Normalization, Review Health, Metric Semantics, and Snapshot Retention Health were adjusted for bilingual display. Additional Chinese helper text was added to Project Distribution, Task Distribution, Token Normalization Summary, and Review Health Summary.

No parser, backend, snapshot JSON, nginx, cron, or systemd changes were made. Existing safety boundaries remain unchanged.


## AgentOps Preview Dashboard Full-width Layout Fix

Task #144.5 moves / expands AgentOps Preview Dashboard into a full-width dashboard section below the hero and privacy boundary row.

KPI cards and summary cards now use the full desktop width. Project / Task Distribution, Token Normalization, and Review Health remain bilingual and readable. Mobile stacking remains preserved.

No parser, backend, snapshot JSON, nginx, cron, or systemd changes were made.


## AgentOps Bilingual Demo Dashboard Release

Task #145 packages Tasks #143, #144, and #144.5 as release `v0.6.24-agentops-bilingual-demo-dashboard`.

The release focuses on bilingual Chinese / English demo copy and layout readability. Preview Dashboard now spans full width below the hero and privacy boundary row.

Chinese helper copy explains privacy boundary, metrics, release readiness, risk indicators, trend snapshots, retention health, and interview demo positioning. Existing safety boundaries remain unchanged.

No parser, backend, snapshot JSON, nginx, cron, or systemd changes were made.
