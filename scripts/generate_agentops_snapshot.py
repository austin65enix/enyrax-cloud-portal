#!/usr/bin/env python3
"""Generate AgentOps dashboard-level historical snapshots from aggregate review JSON."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "agentops_snapshot_v1"
SOURCE = "agentops_preview_review"
DEFAULT_PREVIEW_FILE = "agent_runs_preview.json"
DEFAULT_ORIGINAL_TOTAL_TOKENS = 1_058_156_153
DEFAULT_RELEASE_QUALITY_SCORE = 98
DEFAULT_OVERALL_RISK_LEVEL = "low"
DEFAULT_BLOCKING_RISKS = 0
DEFAULT_CAUTION_ITEMS = 3

ALLOWED_SNAPSHOT_TYPES = {"daily", "release"}
ALLOWED_REVIEW_STATUSES = {"passed", "failed", "warning", "unknown"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical", "unknown"}
REVIEW_FIELD_ALLOWLIST = {
    "records",
    "status",
    "forbidden_hits",
    "extra_fields",
    "quality",
    "totals",
    "top_projects",
    "top_tasks",
}
QUALITY_FIELDS = (
    "unknown_project_count",
    "unknown_task_count",
    "records_with_zero_tokens",
    "records_with_unknown_model",
    "source_mismatch_count",
    "invalid_status_count",
    "invalid_numeric_field_count",
    "unsafe_session_id_count",
    "unsafe_result_count",
    "invalid_timestamp_field_count",
    "warning_count",
    "error_count",
)
TOTAL_FIELDS = (
    "total_tokens",
    "cached_tokens",
    "output_tokens",
    "reasoning_tokens",
    "tool_calls",
    "files_modified",
    "commands_run",
    "warning_count",
    "error_count",
)
SEMANTIC_WARNINGS = [
    "token_values_are_operational_estimates",
    "project_task_values_may_be_pipeline_level",
    "not_billing_grade_cost_data",
    "not_ai_answer_quality",
    "not_session_content_level_correctness",
    "content_based_inference_prohibited",
]
KNOWN_CAUTIONS = [
    "token_estimate_caution",
    "classification_semantics_caution",
    "trend_sample_data_caution",
]
SEMANTIC_BOUNDARY = {
    "content_based_inference": "prohibited",
    "token_values": "operational_estimates",
    "project_task_values": "pipeline_level_possible",
    "ai_answer_quality": "not_evaluated",
    "session_content_correctness": "not_evaluated",
    "disallowed_content": [
        "prompt",
        "response",
        "shell output",
        "command text",
        "diff",
        "file contents",
        "raw JSONL",
        "credentials",
        "secrets",
        "full home paths",
    ],
}


class SnapshotError(ValueError):
    """Raised when snapshot input or output validation fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate AgentOps aggregate historical snapshot JSON."
    )
    parser.add_argument("--review-json", required=True, help="Aggregate review JSON path.")
    parser.add_argument("--snapshot-type", required=True, choices=sorted(ALLOWED_SNAPSHOT_TYPES))
    parser.add_argument("--output", required=True, help="Output snapshot JSON path.")
    parser.add_argument("--snapshot-date", help="Daily snapshot date, YYYY-MM-DD.")
    parser.add_argument("--release-tag", help="Release snapshot tag.")
    parser.add_argument("--commit-sha", help="Release commit SHA.")
    parser.add_argument("--dashboard-version", help="Release dashboard version.")
    parser.add_argument("--generated-at", help="Generation timestamp. Defaults to current UTC time.")
    parser.add_argument("--preview-file", default=DEFAULT_PREVIEW_FILE, help="Preview file basename.")
    parser.add_argument(
        "--original-total-tokens-before-normalization",
        type=int,
        default=DEFAULT_ORIGINAL_TOTAL_TOKENS,
    )
    parser.add_argument(
        "--release-quality-score",
        type=int,
        default=DEFAULT_RELEASE_QUALITY_SCORE,
    )
    parser.add_argument("--overall-risk-level", default=DEFAULT_OVERALL_RISK_LEVEL)
    parser.add_argument("--blocking-risks", type=int, default=DEFAULT_BLOCKING_RISKS)
    parser.add_argument("--caution-items", type=int, default=DEFAULT_CAUTION_ITEMS)
    return parser.parse_args()


