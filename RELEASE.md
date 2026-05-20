# ENYRAX Cloud Portal Release Notes

## v0.3.0-rbac-archive-demo

Release date: 2026-05-20

## Summary

This release upgrades ENYRAX Cloud Portal from a CRUD-enabled prototype into a role-aware operation platform demo.

The platform now includes demo RBAC role guards, frontend role switching, audit logs, and ServiceOps archive / restore workflow.

## Live URL

- https://portal.soc-monitoring.dev

## Completed

- Demo RBAC role model
- Role switcher shared frontend component
- Audit Logs frontend page
- Audit Logs module entry on Portal home
- ServiceOps role-based UI controls
- Viewer read-only behavior
- Operator create / update / archive behavior
- Supervisor restore permission
- Admin full operation permission
- ServiceOps soft delete converted into archive workflow
- Archived Tickets frontend section
- ServiceOps restore workflow
- ProjectOps role switcher frontend controls
- ProjectOps archive / restore API
- ProjectOps archived projects frontend section
- ProjectOps archive and restore audit logs
- Archive and restore audit logs
- New archive API route for ServiceOps archived tickets
- Backward-compatible legacy trash API route

## Role Model

```text
Viewer
  - Read-only
  - Can view dashboards and active work queue
  - Cannot create, update, archive or restore

Operator
  - Can create ServiceOps tickets
  - Can update ticket status
  - Can mark work done or pending
  - Can archive tickets
  - Cannot restore archived tickets

Supervisor
  - Can create and update tickets
  - Can archive tickets
  - Can restore archived tickets
  - Can view audit logs

Admin
  - Full demo access
  - Can create, update, archive and restore
  - Can view audit logs
  - Reserved for future permanent delete / data management
```

## API Changes

### ServiceOps Archive

- `GET /api/serviceops/tickets/archive`
- `GET /api/serviceops/tickets/trash` compatibility route
- `DELETE /api/serviceops/tickets/{ticket_id}` now archives the ticket instead of hard deleting it
- `PUT /api/serviceops/tickets/{ticket_id}/restore`

### ProjectOps Archive

- `GET /api/projectops/projects/archive`
- `DELETE /api/projectops/projects/{project_id}` now archives the project instead of hard deleting it
- `PUT /api/projectops/projects/{project_id}/restore`

### Audit Logs

- `GET /api/audit/logs`
- `archive` action added
- `restore` action added
- ServiceOps archive and restore actions are recorded with actor role
- ProjectOps archive and restore actions are recorded with actor role

## Current Architecture

```text
Browser
  ↓ HTTPS
Nginx
  ├── Static Frontend Pages
  │   ├── /
  │   ├── /soc/
  │   ├── /serviceops/
  │   ├── /projectops/
  │   ├── /audit/
  │   └── /status/
  │
  └── /api/ reverse proxy
        ↓
      FastAPI
        ├── Demo RBAC Guard
        ├── Audit Log Writer
        ├── ServiceOps Archive / Restore
        └── CRUD APIs
        ↓
      PostgreSQL
```

## Current Product Status

```text
Portal        Module entry complete
SOC           CRUD-enabled
ServiceOps    RBAC + Archive / Restore enabled
ProjectOps    RBAC + Archive / Restore enabled
Audit Logs    API-connected and role-protected
Status Page   API-connected
RBAC          Header-based demo role guard
```

## Next Phase

- Add Role Switcher to ProjectOps
- Add Role Switcher to SOC
- Convert ProjectOps delete into archive / restore
- Convert SOC delete into archive / restore or close / reopen workflow
- Add real authentication
- Replace demo role header with login session / JWT
- Add user table and role mapping
- Add action-level audit detail

---

## v0.2.0-crud-demo

Release date: 2026-05-19

## Summary

This release upgrades ENYRAX Cloud Portal from a DB-backed dashboard demo into a CRUD-enabled operation platform prototype.

SOC, ServiceOps and ProjectOps now support database-backed summary APIs and basic create / update / delete workflows.

## Live URL

- https://portal.soc-monitoring.dev

## Completed

- SOC Incident CRUD API
- SOC frontend incident controls
- ServiceOps Ticket CRUD API
- ServiceOps frontend create / mark done / delete controls
- ProjectOps Project CRUD API
- ProjectOps frontend create / status update / delete controls
- ProjectOps start date / end date support
- Native date picker for ProjectOps project form
- PostgreSQL-backed summary APIs
- CRUD count healthcheck coverage

## API Endpoints

### SOC

- `GET /api/soc/summary`
- `GET /api/soc/incidents`
- `GET /api/soc/incidents/{incident_id}`
- `POST /api/soc/incidents`
- `PUT /api/soc/incidents/{incident_id}`
- `DELETE /api/soc/incidents/{incident_id}`

### ServiceOps

- `GET /api/serviceops/summary`
- `GET /api/serviceops/tickets`
- `GET /api/serviceops/tickets/{ticket_id}`
- `POST /api/serviceops/tickets`
- `PUT /api/serviceops/tickets/{ticket_id}`
- `DELETE /api/serviceops/tickets/{ticket_id}`

### ProjectOps

- `GET /api/projectops/summary`
- `GET /api/projectops/projects`
- `GET /api/projectops/projects/{project_id}`
- `POST /api/projectops/projects`
- `PUT /api/projectops/projects/{project_id}`
- `DELETE /api/projectops/projects/{project_id}`

## Current Architecture

```text
Browser
  ↓ HTTPS
Nginx
  ├── Static Frontend Pages
  │   ├── /
  │   ├── /soc/
  │   ├── /serviceops/
  │   ├── /projectops/
  │   └── /status/
  │
  └── /api/ reverse proxy
        ↓
      FastAPI
        ↓
      PostgreSQL
```

## Current Product Status

```text
SOC          CRUD-enabled
ServiceOps   CRUD-enabled
ProjectOps   CRUD-enabled
Status Page  API-connected
Portal Home  Module API-connected
```

## Next Phase

- Add authentication
- Add role-based access control
- Add audit logs for create / update / delete actions
- Add ProjectOps and ServiceOps relationship mapping
- Add SOC incident timeline database table
- Add admin data management page

---

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
