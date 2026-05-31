#!/usr/bin/env python3
"""Report AgentOps snapshot retention candidates without modifying files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any


REPORT_SCHEMA_VERSION = "agentops_retention_report_v1"
SNAPSHOT_SCHEMA_VERSION = "agentops_snapshot_v1"
INDEX_SCHEMA_VERSION = "agentops_snapshot_index_v1"
DEFAULT_SNAPSHOTS_ROOT = "data/agentops/snapshots"


class RetentionReportError(ValueError):
    """Raised when a retention report cannot be created safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report AgentOps snapshot retention candidates. This is dry-run only."
    )
    parser.add_argument("--snapshots-root", default=DEFAULT_SNAPSHOTS_ROOT)
    parser.add_argument("--retention-days", type=positive_int, default=30)
    parser.add_argument("--manual-review-retention-days", type=positive_int, default=90)
    parser.add_argument("--today", type=iso_date, default=date.today())
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must use YYYY-MM-DD format") from exc


def relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def safe_read_json(path: Path, root: Path) -> Any:
    root_resolved = root.resolve()
    try:
        path_resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise RetentionReportError(f"JSON file not found: {relative_path(path, root)}") from exc
    if path.is_symlink() or not path_resolved.is_relative_to(root_resolved):
        raise RetentionReportError(f"refusing to read JSON outside snapshots root: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RetentionReportError(f"invalid JSON in {relative_path(path, root)}: {exc}") from exc


def warning(path: str, message: str) -> str:
    return f"{path}: {message}"


def is_safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("/") or "\\" in value or value.startswith("~"):
        return False
    parts = PurePosixPath(value).parts
    return ".." not in parts and "home" not in parts


def load_index(root: Path, warnings: list[str]) -> tuple[set[str], set[str]]:
    path = root / "index.json"
    if not path.is_file():
        warnings.append("index.json: file is missing")
        return set(), set()
    try:
        index = safe_read_json(path, root)
    except RetentionReportError as exc:
        warnings.append(str(exc))
        return set(), set()
    if not isinstance(index, dict):
        warnings.append("index.json: root value must be an object")
        return set(), set()
    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        warnings.append(warning("index.json", f"schema_version must be {INDEX_SCHEMA_VERSION}"))
    entries = index.get("snapshots")
    if not isinstance(entries, list):
        warnings.append("index.json: snapshots must be an array")
        return set(), set()

    indexed_daily_paths: set[str] = set()
    entries_without_files: set[str] = set()
    for position, entry in enumerate(entries):
        entry_name = f"index.json snapshots[{position}]"
        if not isinstance(entry, dict):
            warnings.append(warning(entry_name, "entry must be an object"))
            continue
        if entry.get("snapshot_type") != "daily":
            continue
        entry_path = entry.get("path")
        if not is_safe_relative_path(entry_path):
            warnings.append(warning(entry_name, "path must be a safe relative path"))
            continue
        indexed_daily_paths.add(entry_path)
        if not (root / entry_path).is_file():
            entries_without_files.add(entry_path)
    return indexed_daily_paths, entries_without_files


def inspect_daily(root: Path, today: date, retention_days: int, warnings: list[str]) -> dict[str, Any]:
    files = sorted((root / "daily").glob("*.json"))
    retained: list[str] = []
    candidates: list[str] = []
    paths: list[str] = []
    for path in files:
        rel_path = relative_path(path, root)
        paths.append(rel_path)
        try:
            filename_date = date.fromisoformat(path.stem)
        except ValueError:
            warnings.append(warning(rel_path, "filename must be YYYY-MM-DD.json"))
            filename_date = None
        try:
            snapshot = safe_read_json(path, root)
        except RetentionReportError as exc:
            warnings.append(str(exc))
            snapshot = None
        if not isinstance(snapshot, dict):
            warnings.append(warning(rel_path, "snapshot must be a JSON object"))
        else:
            if snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
                warnings.append(warning(rel_path, f"schema_version must be {SNAPSHOT_SCHEMA_VERSION}"))
            if snapshot.get("snapshot_type") != "daily":
                warnings.append(warning(rel_path, "snapshot_type must be daily"))
            if filename_date is not None and snapshot.get("snapshot_date") != filename_date.isoformat():
                warnings.append(warning(rel_path, "snapshot_date must match filename date"))
        if filename_date is not None and (today - filename_date).days > retention_days:
            candidates.append(rel_path)
        else:
            retained.append(rel_path)
    return {
        "total": len(files),
        "retained": len(retained),
        "retention_candidates": candidates,
        "paths": paths,
    }


def inspect_releases(root: Path, warnings: list[str]) -> dict[str, Any]:
    files = sorted((root / "releases").glob("*.json"))
    for path in files:
        rel_path = relative_path(path, root)
        try:
            snapshot = safe_read_json(path, root)
        except RetentionReportError as exc:
            warnings.append(str(exc))
            continue
        if not isinstance(snapshot, dict):
            warnings.append(warning(rel_path, "snapshot must be a JSON object"))
            continue
        if snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
            warnings.append(warning(rel_path, f"schema_version must be {SNAPSHOT_SCHEMA_VERSION}"))
        if snapshot.get("snapshot_type") != "release":
            warnings.append(warning(rel_path, "snapshot_type must be release"))
    return {
        "total": len(files),
        "retained_permanently": len(files),
        "prune_candidates": [],
    }


def find_unknown_json(root: Path) -> list[str]:
    known = {root / "index.json"}
    known.update((root / "daily").glob("*.json"))
    known.update((root / "releases").glob("*.json"))
    return sorted(relative_path(path, root) for path in root.rglob("*.json") if path not in known)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.snapshots_root)
    if not root.is_dir():
        raise RetentionReportError(f"snapshots root is not a directory: {root}")

    warnings: list[str] = []
    indexed_daily_paths, entries_without_files = load_index(root, warnings)
    daily = inspect_daily(root, args.today, args.retention_days, warnings)
    daily_paths = set(daily.pop("paths"))
    daily["missing_from_index"] = sorted(daily_paths - indexed_daily_paths)
    daily["index_entries_without_files"] = sorted(entries_without_files)

    unknown_files = find_unknown_json(root)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "mode": "dry_run",
        "snapshots_root": args.snapshots_root,
        "today": args.today.isoformat(),
        "retention_days": args.retention_days,
        "manual_review_retention_days": args.manual_review_retention_days,
        "daily": daily,
        "releases": inspect_releases(root, warnings),
        "unknown": {
            "total": len(unknown_files),
            "files": unknown_files,
        },
        "actions": {
            "delete_files": False,
            "modify_index": False,
            "auto_commit": False,
            "auto_push": False,
        },
        "semantic_warnings": [
            "retention_report_does_not_read_prompt_response",
            "release_snapshots_are_never_pruned",
            "dry_run_only",
        ],
        "warnings": warnings,
    }


