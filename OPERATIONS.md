# ENYRAX Portal Operations

## Overview

ENYRAX Cloud Portal is deployed on Akamai Cloud / Linode Tokyo 3 and served by Nginx.

Primary URL:

- https://portal.soc-monitoring.dev

Main routes:

- `/`
- `/soc/`
- `/serviceops/`
- `/projectops/`
- `/status/`

---

## FastAPI Operations

Check API service:

```bash
sudo systemctl status enyrax-api


## Health Check

Run the health check script:

```bash
cd /var/www/enyrax-portal
./scripts/healthcheck.sh
