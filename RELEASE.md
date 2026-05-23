# ENYRAX Cloud Portal Release Notes

## v0.6.6-command-center-header

Release date: 2026-05-24

## Summary

This release upgrades ENYRAX Cloud Portal into a more unified command-center style interface.

Core modules now share a fixed ENYRAX Command Header with module navigation, active module highlighting, and docked login identity. The previous floating role identity card has been visually integrated into the command header, making SOC, ServiceOps, ProjectOps, Sync Gateway, Audit Logs and Status feel like one connected operation console.

## Completed

- Added shared ENYRAX Command Header
- Added `shared/command-header.js`
- Added fixed top navigation across core modules
- Added active module highlighting
- Added Sync Gateway entry to command navigation
- Added command header identity slot
- Integrated Role Switcher into command header
- Replaced floating login card with compact docked identity
- Added compact logged-in display:
  - display name
  - role badge
  - session active
  - logout
- Added compact preview mode display:
  - PREVIEW ONLY
  - Login
- Updated SOC page script order for command header docking
- Updated SOC Incident Detail page script order
- Updated ServiceOps page script order
- Updated ProjectOps page script order
- Kept fallback floating role switcher for legacy pages without command header

## Command Center Layout

```text
ENYRAX Command Header
  ├── Brand / Module Label
  ├── Portal
  ├── SOC
  ├── ServiceOps
  ├── ProjectOps
  ├── Sync Gateway
  ├── Audit Logs
  ├── Status
  └── Docked Identity / Login State
```

## Role Identity Behavior

```text
Logged in
  - Operator Demo User
  - OPERATOR badge
  - Session active
  - Logout

Preview only
  - PREVIEW ONLY
  - Login
```

## Applied Pages

```text
/soc/
/soc/incident.html
/serviceops/
/projectops/
/sync/
/status/
/audit/
```

## Current Product Status

```text
Command Header   Shared fixed navigation enabled
Role Identity    Docked into command header
SOC              Command-center navigation integrated
ServiceOps       Command-center navigation integrated
ProjectOps       Command-center navigation integrated
Sync Gateway     Command-center navigation integrated
Audit Logs       Command-center navigation integrated
Status Center    Command-center navigation integrated
```

## Next Phase

- Add command header status indicators
- Add global source health mini badge
- Add SOC open incident count in command header
- Add ServiceOps pending ticket count in command header
- Add global command search
- Add notification center
- Add user/session menu
- Add command-center mobile layout refinement

---

## v0.6.4-soc-handling-notes

Release date: 2026-05-23

## Summary

This release adds handling notes to SOC incident detail pages.

Infra / Operator users can now record investigation notes, recovery notes and verification comments directly on a SOC incident. Notes are stored in PostgreSQL and tied to actor identity, role and timestamp.

## Completed

- Added SOC incident comments backend
- Added `soc_incident_comments` table
- Added `GET /api/soc/incidents/{incident_id}/comments`
- Added `POST /api/soc/incidents/{incident_id}/comments`
- Added comment audit log action
- Added Handling Notes section to SOC incident detail page
- Added Add Handling Note form
- Added comment type support:
  - note
  - infra_note
  - investigation
  - recovery
  - review
- Added comment actor / role / timestamp display
- Added preview-only protection for note creation
- Added operator / supervisor / admin handling note workflow

## Handling Notes Flow

```text
SOC Incident Detail
  ↓
Operator / Infra adds handling note
  ↓
Comment stored in soc_incident_comments
  ↓
Audit Logs record comment action
  ↓
Incident page shows full handling notes history
```

## Current Product Status

```text
SOC Detail        Incident summary + lifecycle + audit trail
Handling Notes    Operator / Infra comment workflow enabled
Audit Logs        Comment actions recorded with actor identity
Infra Workflow    Verify / confirm / close + notes
```

## Next Phase

- Add editable resolution / infra verification note form
- Add comment filtering by type
- Add per-incident related sync events
- Add ServiceOps ticket creation from SOC incident
- Add incident report export
- Add SLA timer and overdue state

---

## v0.6.3-soc-incident-detail

Release date: 2026-05-23

## Summary

This release adds a dedicated SOC incident detail and timeline page.

SOC incidents can now be opened from the SOC dashboard into a single incident view that shows the full handling context, lifecycle state, Infra verification trail and incident-specific audit history.

## Completed

- Added SOC incident detail page
- Added `/soc/incident.html?id=<incident_id>`
- Added View Detail link from SOC incident cards
- Added Incident Summary section
- Added Handling Trail section
- Added Lifecycle Timeline section
- Added incident-level action buttons
- Added incident-specific Audit Trail display
- Added operator action support from detail page
- Added supervisor/admin review actions from detail page
- Added admin delete action from detail page
- Preserved preview-only mode behavior

