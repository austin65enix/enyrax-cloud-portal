# AgentOps Parser Safety Tests

## Purpose

These fixtures verify that the parser uses allowlist extraction and does not print sensitive raw JSONL content.

The tests focus on dry-run report safety. They do not generate `data/agentops/agent_runs.json`.

## Fixtures

Safe fixture:

```text
tests/fixtures/codex_sessions/safe/rollout-safe.jsonl
```

The safe fixture contains fake session metadata, fake token usage, fake model data, fake timestamps, and fake tool event metadata.

Unsafe fixture:

```text
tests/fixtures/codex_sessions/unsafe/rollout-unsafe.jsonl
```

The unsafe fixture intentionally contains clearly fake sensitive patterns such as `fake-password`, `fake-test-api-key`, `.env`, `BEGIN PRIVATE KEY`, `/home/atn`, and `token=fake-token`.

## Self Test

Run:

```bash
python3 scripts/parse_codex_sessions.py --self-test
```

The self-test verifies:

* safe fixture passes
* unsafe raw content does not appear in the report
* simulated unsafe output is blocked by the safety scan

## Privacy Boundary

The parser must not output:

* prompt
* response
* shell output
* file contents
* credentials
* API keys
* `.env` values
* full home paths
* raw JSONL lines

## Next Step

After the self-test passes, consider Task #107: Generate AgentOps Runs Preview from Local Codex Sessions.
