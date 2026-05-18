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