def load_review(path: Path) -> dict[str, Any]:
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SnapshotError(f"review JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"review JSON is invalid: {exc}") from exc
    if not isinstance(review, dict):
        raise SnapshotError("review JSON must be an object")
    return {field: review.get(field) for field in REVIEW_FIELD_ALLOWLIST}


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise SnapshotError(f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SnapshotError(f"{field} must be an array")
    return value


def non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SnapshotError(f"{field} must be a non-negative integer")
    if value < 0:
        raise SnapshotError(f"{field} must be non-negative")
    return value


def optional_non_negative_int(value: Any, field: str) -> int:
    if value is None:
        return 0
    return non_negative_int(value, field)


def aggregate_count(mapping: dict[str, Any], field: str) -> int:
    total = 0
    for key, value in mapping.items():
        if not isinstance(key, str):
            raise SnapshotError(f"{field} keys must be strings")
        if isinstance(value, int) and not isinstance(value, bool):
            if value < 0:
                raise SnapshotError(f"{field} values must be non-negative")
            total += value
        elif isinstance(value, list):
            total += len(value)
        else:
            raise SnapshotError(f"{field} values must be counts or arrays")
    return total


def safe_top_counts(value: Any, field: str) -> list[dict[str, int | str]]:
    items = require_list(value, field)
    safe_items: list[dict[str, int | str]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise SnapshotError(f"{field}[{index}] must be an object")
        name = item.get("name")
        count = item.get("count")
        if not isinstance(name, str):
            raise SnapshotError(f"{field}[{index}].name must be a string")
        safe_items.append({"name": name, "count": non_negative_int(count, f"{field}[{index}].count")})
    return safe_items



def ratio(numerator: int, denominator: int, field: str) -> float:
    if denominator == 0:
        return 0.0
    value = round(numerator / denominator, 6)
    validate_ratio(value, field)
    return value


def validate_ratio(value: float, field: str) -> None:
    if value < 0 or value > 1:
        raise SnapshotError(f"{field} must be between 0 and 1")


def validate_basename(value: str, field: str) -> str:
    if not value or Path(value).name != value:
        raise SnapshotError(f"{field} must be a basename only")
    return value


def generated_at(value: str | None) -> str:
    if value:
        return value
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def release_readiness(review_status: str, blocking_risks: int) -> str:
    if review_status == "passed" and blocking_risks == 0:
        return "ready_for_preview"
    if review_status in {"failed", "unknown"} or blocking_risks > 0:
        return "not_ready"
    return "review_with_caution"


def build_snapshot(args: argparse.Namespace, review: dict[str, Any]) -> dict[str, Any]:
    review_status = review.get("status")
    if review_status is None:
        review_status = "unknown"
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise SnapshotError("review_status must be passed, failed, warning, or unknown")

    risk_level = str(args.overall_risk_level).lower()
    if risk_level not in ALLOWED_RISK_LEVELS:
        raise SnapshotError("overall risk level must be low, medium, high, critical, or unknown")

    preview_file = validate_basename(args.preview_file, "preview_file")
    records = optional_non_negative_int(review.get("records"), "records")
    quality = require_mapping(review.get("quality"), "quality")
    totals = require_mapping(review.get("totals"), "totals")
    forbidden_hits = require_mapping(review.get("forbidden_hits"), "forbidden_hits")
    extra_fields = require_mapping(review.get("extra_fields"), "extra_fields")

    total_values = {
        field: optional_non_negative_int(totals.get(field), f"totals.{field}") for field in TOTAL_FIELDS
    }
    quality_values = {
        field: optional_non_negative_int(quality.get(field), f"quality.{field}")
        for field in QUALITY_FIELDS
    }

    unknown_project_count = quality_values["unknown_project_count"]
    unknown_task_count = quality_values["unknown_task_count"]
    project_coverage_ratio = ratio(records - unknown_project_count, records, "project_coverage_ratio")
    task_coverage_ratio = ratio(records - unknown_task_count, records, "task_coverage_ratio")

    original_total = non_negative_int(
        args.original_total_tokens_before_normalization,
        "original_total_tokens_before_normalization",
    )
    normalized_total = total_values["total_tokens"]
    reduction_ratio = 0.0
    if original_total:
        reduction_ratio = round((original_total - normalized_total) / original_total, 6)
    validate_ratio(reduction_ratio, "token_normalization_reduction_ratio")

    release_quality_score = non_negative_int(args.release_quality_score, "release_quality_score")
    if release_quality_score > 100:
        raise SnapshotError("release_quality_score must be between 0 and 100")

    blocking_risks = non_negative_int(args.blocking_risks, "blocking_risks")
    caution_items = non_negative_int(args.caution_items, "caution_items")
    forbidden_hits_count = aggregate_count(forbidden_hits, "forbidden_hits")
    extra_fields_count = aggregate_count(extra_fields, "extra_fields")

    snapshot: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": "",
        "snapshot_type": args.snapshot_type,
        "generated_at": generated_at(args.generated_at),
        "source": SOURCE,
        "preview_file": preview_file,
        "records": records,
        "review_status": review_status,
        "forbidden_hits_count": forbidden_hits_count,
        "extra_fields_count": extra_fields_count,
        **quality_values,
        **total_values,
        "original_total_tokens_before_normalization": original_total,
        "token_normalization_reduction_ratio": reduction_ratio,
        "top_projects": safe_top_counts(review.get("top_projects"), "top_projects"),
        "top_tasks": safe_top_counts(review.get("top_tasks"), "top_tasks"),
        "project_coverage_ratio": project_coverage_ratio,
        "task_coverage_ratio": task_coverage_ratio,
        "release_quality_score": release_quality_score,
        "overall_risk_level": risk_level,
        "blocking_risks": blocking_risks,
        "caution_items": caution_items,
        "semantic_warnings": SEMANTIC_WARNINGS,
        "review_summary": {
            "records": records,
            "review_status": review_status,
            "forbidden_hits_count": forbidden_hits_count,
            "extra_fields_count": extra_fields_count,
            "unknown_project_count": unknown_project_count,
            "unknown_task_count": unknown_task_count,
            "records_with_unknown_model": quality_values["records_with_unknown_model"],
            "records_with_zero_tokens": quality_values["records_with_zero_tokens"],
        },
    }

    if args.snapshot_type == "daily":
        if not args.snapshot_date:
            raise SnapshotError("--snapshot-date is required for daily snapshots")
        snapshot["snapshot_id"] = f"agentops-daily-{args.snapshot_date}"
        snapshot["snapshot_date"] = args.snapshot_date
    elif args.snapshot_type == "release":
        if not args.release_tag or not args.commit_sha or not args.dashboard_version:
            raise SnapshotError(
                "--release-tag, --commit-sha, and --dashboard-version are required for release snapshots"
            )
        if "/" in args.release_tag:
            raise SnapshotError("release_tag must not contain /")
        if "/" in args.commit_sha:
            raise SnapshotError("commit_sha must not contain /")
        snapshot["snapshot_id"] = f"agentops-release-{args.release_tag}"
        snapshot["release_tag"] = args.release_tag
        snapshot["commit_sha"] = args.commit_sha
        snapshot["dashboard_version"] = args.dashboard_version
        snapshot["release_readiness"] = release_readiness(review_status, blocking_risks)
        snapshot["known_cautions"] = KNOWN_CAUTIONS
        snapshot["semantic_boundary"] = SEMANTIC_BOUNDARY
    else:
        raise SnapshotError("snapshot_type must be daily or release")

    validate_snapshot(snapshot)
    return snapshot


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("snapshot_type") not in ALLOWED_SNAPSHOT_TYPES:
        raise SnapshotError("snapshot_type must be daily or release")
    if snapshot.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        raise SnapshotError("review_status must be allowlisted")
    if snapshot.get("overall_risk_level") not in ALLOWED_RISK_LEVELS:
        raise SnapshotError("overall_risk_level must be allowlisted")
    validate_basename(str(snapshot.get("preview_file", "")), "preview_file")
    for field in ("project_coverage_ratio", "task_coverage_ratio", "token_normalization_reduction_ratio"):
        value = snapshot.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise SnapshotError(f"{field} must be numeric")
        validate_ratio(float(value), field)
    for field, value in snapshot.items():
        if field.endswith("_count") or field in {
            "records",
            "total_tokens",
            "cached_tokens",
            "output_tokens",
            "reasoning_tokens",
            "tool_calls",
            "files_modified",
            "commands_run",
            "release_quality_score",
            "blocking_risks",
            "caution_items",
            "original_total_tokens_before_normalization",
        }:
            non_negative_int(value, field)
    if "release_tag" in snapshot and "/" in str(snapshot["release_tag"]):
        raise SnapshotError("release_tag must not contain /")
    if "commit_sha" in snapshot and "/" in str(snapshot["commit_sha"]):
        raise SnapshotError("commit_sha must not contain /")


def write_snapshot(snapshot: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    try:
        review = load_review(Path(args.review_json))
        snapshot = build_snapshot(args, review)
        write_snapshot(snapshot, Path(args.output))
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
