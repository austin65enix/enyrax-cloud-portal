#!/usr/bin/env python3
"""Dry-run Codex session metadata scanner.

This skeleton intentionally uses allowlist metadata extraction only. It does
not generate AgentOps output files and never prints raw JSONL content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


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

TOKEN_KEYS = {
    "input_tokens",
    "cached_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_tokens",
}

TOKEN_CONTAINER_KEYS = {"usage", "token_usage", "tokens"}

TOOL_EVENT_KEYS = {
    "tool_calls",
    "function_call",
    "shell",
    "command",
    "file",
    "edit",
    "patch",
    "search",
}

SHELL_EVENT_KEYS = {"shell", "command"}
FILE_EVENT_KEYS = {"file"}
EDIT_EVENT_KEYS = {"edit", "patch"}

SESSION_ID_KEYS = {"session_id", "sessionId", "conversation_id"}
STARTED_AT_KEYS = {"started_at", "startedAt", "created_at", "timestamp", "time"}
MODEL_KEYS = {"model", "model_name", "model_slug"}
ENDED_AT_KEYS = {"ended_at", "endedAt", "completed_at", "completedAt", "finished_at", "finishedAt"}
STATUS_KEYS = {"status", "state", "outcome"}
SAFE_TEXT_KEYS = {
    "title",
    "summary",
    "result_summary",
    "task_name",
    "task",
    "name",
    "subject",
}
TASK_NUMBER_PATTERN = re.compile(r"Task\s+#\d+")
PROJECT_KEYWORDS = (
    "AgentOps",
    "Vulnerability Inventory",
    "ServiceOps",
    "Sync Gateway",
    "Portal Architecture",
    "SOC",
    "ProjectOps",
    "Backup",
    "Release Docs",
)
PREVIEW_OUTPUT_DIR = Path("data/agentops")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run safe metadata preview for local Codex session JSONL files."
    )
    parser.add_argument(
        "--input",
        default="~/.codex/sessions",
        help="Input directory containing Codex session JSONL files.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Maximum files to preview.")
    parser.add_argument("--since", help="Only consider files modified on or after YYYY-MM-DD.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview safe metadata only. Required by this skeleton.",
    )
    parser.add_argument(
        "--report-format",
        choices=("text", "json"),
        default="text",
        help="Dry-run validation report format.",
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Print aggregate dry-run summary only.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run parser safety self-tests against local fixtures.",
    )
    parser.add_argument(
        "--preview-output",
        help="Write dry-run preview AgentOps run records under data/agentops/.",
    )
    return parser.parse_args()


def safe_input_label(input_value: str) -> str:
    expanded = Path(input_value).expanduser()
    name = expanded.name
    return name or "<input>"


def parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise SystemExit("Invalid --since value. Expected YYYY-MM-DD.")


def iter_jsonl_files(input_dir: Path, since: datetime | None) -> list[Path]:
    files = sorted(input_dir.rglob("*.jsonl"))
    if since is None:
        return files

    considered: list[Path] = []
    for file_path in files:
        modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
        if modified_at >= since:
            considered.append(file_path)
    return considered


def safe_string(value: Any, max_length: int = 96) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    if any(pattern.lower() in value.lower() for pattern in FORBIDDEN_PATTERNS):
        return None
    return value[:max_length]


def first_safe_value(obj: dict[str, Any], keys: set[str]) -> str | None:
    for key in keys:
        if key in obj:
            value = safe_string(obj[key])
            if value:
                return value
    return None


def first_safe_text_value(obj: dict[str, Any], keys: set[str]) -> str | None:
    for key, value in walk_json(obj):
        if key in keys:
            safe_value = safe_string(value, max_length=160)
            if safe_value:
                return safe_value
    return None


def walk_json(value: Any) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def numeric_value(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def extract_token_usage(obj: dict[str, Any]) -> dict[str, int]:
    totals = {key: 0 for key in TOKEN_KEYS}

    for key, value in walk_json(obj):
        if key in TOKEN_KEYS:
            number = numeric_value(value)
            if number:
                totals[key] += number
        elif key in TOKEN_CONTAINER_KEYS and isinstance(value, dict):
            # Container keys are recognized metadata, but child token keys are
            # counted by walk_json to avoid double-counting nested usage blocks.
            continue

    return totals


def token_usage_found(token_usage: dict[str, int]) -> bool:
    return any(value > 0 for value in token_usage.values())


def classify_events(obj: dict[str, Any]) -> tuple[int, int, int, int]:
    tool_events = 0
    shell_events = 0
    file_events = 0
    edit_events = 0

    for key, value in walk_json(obj):
        key_lower = key.lower()
        count = 1
        if isinstance(value, list):
            count = max(len(value), 1)

        if any(event_key in key_lower for event_key in TOOL_EVENT_KEYS):
            tool_events += count
        if any(event_key in key_lower for event_key in SHELL_EVENT_KEYS):
            shell_events += count
        if any(event_key in key_lower for event_key in FILE_EVENT_KEYS):
            file_events += count
        if any(event_key in key_lower for event_key in EDIT_EVENT_KEYS):
            edit_events += count

    return tool_events, shell_events, file_events, edit_events


def summarize_file(file_path: Path, file_index: int) -> dict[str, Any]:
    warning_count = 0
    line_count = 0
    found_token_usage = False
    tool_event_count = 0
    possible_shell_event_count = 0
    possible_file_event_count = 0
    possible_edit_event_count = 0
    detected_session_id = None
    detected_started_at = None
    detected_ended_at = None
    detected_model = None
    detected_status = None
    detected_safe_text = None
    token_totals = {key: 0 for key in TOKEN_KEYS}

    with file_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line_count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                warning_count += 1
                continue

            if not isinstance(obj, dict):
                continue

            if detected_session_id is None:
                detected_session_id = first_safe_value(obj, SESSION_ID_KEYS)
            if detected_started_at is None:
                detected_started_at = first_safe_value(obj, STARTED_AT_KEYS)
            if detected_ended_at is None:
                detected_ended_at = first_safe_value(obj, ENDED_AT_KEYS)
            if detected_model is None:
                detected_model = first_safe_value(obj, MODEL_KEYS)
            if detected_status is None:
                detected_status = first_safe_value(obj, STATUS_KEYS)
            if detected_safe_text is None:
                detected_safe_text = first_safe_text_value(obj, SAFE_TEXT_KEYS)

            extracted_tokens = extract_token_usage(obj)
            for token_key, token_value in extracted_tokens.items():
                token_totals[token_key] += token_value
            if token_usage_found(extracted_tokens):
                found_token_usage = True

            tool_events, shell_events, file_events, edit_events = classify_events(obj)
            tool_event_count += tool_events
            possible_shell_event_count += shell_events
            possible_file_event_count += file_events
            possible_edit_event_count += edit_events

    return {
        "file_index": file_index,
        "file_name": file_path.name,
        "file_size_bytes": file_path.stat().st_size,
        "line_count": line_count,
        "detected_session_id": detected_session_id,
        "detected_started_at": detected_started_at,
        "detected_ended_at": detected_ended_at,
        "detected_model": detected_model,
        "detected_status": detected_status,
        "inferred_project_name": infer_project_name(detected_safe_text),
        "inferred_task_number": infer_task_number(detected_safe_text),
        "inferred_task_name": infer_task_name(detected_safe_text),
        "token_totals": token_totals,
        "token_usage_found": found_token_usage,
        "tool_event_count": tool_event_count,
        "possible_shell_event_count": possible_shell_event_count,
        "possible_file_event_count": possible_file_event_count,
        "possible_edit_event_count": possible_edit_event_count,
        "warning_count": warning_count,
    }


def safety_scan(output_text: str) -> None:
    lower_output = output_text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in lower_output:
            raise SystemExit("Safety scan failed. Refusing to print unsafe output.")


def preview_safety_scan(output_text: str) -> None:
    lower_output = output_text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in lower_output:
            raise SystemExit("Safety scan failed. Refusing to write preview output.")


def validate_preview_output_path(output_path: str) -> Path:
    path = Path(output_path)
    allowed_dir = (Path.cwd() / PREVIEW_OUTPUT_DIR).resolve()
    resolved_path = (Path.cwd() / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        resolved_path.relative_to(allowed_dir)
    except ValueError:
        raise SystemExit("Preview output must be under data/agentops/.")
    return path


def fallback_session_id(file_name: str) -> str:
    digest = hashlib.sha256(file_name.encode("utf-8")).hexdigest()[:12]
    return f"codex-preview-{digest}"


def preview_run_id(session_id: str, file_index: int) -> str:
    digest = hashlib.sha256(f"{session_id}:{file_index}".encode("utf-8")).hexdigest()[:12]
    return f"run-preview-{digest}"


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def duration_seconds(started_at: str | None, ended_at: str | None) -> int:
    started = parse_datetime(started_at)
    ended = parse_datetime(ended_at)
    if started is None or ended is None:
        return 0
    duration = int((ended - started).total_seconds())
    return max(duration, 0)


def infer_project_name(safe_text: str | None) -> str:
    if not safe_text:
        return "unknown"
    text_lower = safe_text.lower()
    for keyword in PROJECT_KEYWORDS:
        if keyword.lower() in text_lower:
            return keyword
    return "unknown"


def infer_task_number(safe_text: str | None) -> str:
    if not safe_text:
        return "unknown"
    match = TASK_NUMBER_PATTERN.search(safe_text)
    if not match:
        return "unknown"
    return match.group(0)


def infer_task_name(safe_text: str | None, task_number: str = "unknown") -> str:
    if not safe_text:
        return "Codex local session preview"
    task_name = TASK_NUMBER_PATTERN.sub("", safe_text).strip(" :-")
    if not task_name or task_name.lower() in {"none", "null", "unknown"}:
        return "Codex local session preview"
    return task_name[:96]


def normalize_status(value: str | None) -> str:
    if not value:
        return "unknown"
    lower_value = value.lower()
    if any(term in lower_value for term in ("success", "succeeded", "complete", "completed", "passed")):
        return "success"
    if any(term in lower_value for term in ("failed", "failure", "error")):
        return "failed"
    if any(term in lower_value for term in ("interrupted", "cancelled", "canceled", "aborted")):
        return "interrupted"
    return "unknown"


def build_preview_records(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    for summary in summaries:
        session_id = summary["detected_session_id"] or fallback_session_id(summary["file_name"])
        task_number = summary.get("inferred_task_number") or "unknown"
        started_at = summary.get("detected_started_at")
        ended_at = summary.get("detected_ended_at") or started_at
        token_totals = summary.get("token_totals", {})
        records.append(
            {
                "id": preview_run_id(session_id, summary["file_index"]),
                "session_id": session_id,
                "source": "codex_local_preview",
                "project_name": summary.get("inferred_project_name") or "unknown",
                "task_name": summary.get("inferred_task_name") or "Codex local session preview",
                "task_number": task_number,
                "started_at": started_at,
                "ended_at": ended_at,
                "duration_seconds": duration_seconds(started_at, ended_at),
                "status": normalize_status(summary.get("detected_status")),
                "result": "Agent run preview generated from local Codex session metadata.",
                "model": summary.get("detected_model") or "unknown",
                "input_tokens": token_totals.get("input_tokens", 0),
                "cached_tokens": token_totals.get("cached_tokens", 0),
                "output_tokens": token_totals.get("output_tokens", 0),
                "reasoning_tokens": token_totals.get("reasoning_tokens", 0),
                "total_tokens": token_totals.get("total_tokens", 0),
                "tool_calls": summary["tool_event_count"],
                "files_modified": summary["possible_file_event_count"] + summary["possible_edit_event_count"],
                "commands_run": summary["possible_shell_event_count"],
                "error_count": 0,
                "warning_count": summary["warning_count"],
                "created_at": created_at,
            }
        )
    return records


def write_preview_output(output_path: Path, summaries: list[dict[str, Any]]) -> None:
    records = build_preview_records(summaries)
    output_text = json.dumps(records, indent=2, sort_keys=True)
    preview_safety_scan(output_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text + "\n", encoding="utf-8")


def build_report(
    input_label: str,
    files_scanned: int,
    summaries: list[dict[str, Any]],
    since_filter: str | None,
    limit: int | None,
    no_details: bool,
) -> dict[str, Any]:
    warnings = sum(item["warning_count"] for item in summaries)
    report: dict[str, Any] = {
        "status": "ok",
        "mode": "dry-run",
        "privacy_mode": "allowlist metadata only",
        "output_generation": "disabled",
        "input_label": input_label,
        "files_scanned": files_scanned,
        "files_considered": len(summaries),
        "records_previewed": len(summaries),
        "warnings": warnings,
        "safety_scan": {
            "status": "passed",
            "forbidden_patterns_checked": len(FORBIDDEN_PATTERNS),
        },
        "since_filter": since_filter,
        "limit": limit,
    }
    if not no_details:
        report["summaries"] = summaries
    return report


def build_json_output(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def build_text_output(report: dict[str, Any], no_details: bool) -> str:
    lines = [
        "Codex Session Parser Dry Run",
        f"Privacy mode: {report['privacy_mode']}",
        f"Output generation: {report['output_generation']}",
        f"Input: {report['input_label']}",
        f"Files scanned: {report['files_scanned']}",
        f"Files considered: {report['files_considered']}",
        f"Records previewed: {report['records_previewed']}",
        f"Warnings: {report['warnings']}",
        f"Safety scan: {report['safety_scan']['status']}",
    ]

    if report["since_filter"] is not None:
        lines.append(f"Since filter: {report['since_filter']}")
    if report["limit"] is not None:
        lines.append(f"Limit: {report['limit']}")

    if no_details:
        return "\n".join(lines)

    lines.extend(["", "Previewed files:"])
    for summary in report.get("summaries", []):
        lines.extend(
            [
                f"{summary['file_index']}. {summary['file_name']}",
                f"   size: {summary['file_size_bytes']} bytes",
                f"   lines: {summary['line_count']}",
                f"   detected session id: {summary['detected_session_id']}",
                f"   detected started at: {summary['detected_started_at']}",
                f"   detected model: {summary['detected_model']}",
                f"   token usage found: {str(summary['token_usage_found']).lower()}",
                f"   tool events: {summary['tool_event_count']}",
                f"   possible shell events: {summary['possible_shell_event_count']}",
                f"   possible file events: {summary['possible_file_event_count']}",
                f"   possible edit events: {summary['possible_edit_event_count']}",
                f"   warnings: {summary['warning_count']}",
            ]
        )
    return "\n".join(lines)


def render_report(report: dict[str, Any], report_format: str, no_details: bool) -> str:
    if report_format == "json":
        return build_json_output(report)
    return build_text_output(report, no_details)


def print_report(report: dict[str, Any], report_format: str, no_details: bool) -> None:
    output_text = render_report(report, report_format, no_details)
    safety_scan(output_text)
    print(output_text)


def build_directory_report(
    input_dir: Path,
    input_label: str,
    since_filter: str | None,
    limit: int | None,
    no_details: bool,
) -> dict[str, Any]:
    since = parse_since(since_filter)
    files = iter_jsonl_files(input_dir, since)
    files_scanned = len(files)
    if limit is not None:
        if limit < 0:
            raise SystemExit("--limit must be 0 or greater.")
        files = files[:limit]

    summaries = [summarize_file(file_path, index + 1) for index, file_path in enumerate(files)]
    return build_report(input_label, files_scanned, summaries, since_filter, limit, no_details)


def self_test_report(input_dir: Path) -> str:
    report = build_directory_report(input_dir, safe_input_label(str(input_dir)), None, None, False)
    if report["records_previewed"] == 0:
        raise RuntimeError("fixture produced no preview records")
    output_text = render_report(report, "json", False)
    safety_scan(output_text)
    return output_text


def run_self_test() -> int:
    root_dir = Path(__file__).resolve().parents[1]
    safe_dir = root_dir / "tests" / "fixtures" / "codex_sessions" / "safe"
    unsafe_dir = root_dir / "tests" / "fixtures" / "codex_sessions" / "unsafe"
    unsafe_values = [
        "fake-password",
        "fake-test-api-key",
        "fake-token",
        "BEGIN PRIVATE KEY",
        "/home/atn",
    ]

    results: list[tuple[str, bool, str]] = []

    try:
        self_test_report(safe_dir)
        results.append(("Safe fixture", True, "passed"))
    except BaseException as exc:  # noqa: BLE001 - self-test reports concise failure messages.
        results.append(("Safe fixture", False, str(exc)))

    try:
        unsafe_output = self_test_report(unsafe_dir)
        leaked_values = [value for value in unsafe_values if value in unsafe_output]
        if leaked_values:
            results.append(("Unsafe raw fixture redaction", False, "leaked fake sensitive value"))
        else:
            results.append(("Unsafe raw fixture redaction", True, "passed"))
    except BaseException as exc:  # noqa: BLE001 - self-test reports concise failure messages.
        results.append(("Unsafe raw fixture redaction", False, str(exc)))

    try:
        safety_scan("simulated output with password and token=fake-token")
        results.append(("Simulated unsafe output rejection", False, "unsafe output was not rejected"))
    except SystemExit as exc:
        if str(exc) == "Safety scan failed. Refusing to print unsafe output.":
            results.append(("Simulated unsafe output rejection", True, "passed"))
        else:
            results.append(("Simulated unsafe output rejection", False, str(exc)))

    print("AgentOps parser self-test")
    for name, passed, message in results:
        print(f"{name}: {'passed' if passed else 'failed'}")
        if not passed and message:
            print(f"Failure: {message}")

    if all(passed for _name, passed, _message in results):
        print("Result: passed")
        return 0

    print("Result: failed")
    return 1


def main() -> int:
    args = parse_args()

    if args.self_test:
        return run_self_test()

    if args.preview_output and not args.dry_run:
        print("This skeleton only supports --dry-run. Output generation is intentionally disabled.")
        return 1

    if not args.dry_run:
        print("This skeleton only supports --dry-run. Output generation is intentionally disabled.")
        return 1

    preview_output_path = None
    if args.preview_output:
        try:
            preview_output_path = validate_preview_output_path(args.preview_output)
        except SystemExit as exc:
            print(exc)
            return 1

    since = parse_since(args.since)
    input_dir = Path(args.input).expanduser()
    input_label = safe_input_label(args.input)

    if not input_dir.exists():
        report = build_report(input_label, 0, [], args.since, args.limit, args.no_details)
        report["status"] = "input_missing"
        if preview_output_path is not None:
            write_preview_output(preview_output_path, [])
        print_report(report, args.report_format, args.no_details)
        return 0

    if not input_dir.is_dir():
        report = build_report(input_label, 0, [], args.since, args.limit, args.no_details)
        report["status"] = "input_not_directory"
        if preview_output_path is not None:
            write_preview_output(preview_output_path, [])
        print_report(report, args.report_format, args.no_details)
        return 0

    report = build_directory_report(input_dir, input_label, args.since, args.limit, args.no_details)
    if preview_output_path is not None:
        try:
            write_preview_output(preview_output_path, report.get("summaries", []))
        except SystemExit as exc:
            print(exc)
            return 1
    print_report(report, args.report_format, args.no_details)
    return 0


if __name__ == "__main__":
    sys.exit(main())
