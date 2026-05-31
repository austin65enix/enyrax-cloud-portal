# AgentOps Historical Snapshot Governance Release Note

## Overview

AgentOps Historical Snapshot Governance provides a safe, dashboard-level telemetry layer for tracking AI agent / Codex preview metrics over time. It adds historical snapshots, snapshot-backed trend data, scheduled update workflow, retention policy, dry-run retention reporting, and dashboard retention health summary while preserving the safety boundary that no prompt / response or raw session content is stored.

## Release Version

```text
v0.6.23-agentops-historical-snapshot-governance
```

## Completed Scope

* Task #130: Historical Snapshots Schema Design
* Task #131: AgentOps Snapshot Generation
* Task #132: Snapshot Trend Integration
* Task #133: Snapshot Index Publish Path
* Task #134: Snapshot Auto Update Workflow
* Task #135: Snapshot Scheduled Update Deployment
* Task #136: Snapshot Scheduled Update Verification
* Task #137: Snapshot Retention Policy
* Task #138: Snapshot Retention Dry-run Report
* Task #139: Retention Dry-run Deployment Check
* Task #140: Retention Report Dashboard Integration

## Key Features

### Historical Snapshots

* Daily snapshot schema
* Release snapshot schema
* `agentops_snapshot_v1`
* JSON storage under `data/agentops/snapshots/`

### Snapshot Generation

* `scripts/generate_agentops_snapshot.py`
* daily snapshot generation
* release snapshot generation
* aggregate review output only

### Snapshot Index and Trend Integration

* `data/agentops/snapshots/index.json`
* `agentops_snapshot_index_v1`
* Dashboard uses snapshot-backed trend when index is available
* Dashboard falls back to sample trend when index is unavailable

### Publish Path

* Only `/data/agentops/snapshots/` is exposed
* `/data/agentops/agent_runs_preview.json` remains blocked
* `Cache-Control: no-store`

### Auto Update Workflow

* `scripts/update_agentops_snapshots.py`
* Updates daily snapshot and index
* Release snapshots require explicit opt-in
* No parser regeneration
* No raw session reads

### Scheduled Update

* cron deployment documented
* manual verification completed
* log path documented: `/var/log/agentops-snapshot-update.log`

### Retention Policy

* Daily snapshots v1 policy: recent 30 days
* Release snapshots retained permanently
* No automatic deletion in v1
* Future prune must start with dry-run

### Retention Dry-run Report

* `scripts/report_agentops_snapshot_retention.py`
* `agentops_retention_report_v1`
* No deletion
* No index modification
* Reports daily retention candidates, release permanence, unknown files, index consistency

### Retention Dashboard Summary

* Dashboard displays Snapshot Retention Health
* Fetches `data/agentops/snapshots/retention_report.json`
* Read-only
* Dry-run only
* No delete / no index modification / no auto commit / no auto push

## Current Operational Evidence

* Remote snapshot index: 200 OK
* Remote retention report: 200 OK
* `Cache-Control: no-store`
* Preview fixture `/data/agentops/agent_runs_preview.json`: 404 Not Found
* Daily snapshots: total 1, retained 1, retention candidates 0
* Release snapshots: total 1, retained permanently 1
* Unknown snapshot files: 0
* Retention actions:
  * `delete_files=false`
  * `modify_index=false`
  * `auto_commit=false`
  * `auto_push=false`

## Safety and Semantic Boundaries

* Snapshots contain aggregate dashboard-level operational metrics only.
* Retention report contains dry-run summary only.
* No prompt / response content is stored.
* No raw session files are read.
* `~/.codex/sessions` is not read.
* No shell output, command text, diff, file contents, raw JSONL, credentials, secrets, or full home paths are stored.
* Token values are operational estimates, not billing-grade cost data.
* Project / task values may be pipeline-level metadata classifications.
* Release Quality Score is not AI answer quality.
* Retention health is not prune automation.
* Content-based inference remains prohibited.

## Non-goals

* no parser changes
* no preview regeneration
* no backend API
* no database migration
* no automatic prune
* no snapshot deletion
* no index mutation by dashboard
* no auto commit / push
* no AI answer quality scoring
* no session-content-level correctness claim

## Known Cautions

* Daily snapshot retention is policy-only; no prune automation yet.
* Daily snapshots are not auto committed by schedule.
* Snapshot trend depends on published snapshot index.
* Retention dashboard depends on published retention report.
* Project / task labels remain operational metadata and may be pipeline-level.
* Token values remain operational estimates.

## Recommended Next Steps

* Task #142: AgentOps Historical Snapshot Governance Release Tag
* Future retention dry-run dashboard refinements
* Future retention inventory report
* Future release snapshot integrity check
* Future optional retention prune with dry-run and explicit approval
* Future pipeline/session schema split
