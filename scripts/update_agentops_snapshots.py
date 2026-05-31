#!/usr/bin/env python3
"""Update AgentOps daily snapshots and index from aggregate review JSON only."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any

import generate_agentops_snapshot as generator


INDEX_SCHEMA_VERSION = "agentops_snapshot_index_v1"
INDEX_SOURCE = "agentops_snapshot_generation"
INDEX_SEMANTIC_WARNINGS = [
    "token_values_are_operational_estimates",
    "project_task_values_may_be_pipeline_level",
    "not_session_content_level_classification",
]
INDEX_SUMMARY_FIELDS = (
    "records",
    "review_status",
    "total_tokens",
    "project_coverage_ratio",
    "task_coverage_ratio",
    "release_quality_score",
    "overall_risk_level",
    "blocking_risks",
    "caution_items",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update AgentOps daily snapshot and index from aggregate review JSON."
    )
    parser.add_argument("--review-json", help="Existing aggregate review JSON path.")
    parser.add_argument("--snapshot-date", required=True, help="Daily snapshot date, YYYY-MM-DD.")
    parser.add_argument("--generated-at", help="Generation timestamp. Defaults to current UTC time.")
    parser.add_argument("--snapshots-root", default="data/agentops/snapshots")
    parser.add_argument("--preview-file", default=generator.DEFAULT_PREVIEW_FILE)
    parser.add_argument("--release-tag", help="Release snapshot tag.")
    parser.add_argument("--commit-sha", help="Release commit SHA.")
    parser.add_argument("--dashboard-version", help="Release dashboard version.")
    parser.add_argument(
        "--write-release",
        action="store_true",
        help="Also write a release snapshot. Requires release metadata.",
    )
    return parser.parse_args()


def validate_snapshot_date(value: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise generator.SnapshotError("snapshot_date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise generator.SnapshotError("snapshot_date must use YYYY-MM-DD")
    return value


def validate_relative_path(value: str, field: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or value.startswith("/")
        or "\\" in value
        or ".." in path.parts
        or str(path) != value
    ):
        raise generator.SnapshotError(f"{field} must be a safe relative path")
    return value


def validate_release_tag(value: str) -> str:
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise generator.SnapshotError("release_tag must be a safe filename component")
    return value


def read_review(args: argparse.Namespace) -> dict[str, Any]:
    if args.review_json:
        return generator.load_review(Path(args.review_json))
    command = [sys.executable, "scripts/review_agentops_preview.py", "--json"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        review = json.loads(result.stdout)
    except subprocess.CalledProcessError as exc:
        raise generator.SnapshotError("aggregate preview review command failed") from exc
    except json.JSONDecodeError as exc:
        raise generator.SnapshotError(f"aggregate preview review JSON is invalid: {exc}") from exc
    if not isinstance(review, dict):
        raise generator.SnapshotError("aggregate preview review JSON must be an object")
    return {field: review.get(field) for field in generator.REVIEW_FIELD_ALLOWLIST}


def snapshot_args(
    args: argparse.Namespace,
    snapshot_type: str,
    *,
    release_tag: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        snapshot_type=snapshot_type,
        snapshot_date=args.snapshot_date,
        release_tag=release_tag,
        commit_sha=args.commit_sha,
        dashboard_version=args.dashboard_version,
        generated_at=args.generated_at,
        preview_file=args.preview_file,
        original_total_tokens_before_normalization=generator.DEFAULT_ORIGINAL_TOTAL_TOKENS,
        release_quality_score=generator.DEFAULT_RELEASE_QUALITY_SCORE,
        overall_risk_level=generator.DEFAULT_OVERALL_RISK_LEVEL,
        blocking_risks=generator.DEFAULT_BLOCKING_RISKS,
        caution_items=generator.DEFAULT_CAUTION_ITEMS,
    )


def load_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "generated_at": "",
            "schema_version": INDEX_SCHEMA_VERSION,
            "semantic_warnings": INDEX_SEMANTIC_WARNINGS,
            "snapshots": [],
            "source": INDEX_SOURCE,
        }
    try:
        index = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise generator.SnapshotError(f"snapshot index JSON is invalid: {exc}") from exc
    if not isinstance(index, dict) or index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise generator.SnapshotError(f"snapshot index schema_version must be {INDEX_SCHEMA_VERSION}")
    snapshots = index.get("snapshots")
    if not isinstance(snapshots, list):
        raise generator.SnapshotError("snapshot index snapshots must be an array")
    for item in snapshots:
        if not isinstance(item, dict):
            raise generator.SnapshotError("snapshot index entries must be objects")
        validate_relative_path(str(item.get("path", "")), "snapshot index path")
    return index


def daily_index_entry(snapshot: dict[str, Any]) -> dict[str, Any]:
    entry = {
        "snapshot_type": "daily",
        "snapshot_date": snapshot["snapshot_date"],
        "path": validate_relative_path(
            f"daily/{snapshot['snapshot_date']}.json", "snapshot index path"
        ),
    }
    entry.update({field: snapshot[field] for field in INDEX_SUMMARY_FIELDS})
    return entry


def update_index(path: Path, snapshot: dict[str, Any]) -> None:
    index = load_index(path)
    entry = daily_index_entry(snapshot)
    snapshots = [
        item
        for item in index["snapshots"]
        if not (
            item.get("snapshot_type") == "daily"
            and item.get("snapshot_date") == entry["snapshot_date"]
        )
    ]
    snapshots.append(entry)
    snapshots.sort(key=lambda item: str(item.get("snapshot_date", "")))
    index.update(
        {
            "generated_at": snapshot["generated_at"],
            "schema_version": INDEX_SCHEMA_VERSION,
            "semantic_warnings": INDEX_SEMANTIC_WARNINGS,
            "snapshots": snapshots,
            "source": INDEX_SOURCE,
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        args.snapshot_date = validate_snapshot_date(args.snapshot_date)
        release_tag = None
        if args.write_release:
            if not args.release_tag or not args.commit_sha or not args.dashboard_version:
                raise generator.SnapshotError(
                    "--write-release requires --release-tag, --commit-sha, and --dashboard-version"
                )
            release_tag = validate_release_tag(args.release_tag)
        review = read_review(args)
        snapshots_root = Path(args.snapshots_root)

        daily_snapshot = generator.build_snapshot(snapshot_args(args, "daily"), review)
        release_snapshot = None
        if args.write_release:
            release_snapshot = generator.build_snapshot(
                snapshot_args(args, "release", release_tag=release_tag), review
            )
        generator.write_snapshot(
            daily_snapshot, snapshots_root / "daily" / f"{args.snapshot_date}.json"
        )
        update_index(snapshots_root / "index.json", daily_snapshot)

        if release_snapshot is not None:
            generator.write_snapshot(
                release_snapshot, snapshots_root / "releases" / f"{release_tag}.json"
            )
    except generator.SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
