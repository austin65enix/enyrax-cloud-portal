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
from datetime import datetime, timezone
from pathlib import Path, PurePath
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
TIMESTAMP_KEYS = {"timestamp", "created_at", "started_at", "ended_at", "time", "ts"}
STARTED_AT_KEYS = {"started_at", "startedAt", "created_at", "timestamp", "time"}
MODEL_KEYS = {
    "model",
    "model_name",
    "selected_model",
    "provider_model",
    "engine",
}
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
    "repo_name",
    "project_name",
}
PATH_BASENAME_KEYS = {
    "file",
    "file_name",
    "filename",
    "file_path",
    "path",
    "cwd",
    "working_directory",
    "repo",
    "repo_name",
    "repository",
}
UNSAFE_TEXT_PARENT_KEYS = {
    "prompt",
    "response",
    "message",
    "messages",
    "content",
    "output",
    "stdout",
    "stderr",
    "command",
    "cmd",
    "diff",
    "patch",
    "file_content",
}
TASK_NUMBER_PATTERN = re.compile(r"Task\s+#\d+", re.IGNORECASE)
PROJECT_MINIMUM_SCORE = 3
PROJECT_FILENAME_BASENAME_MAP = {
    "parse_codex_sessions.py": "AgentOps",
    "review_agentops_preview.py": "AgentOps",
    "agent_runs_preview.json": "AgentOps",
    "agentops_preview_quality_release_note.md": "AgentOps",
    "agentops_preview_full_limit_review.md": "AgentOps",
    "agentops_preview_review_checklist.md": "AgentOps",
    "agentops_safe_metadata_project_signals.md": "AgentOps",
    "codex_session_parser_safe_metadata_plan.md": "AgentOps",
}

TASK_MINIMUM_SCORE = 3
TASK_ALLOWLIST_MARKER = "safe_allowlist"
TASK_FILENAME_BASENAME_MAP = {
    "agentops_preview_quality_release_note.md": "AgentOps Preview Quality Release Note",
    "agentops_safe_metadata_project_signals.md": "Safe Metadata Project Signals Design",
    "agentops_preview_full_limit_review.md": "AgentOps Preview Full Limit Review",
    "agentops_preview_review_checklist.md": "AgentOps Preview Review Checklist",
    "codex_session_parser_safe_metadata_plan.md": "Codex Session Parser Safe Metadata Plan",
    "parse_codex_sessions.py": "Codex Session Parser Maintenance",
    "review_agentops_preview.py": "AgentOps Preview Review",
    "agent_runs_preview.json": "AgentOps Preview Generation",
}

PROJECT_KEYWORD_MAP = (
    (
        "AgentOps",
        (
            "agentops",
            "agent ops",
            "codex",
            "telemetry",
            "parser",
            "preview",
            "token",
            "model inference",
            "safety scan",
            "self-test",
            "agent_runs",
            "source=preview",
        ),
    ),
    (
        "Vulnerability Inventory",
        (
            "vulnerability",
            "cve",
            "remediation",
            "wazuh vulnerability",
            "affected hosts",
            "fixed_version",
            "cvss",
            "openssl",
        ),
    ),
    (
        "ServiceOps",
        (
            "serviceops",
            "service ops",
            "ticket",
            "worklog",
            "sla",
            "assignee",
            "ownership",
            "remediation ticket",
        ),
    ),
    (
        "Sync Gateway",
        (
            "sync gateway",
            "local sync",
            "wazuh local sync",
            "sync source",
            "source metadata",
            "atn-local-lab",
            "local-wazuh-lab",
        ),
    ),
    (
        "SOC",
        (
            "soc",
            "incident",
            "mitre",
            "severity",
            "infra confirm",
            "close incident",
        ),
    ),
    (
        "ProjectOps",
        (
            "projectops",
            "project ops",
            "remediation project",
            "wave",
            "gantt",
        ),
    ),
    (
        "Backup",
        (
            "backup",
            "r2",
            "cloudflare r2",
            "rclone",
            "backup script",
        ),
    ),
    (
        "Release Docs",
        (
            "release",
            "release note",
            "tag",
            "v0.6",
            "document v0",
        ),
    ),
    (
        "Portal Architecture",
        (
            "portal architecture",
            "enterprise ops architecture",
            "homepage architecture",
            "module card",
            "orbit portal",
        ),
    ),
)
PREVIEW_OUTPUT_DIR = Path("data/agentops")
TASK_LABELS = {
    "AgentOps": "AgentOps telemetry update",
    "Vulnerability Inventory": "Vulnerability inventory update",
    "ServiceOps": "ServiceOps workflow update",
    "Sync Gateway": "Sync Gateway update",
    "Portal Architecture": "Portal architecture update",
    "SOC": "SOC workflow update",
    "ProjectOps": "ProjectOps workflow update",
    "Backup": "Backup workflow update",
    "Release Docs": "Release documentation update",
    "unknown": "Codex local session preview",
}


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
    if not value or len(value) > max_length:
        return None
    if any(pattern.lower() in value.lower() for pattern in FORBIDDEN_PATTERNS):
        return None
    return value


