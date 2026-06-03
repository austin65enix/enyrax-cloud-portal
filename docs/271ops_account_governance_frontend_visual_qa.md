# 271ops Account Governance Frontend Visual QA

## Task Summary

Task #212 reviews the Account Governance frontend section added to `/271ops/` in Task #211. The review focuses on layout readiness, API DATA behavior, DEMO FALLBACK behavior, read-only safety boundaries, and no-mutation behavior.

No backend, DB, API, fixture, script, release, deployment, nginx, cron, systemd, or tag changes were made.

## Scope

Reviewed file:

- `271ops/index.html`

Reviewed frontend area:

- `/271ops/` Account Governance section
- Account Governance KPI cards
- BPM Permission Requests
- Access Review Queue
- Access Lifecycle Events
- BPM / ServiceOps / IAM mapping flow
- Account Governance safety boundary
- Account Governance API DATA / DEMO FALLBACK handling

## Visual QA Checklist

| Check | Result | Notes |
| --- | --- | --- |
| Desktop layout | Pass | Account Governance KPI cards use `auto-fit` with responsive `minmax` sizing. Three data sections use a 3-column grid on wide viewports. |
| Tablet layout | Pass | `@media(max-width:980px)` changes Account Governance data cards to one column and KPI cards to two columns. |
| Mobile layout | Pass | `@media(max-width:600px)` changes Account Governance KPI cards and field grids to one column. |
| Flow chips wrapping | Pass | Mapping chips use flex wrap, `min-width: 0`, `overflow-wrap: anywhere`, and `word-break: break-word`. |
| Long IDs wrapping | Pass | Account cards and fields include `overflow-wrap: anywhere` and `word-break: break-word`. |
| Horizontal scroll risk | Pass | Page root keeps `max-width:100%; overflow-x:hidden`; Account Governance grids use `minmax(0,1fr)` and mobile one-column fallbacks. |
| Section clarity | Pass | BPM Permission Requests, Access Review Queue, and Access Lifecycle Events have separate headings, copy, and rendered card containers. |

## API DATA / DEMO FALLBACK Checklist

| Check | Result | Evidence |
| --- | --- | --- |
| `/271ops/` public page responds | Pass | `curl -I https://portal.soc-monitoring.dev/271ops/` returned `HTTP/1.1 200 OK`. |
| BPM Permission Requests API | Pass | Public API returned `source=fixture`, `mode=read_only`, `product=271ops`, `count=6`, `warnings=[]`. |
| Access Review Items API | Pass | Public API returned `source=fixture`, `mode=read_only`, `product=271ops`, `period=2026-06`, `count=8`, `warnings=[]`. |
| Access Lifecycle Events API | Pass | Public API returned `source=fixture`, `mode=read_only`, `product=271ops`, `count=12`, `warnings=[]`. |
| Account API DATA badge | Pass | DOM harness confirmed `ACCOUNT API DATA / 帳號治理 API 資料` renders when all three APIs are valid. |
| Fetch error fallback | Pass | DOM harness confirmed `ACCOUNT DEMO FALLBACK / 帳號治理 DEMO 備援` and fallback data render when one API fails. |
| Invalid schema fallback | Pass | DOM harness confirmed fallback when one API returns invalid schema. |
| Empty valid records | Pass | DOM harness confirmed valid empty `records` arrays keep the section nonblank with zero KPI values. |
| Warnings strip | Pass | DOM harness confirmed endpoint label, code, and message render when warnings are non-empty. |
| Main dashboard isolation | Pass | DOM harness confirmed the main 271ops dashboard still renders API DATA while Account Governance is tested independently. |

## Safety Boundary Checklist

| Safety item | Result |
| --- | --- |
| Does not directly change AD / LDAP / IAM / SaaS permissions | Pass |
| Does not store full BPM form content | Pass |
| Does not store raw attachment content | Pass |
| Does not store passwords | Pass |
| Does not store credentials | Pass |
| Does not store API keys | Pass |
| Does not store private keys | Pass |
| Does not store raw logs | Pass |
| Does not store sensitive personal data | Pass |
| Auditor-facing view remains read-only | Pass |

## No-mutation Checklist

| Check | Result | Notes |
| --- | --- | --- |
| No approve button | Pass | No `<button>` elements are present. Approval text appears only as read-only status metadata. |
| No reject button | Pass | No `<button>` elements are present. Rejected text appears only as read-only summary metadata. |
| No upload control | Pass | No upload input or action exists. Existing upload wording is read-only backup evidence copy outside Account Governance. |
| No delete control | Pass | No delete button or mutation action exists. |
| No edit control | Pass | No edit button or mutation action exists. |
| No localStorage write | Pass | Static scan and DOM harness found no `localStorage` usage. |
| No sessionStorage write | Pass | Static scan and DOM harness found no `sessionStorage` usage. |
| No write API call | Pass | Account Governance fetches use GET only; no POST, PUT, PATCH, or DELETE fetch methods were found. |

## Findings

- No blocking frontend issues were found in the Account Governance section.
- API DATA behavior is valid against the public read-only APIs.
- DEMO FALLBACK behavior is valid for fetch errors and invalid schemas.
- Empty valid record arrays keep the section visible and render zero KPI values instead of blanking the page.
- Safety boundary copy is explicit and auditor-facing.
- No mutation controls or write API calls were found.

## Limitations

- Browser screenshot QA was not executed because no Chromium, Chromium Browser, or Google Chrome binary was available in the execution environment.
- Responsive review was performed through CSS/static checks and DOM harness validation rather than pixel screenshots.
- JS console review was performed through a Node DOM harness that captures blocking script errors; a final browser-console pass is still recommended in a browser-capable QA runner.

## Recommended Next Task

Proceed with Account Governance release note preparation and browser-capable visual QA screenshots for desktop, tablet, and mobile before any release tag.
