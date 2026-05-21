#!/usr/bin/env python3
"""Local push agent for ENYRAX Cloud Portal sync events."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

DEFAULT_SYNC_URL = "https://portal.soc-monitoring.dev/api/sync/events"
DEFAULT_SYNC_KEY = "your-demo-sync-key"
DEFAULT_SYNC_SOURCE = "atn-local-lab"
WAZUH_ALERT_PATH = Path("/var/ossec/logs/alerts/alerts.json")
WAZUH_TAIL_BYTES = 512 * 1024
WAZUH_MAX_LINES = 1000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_config() -> dict[str, str]:
    return {
        "url": os.environ.get("ENYRAX_SYNC_URL", DEFAULT_SYNC_URL),
        "key": os.environ.get("ENYRAX_SYNC_KEY", DEFAULT_SYNC_KEY),
        "source": os.environ.get("ENYRAX_SYNC_SOURCE", DEFAULT_SYNC_SOURCE),
    }


def post_event(
    system: str,
    event_type: str,
    status: str,
    message: str | None,
    payload: dict[str, Any],
) -> bool:
    config = get_config()
    body = json.dumps(
        {
            "source": config["source"],
            "system": system,
            "event_type": event_type,
            "status": status,
            "message": message,
            "payload": payload,
        },
        separators=(",", ":"),
    ).encode("utf-8")

    req = request.Request(
        config["url"],
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Sync-Key": config["key"],
            "User-Agent": "enyrax-local-sync-agent/0.1",
        },
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            print(f"POST {system}/{event_type}: HTTP {response.status} {response.reason}")
            print(response_body)
            return 200 <= response.status < 300
    except error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        print(f"POST {system}/{event_type}: HTTP {exc.code} {exc.reason}", file=sys.stderr)
        if response_body:
            print(response_body, file=sys.stderr)
        return False
    except error.URLError as exc:
        print(f"POST {system}/{event_type}: request failed: {exc.reason}", file=sys.stderr)
        return False
    except TimeoutError:
        print(f"POST {system}/{event_type}: request timed out", file=sys.stderr)
        return False
    except OSError as exc:
        print(f"POST {system}/{event_type}: network error: {exc}", file=sys.stderr)
        return False


def read_meminfo() -> dict[str, int]:
    path = Path("/proc/meminfo")
    if not path.exists():
        return {}

    values: dict[str, int] = {}
    try:
        for line in path.read_text(errors="replace").splitlines():
            if ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            parts = raw_value.strip().split()
            if not parts:
                continue
            values[key] = int(parts[0])
    except OSError:
        return {}

    return {
        "mem_total_kb": values.get("MemTotal", 0),
        "mem_available_kb": values.get("MemAvailable", 0),
        "swap_total_kb": values.get("SwapTotal", 0),
        "swap_free_kb": values.get("SwapFree", 0),
    }


def collect_heartbeat() -> bool:
    payload = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "timestamp": utc_now(),
    }
    return post_event("agent", "heartbeat", "ok", "local sync heartbeat", payload)


def collect_host_summary() -> bool:
    load_average = None
    if hasattr(os, "getloadavg"):
        try:
            load_average = list(os.getloadavg())
        except OSError:
            load_average = None

    payload = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "timestamp": utc_now(),
        "cpu_count": os.cpu_count(),
        "load_average": load_average,
        "memory": read_meminfo(),
    }
    return post_event("host", "host_summary", "ok", "local host summary", payload)


def collect_docker_status() -> bool:
    docker_path = shutil.which("docker")
    if not docker_path:
        return post_event(
            "docker",
            "docker_service_status",
            "warning",
            "docker command not found",
            {"timestamp": utc_now(), "running_containers": 0, "containers": []},
        )

    try:
        result = subprocess.run(
            [docker_path, "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return post_event(
            "docker",
            "docker_service_status",
            "warning",
            "docker ps timed out",
            {"timestamp": utc_now(), "running_containers": 0, "containers": []},
        )
    except OSError as exc:
        return post_event(
            "docker",
            "docker_service_status",
            "warning",
            f"docker ps failed: {exc}",
            {"timestamp": utc_now(), "running_containers": 0, "containers": []},
        )

    if result.returncode != 0:
        message = result.stderr.strip() or "docker ps returned non-zero exit status"
        return post_event(
            "docker",
            "docker_service_status",
            "warning",
            message,
            {
                "timestamp": utc_now(),
                "running_containers": 0,
                "containers": [],
                "returncode": result.returncode,
            },
        )

    containers = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        name, image, status = (line.split("\t") + ["", "", ""])[:3]
        containers.append({"name": name, "image": image, "status": status})

    payload = {
        "timestamp": utc_now(),
        "running_containers": len(containers),
        "containers": containers,
    }
    return post_event("docker", "docker_service_status", "ok", "docker status collected", payload)


def tail_text_lines(path: Path, max_bytes: int, max_lines: int) -> list[str]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size > max_bytes:
            handle.seek(size - max_bytes)
            handle.readline()
        data = handle.read()

    return data.decode("utf-8", errors="replace").splitlines()[-max_lines:]


def collect_wazuh_summary() -> bool:
    if not WAZUH_ALERT_PATH.exists():
        return post_event(
            "wazuh",
            "wazuh_alert_summary",
            "warning",
            f"wazuh alerts file not found: {WAZUH_ALERT_PATH}",
            {"timestamp": utc_now(), "alerts_path": str(WAZUH_ALERT_PATH)},
        )

    level_counts: Counter[str] = Counter()
    rule_counts: Counter[str] = Counter()
    agent_counts: Counter[str] = Counter()
    parsed = 0
    skipped = 0

    try:
        lines = tail_text_lines(WAZUH_ALERT_PATH, WAZUH_TAIL_BYTES, WAZUH_MAX_LINES)
    except OSError as exc:
        return post_event(
            "wazuh",
            "wazuh_alert_summary",
            "warning",
            f"failed to read wazuh alerts: {exc}",
            {"timestamp": utc_now(), "alerts_path": str(WAZUH_ALERT_PATH)},
        )

    for line in lines:
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue

        rule = item.get("rule") or {}
        agent = item.get("agent") or {}
        level = rule.get("level", "unknown")
        rule_id = rule.get("id") or rule.get("description") or "unknown"
        agent_name = agent.get("name") or agent.get("id") or "unknown"

        level_counts[str(level)] += 1
        rule_counts[str(rule_id)] += 1
        agent_counts[str(agent_name)] += 1
        parsed += 1

    payload = {
        "timestamp": utc_now(),
        "alerts_path": str(WAZUH_ALERT_PATH),
        "tail_bytes": WAZUH_TAIL_BYTES,
        "max_lines": WAZUH_MAX_LINES,
        "parsed_alerts": parsed,
        "skipped_lines": skipped,
        "level_counts": dict(level_counts.most_common(20)),
        "rule_counts": dict(rule_counts.most_common(20)),
        "agent_counts": dict(agent_counts.most_common(20)),
    }
    return post_event("wazuh", "wazuh_alert_summary", "ok", "wazuh alerts summarized", payload)


def run_collection(collection_type: str) -> bool:
    collectors = {
        "heartbeat": [collect_heartbeat],
        "host": [collect_host_summary],
        "docker": [collect_docker_status],
        "wazuh": [collect_wazuh_summary],
        "all": [
            collect_heartbeat,
            collect_host_summary,
            collect_docker_status,
            collect_wazuh_summary,
        ],
    }
    ok = True
    for collector in collectors[collection_type]:
        ok = collector() and ok
        time.sleep(0.2)
    return ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Push local summary events to ENYRAX Cloud Portal.")
    parser.add_argument("--once", action="store_true", help="run all collectors once")
    parser.add_argument(
        "--type",
        choices=["heartbeat", "host", "docker", "wazuh", "all"],
        default="all",
        help="collector to run",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    collection_type = "all" if args.once else args.type
    return 0 if run_collection(collection_type) else 1


if __name__ == "__main__":
    raise SystemExit(main())
