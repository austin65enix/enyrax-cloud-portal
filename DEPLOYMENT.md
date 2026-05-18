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
