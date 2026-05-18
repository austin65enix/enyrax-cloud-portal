# ENYRAX Cloud Portal Release Notes

## v0.1.0-cloud-api-db-demo

Release date: 2026-05-18

## Summary

This release marks the first cloud-hosted ENYRAX Portal checkpoint.

The portal is deployed on Akamai Cloud / Linode Tokyo 3 with Nginx, HTTPS, FastAPI backend and PostgreSQL-backed demo APIs.

## Live URL

- https://portal.soc-monitoring.dev

## Completed

- Akamai Cloud VM online
- Ubuntu 24.04 LTS configured
- Nginx static portal deployed
- HTTPS enabled with Let's Encrypt / Certbot
- FastAPI backend enabled through Nginx reverse proxy
- PostgreSQL connected
- API-driven frontend pages
- Healthcheck script
- Database seed script
- Database backup script
- Database restore script
- GitHub remote backup

## API Endpoints

- `/api/health`
- `/api/modules`
- `/api/soc/summary`
- `/api/serviceops/summary`
- `/api/projectops/summary`

## DB-backed Modules

- Portal modules
- SOC incidents
- ServiceOps tickets
- ProjectOps projects

## Operations Scripts

- `scripts/healthcheck.sh`
- `scripts/backup_db.sh`
- `scripts/restore_db.sh`
- `backend/seed_all.py`

## Next Phase

- Add real CRUD APIs
- Add admin/demo data management page
- Add PostgreSQL models for ServiceOps and ProjectOps
- Add authentication and role-based view
- Add SOC incident timeline database table
