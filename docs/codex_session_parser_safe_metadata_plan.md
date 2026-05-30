# Codex Session Parser Safe Metadata Plan

## 1. Goal

Establish a safe Codex session parser plan for extracting AgentOps metadata from local Codex session logs.

The first phase extracts statistics only. It does not save full conversation content.

Core question:

```text
How much work did my Codex / AI Agent do for me today?
```

## 2. Expected Local Source

Possible local sources:

```text
~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
~/.codex/history.jsonl
```

Notes:

* `sessions` JSONL may contain full conversations, tool calls, token usage, timestamps, working directories, and related execution metadata.
* `history.jsonl` may help infer command, cwd, and started context.
* Actual field formats may change across Codex CLI versions, so the parser must use defensive parsing.

## 3. Safety Principle

Use allowlist extraction, not blocklist filtering.

This means:

* Read only explicitly allowed metadata fields.
* Do not save full JSONL first and then try to delete sensitive content.
* Treat every raw line as potentially sensitive unless a specific metadata field has been approved for extraction.

## 4. Allowed Metadata

The first version may extract only:

* `session_id`
* `source`
* `project_name`
* `task_name`
* `task_number`
* `started_at`
* `ended_at`
* `duration_seconds`
* `status`
* `result_summary`
* `model`
* `input_tokens`
* `cached_tokens`
* `output_tokens`
* `reasoning_tokens`
* `total_tokens`
* `tool_calls`
* `files_modified_count`
* `commands_run_count`
* `error_count`
* `warning_count`
* `working_directory_hash`
* `repo_name`
* `created_at`

`working_directory_hash` may store a hash, but not the full path.

`repo_name` may be inferred from the cwd basename, but it must not include the full home path.

## 5. Explicitly Forbidden Data

The parser must never save:

* full prompt
* full assistant response
* full shell output
* file contents
* patch contents
* secrets
* API keys
* passwords
* tokens
* `.env` values
* private notes
* raw JSONL lines
* full home directory path
* full command output
* uploaded file contents
* personal conversation content

## 6. Tool Call Handling

Tool calls are counted for metadata only.

Allowed:

* tool call count
* tool type count
* edited file count
* shell command count
* failed tool call count

Forbidden:

* shell command full text
* command output
* file diff content
* file content
* API response body
* credentials inside command

The parser may save simplified categories:

```text
tool_type:
  shell
  file_edit
  file_read
  search
  web
  unknown
```

## 7. Token Usage Handling

Allowed token usage fields:

* `input_tokens`
* `cached_tokens`
* `output_tokens`
* `reasoning_tokens`
* `total_tokens`

If token usage is spread across multiple JSONL lines:

* The parser may sum the values.
* Missing fields should be treated as `0`.
* Unknown formats should increment `warning_count`, but the parser must not save the original line.

## 8. Task / Project Detection

Task inference should use safe metadata and short generated summaries only.

### Task Number

Infer task numbers from safe text sources, such as:

* commit message
* result summary
* assistant final summary short text if safe
* user provided task title if it explicitly looks like `Task #NNN`

Regex:

```text
Task\s+#\d+
```

### Project Name

Infer project names with allowlist keywords:

* AgentOps
* Vulnerability Inventory
* ServiceOps
* Sync Gateway
* Portal Architecture
* SOC
* ProjectOps
* Backup
* Release Docs

If no allowlist keyword matches, use:

```text
unknown
```

## 9. Result Summary Policy

`result_summary` must be a short parser-generated summary. It must not directly save the model output in full.

Example:

```text
Updated AgentOps dashboard UI and command header navigation.
```

Forbidden:

* multi-paragraph original summaries
* private conversation content
* shell output
* secrets

## 10. Normalized Output

Future parser output:

```text
data/agentops/agent_runs.json
```

The format must match the current `demo_agent_runs.json` shape:

* `id`
* `session_id`
* `source`
* `project_name`
* `task_name`
* `task_number`
* `started_at`
* `ended_at`
* `duration_seconds`
* `status`
* `result`
* `model`
* `input_tokens`
* `cached_tokens`
* `output_tokens`
* `reasoning_tokens`
* `total_tokens`
* `tool_calls`
* `files_modified`
* `commands_run`
* `error_count`
* `warning_count`
* `created_at`

`result` is the normalized output field for the safe `result_summary` value.

## 11. Parser CLI Design

Future script:

```text
scripts/parse_codex_sessions.py
```

