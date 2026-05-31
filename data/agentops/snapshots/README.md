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
