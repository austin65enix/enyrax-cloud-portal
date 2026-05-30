# AgentOps Safe Metadata Project Signals

## Overview

AgentOps preview currently uses safety-first inference. Preview project inference intentionally prefers `unknown` over unsafe or weakly supported project labels.

Project inference is currently all unknown because Task #117 removed overly broad keyword matching and the parser does not yet have enough safe metadata signals to recover recall.

This document defines the next-stage project inference signals that Task #121 may use without reading sensitive content.

## Project Inference Semantics

Project inference currently uses safety-first metadata signals.

`agent_runs_preview.json` is a safe filename basename signal. When the preview output basename maps to AgentOps, the classification means the preview telemetry output is associated with the AgentOps pipeline.

This does not imply that the parser inspected session prompt, response, shell output, command text, diff, file contents, or raw JSONL content. It also does not guarantee that every underlying session's work content was AgentOps.

The current result should be interpreted as pipeline-level operational classification. Preview project values are operational metadata, not authoritative content-level labels.

## Current Problem

Current preview review status:

* records: 50
* unknown_project_count: 50
* unknown_task_count: 50
* top_projects: unknown: 50
* review status: passed
* forbidden_hits: {}
* extra_fields: {}

Portal Architecture overmatching has been eliminated. False positive risk is lower, but recall is also low.

The next step is to strengthen safe metadata signals. It must not return to content-based inference.

## Safety Boundary

The following content must not be used for project inference:

* prompt
* response
* shell output
* command text
* file contents
* diff
* raw JSONL line
* credentials
* full home path
* secret values
* arbitrary source code content

Project inference must not inspect user-authored content or generated content.

## Allowed Safe Metadata Signals

### 1. Allowlisted Filename Basename

Allowlisted filename basenames may be used as strong safe signals.

Examples:

* agentops_preview_full_limit_review.md
* agentops_preview_quality_release_note.md
* codex_session_parser_safe_metadata_plan.md
* parse_codex_sessions.py
* review_agentops_preview.py

Only the basename is allowed. Full paths must not be used.

### 2. Known Project Directory Basename

Known project directory basenames may be considered when they are allowlisted and do not include full home paths.

Examples:

* enyrax-portal
* agentops
* docs
* scripts
* data/agentops

Only allowlisted project root basenames or repo basenames may be used. Full home paths must not be stored or used.

### 3. Explicit Safe Metadata Fields

If Codex session metadata includes explicit safe fields, Task #121 may consider:

* model
* timestamp
* session id hash
* working directory basename
* tool name category
* file basename list
* git branch basename
* git tag name if already safe and explicit

Raw JSONL content must not be read or saved for inference.

### 4. Allowlisted Document Title Hints

Known safe document basename or release note title hints may be used.

Examples:

* AgentOps Preview Quality Release Note
* AgentOps Preview Full Limit Review
* Codex Session Parser Safe Metadata Plan

Titles must not be inferred from prompt or response content.

### 5. Explicit Project Mapping Table

Task #121 can use a conservative allowlist mapping table.

Examples:

* parse_codex_sessions.py -> AgentOps
* review_agentops_preview.py -> AgentOps
* agent_runs_preview.json -> AgentOps
* agentops_preview_quality_release_note.md -> AgentOps
* codex_session_parser_safe_metadata_plan.md -> AgentOps

The mapping should remain conservative. If no explicit mapping matches, inference should return `unknown`.

### 6. Preview Output Basename

The preview output basename is allowed as a safe metadata signal, but it should be treated as a pipeline-level signal.

`agent_runs_preview.json` may map to AgentOps because the preview telemetry output belongs to the AgentOps pipeline. Per-session safe filename basenames are preferred when available because they are closer to the underlying session metadata.

Future schema work may split project metadata into:

* `pipeline_project`
* `session_project`

No schema change is included in this task.

## Disallowed Signals

The following signals are explicitly prohibited:

* project inference from prompt text
* project inference from response text
* project inference from shell command text
* project inference from git diff content
* project inference from source code content
* project inference from full path values
* project inference from secrets, credentials or environment values
* project inference from arbitrary log content