Supported commands:

```bash
python3 scripts/parse_codex_sessions.py --dry-run
python3 scripts/parse_codex_sessions.py --input ~/.codex/sessions --output data/agentops/agent_runs.json
python3 scripts/parse_codex_sessions.py --since 2026-05-01
python3 scripts/parse_codex_sessions.py --limit 50
```

Dry run should display only:

* files scanned
* sessions detected
* records generated
* warnings
* skipped sensitive fields count

Dry run must not write output.

## 12. Parser Validation Rules

After the parser is implemented, it must check:

* output JSON is valid
* output does not contain `"prompt"`
* output does not contain `"response"`
* output does not contain `"api_key"`
* output does not contain `"password"`
* output does not contain `".env"`
* output does not contain home paths such as `/home/atn`
* output does not contain long shell output text
* output does not contain raw file contents

The script may include a safety scan:

```text
forbidden_patterns:
  prompt
  response
  api_key
  password
  .env
  /home/
  BEGIN PRIVATE KEY
```

If any forbidden pattern matches, the parser must stop before writing output.

## 13. Recommended MVP Flow

First phase:

```text
Codex session files
  -> Safe metadata parser
  -> Safety scan
  -> data/agentops/agent_runs.json
  -> /api/agentops/summary
  -> /agentops/ dashboard
```

## 14. Risks

Risks:

* Codex session JSONL format may change.
* Session files may contain full prompts and responses.
* Tool outputs may contain secrets.
* Shell commands may include credentials.
* File diffs may reveal private code.
* Storing full paths may leak usernames or machine structure.
* Parser mistakes could turn AgentOps into sensitive data storage.

## 15. Decision

AgentOps parser will use an allowlist metadata extraction strategy.

AgentOps will not become a conversation archive.

AgentOps will not store raw Codex session logs.

AgentOps will measure work, cost, tool usage, and delivery metadata only.

## Parser Skeleton Status

`scripts/parse_codex_sessions.py` has been created as a dry-run skeleton.

The first version scans session files and prints a safe metadata preview only.

Output generation is disabled.

The skeleton does not save raw JSONL.

The next step is normalized output generation, but any generated output must still pass the safety scan before it can be written.

## Dry Run Validation Report

`scripts/parse_codex_sessions.py` supports text and JSON dry-run validation reports.

The JSON report format is intended to support later automated tests.

`--no-details` can print only the aggregate summary without per-file previews.

The safety scan checks the report before output is printed.

Output generation remains disabled.

The parser still does not generate `data/agentops/agent_runs.json`.

## Safety Test Fixtures

Safety test fixtures have been added for parser validation:

* `tests/fixtures/codex_sessions/safe/rollout-safe.jsonl`
* `tests/fixtures/codex_sessions/unsafe/rollout-unsafe.jsonl`

`--self-test` verifies allowlist extraction and the safety scan.

The unsafe fixture contains clearly fake sensitive patterns to confirm raw JSONL content does not appear in the dry-run report.

## Preview Output Mode

`--preview-output` can generate a local preview file such as:

```text
data/agentops/agent_runs_preview.json
```

Preview output still requires `--dry-run`. It is preview generation only, not production output generation.

Preview records use allowlist metadata only. They do not store prompts, responses, shell output, command text, file contents, diffs, raw JSONL lines, full home paths, secrets, `.env` values, private notes, or raw tool results.

Before writing the preview file, the parser runs a safety scan on the rendered JSON string. If a forbidden pattern is detected, the parser refuses to write the preview output.

Preview output can only be written under `data/agentops/`.

This mode does not overwrite `data/agentops/demo_agent_runs.json`.

## Preview Review Gate

After `agent_runs_preview.json` is generated, it must pass `scripts/review_agentops_preview.py` before any API source toggle is considered.

The review checks preview structure, allowlist fields, forbidden patterns, and basic quality metrics.

The review does not modify the preview file.

The review does not connect the preview output to the backend or UI.

## 16. Next Tasks

* Task #104: Create Safe Codex Session Parser Skeleton
* Task #105: Add AgentOps Parser Dry Run Mode
* Task #106: Generate AgentOps Runs from Local Codex Sessions
* Task #107: AgentOps Safety Scan for Parser Output
* Task #108: AgentOps Run Detail Page
* Task #109: AgentOps Cost Estimation
* Task #110: Link AgentOps Runs to ServiceOps and ProjectOps
