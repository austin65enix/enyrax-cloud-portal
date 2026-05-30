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
