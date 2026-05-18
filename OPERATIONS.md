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

## Seed Demo Database

Run all seed scripts:

```bash
cd /var/www/enyrax-portal/backend
source venv/bin/activate
source .env
python seed_all.py


## Database Backup

Run PostgreSQL backup:

```bash
cd /var/www/enyrax-portal
./scripts/backup_db.sh

## Database Restore

Restore from a backup:

```bash
cd /var/www/enyrax-portal
./scripts/restore_db.sh backups/<backup-file>.sql.gz

## Health Check

Run the health check script:

```bash
cd /var/www/enyrax-portal
./scripts/healthcheck.sh
