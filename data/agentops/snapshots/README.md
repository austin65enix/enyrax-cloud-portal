# AgentOps Historical Snapshots

This directory stores AgentOps dashboard-level historical snapshots.

Snapshot files contain aggregate operational metrics only.

Snapshot files do not store prompt / response content.

Snapshot files do not store shell output, command text, diff, file contents, raw JSONL, credentials, secrets, or full home paths.

Token values are operational estimates, not billing-grade cost data.

Project/task values may be pipeline-level metadata classifications.

Snapshot schema version: `agentops_snapshot_v1`.

## Directories

* `daily/` stores daily AgentOps snapshot files.
* `releases/` stores release AgentOps snapshot files.

## Auto Update Workflow

```bash
python3 scripts/update_agentops_snapshots.py \
  --snapshot-date YYYY-MM-DD
```

The workflow updates the daily snapshot and snapshot index. It uses aggregate review output only.

The workflow does not regenerate preview JSON, does not read raw sessions, and does not inspect prompt / response content.

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

## AgentOps Snapshot Retention Dry-run Deployment Check

Task #139 documents deployment verification for the retention dry-run report.

The deployment check verifies human-readable and JSON dry-run output, remote snapshot index availability, and that the preview fixture remains blocked with `404`. It also confirms the remote index keeps `Cache-Control: no-store`.

The check does not delete snapshots, modify `index.json`, change cron / nginx / systemd, auto commit, or auto push.

See `docs/agentops_snapshot_retention_dry_run_deployment_check.md`.
