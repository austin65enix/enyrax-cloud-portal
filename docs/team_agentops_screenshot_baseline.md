# Team_AgentOps Screenshot Baseline

Task: `#170 Team_AgentOps Static Dashboard Screenshot Baseline`

## Purpose

This checklist defines the screenshot baseline and visual regression review for
`/team-agentops/`. The dashboard is read-only and API-first:

* Primary state: `GET /api/team-agentops/dashboard` succeeds and the source badge
  shows `API DATA / API 資料`.
* Fallback state: the API is unavailable, invalid, or incomplete and the source
  badge shows `DEMO FALLBACK / DEMO 備援`.

The baseline must not change backend behavior, DB state, API contracts, fixtures,
or parser behavior.

## Task #170 Environment Result

Screenshot PNG files were not generated during Task #170 because the execution
environment did not provide Chromium, Chrome, Firefox, Playwright, or another
browser screenshot tool.

The local read-only fixture API was verified:

```text
GET http://127.0.0.1:8000/api/team-agentops/dashboard
source: fixture
mode: read_only
```

Expected future screenshot output paths:

```text
docs/screenshots/team-agentops/desktop-api-data.png
docs/screenshots/team-agentops/tablet-api-data.png
docs/screenshots/team-agentops/mobile-api-data.png
```

Optional fallback evidence:

```text
docs/screenshots/team-agentops/desktop-demo-fallback.png
docs/screenshots/team-agentops/tablet-demo-fallback.png
docs/screenshots/team-agentops/mobile-demo-fallback.png
```

## Capture Matrix

| Baseline | Viewport | Required state | Output |
| --- | --- | --- | --- |
| Desktop | `1440 x 1200` | API returns fixture dashboard | `desktop-api-data.png` |
| Tablet | `820 x 1180` | API returns fixture dashboard | `tablet-api-data.png` |
| Mobile | `390 x 844` | API returns fixture dashboard | `mobile-api-data.png` |

Capture full-page screenshots so the activity timeline, contribution cards,
review flow, scorecard, safety confirmation, and Shadow AI risk sections remain
reviewable.

## Stable Capture Setup

Before capturing the primary baseline:

* Serve the current portal locally.
* Confirm `GET /api/team-agentops/dashboard` returns HTTP `200`.
* Confirm the response includes `source: fixture` and `mode: read_only`.
* Open `/team-agentops/`.
* Wait until the source badge changes from `LOADING`.
* Confirm the badge reads `API DATA / API 資料`.
* Capture after fonts, shared headers, and dashboard content have rendered.
* Record the commit SHA used for capture.

For fallback evidence, block or mock `GET /api/team-agentops/dashboard` with a
non-`200` response, reload the same page, and confirm the badge reads
`DEMO FALLBACK / DEMO 備援`. Do not edit fixtures to force fallback mode.

## Visual Regression Checklist

### Shared Checks

* Page uses the dark ENYRAX glass dashboard style without a blank loading state.
* Bilingual English and Traditional Chinese copy remains visible.
* Shared portal navigation does not overlap the dashboard.
* No horizontal page overflow is visible.
* Source badge is visible and matches the captured mode.
* KPI cards render: Active Agents, Pending Review, Project Impact, Failed Runs,
  and Usage Cost.
* Usage Cost remains labeled as an operational estimate, not billing-grade data.
* Agent Activity Timeline rows remain readable and badges do not clip.
* Project Agent Contribution cards show progress meters and review badges.
* Human Review Flow preserves the human review delivery gate.
* Team Scorecard governance note remains visible.
* Safety Boundary Confirmation shows safe metadata constraints and read-only
  dashboard behavior.
* Shadow AI Risk copy remains visible.
* No prompt, response, raw session, credential, secret, API key, or full home
  path content appears in screenshots.

### Desktop `1440 x 1200`

* Hero copy and Safety Boundary panel render side by side.
* Five KPI cards render in one row.
* Activity Timeline and Project Agent Contribution render as two columns.
* Timeline task text and right-aligned status badges remain readable.
* Five Team Scorecard cards render in one row.

### Tablet `820 x 1180`

* Hero and Safety Boundary panel stack cleanly.
* KPI and Team Scorecard grids render as three columns where space permits.
* Activity Timeline and Project Agent Contribution sections stack vertically.
* Project contribution cards remain two columns.
* Human Review Flow wraps without clipped text.

### Mobile `390 x 844`

* Page padding remains consistent and no content touches the viewport edge.
* KPI and Team Scorecard cards stack into one column.
* Timeline rows use the mobile layout: time and agent first, with project, task,
  and badges stacked below.
* Project contribution cards stack into one column.
* Human Review Flow stacks vertically and hides separator arrows.
* Long bilingual copy and badges wrap without horizontal overflow.

## API And Fallback Comparison

The screenshot review must cover both source modes:

| Check | API DATA | DEMO FALLBACK |
| --- | --- | --- |
| Source badge | Cyan `API DATA / API 資料` | Amber `DEMO FALLBACK / DEMO 備援` |
| Helper copy | Read-only fixture API | API unavailable; local demo data |
| Dashboard content | API fixture records | Embedded safe demo records |
| Safety boundary | Visible | Visible |
| Read-only note | Visible | Visible |

API warnings, when returned, must render as a visible amber warning strip without
breaking the dashboard layout.

## Approval Record

When browser tooling becomes available, append:

```text
Capture date:
Commit SHA:
Browser and version:
API DATA desktop:
API DATA tablet:
API DATA mobile:
DEMO FALLBACK evidence:
Reviewer:
Result:
```

