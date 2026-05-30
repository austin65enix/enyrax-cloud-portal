#!/usr/bin/env python3
"""Review AgentOps preview output without modifying it."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("data/agentops/agent_runs_preview.json")

ALLOWLIST_FIELDS = {
    "id",
    "session_id",
    "source",
    "project_name",
    "task_name",
    "task_number",
    "started_at",
    "ended_at",
    "duration_seconds",
    "status",
    "result",
    "model",
    "input_tokens",
    "cached_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_tokens",
    "tool_calls",
    "files_modified",
    "commands_run",
    "error_count",
    "warning_count",
    "created_at",
}

FORBIDDEN_PATTERNS = [
    "prompt",
    "response",
    "api_key",
    "password",
    ".env",
    "BEGIN PRIVATE KEY",
    "/home/",
    "secret",
    "token=",
]

VALID_STATUSES = {"success", "failed", "interrupted", "unknown"}
NUMERIC_FIELDS = {
    "total_tokens",
    "duration_seconds",
    "files_modified",
    "commands_run",
    "input_tokens",
    "cached_tokens",
    "output_tokens",
    "reasoning_tokens",
    "tool_calls",
    "error_count",
    "warning_count",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review AgentOps preview JSON safety and quality.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Preview JSON file to review.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary.")
    return parser.parse_args()


def input_label(path: Path) -> str:
    return path.name or "agent_runs_preview.json"


def count_forbidden_hits(raw_text: str) -> dict[str, int]:
    lower_text = raw_text.lower()
    hits: dict[str, int] = {}
    for pattern in FORBIDDEN_PATTERNS:
        count = lower_text.count(pattern.lower())
        if count:
            hits[pattern] = count
    return hits


def top_counts(counter: Counter[str], limit: int = 5) -> list[dict[str, int | str]]:
    return [{"name": name, "count": count} for name, count in counter.most_common(limit)]


def empty_result(path: Path, status: str, message: str) -> dict[str, Any]:
    return {
        "status": status,
        "input_label": input_label(path),
        "records": 0,
        "forbidden_hits": {},
        "extra_fields": {},
        "status_counts": {},
        "totals": {},
        "quality": {"messages": [message]},
        "top_projects": [],
        "top_tasks": [],
    }


def review_preview(path: Path) -> dict[str, Any]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return empty_result(path, "failed", "input file not found")

    forbidden_hits = count_forbidden_hits(raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        result = empty_result(path, "failed", "input JSON is invalid")
        result["forbidden_hits"] = forbidden_hits
        return result

    if not isinstance(data, list):
        result = empty_result(path, "failed", "input JSON is not an array")
        result["forbidden_hits"] = forbidden_hits
        return result

    warning_count = 0
    error_count = 0
    extra_fields: dict[str, list[str]] = {}
    status_counts: Counter[str] = Counter()
    project_counts: Counter[str] = Counter()
    task_counts: Counter[str] = Counter()
    totals = {
        "total_tokens": 0,
        "cached_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "tool_calls": 0,
        "files_modified": 0,
        "commands_run": 0,
        "warning_count": 0,
        "error_count": 0,
    }
    quality = {
        "unknown_project_count": 0,
        "unknown_task_count": 0,
        "records_with_zero_tokens": 0,
        "records_with_unknown_model": 0,
        "source_mismatch_count": 0,
        "invalid_status_count": 0,
        "invalid_numeric_field_count": 0,
        "unsafe_session_id_count": 0,
        "unsafe_result_count": 0,
        "invalid_timestamp_field_count": 0,
    }

    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            error_count += 1
            continue

        extras = sorted(set(record) - ALLOWLIST_FIELDS)
        if extras:
            warning_count += 1
            extra_fields[str(index)] = extras

        source = record.get("source")
        if source != "codex_local_preview":
            quality["source_mismatch_count"] += 1
            error_count += 1

        status = record.get("status")
        if status not in VALID_STATUSES:
            quality["invalid_status_count"] += 1
            error_count += 1
        else:
            status_counts[str(status)] += 1

        for field in NUMERIC_FIELDS:
            if not isinstance(record.get(field), (int, float)) or isinstance(record.get(field), bool):
                quality["invalid_numeric_field_count"] += 1
                error_count += 1

        for field in ("started_at", "ended_at"):
            value = record.get(field)
            if value is not None and not isinstance(value, str):
                quality["invalid_timestamp_field_count"] += 1
                error_count += 1

        session_id = record.get("session_id")
        if isinstance(session_id, str) and "/home/" in session_id:
            quality["unsafe_session_id_count"] += 1
            error_count += 1

        result_text = record.get("result")
        if isinstance(result_text, str):
            result_lower = result_text.lower()
            if any(term in result_lower for term in ("prompt", "response", "shell output")):
                quality["unsafe_result_count"] += 1
                error_count += 1

        for field in totals:
            value = record.get(field, 0)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[field] += int(value)

        project = record.get("project_name") if isinstance(record.get("project_name"), str) else "unknown"
        task = record.get("task_name") if isinstance(record.get("task_name"), str) else "unknown"
        project_counts[project] += 1
        task_counts[task] += 1

        if project == "unknown":
            quality["unknown_project_count"] += 1
        if record.get("task_number") == "unknown" or task in {"unknown", "Codex local session preview"}:
            quality["unknown_task_count"] += 1
        if record.get("total_tokens") == 0:
            quality["records_with_zero_tokens"] += 1
        if record.get("model") == "unknown":
            quality["records_with_unknown_model"] += 1

    status = "passed"
    if forbidden_hits or error_count:
        status = "failed"
    elif warning_count:
        status = "warning"

    quality["warning_count"] = warning_count
    quality["error_count"] = error_count

    return {
        "status": status,
        "input_label": input_label(path),
        "records": len(data),
        "forbidden_hits": forbidden_hits,
        "extra_fields": extra_fields,
        "status_counts": dict(status_counts),
        "totals": totals,
        "quality": quality,
        "top_projects": top_counts(project_counts),
        "top_tasks": top_counts(task_counts),
    }


def render_text(result: dict[str, Any]) -> str:
    forbidden_hits = result["forbidden_hits"] or "none"
    extra_fields = result["extra_fields"] or "none"
    totals = result["totals"]
    quality = result["quality"]
    lines = [
        "AgentOps Preview Review",
        f"Input: {result['input_label']}",
        f"Status: {result['status']}",
        f"Records: {result['records']}",
        f"Forbidden hits: {forbidden_hits}",
        f"Extra fields: {extra_fields}",
        "",
        "Totals:",
    ]
    for field in (
        "total_tokens",
        "cached_tokens",
        "output_tokens",
        "reasoning_tokens",
        "tool_calls",
        "files_modified",
        "commands_run",
        "warning_count",
        "error_count",
    ):
        lines.append(f"  {field}: {totals.get(field, 0)}")

    lines.extend(["", "Status Counts:"])
    if result["status_counts"]:
        for name, count in result["status_counts"].items():
            lines.append(f"  {name}: {count}")
    else:
        lines.append("  none")

    lines.extend(["", "Quality:"])
    for field in (
        "unknown_project_count",
        "unknown_task_count",
        "records_with_zero_tokens",
        "records_with_unknown_model",
    ):
        lines.append(f"  {field}: {quality.get(field, 0)}")

    lines.extend(["", "Top Projects:"])
    if result["top_projects"]:
        for item in result["top_projects"]:
            lines.append(f"  {item['name']}: {item['count']}")
    else:
        lines.append("  none")

    lines.extend(["", "Top Tasks:"])
    if result["top_tasks"]:
        for item in result["top_tasks"]:
            lines.append(f"  {item['name']}: {item['count']}")
    else:
        lines.append("  none")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result = review_preview(Path(args.input))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 1 if result["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