## Scoring Proposal

Task #121 should use conservative scoring, but this task does not implement it.

Suggested scoring:

* strong allowlisted filename basename match: +3
* known project directory basename match: +2
* explicit safe metadata project tag: +4
* safe release/document basename match: +3
* weak generic terms: 0
* ambiguous match: 0
* minimum score for project inference: 3
* tie returns unknown unless priority is explicitly defined and documented

Requirements:

* No first-match wins.
* No generic words like `portal`, `architecture`, `docs`, or `scripts` alone.
* No content-based scoring.
* Unknown is preferred over unsafe inference.

## Example Mapping

| Safe signal        | Example                                  | Project  | Score | Notes                   |
| ------------------ | ---------------------------------------- | -------- | ----: | ----------------------- |
| filename basename  | parse_codex_sessions.py                  | AgentOps |     3 | explicit parser file    |
| filename basename  | review_agentops_preview.py               | AgentOps |     3 | explicit review file    |
| filename basename  | agent_runs_preview.json                  | AgentOps |     3 | explicit preview output |
| document basename  | agentops_preview_quality_release_note.md | AgentOps |     3 | explicit release note   |
| directory basename | agentops                                 | AgentOps |     2 | safe directory basename |
| generic word       | portal                                   | unknown  |     0 | too broad               |
| generic word       | architecture                             | unknown  |     0 | too broad               |


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

`AgentOps: 50` is based on safe preview output basename mapping from `agent_runs_preview.json`. This is a conservative pipeline-level classification, not content-level session classification. Future work may separate `pipeline_project` from `session_project` if schema changes are approved.

## Task Inference Safe Allowlist

Task inference uses a safe metadata allowlist only. Explicit filename basename mapping can infer AgentOps task names when the basename is allowlisted. Generic words do not receive score, content-based inference remains prohibited, tie or ambiguous matches return `unknown`, and `unknown` remains preferred over unsafe inference.

Allowed AgentOps task basename mapping:

| filename basename                          | task                                    |
| ------------------------------------------ | --------------------------------------- |
| agentops_preview_quality_release_note.md   | AgentOps Preview Quality Release Note   |
| agentops_safe_metadata_project_signals.md  | Safe Metadata Project Signals Design    |
| agentops_preview_full_limit_review.md      | AgentOps Preview Full Limit Review      |
| agentops_preview_review_checklist.md       | AgentOps Preview Review Checklist       |
| codex_session_parser_safe_metadata_plan.md | Codex Session Parser Safe Metadata Plan |
| parse_codex_sessions.py                    | Codex Session Parser Maintenance        |
| review_agentops_preview.py                 | AgentOps Preview Review                 |
| agent_runs_preview.json                    | AgentOps Preview Generation             |

Task scoring uses `TASK_MINIMUM_SCORE = 3`. Strong allowlisted filename basename matches score 3. Safe document basename matches score 3. The preview output basename `agent_runs_preview.json` scores 3. Weak generic words score 0. Ambiguous matches and ties return `unknown`; there is no first-match-wins task inference.

If `agent_runs_preview.json` is used as a task signal, the task classification means the preview telemetry output is associated with AgentOps Preview Generation. This is pipeline-level operational task classification, not authoritative session-content-level task classification.

Future schema may separate:

* `pipeline_project`
* `session_project`
* `pipeline_task`
* `session_task`

Task #122 result:

* before unknown_task_count: 50
* after unknown_task_count: 0
* top_tasks: AgentOps Preview Generation: 50
* review status: passed

## Review Requirements for Future Task #121

Task #121 implementation should preserve:

* review status passed
* forbidden_hits: {}
* extra_fields: {}
* records_with_unknown_model: 0
* records_with_zero_tokens reasonable
* no preview schema changes unless explicitly approved
* no content-based project inference

Task #121 should compare before / after:

* unknown_project_count
* top_projects
* false positive risk
* review result
* grep checks for forbidden terms
