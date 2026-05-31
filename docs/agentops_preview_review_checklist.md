# AgentOps Preview Review Checklist

## Purpose

AgentOps preview output review is the safety and quality check before parser preview data is considered for API or UI integration.

The review confirms that `data/agentops/agent_runs_preview.json` contains only safe metadata and remains separate from production demo data.

## Checklist

* JSON is valid
* JSON is an array
* records only use allowlist fields
* no prompt / response
* no shell output
* no file contents
* no .env values
* no API keys
* no password
* no full /home/ path
* no raw JSONL lines
* source is codex_local_preview
* demo_agent_runs.json is not overwritten
* preview output is not yet used as production data

## Review Command

```bash
python3 scripts/review_agentops_preview.py
python3 scripts/review_agentops_preview.py --json | python3 -m json.tool
```

## Inference Quality Review

Review preview quality metrics after regenerating `data/agentops/agent_runs_preview.json`:

* `unknown_project_count`
* `unknown_task_count`
* `unknown_model_count` / `records_with_unknown_model`
* `zero_duration_count` / records with `duration_seconds` equal to `0`
* `large_token_run_count`

Unknown values are acceptable when safe inference is not possible. The review should confirm that quality improved where safe metadata exists without expanding the parser beyond its safety boundary.

## Inference UI Indicators

Preview UI must indicate inferred values so users can distinguish safety-reviewed preview telemetry from reporting data.

Unknown task values are acceptable when safe metadata does not include `Task #NNN`. The UI should explain that task numbers are not inferred from prompts or responses.

Project inference may over-match keywords and should be reviewed before reporting. If most preview runs map to one project, the UI should show a review hint.

Preview telemetry is operational insight, not an official productivity or billing report.

## Project Inference Semantics

Project inference currently uses safety-first metadata signals.

`agent_runs_preview.json` is a safe filename basename signal. When the preview output basename maps to AgentOps, the classification means the preview telemetry output is associated with the AgentOps pipeline.

This does not imply that the parser inspected session prompt, response, shell output, command text, diff, file contents, or raw JSONL content. It also does not guarantee that every underlying session's work content was AgentOps.

The current result should be interpreted as pipeline-level operational classification. Preview project values are operational metadata, not authoritative content-level labels.

Checklist additions:

* If preview output basename is used as a project signal, document that the result is pipeline-level classification.
* Do not present pipeline-level classification as content-level session classification.
* Continue to avoid content-based inference.
* Unknown remains preferred when safe per-session metadata is insufficient.

## Task Inference Safe Allowlist

Task inference review must verify that task values use safe metadata allowlist signals only. Explicit filename basename mapping may infer AgentOps task names, but generic words such as `preview`, `review`, `docs`, `scripts`, or `parser` must not infer task values by themselves.

Checklist additions:

* Confirm `TASK_MINIMUM_SCORE = 3` remains documented and enforced.
* Confirm allowlisted filename basename matches can infer AgentOps task names.
* Confirm content-based inference remains prohibited.
* Confirm tie or ambiguous match returns `unknown`.
* Confirm `unknown` remains preferred over unsafe inference.
* If `agent_runs_preview.json` is used as a task signal, document that the result is pipeline-level operational task classification.
* Do not present pipeline-level task classification as authoritative session-content-level task classification.

Task #122 result:

* before unknown_task_count: 50
* after unknown_task_count: 0
* top_tasks: AgentOps Preview Generation: 50
* review status: passed

## AgentOps Dashboard Metrics Design

Task #123 defines dashboard KPI cards, chart sections, metric semantics, warning copy, and Task #124 UI handoff.

Dashboard metrics remain operational indicators. Token values are not billing-grade cost data. Project / task values may be pipeline-level metadata classifications. Content-based inference remains prohibited.

## AgentOps Preview Dashboard UI

Task #124 implements the first AgentOps Preview Dashboard UI.

The UI includes KPI cards, project/task distribution, token normalization summary, review health, and metric semantics. Dashboard uses operational metrics defined in Task #123. Token values remain operational estimates, not billing-grade cost data. Project / task values may be pipeline-level metadata classifications. Content-based inference remains prohibited.

No parser, schema, backend, or preview JSON changes were made.

## AgentOps Dashboard Visual QA and Demo Notes

Task #125 performs visual QA / responsive pass for the AgentOps Preview Dashboard UI.

Task #125 adds explainability demo notes for non-parser audiences. Demo notes explain AgentOps positioning, token normalization, review health, project/task semantic boundaries, and safety constraints.

No parser, schema, backend, review script, or preview JSON changes were made.

## AgentOps Dashboard Preview Release

Task #129 packages Tasks #123-#128 as AgentOps Dashboard Preview.

Suggested tag: `v0.6.22-agentops-dashboard-preview`. Preview review remains passed. This release preserves safety boundaries and semantic warnings. Future work should focus on historical snapshots and schema split design.

## AgentOps Historical Snapshots Schema Design

