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
