# AgentOps Preview Full Limit Review

## 1. Purpose

This review regenerated AgentOps preview telemetry with a larger `--limit 50` sample to check:

* whether project inference is over-concentrated
* whether model inference is stable
* whether duration inference is effective
* whether unknown `task_number` values match the safety strategy
* whether token totals may be cumulative estimates
* whether preview output still passes safety review

## 2. Command Used

```bash
python3 scripts/parse_codex_sessions.py \
  --dry-run \
  --input ~/.codex/sessions \
  --limit 50 \
  --preview-output data/agentops/agent_runs_preview.json

python3 scripts/review_agentops_preview.py
python3 scripts/review_agentops_preview.py --json | python3 -m json.tool
```

## 3. Review Result

* review status: passed
* records: 50
* forbidden hits: {}
* extra fields: {}
* status counts: unknown 50
* total tokens: 1058156153
* cached tokens: 0
* output tokens: 11661168
* reasoning tokens: 0
* tool calls: 1355
* files modified: 1354
* commands run: 1
* unknown project count: 0
* unknown task count: 50
* records with unknown model: 0
* zero duration count: 0
* records with zero tokens: 0

## 4. Project Inference Distribution

Top projects:

* Portal Architecture: 48
* AgentOps: 2

Project inference may be overmatching. Keyword priority should be reviewed before using preview data for reporting.


## Project Keyword Priority Review

Original distribution before Task #117:

* Portal Architecture: 48
* AgentOps: 2

Adjustment strategy:

* switched to scoring-based inference
* reduced generic portal / architecture overmatching
* added tie priority
* required minimum score threshold

New distribution after Task #117:

* unknown: 50

Portal Architecture overmatching improved because generic `portal` and `architecture` no longer assign Portal Architecture by themselves. AgentOps did not increase in this 50-record preview because the safe metadata candidates did not reach the minimum score threshold. The current result is conservative and should be treated as low-confidence project inference rather than reporting-ready project telemetry.

## 5. Task Number Inference

The review found `unknown_task_count` at 50 of 50 records.

Most task numbers remain unknown because the parser keeps task inference safety-first and does not derive task numbers from prompts or responses.

Task number inference remains conservative. Unknown task values are acceptable when safe metadata does not include Task #NNN.

## 6. Token Quality

Token totals are large for preview telemetry, with `total_tokens` at 1058156153 and `output_tokens` at 11661168 across 50 records.

These totals may represent cumulative session usage rather than normalized per-run usage.

Preview token totals are operational estimates only and should not be used as billing-grade cost data.


## Token Normalization Review

Original `total_tokens` before Task #118:

* 1058156153

Normalization strategy:

* cumulative snapshots use max value
* delta-like snapshots may be summed
* `total_tokens` missing values use component tokens for estimation

New `total_tokens` after Task #118:

* 50078459

Token normalization produced a clear improvement. The full limit preview total dropped from 1058156153 to 50078459 while keeping `records_with_zero_tokens` at 0 and the safety review status at passed.

Preview token totals remain operational estimates and are not billing-grade cost data.

## 7. Safety Boundary

The preview output does not store raw prompts, responses, shell output, command text, file contents, diffs, raw JSONL lines, credentials, API keys, passwords, .env values or full home directory paths.

## 8. Decision

The preview output passed safety review and can remain available behind the explicit source=preview toggle.

Project inference should be improved before using preview telemetry in reports.

Token normalization should be improved before cost estimation.


## Task #119 Preview Quality Release Note

Task #119 added `docs/agentops_preview_quality_release_note.md` to summarize the AgentOps preview quality work from Tasks #116 through #118.

The release note records the passed full limit review, Project Inference overmatching fix, Token Normalization improvement, unchanged preview schema, safety boundary, known limitations, and recommended next step for improving safe metadata project signals.

Preview token totals remain operational estimates and are not billing-grade cost data.


## Task #120 Safe Metadata Project Signals

Task #120 added `docs/agentops_safe_metadata_project_signals.md` as the design input for future Task #121 project inference recall work.