Task #130 defines the historical snapshot schema for future real Trend Chart data.

Snapshot v1 stores aggregate dashboard-level operational metrics. Snapshot v1 does not store prompt / response, shell output, command text, diff, file contents, raw JSONL, credentials, or full home paths.

Recommended MVP storage is JSON files under `data/agentops/snapshots/`. Token values remain operational estimates, not billing-grade cost data. Project / task values may remain pipeline-level metadata classifications.

Future work should implement snapshot generation in Task #131.

Historical Snapshot review items:

* Snapshot files must use `schema_version`.
* Snapshot files must not store raw prompt / response / command output.
* Snapshot files must not store credentials or full home paths.
* Snapshot `preview_file` must be basename only.
* Snapshot values must be aggregate operational metrics.
* Snapshot token values must preserve operational-estimate warning.
* Snapshot project / task values must preserve pipeline-level warning.
* Snapshot schema changes must be versioned.

## AgentOps Risk & Anomaly Detection

Task #128 adds a first Risk & Anomaly Detection section to the AgentOps Preview Dashboard.

The first version uses explainable rule-based indicators. Current overall risk level: Low. Blocking risks: 0. Caution items: 3. Caution items are token estimate caution, classification semantics caution, and trend sample data caution.

Risk indicators are based on review status, forbidden hits, extra fields, unknown model count, zero token records, token normalization, project/task coverage, and trend sample status. Risk indicators are not AI answer quality. Risk indicators are not session-content-level correctness. Risk indicators are not billing-grade cost detection.

No parser, schema, backend, review script, or preview JSON changes were made.

Risk & Anomaly Detection review items:

* Risk indicators must be rule-based and explainable.
* Risk indicators must not be presented as AI answer quality.
* Risk indicators must not be presented as session-content-level correctness.
* Risk indicators must preserve token operational estimate warning.
* Risk indicators must preserve pipeline-level classification warning.
* Risk indicators must clearly label sample trend data.
* Overall risk must not say "no risk" when caution items exist.
* Blocking risks and caution items must be visible.
* Risk UI must remain readable on mobile.

## AgentOps Release Quality Score

Task #127 adds a first Release Quality Score section to the AgentOps Preview Dashboard.

The first score is a dashboard-level preview release/readiness indicator. Current score: 98 / 100. Score is based on review status, forbidden hits, extra fields, unknown model count, zero token records, project/task coverage, and token estimate caution.

Score is not billing-grade cost data. Score is not AI answer quality. Score is not session-content-level correctness. No parser, schema, backend, review script, or preview JSON changes were made.

Release Quality Score review items:

* Score must be labeled as preview release/readiness quality.
* Score must not be presented as AI answer quality.
* Score must not be presented as session-content-level correctness.
* Score must preserve token operational estimate warning.
* Score must preserve pipeline-level classification warning.
* Score must remain explainable by visible metrics.
* Score must not hide failed review, forbidden hits, extra fields, unknown model, or zero token warnings.

## AgentOps Trend Chart

Task #126 adds a first Trend Chart / Trend Snapshot section to the AgentOps Preview Dashboard.

The first version uses static sample trend data or dashboard-local constants. No parser, schema, backend, review script, or preview JSON changes were made. Trend metrics are dashboard-level operational indicators. Token values remain operational estimates, not billing-grade cost data. Project / task coverage trend does not imply content-level classification accuracy.

Future versions may use generated historical snapshots after schema and storage design are approved.

Trend Chart review items:

* Trend chart must label sample data clearly.
* Trend chart must not imply full historical telemetry unless real historical data exists.
* Token trend must preserve operational estimate warning.
* Project / task coverage trend must preserve pipeline-level / non-content-level warning.
* Trend UI must remain readable on mobile.

## Decision Gate

Only when review status is `passed` may the work proceed to Task #109: AgentOps Preview API Source Toggle.

## API Source Toggle

API default remains demo data.

Preview data is only used when `source=preview` is explicitly requested.

Preview data must pass review before use.

Preview responses include a warning and quality notes.

Preview is not production telemetry.

## Preview Quality Guard

Preview telemetry may include cumulative token totals.

Unknown project/task/model values are expected when the parser cannot infer safely.

Large token totals are flagged but not blocked.

Preview data is not billing-grade cost data.

Preview data is for operational insight only.

## Full Limit Review

Small preview samples may hide inference bias.

Larger preview review should be run before using preview telemetry for reports.

Full limit review should check project distribution, unknown task count, zero duration count and large token totals.

If one project dominates unexpectedly, keyword inference may be overmatching.

Preview remains opt-in and not production telemetry.

## Token Normalization Review

Full limit preview should compare token totals before and after normalization.

Large token totals may still occur.

Token values are operational estimates, not billing-grade.

If token values remain inflated, UI must continue showing estimated / cumulative warning.

## Project Inference Recall Improvement

Task #121 implemented safe metadata scoring for project inference.

