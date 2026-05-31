# AgentOps Snapshot Retention Policy

## Overview

The AgentOps Snapshot Retention Policy controls the number of daily snapshots so long-running scheduled updates do not pollute repository history or the static data directory with unbounded daily JSON files.

The policy preserves recent trend data, keeps release snapshots permanently as release evidence, and maintains the existing snapshot safety boundary.

## Retention Policy v1

### Daily snapshots

* Retain the most recent 30 days of daily snapshots.
* `index.json` should list at most the most recent 30 daily snapshots.
* Daily snapshots older than 30 days are not automatically deleted in v1. Review them manually and consider archiving them.
* Future automated prune support must provide an explicit dry-run mode first.

### Release snapshots

* Keep release snapshots permanently.
* Release snapshots are not affected by daily retention.
* Release snapshots may be used as release evidence and an audit trail.

### Manual review snapshots

* Retain future manual review snapshots for 90 days or until manual review is complete.
* v1 defines this policy only. It does not implement manual review snapshots or retention automation.

## Repo Policy

* Do not auto commit or auto push daily snapshots.
* Review snapshot files manually before committing them at a major milestone or before a release.
* Release snapshots may be committed with release documentation.
* `index.json` may be committed manually when a preview or demo needs it.
* The scheduled auto update workflow updates the working tree only. It does not auto commit or auto push.

## Storage Policy

Recommended layout:

```text
data/agentops/snapshots/
  daily/       retain recent daily snapshots
  releases/    keep permanently
  manual/      future manual review snapshots
  archive/     future archived daily snapshots
```

v1 does not create `manual/` or `archive/`. These directories are documented for future use only.

## Index Policy

* `index.json` should list only snapshots currently needed by the UI.
* The MVP should list at most 30 daily entries.
* Entries must be sorted by `snapshot_date`.
* Entries must not reference snapshot paths that do not exist.
* Snapshot paths must be safe relative paths.
* The index stores aggregate summaries only. It must not store the full snapshot body.

## Safety Boundary

The retention workflow:

* must not read prompt / response content
* must not read raw sessions
* must not read `~/.codex/sessions`
* must not store raw JSONL
* must not store credentials, secrets, or full home paths
* must treat token values as operational estimates, not billing-grade cost data
* must treat project / task values as possible pipeline-level metadata classifications

Snapshot files remain aggregate dashboard-level operational metrics only. Content-based inference remains prohibited.

## Future Automation

Possible future options:

* `--retention-days 30`
* `--prune-daily`
* `--dry-run-prune`
* `--archive-old-daily`
* retention validation script
* snapshot inventory report
* release snapshot lock / integrity check

Future prune support must start with dry-run reporting. It must never delete release snapshots. It must report unknown snapshot types for review instead of deleting them.

## Non-goals

* no script changes
* no snapshot deletion
* no cron changes
* no nginx changes
* no systemd changes
* no snapshot regeneration
* no parser changes
* no backend changes
* no UI changes
* no auto commit / push

## Task #138 Handoff

Task #138 can implement a snapshot retention dry-run report, for example:

```bash
python3 scripts/report_agentops_snapshot_retention.py --retention-days 30
```

The first version should only report daily snapshots older than the retention window. It must not delete snapshots.

## AgentOps Snapshot Retention Dry-run Report

Task #138 adds `scripts/report_agentops_snapshot_retention.py`.

The script outputs a retention dry-run report. It does not delete snapshots, modify `index.json`, auto commit, or auto push. It does not read raw sessions or prompt / response content.

The report verifies daily snapshot retention, release snapshot permanence, unknown snapshot files, and index consistency. Future prune automation must build on the dry-run report first.

## AgentOps Snapshot Retention Dry-run Deployment Check

Task #139 documents deployment verification for the retention dry-run report.

The deployment check verifies human-readable and JSON dry-run output, remote snapshot index availability, and that the preview fixture remains blocked with `404`. It also confirms the remote index keeps `Cache-Control: no-store`.

The check does not delete snapshots, modify `index.json`, change cron / nginx / systemd, auto commit, or auto push.

See `docs/agentops_snapshot_retention_dry_run_deployment_check.md`.

## AgentOps Retention Report Dashboard Integration

Task #140 adds a read-only retention dry-run summary to the AgentOps Dashboard. The Dashboard fetches `data/agentops/snapshots/retention_report.json` when available and displays daily snapshot retention, release snapshot permanence, unknown files, and index consistency.

The Dashboard does not delete snapshots, modify `index.json`, auto commit, or auto push. The retention report remains dry-run only. If the retention report is unavailable, the Dashboard falls back to a read-only unavailable state.