The design keeps the Safety Boundary intact and recommends conservative metadata-only signals: allowlisted filename basenames, known project directory basenames, explicit safe metadata fields, allowlisted document title hints, and explicit project mapping tables.

It explicitly disallows content-based inference and keeps `unknown` preferred over unsafe project inference.


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

`AgentOps: 50` is based on safe preview output basename mapping from `agent_runs_preview.json`. This is a conservative pipeline-level classification, not billing-grade, content-derived, or session-content-level project classification. Future work may separate `pipeline_project` from `session_project` if schema changes are approved.

## Project Inference Semantics

Project inference currently uses safety-first metadata signals.

`agent_runs_preview.json` is a safe filename basename signal. When the preview output basename maps to AgentOps, the classification means the preview telemetry output is associated with the AgentOps pipeline.

This does not imply that the parser inspected session prompt, response, shell output, command text, diff, file contents, or raw JSONL content. It also does not guarantee that every underlying session's work content was AgentOps.

The current result should be interpreted as pipeline-level operational classification. Preview project values are operational metadata, not authoritative content-level labels.

## Task Inference Safe Allowlist

Task inference uses a safe metadata allowlist only. Explicit filename basename mapping can infer AgentOps task names when the basename is allowlisted. Generic words do not receive score, content-based inference remains prohibited, tie or ambiguous matches return `unknown`, and `unknown` remains preferred over unsafe inference.

Task scoring uses `TASK_MINIMUM_SCORE = 3`. Strong allowlisted filename basename matches score 3. Safe document basename matches score 3. The preview output basename `agent_runs_preview.json` scores 3 and maps to `AgentOps Preview Generation`. Weak generic words score 0. Ambiguous matches and ties return `unknown`; there is no first-match-wins task inference.

If `agent_runs_preview.json` is used as a task signal, the task classification means the preview telemetry output is associated with AgentOps Preview Generation. This is pipeline-level operational task classification, not authoritative session-content-level task classification. Future schema may separate `pipeline_project`, `session_project`, `pipeline_task`, and `session_task`.

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

## AgentOps Risk & Anomaly Detection

Task #128 adds a first Risk & Anomaly Detection section to the AgentOps Preview Dashboard.

The first version uses explainable rule-based indicators. Current overall risk level: Low. Blocking risks: 0. Caution items: 3. Caution items are token estimate caution, classification semantics caution, and trend sample data caution.

Risk indicators are based on review status, forbidden hits, extra fields, unknown model count, zero token records, token normalization, project/task coverage, and trend sample status. Risk indicators are not AI answer quality. Risk indicators are not session-content-level correctness. Risk indicators are not billing-grade cost detection.

No parser, schema, backend, review script, or preview JSON changes were made.

## AgentOps Release Quality Score

Task #127 adds a first Release Quality Score section to the AgentOps Preview Dashboard.

The first score is a dashboard-level preview release/readiness indicator. Current score: 98 / 100. Score is based on review status, forbidden hits, extra fields, unknown model count, zero token records, project/task coverage, and token estimate caution.

Score is not billing-grade cost data. Score is not AI answer quality. Score is not session-content-level correctness. No parser, schema, backend, review script, or preview JSON changes were made.

## AgentOps Trend Chart

Task #126 adds a first Trend Chart / Trend Snapshot section to the AgentOps Preview Dashboard.

The first version uses static sample trend data or dashboard-local constants. No parser, schema, backend, review script, or preview JSON changes were made. Trend metrics are dashboard-level operational indicators. Token values remain operational estimates, not billing-grade cost data. Project / task coverage trend does not imply content-level classification accuracy.

Future versions may use generated historical snapshots after schema and storage design are approved.

## 9. Recommended Next Step

Recommended next tasks:

* Task #117: Improve AgentOps Project Keyword Priority
* Task #118: Normalize AgentOps Token Usage for Cumulative Sessions

Prioritize Task #117 first because project overmatching affects reporting categorization before cost estimation.
