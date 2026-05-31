## Domain / HTTPS

Primary domain:

- https://portal.soc-monitoring.dev

DNS:

- A record: portal → 172.237.30.246

TLS:

- Let's Encrypt
- Certbot Nginx plugin
- Auto-renewal managed by certbot systemd timer

Useful commands:

```bash
sudo certbot certificates
sudo systemctl status certbot.timer
sudo certbot renew --dry-run


## FastAPI Backend

Service:

```bash
sudo systemctl status enyrax-api

## Current Production URL

- https://portal.soc-monitoring.dev

## Runtime Architecture

```text
Nginx
  ├── Static files from /var/www/enyrax-portal
  └── /api/ proxy to FastAPI on 127.0.0.1:8000


## AgentOps Snapshot Index Publish Path

Task #133 publishes the AgentOps Trend UI snapshot index without exposing the entire `/data/` tree.

Add these locations before the general `location /` block in `/etc/nginx/sites-available/enyrax-portal`:

```nginx
location ^~ /data/agentops/snapshots/ {
    root /var/www/enyrax-portal;
    default_type application/json;
    add_header Cache-Control "no-store";
    try_files $uri =404;
}

location ^~ /data/ {
    return 404;
}
```

Snapshot files contain aggregate operational metrics only. Trend UI falls back to clearly labeled sample data if the index is unavailable.

Validate and apply the server-side change manually:

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json
curl -s https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json | python3 -m json.tool >/tmp/agentops_snapshot_index_remote_check.json
```

## AgentOps Snapshot Auto Update Workflow

Task #134 adds `scripts/update_agentops_snapshots.py`.

The auto update workflow generates daily snapshots and updates the snapshot index from aggregate review JSON only. It does not regenerate preview JSON and does not read raw sessions or prompt / response content.

This keeps snapshot trend data aligned with generated historical snapshots. Release snapshots remain explicit and require `--write-release`.

## AgentOps Snapshot Scheduled Update

Task #135 documents manual deployment of a daily scheduled update. The schedule runs `scripts/update_agentops_snapshots.py`, updates the daily snapshot and snapshot index, and does not auto commit or auto push generated files.

Manual run:

```bash
cd /var/www/enyrax-portal
python3 scripts/update_agentops_snapshots.py --snapshot-date "$(date +%F)"
```

Cron example:

```cron
30 23 * * * cd /var/www/enyrax-portal && python3 scripts/update_agentops_snapshots.py --snapshot-date "$(date +\%F)" >> /var/log/agentops-snapshot-update.log 2>&1
```

Cron requires `%` to be escaped as `\%`.

Verify the remote index:

```bash
curl -I https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json
curl -s https://portal.soc-monitoring.dev/data/agentops/snapshots/index.json | python3 -m json.tool >/tmp/agentops_snapshot_index_remote_check.json
```

Only `/data/agentops/snapshots/` is published. The remaining `/data/` tree, including preview fixtures, must stay unavailable.

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

## AgentOps Retention Report Dashboard Integration

Task #140 adds a read-only retention dry-run summary to the AgentOps Dashboard. The Dashboard fetches `data/agentops/snapshots/retention_report.json` when available and displays daily snapshot retention, release snapshot permanence, unknown files, and index consistency.

The Dashboard does not delete snapshots, modify `index.json`, auto commit, or auto push. The retention report remains dry-run only. If the retention report is unavailable, the Dashboard falls back to a read-only unavailable state.
