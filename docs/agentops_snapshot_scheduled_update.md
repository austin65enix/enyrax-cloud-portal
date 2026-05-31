# AgentOps Snapshot Scheduled Update Deployment

## Overview

Task #135 documents the scheduled deployment for the AgentOps snapshot auto update workflow.

The schedule periodically runs `scripts/update_agentops_snapshots.py` to update the daily snapshot and snapshot index. This allows Trend Snapshot to use actual historical snapshot data.

The scheduled update does not read raw sessions, does not read prompt / response content, and does not regenerate preview JSON.

## Recommended Schedule

Run the update once per day, for example:

```text
Every day at 23:30
```

Cron example:

```cron
30 23 * * * cd /var/www/enyrax-portal && python3 scripts/update_agentops_snapshots.py --snapshot-date "$(date +\%F)" >> /var/log/agentops-snapshot-update.log 2>&1
```

Cron treats `%` specially, so the date format must escape `%` as `\%`.

## Manual Run

```bash
cd /var/www/enyrax-portal
python3 scripts/update_agentops_snapshots.py --snapshot-date "$(date +%F)"
```

## Verification

```bash
python3 -m json.tool data/agentops/snapshots/index.json >/tmp/agentops_snapshot_index_check.json

curl -I https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json

curl -s https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json \
  | python3 -m json.tool >/tmp/agentops_snapshot_index_remote_check.json
```

Expected results:

* index JSON is valid
* remote snapshot index returns `200`
* remote snapshot index uses `Cache-Control: no-store`
* Trend UI displays snapshot-backed trend data

## Safety Boundary

* Do not run parser preview regeneration.
* Do not read `~/.codex/sessions`.
* Do not read prompt / response content.
* Do not read raw session files.
* Do not save credentials, secrets, or full home paths.
* Save aggregate dashboard-level operational metrics only.
* Token values are operational estimates, not billing-grade cost data.

## Failure Handling

If the update script fails, retain the previous index. Trend UI should fall back to sample data or continue displaying the previous snapshot-backed data.

Check `/var/log/agentops-snapshot-update.log` when an update fails. Do not automatically delete snapshots after a failure.

## Git Policy

The first scheduled deployment must not auto commit or auto push snapshot files.

Automatic daily commits would pollute repository history. Review generated snapshots manually before committing them. A future task may define a release snapshot commit policy.

## Future Options

* systemd timer
* snapshot retention policy
* weekly snapshot summary
* release snapshot automation
* snapshot validation script
* audit export

## AgentOps Snapshot Retention Policy

Task #137 defines retention policy for AgentOps snapshots. Daily snapshots retain the recent 30 days, while release snapshots are kept permanently.

The auto update workflow updates the working tree only and does not auto commit or auto push. This task does not delete snapshots. Future retention automation must start with dry-run reporting.
