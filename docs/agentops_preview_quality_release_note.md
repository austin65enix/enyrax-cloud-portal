# AgentOps Preview Quality Release Note

## 1. Overview

This release note summarizes the AgentOps preview quality improvements completed across the full limit review, project inference priority update, and token normalization work.

The purpose is to make preview telemetry safer and less misleading before it is used for operational reporting. Preview data remains opt-in, safety-reviewed metadata for operational reporting only. It is not billing-grade cost data.

## 2. Completed Improvements

* Full limit review completed with `--limit 50` preview telemetry.
* Project inference overmatching fixed by reducing generic Portal Architecture matches.
* Token normalization completed for cumulative-looking token snapshots.
* Preview schema remains unchanged.
* Review status passed.

## 3. Project Inference Quality

Original project inference distribution:

* Portal Architecture: 48
* AgentOps: 2

Updated project inference distribution:

* unknown: 50

Portal Architecture overmatching has been eliminated. Generic `portal` and `architecture` signals no longer infer Portal Architecture by themselves.

Project inference recall is currently low, but this is acceptable for the safety-first preview strategy. The next improvement should strengthen safe metadata project signals without returning to content-based inference.

Task #121 project inference recall result:

* after unknown_project_count: 0
* top_projects: AgentOps: 50
* review status: passed

`AgentOps: 50` is based on safe preview output basename mapping from `agent_runs_preview.json`. This is a conservative pipeline-level classification, not billing-grade, content-derived, or session-content-level project classification. Future work may separate `pipeline_project` from `session_project` if schema changes are approved.

## Project Inference Semantics

Project inference currently uses safety-first metadata signals.

`agent_runs_preview.json` is a safe filename basename signal. When the preview output basename maps to AgentOps, the classification means the preview telemetry output is associated with the AgentOps pipeline.

This does not imply that the parser inspected session prompt, response, shell output, command text, diff, file contents, or raw JSONL content. It also does not guarantee that every underlying session's work content was AgentOps.

The current result should be interpreted as pipeline-level operational classification. Preview project values are operational metadata, not authoritative content-level labels.

## Task Inference Safe Allowlist

Task #122 added safe metadata allowlist task inference for AgentOps task names. Explicit filename basename mapping can infer AgentOps tasks, generic words do not receive score, content-based inference remains prohibited, tie or ambiguous matches return `unknown`, and `unknown` remains preferred over unsafe inference.

Task scoring uses `TASK_MINIMUM_SCORE = 3`. Strong allowlisted filename basename matches score 3. Safe document basename matches score 3. The preview output basename `agent_runs_preview.json` scores 3 and maps to `AgentOps Preview Generation`.

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

## 4. Token Normalization Quality

Original `total_tokens`:

* 1058156153

New `total_tokens`:

* 50078459

Cumulative-looking snapshots use the maximum observed numeric value. Delta-like snapshots may be summed conservatively. If `total_tokens` is missing, component tokens are used for estimation.

Preview token totals remain operational estimates and are not billing-grade cost data.

## 5. Review Result

* records: 50
* status: passed
* forbidden_hits: {}
* extra_fields: {}
* records_with_zero_tokens: 0
* records_with_unknown_model: 0
* unknown_project_count: 50
* unknown_task_count: 50

## 6. Safety Boundary

The preview parser and this release note do not read or store sensitive content for preview quality reporting.

Disallowed content includes:

* prompt
* response
* shell output
* command text
* file contents
* diff
* raw JSONL line
* credentials
* full home path

This release note only describes preview metadata quality and does not introduce sensitive content.

## 7. Known Limitations

* Project inference recall is currently low.
* Task inference remains unknown for all 50 records.
* Token values may still be large because sessions can be long or cumulative.
* Values should continue to be displayed with estimated / cumulative warning.

## 8. Recommended Next Step

Strengthen safe metadata project signals without returning to content-based inference.

Do not use prompts, responses, shell output, or command text to infer project or task values.

Possible recall improvements can use allowlisted filename signals, safe tags, known project directory basenames, and explicit metadata fields.

## 9. Task #120 Safe Metadata Project Signals

Task #120 added `docs/agentops_safe_metadata_project_signals.md` to define safe metadata signals for a future project inference recall improvement.

The design allows conservative signals such as allowlisted filename basenames, known project directory basenames, explicit safe metadata fields, allowlisted document title hints, and explicit project mapping tables.

It rejects content-based inference from prompts, responses, shell output, command text, file contents, diffs, raw JSONL lines, credentials, full home paths, and arbitrary source code content. Preview token totals remain operational estimates and are not billing-grade cost data.
