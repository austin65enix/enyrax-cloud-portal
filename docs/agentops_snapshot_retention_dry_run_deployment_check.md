# AgentOps Snapshot Retention Dry-run Deployment Check

## Overview

This document verifies that the retention dry-run report can run in the deployment environment.

The deployment check confirms that the report:

* reads snapshot files and `index.json` only
* does not delete snapshots
* does not modify `index.json`
* does not auto commit or auto push
* retains release snapshots permanently
* reports unknown snapshots for manual review only

## Manual Deployment Check

Run the human-readable report:

```bash
cd /var/www/enyrax-portal

python3 scripts/report_agentops_snapshot_retention.py \
  --snapshots-root data/agentops/snapshots \
  --retention-days 30 \
  --today "$(date +%F)"
```

Validate the JSON report:

```bash
python3 scripts/report_agentops_snapshot_retention.py \
  --snapshots-root data/agentops/snapshots \
  --retention-days 30 \
  --today "$(date +%F)" \
  --json | python3 -m json.tool >/tmp/agentops_retention_report_check.json
```

## Expected Current Result

With the current snapshot data:

* Daily snapshots total: 1
* Daily retained: 1
* Daily retention candidates: 0
* Daily missing from index: 0
* Index entries without files: 0
* Release snapshots total: 1
* Release retained permanently: 1
* Release prune candidates: 0
* Unknown snapshot files: 0
* `delete_files`: `false`
* `modify_index`: `false`
* `auto_commit`: `false`
* `auto_push`: `false`

## Remote Snapshot Availability Check

Confirm that the snapshot index remains publicly available:

```bash
curl -I https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json

curl -s https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json \
  | python3 -m json.tool >/tmp/agentops_snapshot_index_remote_check.json
```

Expected result:

* remote index returns `200`
* `Cache-Control: no-store`

Confirm that the preview fixture remains blocked:

```bash
curl -I https://portal.soc-monitoring.dev/data/agentops/agent_runs_preview.json
```

Expected result:

* `404 Not Found`

## Safety Boundary

* The dry-run report does not delete files.
* The dry-run report does not modify `index.json`.
* The dry-run report does not read raw sessions.
* The dry-run report does not read prompt / response content.
* The dry-run report does not read `~/.codex/sessions`.
* The dry-run report does not read raw JSONL.
* The dry-run report does not read credentials, secrets, or full home paths.
* The dry-run report does not auto commit or auto push.

## Log / Evidence

Store manual verification evidence temporarily under `/tmp`:

* `/tmp/agentops_retention_report_check.json`
* `/tmp/agentops_snapshot_index_remote_check.json`

Do not commit `/tmp` content.

## Failure Handling

* If the dry-run report shows retention candidates, do not delete them automatically.
* If a release snapshot appears in prune candidates, treat it as an error.
* If unknown snapshot files appear, review them manually only.
* If index entries without files appear, repair the index or restore the snapshot. Do not delete automatically.
* If the remote index does not return `200`, check the nginx publish path.
* If the preview fixture does not return `404`, check the `/data/` block.

## Non-goals

* no snapshot deletion
* no prune automation
* no index modification
* no cron changes
* no nginx changes
* no systemd changes
* no parser changes
* no preview regeneration
* no auto commit / push

## Task #140 Handoff

Task #140 can design Retention Report Integration, for example:

* show a retention dry-run summary in the AgentOps Dashboard
* generate `data/agentops/snapshots/retention_report.json`

The integration must remain dry-run and read-only. It must not delete snapshots.

## AgentOps Retention Report Dashboard Integration

Task #140 adds a read-only retention dry-run summary to the AgentOps Dashboard. The Dashboard fetches `data/agentops/snapshots/retention_report.json` when available and displays daily snapshot retention, release snapshot permanence, unknown files, and index consistency.

The Dashboard does not delete snapshots, modify `index.json`, auto commit, or auto push. The retention report remains dry-run only. If the retention report is unavailable, the Dashboard falls back to a read-only unavailable state.