def safe_basename(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw_value = value.strip()
    if not raw_value:
        return None
    basename = PurePath(raw_value).name or raw_value.rstrip("/").split("/")[-1]
    return safe_string(basename, max_length=120)


def first_safe_value(obj: dict[str, Any], keys: set[str]) -> str | None:
    for key in keys:
        if key in obj:
            value = safe_string(obj[key])
            if value:
                return value
    return None


def walk_json(value: Any) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def collect_safe_text_candidates(obj: dict[str, Any], file_path: Path) -> list[str]:
    candidates: list[str] = []

    file_name = safe_basename(file_path.name)
    if file_name:
        candidates.append(file_name)

    def collect(value: Any, parent_keys: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_lower = key.lower()
                next_parents = parent_keys + (key_lower,)
                unsafe_parent = any(parent in UNSAFE_TEXT_PARENT_KEYS for parent in parent_keys)

                if not unsafe_parent and key in SESSION_ID_KEYS:
                    safe_value = safe_string(child, max_length=120)
                    if safe_value:
                        candidates.append(safe_value)
                if not unsafe_parent and key in SAFE_TEXT_KEYS:
                    safe_value = safe_string(child, max_length=120)
                    if safe_value:
                        candidates.append(safe_value)
                if not unsafe_parent and key_lower in PATH_BASENAME_KEYS:
                    basename = safe_basename(child)
                    if basename:
                        candidates.append(basename)

                collect(child, next_parents)
        elif isinstance(value, list):
            for child in value:
                collect(child, parent_keys)

    collect(obj)
    return candidates


def first_inferred_model(obj: dict[str, Any]) -> str | None:
    for key, value in walk_json(obj):
        if key in MODEL_KEYS:
            safe_value = safe_string(value, max_length=120)
            if safe_value:
                return safe_value
    return None


def numeric_value(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    safe_value = safe_string(value, max_length=80)
    if not safe_value:
        return None
    if re.fullmatch(r"\d+(?:\.\d+)?", safe_value):
        try:
            return datetime.fromtimestamp(float(safe_value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    normalized = safe_value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def collect_timestamps(obj: dict[str, Any]) -> list[datetime]:
    timestamps: list[datetime] = []
    for key, value in walk_json(obj):
        if key in TIMESTAMP_KEYS:
            parsed = parse_timestamp(value)
            if parsed is not None:
                timestamps.append(parsed)
    return timestamps


def format_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def extract_token_usage(obj: dict[str, Any]) -> dict[str, list[int]]:
    snapshots = {key: [] for key in TOKEN_KEYS}

    for key, value in walk_json(obj):
        if key in TOKEN_KEYS:
            number = numeric_value(value)
            if number:
                snapshots[key].append(number)
        elif key in TOKEN_CONTAINER_KEYS and isinstance(value, dict):
            # Container keys are recognized metadata, but child token keys are
            # counted by walk_json to avoid double-counting nested usage blocks.
            continue

    return snapshots


def token_values_are_cumulative(values: list[int]) -> bool:
    if len(values) < 2:
        return False
    pairs = list(zip(values, values[1:]))
    if all(previous <= current for previous, current in pairs):
        return True
    increases = sum(1 for previous, current in pairs if current > previous)
    if increases > len(pairs) / 2:
        return True

    # Token Normalization: some Codex logs interleave cumulative snapshots
    # with smaller delta-like component values. Detect that numeric-only shape
    # without reading or saving prompt, response, command, or file content.
    max_value = max(values)
    for offset in (0, 1):
        subsequence = values[offset::2]
        if len(subsequence) < 3 or max(subsequence) != max_value:
            continue
        subsequence_pairs = list(zip(subsequence, subsequence[1:]))
        if all(previous <= current for previous, current in subsequence_pairs):
            return True

    return False


def normalize_token_values(values: list[int]) -> dict[str, int | str | bool]:
    original_sum = sum(values)
    cumulative_detected = token_values_are_cumulative(values)
    if cumulative_detected:
        normalized_value = max(values)
        token_normalization_mode = "cumulative_max"
    else:
        normalized_value = original_sum
        token_normalization_mode = "delta_sum"
    return {
        "token_normalization_mode": token_normalization_mode,
        "cumulative_detected": cumulative_detected,
        "original_sum": original_sum,
        "normalized_value": normalized_value,
    }


def normalize_token_usage(token_snapshots: dict[str, list[int]]) -> tuple[dict[str, int], dict[str, dict[str, int | str | bool]]]:
    normalized = {key: 0 for key in TOKEN_KEYS}
    debug: dict[str, dict[str, int | str | bool]] = {}

    for token_key in TOKEN_KEYS:
        values = token_snapshots.get(token_key, [])
        debug[token_key] = normalize_token_values(values)
        normalized[token_key] = int(debug[token_key]["normalized_value"])

    if not token_snapshots.get("total_tokens"):
        normalized["total_tokens"] = (
            normalized.get("input_tokens", 0)
            + normalized.get("output_tokens", 0)
            + normalized.get("reasoning_tokens", 0)
        )
        debug["total_tokens"] = {
            "token_normalization_mode": "component_estimate",
            "cumulative_detected": False,
            "original_sum": 0,
            "normalized_value": normalized["total_tokens"],
        }

    return normalized, debug


def token_usage_found(token_usage: dict[str, int] | dict[str, list[int]]) -> bool:
    for value in token_usage.values():
        if isinstance(value, list):
            if any(item > 0 for item in value):
                return True
        elif value > 0:
            return True
    return False


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
    detected_model = None
    detected_status = None
    safe_text_candidates: list[str] = []
    timestamp_values: list[datetime] = []
    token_snapshots = {key: [] for key in TOKEN_KEYS}

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
            if detected_model is None:
                detected_model = first_inferred_model(obj)
            if detected_status is None:
                detected_status = first_safe_value(obj, STATUS_KEYS)

            timestamp_values.extend(collect_timestamps(obj))
            safe_text_candidates.extend(collect_safe_text_candidates(obj, file_path))

            extracted_tokens = extract_token_usage(obj)
            for token_key, token_values in extracted_tokens.items():
                token_snapshots[token_key].extend(token_values)
            if token_usage_found(extracted_tokens):
                found_token_usage = True

            tool_events, shell_events, file_events, edit_events = classify_events(obj)
            tool_event_count += tool_events
            possible_shell_event_count += shell_events
            possible_file_event_count += file_events
            possible_edit_event_count += edit_events

    started_at, ended_at = infer_time_bounds(timestamp_values)
    project_name = infer_project_name(safe_text_candidates)
    task_number = infer_task_number(safe_text_candidates)
    token_totals, _token_normalization_debug = normalize_token_usage(token_snapshots)

    return {
        "file_index": file_index,
        "file_name": file_path.name,
        "file_size_bytes": file_path.stat().st_size,
        "line_count": line_count,
        "detected_session_id": detected_session_id,
        "detected_started_at": started_at,
        "detected_ended_at": ended_at,
        "detected_model": detected_model,
        "detected_status": detected_status,
        "inferred_project_name": project_name,
        "inferred_task_number": task_number,
        "inferred_task_name": infer_task_name(project_name, task_number, safe_text_candidates),
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
    return parse_timestamp(value)


def duration_seconds(started_at: str | None, ended_at: str | None) -> int:
    started = parse_datetime(started_at)
    ended = parse_datetime(ended_at)
    if started is None or ended is None:
        return 0
    duration = int((ended - started).total_seconds())
    return max(duration, 0)


def infer_time_bounds(timestamps: list[datetime]) -> tuple[str | None, str | None]:
    if not timestamps:
        return None, None
    started = min(timestamps)
    ended = max(timestamps)
    return format_timestamp(started), format_timestamp(ended)


def project_keyword_score(keyword: str) -> int:
    if re.fullmatch(r"[a-z0-9]+", keyword):
        return 0
    return 3


def infer_project_name(safe_text_candidates: list[str]) -> str:
    # Project Inference Recall Improvement: score safe metadata only.
    scores = {project_name: 0 for project_name, _keywords in PROJECT_KEYWORD_MAP}
    seen_matches: set[tuple[str, str, str]] = set()

    for candidate in safe_text_candidates:
        safe_candidate = safe_basename(candidate) or safe_string(candidate, max_length=120)
        if not safe_candidate:
            continue

        candidate_basename = safe_basename(safe_candidate)
        if candidate_basename in PROJECT_FILENAME_BASENAME_MAP:
            project_name = PROJECT_FILENAME_BASENAME_MAP[candidate_basename]
            match_key = (project_name, "filename_basename", candidate_basename)
            if match_key not in seen_matches:
                seen_matches.add(match_key)
                scores[project_name] += 3

        text_lower = safe_candidate.lower()
        for project_name, keywords in PROJECT_KEYWORD_MAP:
            for keyword in keywords:
                keyword_score = project_keyword_score(keyword)
                if keyword_score == 0 or keyword not in text_lower:
                    continue
                match_key = (project_name, keyword, text_lower)
                if match_key in seen_matches:
                    continue
                seen_matches.add(match_key)
                scores[project_name] += keyword_score

    highest_score = max(scores.values()) if scores else 0
    if highest_score < PROJECT_MINIMUM_SCORE:
        return "unknown"

    top_projects = [project_name for project_name, score in scores.items() if score == highest_score]
    if len(top_projects) != 1:
        return "unknown"
    return top_projects[0]


def infer_task_name_from_safe_metadata(safe_text_candidates: list[str]) -> str:
    # Task Inference Safe Allowlist: score safe metadata only.
    scores = {task_name: 0 for task_name in TASK_FILENAME_BASENAME_MAP.values()}
    seen_matches: set[tuple[str, str]] = set()

    for candidate in safe_text_candidates:
        candidate_basename = safe_basename(candidate)
        if not candidate_basename:
            continue
        task_name = TASK_FILENAME_BASENAME_MAP.get(candidate_basename)
        if not task_name:
            continue
        match_key = (task_name, candidate_basename)
        if match_key in seen_matches:
            continue
        seen_matches.add(match_key)
        scores[task_name] += 3

    highest_score = max(scores.values()) if scores else 0
    if highest_score < TASK_MINIMUM_SCORE:
        return "unknown"

    top_tasks = [task_name for task_name, score in scores.items() if score == highest_score]
    if len(top_tasks) != 1:
        return "unknown"
    return top_tasks[0]



def infer_task_number(safe_text_candidates: list[str]) -> str:
    for candidate in safe_text_candidates:
        match = TASK_NUMBER_PATTERN.search(candidate)
        if match:
            value = match.group(0)
            return f"Task #{value.split('#', 1)[1]}"
    return "unknown"


def infer_task_name(
    project_name: str,
    task_number: str = "unknown",
    safe_text_candidates: list[str] | None = None,
) -> str:
    inferred_task = infer_task_name_from_safe_metadata(safe_text_candidates or [])
    if inferred_task != "unknown":
        return inferred_task
    if task_number == "unknown":
        return "Codex local session preview"
    label = TASK_LABELS.get(project_name, TASK_LABELS["unknown"])
    if label == TASK_LABELS["unknown"]:
        return label
    return f"{task_number} · {label}"


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


def build_preview_records(
    summaries: list[dict[str, Any]], preview_output_basename: str | None = None
) -> list[dict[str, Any]]:
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    preview_output_project = infer_project_name([preview_output_basename]) if preview_output_basename else "unknown"
    preview_output_task = infer_task_name_from_safe_metadata([preview_output_basename]) if preview_output_basename else "unknown"
    for summary in summaries:
        session_id = summary["detected_session_id"] or fallback_session_id(summary["file_name"])
        task_number = summary.get("inferred_task_number") or "unknown"
        started_at = summary.get("detected_started_at")
        ended_at = summary.get("detected_ended_at") or started_at
        token_totals = summary.get("token_totals", {})
        project_name = summary.get("inferred_project_name") or "unknown"
        if project_name == "unknown" and preview_output_project != "unknown":
            project_name = preview_output_project
        task_name = summary.get("inferred_task_name") or "Codex local session preview"
        if task_name == "Codex local session preview" and preview_output_task != "unknown":
            task_name = preview_output_task
        if task_number == "unknown" and task_name != "Codex local session preview":
            task_number = TASK_ALLOWLIST_MARKER
        records.append(
            {
                "id": preview_run_id(session_id, summary["file_index"]),
                "session_id": session_id,
                "source": "codex_local_preview",
                "project_name": project_name,
                "task_name": task_name,
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
    records = build_preview_records(summaries, safe_basename(output_path.name))
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

    project_priority_cases = [
        (["parse_codex_sessions.py"], "AgentOps"),
        (["review_agentops_preview.py"], "AgentOps"),
        (["agent_runs_preview.json"], "AgentOps"),
        (["agentops_preview_quality_release_note.md"], "AgentOps"),
        (["portal"], "unknown"),
        (["architecture"], "unknown"),
        (["docs"], "unknown"),
        (["scripts"], "unknown"),
        (["unrelated_filename.md"], "unknown"),
        (["project"], "unknown"),
        (["portal architecture", "agent ops"], "unknown"),
        (["portal architecture"], "Portal Architecture"),
    ]
    failed_priority_cases = [
        f"{candidates!r} -> {infer_project_name(candidates)!r}, expected {expected!r}"
        for candidates, expected in project_priority_cases
        if infer_project_name(candidates) != expected
    ]
    content_candidate_obj = {
        "prompt": "parse_codex_sessions.py",
        "response": "review_agentops_preview.py",
        "command": "cat agent_runs_preview.json",
    }
    content_candidates = collect_safe_text_candidates(content_candidate_obj, Path("unrelated.jsonl"))
    content_project = infer_project_name(content_candidates)
    if content_project != "unknown":
        failed_priority_cases.append(
            f"content-based fields -> {content_project!r}, expected 'unknown'"
        )

    preview_records = build_preview_records(
        [
            {
                "detected_session_id": None,
                "file_name": "rollout-test.jsonl",
                "file_index": 1,
                "inferred_task_number": "unknown",
                "detected_started_at": None,
                "detected_ended_at": None,
                "token_totals": {},
                "inferred_project_name": "unknown",
                "inferred_task_name": "Codex local session preview",
                "detected_status": None,
                "detected_model": "gpt-5.5",
                "tool_event_count": 0,
                "possible_file_event_count": 0,
                "possible_edit_event_count": 0,
                "possible_shell_event_count": 0,
                "warning_count": 0,
            }
        ],
        "agent_runs_preview.json",
    )
    if preview_records[0]["project_name"] != "AgentOps":
        failed_priority_cases.append("preview output basename did not infer AgentOps")

    if failed_priority_cases:
        results.append(("Project keyword priority", False, "; ".join(failed_priority_cases)))
    else:
        results.append(("Project keyword priority", True, "passed"))

    task_allowlist_cases = [
        (["agentops_preview_quality_release_note.md"], "AgentOps Preview Quality Release Note"),
        (["agentops_safe_metadata_project_signals.md"], "Safe Metadata Project Signals Design"),
        (["agentops_preview_full_limit_review.md"], "AgentOps Preview Full Limit Review"),
        (["parse_codex_sessions.py"], "Codex Session Parser Maintenance"),
        (["review_agentops_preview.py"], "AgentOps Preview Review"),
        (["agent_runs_preview.json"], "AgentOps Preview Generation"),
        (["preview"], "unknown"),
        (["review"], "unknown"),
        (["docs"], "unknown"),
        (["scripts"], "unknown"),
        (["parser"], "unknown"),
        (["preview", "review"], "unknown"),
        (["parse_codex_sessions.py", "review_agentops_preview.py"], "unknown"),
    ]
    failed_task_cases = [
        f"{candidates!r} -> {infer_task_name_from_safe_metadata(candidates)!r}, expected {expected!r}"
        for candidates, expected in task_allowlist_cases
        if infer_task_name_from_safe_metadata(candidates) != expected
    ]
    content_task_candidate_obj = {
        "prompt": "AgentOps Preview Quality Release Note",
        "response": "AgentOps Preview Review",
        "command": "cat agent_runs_preview.json",
        "diff": "agentops_safe_metadata_project_signals.md",
        "file_content": "parse_codex_sessions.py",
    }
    content_task_candidates = collect_safe_text_candidates(content_task_candidate_obj, Path("unrelated.jsonl"))
    content_task = infer_task_name_from_safe_metadata(content_task_candidates)
    if content_task != "unknown":
        failed_task_cases.append(
            f"content-based fields -> {content_task!r}, expected unknown"
        )
    preview_task_records = build_preview_records(
        [
            {
                "detected_session_id": None,
                "file_name": "rollout-test.jsonl",
                "file_index": 1,
                "inferred_task_number": "unknown",
                "detected_started_at": None,
                "detected_ended_at": None,
                "token_totals": {},
                "inferred_project_name": "unknown",
                "inferred_task_name": "Codex local session preview",
                "detected_status": None,
                "detected_model": "gpt-5.5",
                "tool_event_count": 0,
                "possible_file_event_count": 0,
                "possible_edit_event_count": 0,
                "possible_shell_event_count": 0,
                "warning_count": 0,
            }
        ],
        "agent_runs_preview.json",
    )
    if preview_task_records[0]["task_name"] != "AgentOps Preview Generation":
        failed_task_cases.append("preview output basename did not infer AgentOps Preview Generation")
    if preview_task_records[0]["task_number"] != TASK_ALLOWLIST_MARKER:
        failed_task_cases.append("safe allowlist task did not set task review marker")

    if failed_task_cases:
        results.append(("Task Inference Safe Allowlist", False, "; ".join(failed_task_cases)))
    else:
        results.append(("Task Inference Safe Allowlist", True, "passed"))


    token_normalization_cases = [
        ([10, 20, 20, 30], 30),
        ([5, 3, 7], 15),
        ([4], 4),
    ]
    failed_token_cases = [
        f"{values!r} -> {normalize_token_values(values)['normalized_value']!r}, expected {expected!r}"
        for values, expected in token_normalization_cases
        if normalize_token_values(values)["normalized_value"] != expected
    ]
    missing_total, _missing_total_debug = normalize_token_usage(
        {
            "input_tokens": [10, 15],
            "cached_tokens": [],
            "output_tokens": [4],
            "reasoning_tokens": [1],
            "total_tokens": [],
        }
    )
    if missing_total["total_tokens"] != 20:
        failed_token_cases.append(
            f"missing total -> {missing_total['total_tokens']!r}, expected 20"
        )
    if failed_token_cases:
        results.append(("Token Normalization", False, "; ".join(failed_token_cases)))
    else:
        results.append(("Token Normalization", True, "passed"))

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