## Incident Detail Flow

```text
/sync/
  ↓ SOC Incident Candidate

/soc/
  ↓ View Detail

/soc/incident.html?id=<incident_id>
  ├── Incident Summary
  ├── Handling Trail
  ├── Lifecycle Timeline
  ├── Action Buttons
  └── Audit Trail
```

## Role Behavior

```text
Preview only
  - Can view incident detail
  - Cannot perform write actions

Operator / Infra
  - Investigate
  - Contain
  - Resolve
  - Infra Verify
  - Infra Confirm Normal
  - Close Incident

Supervisor
  - View Audit Trail
  - False Positive
  - Reopen
  - Close Incident

Admin
  - Full access
  - Delete incident
```

## Current Product Status

```text
Sync Gateway     Local source health and incident candidates
SOC Dashboard    Incident overview and action entry
SOC Detail       Single incident timeline and handling page
Infra Workflow   Verify / confirm / close flow
Audit Logs       Incident-specific actor trail
```

## Next Phase

- Add editable resolution / infra verification notes
- Add incident comments
- Add ServiceOps ticket creation from SOC incident
- Add per-incident related sync events
- Add per-incident source health snapshot
- Add incident SLA timer
- Add incident export / report view

---

## v0.6.2-sync-to-soc-workflow

Release date: 2026-05-22

## Summary

This release connects Local Sync Gateway abnormalities into the SOC incident handling workflow.

ENYRAX Cloud Portal can now detect stale / error / unknown local sync sources, show them as SOC incident candidates, create SOC incidents from those candidates, and let Infra / Operator complete the handling workflow with verification, confirmation and closure.

## Completed

- Sync incident candidates API
- `GET /api/sync/incident-candidates`
- Create SOC incident from sync candidate API
- `POST /api/sync/incident-candidates/{source}/create-soc-incident`
- Duplicate prevention for existing sync-origin SOC incidents
- SOC infra verification backend workflow
- `PUT /api/soc/incidents/{id}/infra-verify`
- `PUT /api/soc/incidents/{id}/infra-confirm`
- `PUT /api/soc/incidents/{id}/close`
- Operator can close incidents after Infra confirmation
- SOC Handling Trail displayed on incident cards
- Sync Candidate UI create action
- `/sync/` candidate cards can create or link existing SOC incidents
- Audit trail for sync candidate creation
- Audit trail for investigate / resolve / infra verify / infra confirm / close

## Workflow

```text
Local Sync Source
  ↓ stale / error / unknown

Sync Incident Candidate
  ↓ operator creates SOC incident

SOC Incident
  ↓ investigate
  ↓ resolve
  ↓ infra verify
  ↓ infra confirm normal
  ↓ close

Audit Logs
  ↓ complete actor trail
```

## Role Behavior

```text
Operator / Infra
  - Create SOC incident from sync candidate
  - Investigate incident
  - Resolve incident
  - Start Infra verification
  - Confirm normal
  - Close incident

Supervisor
  - Review Audit Logs
  - Mark false positive
  - Reopen incident if needed

Admin
  - Full access
  - Delete remains admin-only
```

## API Changes

### Sync to SOC

- `GET /api/sync/incident-candidates`
- `POST /api/sync/incident-candidates/{source}/create-soc-incident`

### SOC Infra Verification

- `PUT /api/soc/incidents/{incident_id}/infra-verify`
- `PUT /api/soc/incidents/{incident_id}/infra-confirm`
- `PUT /api/soc/incidents/{incident_id}/close`

## Current Product Status

```text
Sync Gateway  Detects local source health
Sync Candidate  Converts stale/error/unknown sources into SOC candidates
SOC             Incident lifecycle + Infra verification workflow
Infra / Operator Handles, verifies, confirms and closes incidents
Supervisor      Reviews audit trail and reopens if needed
Audit Logs      Records full handling trail with actor identity
```

## Next Phase

- Add SOC incident detail page
- Add per-incident timeline view
- Add source-to-incident relation view
- Add ServiceOps ticket creation from SOC incident
- Add automatic stale source SOC candidate refresh
- Add handled / ignored state for sync candidates
- Add source registration and ownership mapping
- Add SLA timer for unresolved incidents

---

## v0.6.1-sync-health-ui

Release date: 2026-05-21

## Summary

This release improves the Local Sync Gateway by adding source-level health detection and visual health summaries.

ENYRAX Cloud Portal can now determine whether each local source is healthy, warning, stale, error or unknown based on heartbeat freshness and recent error events.

## Completed

- Added Sync Source Health API
- Added `GET /api/sync/sources`
- Added stale heartbeat detection
- Added source health summary to `/api/sync/status`
- Added Source Health section to `/sync/`
- Added source health cards for local sync sources
- Added health badges for healthy / warning / stale / error / unknown
- Added source health summary row to `/status/`
- Added recent sync event compact display on `/status/`
- Improved Sync Gateway monitoring visibility