def print_human_report(report: dict[str, Any]) -> None:
    daily = report["daily"]
    releases = report["releases"]
    unknown = report["unknown"]
    print("AgentOps Snapshot Retention Dry-run Report")
    print()
    print(f"Snapshots root: {report['snapshots_root']}")
    print(f"Today: {report['today']}")
    print(f"Daily retention days: {report['retention_days']}")
    print(f"Manual review retention days: {report['manual_review_retention_days']}")
    print()
    print("Daily snapshots:")
    print(f"- total: {daily['total']}")
    print(f"- retained: {daily['retained']}")
    print(f"- retention candidates: {len(daily['retention_candidates'])}")
    print(f"- missing from index: {len(daily['missing_from_index'])}")
    print(f"- index entries without files: {len(daily['index_entries_without_files'])}")
    print()
    print("Release snapshots:")
    print(f"- total: {releases['total']}")
    print(f"- retained permanently: {releases['retained_permanently']}")
    print(f"- prune candidates: {len(releases['prune_candidates'])}")
    print()
    print("Unknown snapshot files:")
    print(f"- total: {unknown['total']}")
    print("- action: review manually, do not delete automatically")
    print()
    print("Actions:")
    print("- No files will be deleted.")
    print("- No index changes will be made.")
    print("- This is a dry-run report only.")
    if report["warnings"]:
        print()
        print("Warnings:")
        for item in report["warnings"]:
            print(f"- {item}")


def main() -> int:
    args = parse_args()
    try:
        report = build_report(args)
    except RetentionReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
