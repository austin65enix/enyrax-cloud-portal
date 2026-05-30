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
