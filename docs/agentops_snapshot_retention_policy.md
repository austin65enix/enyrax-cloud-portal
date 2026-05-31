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
