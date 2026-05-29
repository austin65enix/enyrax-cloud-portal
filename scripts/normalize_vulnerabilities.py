#!/usr/bin/env python3
"""Normalize demo Wazuh vulnerability records into ENYRAX inventory JSON."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("data/vulnerabilities/demo_wazuh_vulnerabilities.json")
DEFAULT_OUTPUT = Path("data/vulnerabilities/normalized_vulnerabilities.json")

NORMALIZED_FIELDS = [
    "cve_id",
    "severity",
    "cvss_score",
    "title",
    "package_name",
    "installed_version",
    "fixed_version",
    "host_id",
    "hostname",
    "agent_id",
    "os_name",
    "os_version",
    "detected_at",
    "last_seen_at",
    "status",
    "remediation_status",
    "remediation_hint",
    "reference_urls",
    "source",
    "source_index",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize Wazuh vulnerability demo data for ENYRAX."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input JSON path")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output JSON path")
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError(f"Input must be a JSON array: {path}")

    records = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Record #{index} must be a JSON object")
        records.append(item)
    return records


def build_remediation_hint(record: dict[str, Any]) -> str:
    package_name = str(record.get("package_name") or "package")
    fixed_version = str(record.get("fixed_version") or "").strip()
    cve_id = str(record.get("cve_id") or "unknown CVE")

    if fixed_version:
        return f"Update {package_name} to {fixed_version}"
    return f"Review vendor advisory for {cve_id}"


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = {field: record.get(field) for field in NORMALIZED_FIELDS}
    normalized["severity"] = str(record.get("severity") or "unknown").lower()
    normalized["remediation_status"] = "detected"
    normalized["remediation_hint"] = build_remediation_hint(record)

    reference_urls = record.get("reference_urls")
    if reference_urls is None:
        normalized["reference_urls"] = []
    elif isinstance(reference_urls, list):
        normalized["reference_urls"] = reference_urls
    else:
        normalized["reference_urls"] = [str(reference_urls)]

    return normalized


def write_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def print_summary(records: list[dict[str, Any]]) -> None:
    severity_counts = Counter(str(record.get("severity", "unknown")).lower() for record in records)
    affected_hosts = {record.get("hostname") for record in records if record.get("hostname")}

    print(f"Normalized vulnerabilities: {len(records)}")
    print(f"Critical: {severity_counts.get('critical', 0)}")
    print(f"High: {severity_counts.get('high', 0)}")
    print(f"Medium: {severity_counts.get('medium', 0)}")
    print(f"Low: {severity_counts.get('low', 0)}")
    print(f"Affected hosts: {len(affected_hosts)}")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    source_records = load_records(input_path)
    normalized_records = [normalize_record(record) for record in source_records]
    write_records(output_path, normalized_records)
    print_summary(normalized_records)


if __name__ == "__main__":
    main()