The parser uses explicit AgentOps filename basename mapping and conservative scoring. Generic words do not receive score, content-based inference remains prohibited, and tie or ambiguous matches return `unknown`. Unknown remains preferred over unsafe inference.

Current scoring uses `PROJECT_MINIMUM_SCORE = 3`. Explicit AgentOps filename basename matches score 3.

Before Task #121:

* unknown_project_count: 50
* top_projects: unknown: 50

After Task #121:

* unknown_project_count: 0
* top_projects: AgentOps: 50
* review status: passed
`AgentOps: 50` is based on safe preview output basename mapping from `agent_runs_preview.json`. This is a conservative pipeline-level classification. Future work may separate `pipeline_project` from `session_project` if schema changes are approved.

## AgentOps Snapshot Generation

Task #131 implements the first snapshot generator.

Generator reads `review_agentops_preview.py --json` aggregate review output.

Generator does not read raw session files or prompt / response content.

Generated snapshots are stored under `data/agentops/snapshots/`.

First generated snapshots:

* `data/agentops/snapshots/daily/2026-05-31.json`
* `data/agentops/snapshots/releases/v0.6.22-agentops-dashboard-preview.json`

Snapshot values remain operational estimates and dashboard-level indicators.

Snapshot Generation review items:

* Generator must only read aggregate review JSON.
* Generator must not read raw session files.
* Generator must not read prompt / response content.
* Generator must not copy arbitrary review JSON fields.
* Snapshot `preview_file` must be basename only.
* Snapshot output must use `schema_version: agentops_snapshot_v1`.
* Snapshot JSON must be valid and pretty-printed.
* Snapshot values must preserve operational-estimate and pipeline-level warnings.

## AgentOps Snapshot Trend Integration

Task #132 connects Trend Snapshot UI to historical snapshot index data.

Trend UI uses `data/agentops/snapshots/index.json` when available.

If snapshot index is unavailable, UI falls back to static sample data.

Snapshot index contains aggregate dashboard-level metrics only.

Snapshot trend values remain operational indicators.

Token values are not billing-grade cost data.

Project / task coverage does not imply content-level classification accuracy.

No prompt / response content is used.

Snapshot Trend Integration review items:

* Snapshot index must not contain raw prompt / response / command output.
* Snapshot index paths must be relative safe paths.
* Trend UI must clearly label snapshot-backed data vs sample fallback.
* Trend UI must preserve token operational estimate warning.
* Trend UI must preserve pipeline-level classification warning.
* Fetch failure must not break the dashboard.
* Trend UI must remain mobile readable.


## AgentOps Snapshot Index Publish Path

Task #133 documents how `/data/agentops/snapshots/index.json` should be served by nginx.

Only `/data/agentops/snapshots/` should be exposed, not the entire `/data/` tree. Snapshot files contain aggregate operational metrics only. Use `Cache-Control: no-store` for preview dashboard freshness. Trend UI must fall back to clearly labeled sample data if the snapshot index is unavailable.

Snapshot Index Publish Path review items:

* Confirm nginx uses `root /var/www/enyrax-portal`.
* Confirm `/data/agentops/snapshots/index.json` returns `200`.
* Confirm `/data/agentops/snapshots/` uses `Cache-Control: no-store`.
* Confirm other `/data/` paths return `404`.
* Confirm snapshot files contain aggregate operational metrics only.
* Confirm Trend UI fallback remains labeled as sample data.

## AgentOps Snapshot Auto Update Workflow

Task #134 adds `scripts/update_agentops_snapshots.py`.

The auto update workflow generates daily snapshots and updates the snapshot index from aggregate review JSON only. It does not regenerate preview JSON and does not read raw sessions or prompt / response content.

This keeps snapshot trend data aligned with generated historical snapshots. Release snapshots remain explicit and require `--write-release`.

Auto Update review items:

* Auto update script must not run parser preview regeneration.
* Auto update script must not read `~/.codex/sessions`.
* Auto update script must only use aggregate review output.
* Auto update script must update index without duplicate `snapshot_date` entries.
* Snapshot index paths must remain safe relative paths.
* Release snapshot update must require explicit `--write-release`.
* Generated JSON must be pretty-printed and valid.
* Trend UI must still fallback if index is unavailable.

## AgentOps Snapshot Scheduled Update

Task #135 documents scheduled update deployment. The schedule runs `scripts/update_agentops_snapshots.py` to update the daily snapshot and snapshot index.

The schedule does not regenerate preview JSON and does not read raw sessions or prompt / response content. The first version does not auto commit or auto push generated files.

Scheduled Update review items:

* Scheduled update must not run parser regeneration.
* Scheduled update must not read `~/.codex/sessions`.
* Scheduled update must log output to a known file.
* Scheduled update must not auto commit or auto push in v1.
* Remote snapshot index must return `200`.
* Preview fixture must remain `404`.
* `Cache-Control` should remain `no-store`.