## Source Health Rules

```text
Recent 30 events include error
  → error

Latest heartbeat within 10 minutes
  → healthy

Latest heartbeat between 10 and 30 minutes
  → warning

Latest heartbeat older than 30 minutes
  → stale

No heartbeat
  → unknown
```

## API Changes

### Sync Gateway

- `GET /api/sync/sources`
- `GET /api/sync/status` now includes `source_health_summary`

## UI Changes

```text
/sync/
  - Source Health cards
  - Source health badge
  - Latest heartbeat
  - Latest event
  - Per-source ok / warning / error counts

/status/
  - Compact source health summary
  - Recent sync event display
  - Open Sync Gateway link remains available
```

## Current Product Status

```text
Sync Gateway  Local push API + dashboard enabled
Source Health  Healthy / Warning / Stale / Error / Unknown detection enabled
Local Agent   Prototype heartbeat / host / Docker / Wazuh collector enabled
Status Page   Cloud status + sync gateway source health summary
Sync Page     Detailed local source health dashboard
```

## Next Phase

- Add stale source alert generation
- Convert stale sync source into SOC incident candidate
- Add `/sync/events` filtering UI
- Add per-source detail page
- Add source registration table
- Add Wazuh agent status visualization
- Add local agent cron / systemd timer deployment guide
- Replace demo sync key with production key rotation

---

## v0.6.0-sync-gateway-demo

Release date: 2026-05-21

## Summary

This release introduces the Local Sync Gateway architecture for ENYRAX Cloud Portal.

The Tokyo cloud portal can now receive summarized events from local hosts through a controlled inbound API. Local machines can push heartbeat, host, Docker and Wazuh summaries without exposing local inbound ports.

This establishes the first version of ENYRAX hybrid-cloud operation monitoring:

```text
Tokyo Cloud Portal
  = Control Plane

Local Host / Lab / On-Prem Services
  = Data Plane

Local Sync Agent
  = Push-based sync bridge
```

## Completed

- Local Sync Gateway backend API
- `POST /api/sync/events`
- `GET /api/sync/events`
- `GET /api/sync/status`
- `local_sync_events` PostgreSQL table
- Sync API key protection with `X-Sync-Key`
- Local Sync Agent prototype
- `agents/local_sync_agent.py`
- Local heartbeat collector
- Local host summary collector
- Docker service status collector
- Wazuh alert summary collector
- `agents/README.md`
- `/sync/` frontend dashboard
- Portal homepage Sync Gateway module card
- `/status/` Sync Gateway status card
- Recent sync events display
- Warning / error sync status visibility

## API Endpoints

### Sync Gateway

- `POST /api/sync/events`
- `GET /api/sync/events`
- `GET /api/sync/status`

## Local Agent

```text
agents/local_sync_agent.py

Supported event types:
- heartbeat
- host_summary
- docker_service_status
- wazuh_alert_summary
```

## Environment Variables

```text
ENYRAX_SYNC_URL
  Default: https://portal.soc-monitoring.dev/api/sync/events

ENYRAX_SYNC_KEY
  Default: your-demo-sync-key

ENYRAX_SYNC_SOURCE
  Default: atn-local-lab
```

## Architecture

```text
Local Host
  ├── Docker
  ├── Wazuh
  ├── ERP / MES / HRM future systems
  └── local_sync_agent.py
          ↓ HTTPS POST + X-Sync-Key

Tokyo ENYRAX Cloud Portal
  ├── FastAPI /api/sync/events
  ├── PostgreSQL local_sync_events
  ├── /api/sync/status
  ├── /sync/
  └── /status/
```

## Current Product Status

```text
Portal        Public module entry
Login         Demo auth page enabled
Users         Demo users table enabled
SOC           RBAC + incident lifecycle backend
ServiceOps    RBAC + Archive / Restore
ProjectOps    RBAC + Archive / Restore
Audit Logs    Supervisor/Admin protected
Sync Gateway  Local push API + dashboard enabled
Local Agent   Prototype event collector enabled
Status Page   Cloud status + sync gateway summary
```

## Security Notes

- Local hosts push summaries to Tokyo cloud.
- Tokyo cloud does not need inbound access to local hosts.
- Sync API requires `X-Sync-Key`.
- Demo fallback key should be replaced before production use.
- First version syncs summaries, not full raw logs.

## Next Phase

- Add `/sync/events` filtering UI
- Add source health state calculation
- Add stale heartbeat detection
- Add Wazuh agent status visualization
- Add local agent cron or systemd timer
- Add stronger sync key rotation
- Add per-source registration table
- Connect sync warning events into SOC incidents

---

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
