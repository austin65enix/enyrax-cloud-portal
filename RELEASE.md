# ENYRAX Cloud Portal Release Notes

## v0.5.0-auth-guard-demo

Release date: 2026-05-21

## Summary

This release adds a frontend auth guard prompt across core operation modules.

The portal remains accessible for public navigation, while SOC, ServiceOps, ProjectOps and Audit Logs now display a login prompt when no demo user is signed in. The guard keeps demo flexibility by allowing users to continue in Demo Role mode.

## Completed

- Added shared frontend auth guard
- Added login-required prompt for SOC
- Added login-required prompt for ServiceOps
- Added login-required prompt for ProjectOps
- Added login-required prompt for Audit Logs
- Added Go to Login action
- Added Continue in Demo Role action
- Preserved existing Role Switcher behavior
- Preserved demo-mode access for presentations
- Added session-based dismissal for the auth guard prompt

## Auth Guard Behavior

```text
Portal /
  - Public module entry

/login/
  - Public demo login page

/status/
  - Public system status page

/soc/
  - Shows login prompt when not signed in

/serviceops/
  - Shows login prompt when not signed in

/projectops/
  - Shows login prompt when not signed in

/audit/
  - Shows login prompt when not signed in
  - Backend still requires Supervisor/Admin for audit access
```

## Current Product Status

```text
Portal        Public module entry
Login         Demo auth page enabled
Users         Demo users table enabled
Auth Guard    Soft login prompt enabled
SOC           RBAC demo controls + auth prompt
ServiceOps    RBAC + Archive / Restore + auth prompt
ProjectOps    RBAC + Archive / Restore + auth prompt
Audit Logs    Supervisor/Admin protected + auth prompt
Role Source   Login identity first, demo role fallback
Audit Actor   Logged-in email first, role fallback
```

## Next Phase

- Validate demo token with `/api/auth/me` on page load
- Replace soft auth guard with route-level protection
- Add user-specific My Activity page
- Add user management page
- Replace demo token with signed JWT
- Replace `X-Demo-Role` with authenticated backend role
- Add session expiration handling

---

## v0.4.1-audit-actor-ui-polish

Release date: 2026-05-21

## Summary

This release polishes the v0.4.0 login-aware workflow by improving audit actor identity, logged-in header layout, and audit access messaging.

Audit Logs now record demo actor identity from the logged-in user, while the shared Role Switcher sends both role and actor headers to backend APIs.

## Completed

- Shared Role Switcher now sends `X-Demo-Actor`
- `ENYRAXRole.actor()` added
- Audit Logs actor now supports logged-in user email
- Backend audit writers now prefer `X-Demo-Actor` over role fallback
- Logged-in identity card layout improved
- Login identity card no longer shows role select after login
- Audit Logs permission message improved for Viewer / Operator
- SOC header layout adjusted to avoid overlap with login identity card

## Header Flow

```text
Login
  ↓
localStorage.enyrax_auth_user
  ↓
shared/role-switcher.js
  ├── X-Demo-Role: role
  └── X-Demo-Actor: email
        ↓
FastAPI audit writer
        ↓
audit_logs.actor
```

## Current Product Status

```text
Login         Demo auth page enabled
Users         Demo users table enabled
Role Source   Login identity first, demo role fallback
Audit Actor   Logged-in email first, role fallback
SOC           RBAC demo controls enabled
ServiceOps    RBAC + Archive / Restore enabled
ProjectOps    RBAC + Archive / Restore enabled
Audit Logs    Supervisor/Admin protected with clearer access message
```

## Next Phase

- Validate demo token with `/api/auth/me` on page load
- Replace demo token with signed JWT
- Replace `X-Demo-Role` with authenticated backend role
- Add user management page
- Add user-specific My Activity page
- Add audit detail view per event

---

## v0.4.0-auth-users-demo

Release date: 2026-05-20

## Summary

This release upgrades ENYRAX Cloud Portal from header-based RBAC demo controls into a login-aware user identity demo.

Demo users can now log in through `/login/`, store a demo auth token and user profile in localStorage, and have the shared Role Switcher automatically use the logged-in user's role across SOC, ServiceOps, ProjectOps and Audit Logs.

## Live URL

- https://portal.soc-monitoring.dev
- https://portal.soc-monitoring.dev/login/

## Completed

- Users table initializer
- Demo users seed
- Demo Auth API
- `/api/auth/login`
- `/api/auth/me`
- Login page at `/login/`
- Demo account quick-select buttons
- localStorage demo auth token support
- localStorage auth user profile support
- Shared Role Switcher connected to login identity
- Logged-in Role Switcher UI
- Logout support
- Existing demo role switcher preserved for non-login mode

## Demo Users

```text
viewer@enyrax.local      Viewer      demo1234
operator@enyrax.local    Operator    demo1234
supervisor@enyrax.local  Supervisor  demo1234
admin@enyrax.local       Admin       demo1234
```

## Auth Flow

```text
Login Page
  ↓ POST /api/auth/login
FastAPI
  ↓ users table
PostgreSQL
  ↓ returns demo token + user profile
Browser localStorage
  ├── enyrax_auth_token
  └── enyrax_auth_user
        ↓
Shared Role Switcher
        ↓
SOC / ServiceOps / ProjectOps / Audit Logs use logged-in role
```

## API Changes

### Auth

- `POST /api/auth/login`
- `GET /api/auth/me`

## Current Product Status

```text
Portal        Module entry complete
Login         Demo auth page enabled
Users         Demo users table enabled
SOC           RBAC demo controls enabled
ServiceOps    RBAC + Archive / Restore enabled
ProjectOps    RBAC + Archive / Restore enabled
Audit Logs    API-connected and role-protected
Role Source   Login identity first, demo role fallback
```

## Next Phase

- Use `/api/auth/me` to validate token on page load
- Replace demo token with signed JWT
- Replace `X-Demo-Role` with authenticated role from backend
- Store password hashes instead of demo password
- Add user management page
- Add actor identity to audit logs
- Add session expiration / logout redirect

---

## v0.3.0-rbac-archive-demo

Release date: 2026-05-20

## Summary

This release upgrades ENYRAX Cloud Portal from a CRUD-enabled prototype into a role-aware operation platform demo.

The platform now includes demo RBAC role guards, frontend role switching, audit logs, and ServiceOps / ProjectOps archive / restore workflow.

SOC, ServiceOps and ProjectOps now all include RBAC demo controls.

## Live URL

- https://portal.soc-monitoring.dev

## Completed

- Demo RBAC role model
- Role switcher shared frontend component
- Audit Logs frontend page
- Audit Logs module entry on Portal home
- ServiceOps role-based UI controls
- ProjectOps role-based UI controls
- SOC role-based UI controls
- All core modules now support RBAC demo controls
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
SOC           RBAC demo controls enabled
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
