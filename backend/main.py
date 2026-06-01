from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional
import json
import os
import shutil
import socket
import subprocess

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import SQLAlchemyError


app = FastAPI(
    title="ENYRAX Cloud API",
    version="1.4.0",
)


def load_env() -> None:
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


load_env()

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NORMALIZED_VULNERABILITIES_PATH = (
    PROJECT_ROOT / "data" / "vulnerabilities" / "normalized_vulnerabilities.json"
)
AGENT_RUNS_PATH = PROJECT_ROOT / "data" / "agentops" / "demo_agent_runs.json"
AGENT_RUNS_PREVIEW_PATH = PROJECT_ROOT / "data" / "agentops" / "agent_runs_preview.json"
TEAM_AGENTOPS_FIXTURE_DIR = PROJECT_ROOT / "data" / "team-agentops"
TEAM_AGENTOPS_FIXTURE_FILENAMES = {
    "demo_agent_runs.json",
    "demo_agent_reviews.json",
    "demo_agent_outputs.json",
    "demo_project_contribution.json",
    "demo_scorecard.json",
}
TEAM_AGENTOPS_FIXTURE_WARNING = {
    "code": "fixture_unavailable",
    "message": "Team_AgentOps fixture data is temporarily unavailable.",
}
TEAM_AGENTOPS_RUN_FIELDS = (
    "run_uid",
    "agent_name",
    "agent_type",
    "triggered_by",
    "project_id",
    "project_name",
    "ticket_id",
    "ticket_label",
    "task_title",
    "task_type",
    "status",
    "started_at",
    "ended_at",
    "duration_seconds",
    "output_type",
    "output_ref",
    "output_summary",
    "reviewer",
    "review_status",
    "review_required",
    "token_estimate",
    "cost_estimate",
    "risk_level",
)
TEAM_AGENTOPS_OUTPUT_FIELDS = (
    "agent_run_uid",
    "output_type",
    "output_ref",
    "output_title",
    "checksum",
    "created_at",
)
TEAM_AGENTOPS_REVIEW_FIELDS = (
    "review_uid",
    "agent_run_uid",
    "reviewer",
    "decision",
    "comment",
    "evidence_ref",
    "reviewed_at",
)
TEAM_AGENTOPS_SAFETY_BOUNDARY = {
    "safe_metadata_only": True,
    "no_prompt_response_storage": True,
    "no_raw_sessions": True,
    "no_credentials_or_secrets": True,
    "not_employee_surveillance": True,
    "operational_estimates_only": True,
}
AGENTOPS_LARGE_TOKEN_THRESHOLD = 10000000
AGENTOPS_PREVIEW_WARNING = (
    "Preview telemetry is safety-reviewed metadata. Token totals may be estimated, "
    "cumulative, or inflated depending on Codex session format."
)
AGENTOPS_PREVIEW_QUALITY_NOTES = [
    "Large token totals may indicate cumulative session usage.",
    "Unknown task/project/model values indicate conservative inference.",
    "Preview data should not be used as billing-grade cost data.",
]
SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "unknown": 4,
}
PROJECT_ESCALATION_THRESHOLD = {
    "affected_hosts": 10,
    "critical_count": 3,
}


class ServiceOpsTicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    status: str = Field(default="pending_approval", max_length=50)
    owner: str = Field(..., min_length=1, max_length=100)
    project: str = Field(..., min_length=1, max_length=120)
    estimate_hours: float = 0
    actual_hours: float = 0
    task: str = Field(..., min_length=1)


class VulnerabilityServiceOpsTicketCreate(BaseModel):
    cve_id: str = Field(..., min_length=1, max_length=80)
    hostname: str = Field(..., min_length=1, max_length=160)
    package_name: str = Field(..., min_length=1, max_length=160)
    assignee: Optional[str] = Field(default=None, max_length=160)
    note: Optional[str] = Field(default=None, max_length=2000)


class ServiceOpsTicketUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, max_length=50)
    owner: Optional[str] = Field(default=None, max_length=100)
    project: Optional[str] = Field(default=None, max_length=120)
    estimate_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    task: Optional[str] = None


class ServiceOpsTicketProgressUpdate(BaseModel):
    progress_status: str = Field(..., max_length=50)
    progress_note: Optional[str] = Field(default=None, max_length=2000)


class ServiceOpsTicketSlaUpdate(BaseModel):
    due_at: Optional[str] = None
    sla_level: str = Field(default="normal", max_length=50)
    blocked_reason: Optional[str] = Field(default=None, max_length=2000)


class ServiceOpsTicketCommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)
    comment_type: Optional[str] = Field(default="worklog", max_length=50)


class ProjectOpsProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    status: str = Field(default="watch", max_length=50)
    owner: str = Field(..., min_length=1, max_length=120)
    budget_hours: float = 0
    actual_hours: float = 0
    linked_tickets: int = 0
    scope: str = Field(..., min_length=1)
    progress: int = Field(default=0, ge=0, le=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectOpsProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, max_length=50)
    owner: Optional[str] = Field(default=None, max_length=120)
    budget_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    linked_tickets: Optional[int] = None
    scope: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class SocIncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=220)
    severity: str = Field(default="medium", max_length=50)
    source_ip: str = Field(..., min_length=1, max_length=80)
    target: str = Field(..., min_length=1, max_length=120)
    duplicate_count: int = 1
    analysis_type: str = Field(..., min_length=1, max_length=120)
    mitre: str = Field(default="Unmapped", max_length=160)
    status: str = Field(default="open", max_length=50)


class SocIncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=220)
    severity: Optional[str] = Field(default=None, max_length=50)
    source_ip: Optional[str] = Field(default=None, max_length=80)
    target: Optional[str] = Field(default=None, max_length=120)
    duplicate_count: Optional[int] = None
    analysis_type: Optional[str] = Field(default=None, max_length=120)
    mitre: Optional[str] = Field(default=None, max_length=160)
    status: Optional[str] = Field(default=None, max_length=50)
    resolution_note: Optional[str] = None


class SocIncidentNoteUpdate(BaseModel):
    note: Optional[str] = None


class SocIncidentCommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)
    comment_type: str = Field(default="note", max_length=50)


class LocalSyncEventCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=120)
    system: str = Field(..., min_length=1, max_length=80)
    event_type: str = Field(..., min_length=1, max_length=120)
    status: str = Field(default="ok", max_length=50)
    message: Optional[str] = None
    payload: dict = Field(default_factory=dict)


class SyncSourceMetadataUpdate(BaseModel):
    status: str = Field(..., max_length=50)
    note: Optional[str] = Field(default=None, max_length=2000)


class AuthLoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)


class AuthUserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    role: str


MODULES = [
    {
        "key": "portal",
        "name": "ENYRAX Orbit Portal",
        "route": "/",
        "status": "online",
        "description": "Public landing page and module navigation.",
    },
    {
        "key": "soc",
        "name": "SOC Monitoring",
        "route": "/soc/",
        "status": "api-driven",
        "description": "Security alerts, incident timeline and AI-assisted investigation demo.",
    },
    {
        "key": "serviceops",
        "name": "ServiceOps",
        "route": "/serviceops/",
        "status": "api-driven",
        "description": "Infra work orders, labor time, supervisor view and operation workflow.",
    },
    {
        "key": "projectops",
        "name": "ProjectOps",
        "route": "/projectops/",
        "status": "api-driven",
        "description": "Project timeline, worklog cost mapping and overrun risk view.",
    },
    {
        "key": "audit",
        "name": "Audit Logs",
        "route": "/audit/",
        "status": "api-connected",
        "description": "Operation trail for SOC, ServiceOps and ProjectOps create / update / archive / restore actions.",
    },
    {
        "key": "status",
        "name": "Server Status",
        "route": "/status/",
        "status": "api-connected",
        "description": "Cloud host, Nginx, HTTPS, API health and deployment checkpoint.",
    },
]


ROLE_LEVELS = {
    "viewer": 1,
    "operator": 2,
    "supervisor": 3,
    "admin": 4,
}


DEMO_PASSWORD = "demo1234"

DEMO_TOKENS = {
    "demo-token-viewer": "viewer@enyrax.local",
    "demo-token-operator": "operator@enyrax.local",
    "demo-token-supervisor": "supervisor@enyrax.local",
    "demo-token-admin": "admin@enyrax.local",
}


SOC_INCIDENT_COLUMNS = """
    id, title, severity, source_ip, target,
    duplicate_count, analysis_type, mitre, status,
    handled_by, handled_at, resolution_note,
    infra_verified_by, infra_verified_at,
    infra_verification_note, infra_verification_result,
    display_order, created_at, updated_at
"""


def normalize_demo_role(role: Optional[str]) -> str:
    normalized = (role or "viewer").strip().lower()

    if normalized not in ROLE_LEVELS:
        raise HTTPException(status_code=403, detail=f"Invalid demo role: {normalized}")

    return normalized


def require_role(current_role: Optional[str], minimum_role: str) -> str:
    role = normalize_demo_role(current_role)

    if ROLE_LEVELS[role] < ROLE_LEVELS[minimum_role]:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{role}' requires '{minimum_role}' or higher",
        )

    return role


def require_db():
    if engine is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return engine


def require_sync_key(x_sync_key: Optional[str]) -> None:
    expected_key = os.environ.get("SYNC_API_KEY") or "your-demo-sync-key"

    if x_sync_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid sync key")


def sync_event_row_to_dict(row):
    return {
        "id": row["id"],
        "source": row["source"],
        "system": row["system"],
        "event_type": row["event_type"],
        "status": row["status"],
        "message": row["message"],
        "payload": row["payload"] or {},
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }


SYNC_SOURCE_STATUSES = {"active", "deprecated", "archived"}


def sync_source_row_to_dict(row):
    source_status = row.get("source_status") or "active"

    return {
        "source": row["source"],
        "health": row["health"],
        "latest_event_at": row["latest_event_at"].isoformat() if row["latest_event_at"] else None,
        "latest_heartbeat_at": row["latest_heartbeat_at"].isoformat() if row["latest_heartbeat_at"] else None,
        "systems": row["systems"] or [],
        "total_events": int(row["total_events"] or 0),
        "ok_count": int(row["ok_count"] or 0),
        "warning_count": int(row["warning_count"] or 0),
        "error_count": int(row["error_count"] or 0),
        "latest_message": row["latest_message"],
        "source_status": source_status if source_status in SYNC_SOURCE_STATUSES else "active",
        "source_note": row.get("source_note"),
        "archived_at": row["archived_at"].isoformat() if source_status == "archived" and row.get("archived_at") else None,
        "archived_by": row.get("archived_by") if source_status == "archived" else None,
    }


SYNC_INCIDENT_RECOMMENDED_ACTION = (
    "Check local agent service, network path, Docker/Wazuh status and sync key configuration."
)


def sync_incident_candidate_from_source(row):
    health = row["health"]
    severity_by_health = {
        "error": "high",
        "stale": "medium",
        "unknown": "low",
    }
    reason_by_health = {
        "error": "Recent sync event reported error status.",
        "stale": "No heartbeat received for more than 30 minutes.",
        "unknown": "No heartbeat event found for this source.",
    }

    return {
        "source": row["source"],
        "health": health,
        "severity": severity_by_health[health],
        "title": f"Local sync source {health}: {row['source']}",
        "reason": reason_by_health[health],
        "latest_event_at": row["latest_event_at"].isoformat() if row["latest_event_at"] else None,
        "latest_heartbeat_at": row["latest_heartbeat_at"].isoformat() if row["latest_heartbeat_at"] else None,
        "systems": row["systems"] or [],
        "latest_message": row["latest_message"],
        "recommended_action": SYNC_INCIDENT_RECOMMENDED_ACTION,
    }


def fetch_sync_source_rows(conn, include_metadata: bool = False):
    metadata_select = ""
    metadata_join = ""

    if include_metadata:
        metadata_select = """
                COALESCE(metadata.status, 'active') AS source_status,
                metadata.note AS source_note,
                metadata.archived_at,
                metadata.archived_by,
        """
        metadata_join = """
            LEFT JOIN sync_source_metadata metadata
              ON metadata.source = source_rollup.source
        """

    return conn.execute(
        text(
            f"""
            WITH source_rollup AS (
                SELECT
                    source,
                    MAX(created_at) AS latest_event_at,
                    MAX(created_at) FILTER (WHERE event_type = 'heartbeat') AS latest_heartbeat_at,
                    ARRAY_AGG(DISTINCT system ORDER BY system) AS systems,
                    COUNT(*) AS total_events,
                    COUNT(*) FILTER (WHERE status = 'ok') AS ok_count,
                    COUNT(*) FILTER (WHERE status = 'warning') AS warning_count,
                    COUNT(*) FILTER (WHERE status = 'error') AS error_count,
                    (ARRAY_AGG(status ORDER BY created_at DESC, id DESC))[1] AS latest_status,
                    (ARRAY_AGG(message ORDER BY created_at DESC, id DESC))[1] AS latest_message
                FROM local_sync_events
                GROUP BY source
            )
            SELECT
                source_rollup.source,
                CASE
                    WHEN source_rollup.latest_heartbeat_at IS NULL THEN 'unknown'
                    WHEN source_rollup.latest_status = 'error' THEN 'error'
                    WHEN source_rollup.latest_status = 'warning' THEN 'warning'
                    WHEN source_rollup.latest_heartbeat_at < NOW() - INTERVAL '30 minutes' THEN 'stale'
                    WHEN source_rollup.latest_heartbeat_at < NOW() - INTERVAL '10 minutes' THEN 'warning'
                    WHEN source_rollup.latest_status = 'ok' THEN 'healthy'
                    ELSE 'unknown'
                END AS health,
                {metadata_select}
                source_rollup.latest_event_at,
                source_rollup.latest_heartbeat_at,
                source_rollup.systems,
                source_rollup.total_events,
                source_rollup.ok_count,
                source_rollup.warning_count,
                source_rollup.error_count,
                source_rollup.latest_message
            FROM source_rollup
            {metadata_join}
            ORDER BY source_rollup.source ASC
            """
        )
    ).mappings().all()


def get_user_by_email(conn, email):
    return conn.execute(
        text(
            """
            SELECT
                id, email, display_name, role, is_active
            FROM users
            WHERE email = :email
            """
        ),
        {"email": email},
    ).mappings().first()


def token_to_email(token):
    return DEMO_TOKENS.get(token)


def extract_bearer_token(authorization):
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token.strip():
        return None

    return token.strip()


def auth_user_response(row):
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "role": row["role"],
    }


SERVICEOPS_TICKET_COLUMNS = """
    id, title, status, owner, project,
    estimate_hours, actual_hours, task,
    assignee, progress_status, progress_note,
    progress_updated_by, progress_updated_at,
    due_at, sla_level, blocked_reason,
    display_order, created_at, updated_at,
    deleted_at, deleted_by, delete_reason
"""


SERVICEOPS_PROGRESS_STATUSES = {"not_started", "in_progress", "waiting", "blocked", "done"}
SERVICEOPS_SLA_LEVELS = {"low", "normal", "high", "urgent"}


PROJECTOPS_PROJECT_COLUMNS = """
    id, title, status, owner,
    budget_hours, actual_hours, linked_tickets,
    scope, progress, start_date, end_date,
    display_order, created_at, updated_at,
    archived_at, archived_by, archive_reason
"""


def ticket_row_to_dict(row):
    data = dict(row)

    return {
        "id": data["id"],
        "title": data["title"],
        "status": data["status"],
        "owner": data["owner"],
        "project": data["project"],
        "estimate_hours": float(data["estimate_hours"]),
        "actual_hours": float(data["actual_hours"]),
        "task": data["task"],
        "assignee": data.get("assignee"),
        "progress_status": data.get("progress_status"),
        "progress_note": data.get("progress_note"),
        "progress_updated_by": data.get("progress_updated_by"),
        "progress_updated_at": data["progress_updated_at"].isoformat() if data.get("progress_updated_at") else None,
        "due_at": data["due_at"].isoformat() if data.get("due_at") else None,
        "sla_level": data.get("sla_level") or "normal",
        "blocked_reason": data.get("blocked_reason"),
        "display_order": data["display_order"],
        "created_at": data["created_at"].isoformat() if data.get("created_at") else None,
        "updated_at": data["updated_at"].isoformat() if data.get("updated_at") else None,
        "deleted_at": data["deleted_at"].isoformat() if data.get("deleted_at") else None,
        "deleted_by": data.get("deleted_by"),
        "delete_reason": data.get("delete_reason"),
    }


def project_row_to_dict(row):
    data = dict(row)

    return {
        "id": data["id"],
        "title": data["title"],
        "status": data["status"],
        "owner": data["owner"],
        "budget_hours": float(data["budget_hours"]),
        "actual_hours": float(data["actual_hours"]),
        "linked_tickets": int(data["linked_tickets"]),
        "scope": data["scope"],
        "progress": int(data["progress"]),
        "start_date": data["start_date"].isoformat() if data.get("start_date") else None,
        "end_date": data["end_date"].isoformat() if data.get("end_date") else None,
        "display_order": data["display_order"],
        "created_at": data["created_at"].isoformat() if data.get("created_at") else None,
        "updated_at": data["updated_at"].isoformat() if data.get("updated_at") else None,
        "archived_at": data["archived_at"].isoformat() if data.get("archived_at") else None,
        "archived_by": data.get("archived_by"),
        "archive_reason": data.get("archive_reason"),
    }


PLAN_SERVICEOPS_WARNING_MESSAGES = {
    "serviceops_unavailable": "ServiceOps ticket data is temporarily unavailable.",
    "projectops_unavailable": "Project deadline data is temporarily unavailable.",
}
PLAN_SERVICEOPS_PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
PLAN_SERVICEOPS_PROJECT_RISK_ORDER = {"Delayed": 0, "At Risk": 1, "Watch": 2, "On Track": 3}


def normalize_plan_serviceops_role(role: Optional[str]) -> str:
    normalized = (role or "viewer").strip().lower()

    if normalized == "preview":
        return "viewer"
    if normalized not in ROLE_LEVELS:
        return "viewer"

    return normalized


def plan_serviceops_scope(role: str) -> str:
    return {
        "viewer": "limited",
        "operator": "personal",
        "supervisor": "team",
        "admin": "cross-team",
    }[role]


def normalize_plan_serviceops_status(value: Optional[str]) -> str:
    normalized = (value or "").strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in {"blocked", "waiting", "pending_approval"}:
        return "Blocked"
    if normalized in {"doing", "in_progress"}:
        return "Doing"
    if normalized in {"done", "closed", "completed", "complete"}:
        return "Done"
    if normalized in {"pending", "open", "not_started"}:
        return "Pending"

    return "Pending"


def plan_serviceops_ticket_status(ticket) -> str:
    statuses = [
        normalize_plan_serviceops_status(ticket.get("status")),
        normalize_plan_serviceops_status(ticket.get("progress_status")),
    ]

    for status in ("Blocked", "Done", "Doing", "Pending"):
        if status in statuses:
            return status

    return "Pending"


def is_archived_or_deleted_status(value: Optional[str]) -> bool:
    normalized = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {"archived", "deleted", "trash", "trashed"}


def plan_serviceops_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def plan_serviceops_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def plan_serviceops_local_datetime(value, reference: datetime):
    parsed = plan_serviceops_datetime(value)

    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=reference.tzinfo)

    return parsed.astimezone(reference.tzinfo)


def normalize_plan_serviceops_priority(ticket) -> str:
    raw_priority = ticket.get("priority") or ticket.get("sla_level")
    normalized = (raw_priority or "").strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in {"high", "critical", "urgent", "sla_urgent"}:
        return "High"
    if normalized == "low":
        return "Low"

    if not normalized and ticket.get("due_at"):
        due_at = plan_serviceops_datetime(ticket.get("due_at"))
        if due_at and due_at.date() <= datetime.now().astimezone().date():
            return "High"

    return "Medium"


def plan_serviceops_sort_timestamp(value) -> float:
    return value.timestamp() if value else 0


def format_deadline_label(remaining_days: int) -> str:
    if remaining_days < 0:
        return f"Overdue {abs(remaining_days)} days"
    if remaining_days == 0:
        return "Today"

    return f"D-{remaining_days}"


def compute_remaining_days(deadline_date: date, today: date) -> int:
    return (deadline_date - today).days


def plan_serviceops_project_status(value: Optional[str]) -> str:
    normalized = (value or "").strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in {"risk", "at_risk"}:
        return "At Risk"
    if normalized in {"delayed", "overdue"}:
        return "Delayed"
    if normalized in {"watch", "warning"}:
        return "Watch"

    return "On Track"


def plan_serviceops_ticket_id(source_id) -> str:
    return f"TCK-SVC-{int(source_id):03d}" if source_id is not None else "TCK-SVC-UNKNOWN"


def plan_serviceops_due_time(due_at, now: datetime):
    if due_at is None:
        return None
    if due_at.date() == now.date():
        return "Today " + due_at.strftime("%H:%M")

    return due_at.strftime("%Y-%m-%d %H:%M")


def plan_serviceops_waiting_reason(ticket, status: str):
    if ticket.get("blocked_reason"):
        return ticket["blocked_reason"]
    if (ticket.get("status") or "").strip().lower() == "pending_approval":
        return "Waiting approval"
    if status == "Blocked":
        return "Waiting for follow-up"

    return None


def plan_serviceops_sla_label(due_at, now: datetime):
    if due_at is None:
        return None
    if due_at < now:
        return "Overdue"
    if due_at.date() == now.date():
        return "Today"

    return due_at.date().isoformat()


def build_plan_serviceops_dashboard(tickets, projects, role: str, generated_at: datetime, warnings):
    viewer_user = "atn"
    today = generated_at.date()
    project_ids = {
        (project.get("title") or "").strip().lower(): project.get("id")
        for project in projects
        if project.get("title")
    }
    today_candidates = []
    team_candidates = []

    for ticket in tickets:
        source_status = ticket.get("status")
        status = plan_serviceops_ticket_status(ticket)
        if ticket.get("deleted_at") or is_archived_or_deleted_status(source_status) or status == "Done":
            continue

        due_at = plan_serviceops_local_datetime(ticket.get("due_at"), generated_at)
        is_overdue = bool(due_at and due_at < generated_at)
        is_due_today = bool(due_at and due_at.date() == today)
        priority = normalize_plan_serviceops_priority(ticket)
        assignee = ticket.get("assignee") or ticket.get("owner")
        related_project = ticket.get("project")
        created_at = plan_serviceops_local_datetime(ticket.get("created_at"), generated_at)
        updated_at = plan_serviceops_local_datetime(ticket.get("updated_at"), generated_at)

        if is_due_today or is_overdue:
            if role in {"supervisor", "admin"} or not assignee or assignee == viewer_user:
                today_candidates.append({
                    "ticket_id": plan_serviceops_ticket_id(ticket.get("id")),
                    "source_id": ticket.get("id"),
                    "title": ticket.get("title"),
                    "priority": priority,
                    "status": status,
                    "assignee": assignee,
                    "due_time": plan_serviceops_due_time(due_at, generated_at),
                    "due_at": due_at.isoformat() if due_at else None,
                    "related_project": related_project,
                    "related_project_id": project_ids.get((related_project or "").strip().lower()),
                    "is_overdue": is_overdue,
                    "source": "serviceops",
                    "_due_at": due_at,
                    "_created_at": created_at,
                })

        waiting_reason = plan_serviceops_waiting_reason(ticket, status)
        if role != "viewer" and status in {"Pending", "Doing", "Blocked"} and (is_due_today or is_overdue or waiting_reason):
            team_candidates.append({
                "ticket_id": plan_serviceops_ticket_id(ticket.get("id")),
                "source_id": ticket.get("id"),
                "type": "Infra",
                "title": ticket.get("title"),
                "owner": ticket.get("owner"),
                "status": status,
                "waiting_reason": waiting_reason,
                "sla": plan_serviceops_sla_label(due_at, generated_at),
                "due_at": due_at.isoformat() if due_at else None,
                "source": "serviceops",
                "_is_overdue": is_overdue,
                "_is_due_today": is_due_today,
                "_priority": priority,
                "_updated_at": updated_at,
            })

    max_datetime = datetime.max.replace(tzinfo=generated_at.tzinfo)
    today_candidates.sort(key=lambda item: (
        not item["is_overdue"],
        PLAN_SERVICEOPS_PRIORITY_ORDER[item["priority"]],
        item["_due_at"] or max_datetime,
        -plan_serviceops_sort_timestamp(item["_created_at"]),
    ))
    team_candidates.sort(key=lambda item: (
        item["status"] != "Blocked",
        not item["_is_overdue"],
        not item["_is_due_today"],
        PLAN_SERVICEOPS_PRIORITY_ORDER[item["_priority"]],
        -plan_serviceops_sort_timestamp(item["_updated_at"]),
    ))

    project_deadlines = []
    for project in projects:
        deadline = plan_serviceops_date(project.get("end_date"))
        source_status = project.get("status")
        if deadline is None or project.get("archived_at") or is_archived_or_deleted_status(source_status) or normalize_plan_serviceops_status(source_status) == "Done":
            continue

        remaining_days = compute_remaining_days(deadline, today)
        if remaining_days < 0 or remaining_days > 30:
            continue

        display_status = plan_serviceops_project_status(source_status)
        project_deadlines.append({
            "project_id": project.get("id"),
            "project_name": project.get("title"),
            "owner": project.get("owner"),
            "deadline": deadline.isoformat(),
            "remaining_days": remaining_days,
            "deadline_label": format_deadline_label(remaining_days),
            "status": display_status,
            "related_ticket_count": int(project.get("linked_tickets") or 0),
            "source": "projectops",
        })

    project_deadlines.sort(key=lambda item: (
        item["remaining_days"],
        PLAN_SERVICEOPS_PROJECT_RISK_ORDER[item["status"]],
        item["project_name"] or "",
    ))
    today_tickets = [
        {key: value for key, value in item.items() if not key.startswith("_")}
        for item in today_candidates[:10]
    ]
    team_tickets = [
        {key: value for key, value in item.items() if not key.startswith("_")}
        for item in team_candidates[:10]
    ]
    project_deadlines = project_deadlines[:10]
    nearest_deadline = project_deadlines[0] if project_deadlines else None

    return {
        "generated_at": generated_at.isoformat(),
        "viewer": {"role": role, "user": viewer_user, "scope": plan_serviceops_scope(role)},
        "summary": {
            "today_tickets": len(today_tickets),
            "doing": sum(1 for item in today_tickets if item["status"] == "Doing"),
            "overdue": sum(1 for item in today_tickets if item["is_overdue"]),
            "nearest_deadline_days": nearest_deadline["remaining_days"] if nearest_deadline else 0,
            "nearest_deadline_label": nearest_deadline["deadline_label"] if nearest_deadline else None,
            "blocked_team_tickets": sum(1 for item in team_tickets if item["status"] == "Blocked"),
        },
        "today_tickets": today_tickets,
        "team_tickets": team_tickets,
        "project_deadlines": project_deadlines,
        "warnings": warnings,
    }


def incident_row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "severity": row["severity"],
        "source_ip": row["source_ip"],
        "target": row["target"],
        "duplicate_count": int(row["duplicate_count"]),
        "analysis_type": row["analysis_type"],
        "mitre": row["mitre"],
        "status": row["status"],
        "handled_by": row["handled_by"],
        "handled_at": row["handled_at"].isoformat() if row["handled_at"] else None,
        "resolution_note": row["resolution_note"],
        "infra_verified_by": row["infra_verified_by"],
        "infra_verified_at": row["infra_verified_at"].isoformat() if row["infra_verified_at"] else None,
        "infra_verification_note": row["infra_verification_note"],
        "infra_verification_result": row["infra_verification_result"],
        "display_order": row["display_order"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def incident_comment_row_to_dict(row):
    return {
        "id": row["id"],
        "incident_id": row["incident_id"],
        "actor": row["actor"],
        "role": row["role"],
        "comment": row["comment"],
        "comment_type": row["comment_type"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }


def serviceops_ticket_comment_row_to_dict(row):
    return {
        "id": row["id"],
        "ticket_id": row["ticket_id"],
        "actor": row["actor"],
        "role": row["role"],
        "comment": row["comment"],
        "comment_type": row["comment_type"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }


def soc_incident_serviceops_priority(severity: Optional[str]) -> str:
    normalized = (severity or "medium").strip().lower()

    if normalized in {"critical", "high"}:
        return "high"
    if normalized == "low":
        return "low"

    return "medium"


def soc_incident_serviceops_task(incident) -> str:
    priority = soc_incident_serviceops_priority(incident["severity"])
    lines = [
        f"SOC incident id: {incident['id']}",
        f"Severity: {incident['severity']}",
        f"ServiceOps priority: {priority}",
        f"Source IP: {incident['source_ip']}",
        f"Target: {incident['target']}",
        f"Analysis type: {incident['analysis_type']}",
        f"MITRE: {incident['mitre']}",
        f"Resolution note: {incident['resolution_note'] or 'Not recorded'}",
    ]

    return "\n".join(lines)


def write_audit_log(
    conn,
    module: str,
    entity_type: str,
    entity_id,
    action: str,
    summary: str,
    actor: str = "demo-user",
) -> None:
    conn.execute(
        text(
            """
            INSERT INTO audit_logs
                (module, entity_type, entity_id, action, summary, actor)
            VALUES
                (:module, :entity_type, :entity_id, :action, :summary, :actor)
            """
        ),
        {
            "module": module,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "summary": summary,
            "actor": actor,
        },
    )



def normalized_severity(value) -> str:
    severity = str(value or "unknown").strip().lower()
    if severity in SEVERITY_ORDER:
        return severity
    return "unknown"


def load_normalized_vulnerabilities():
    load_normalized_vulnerabilities.warning = None

    try:
        data = json.loads(NORMALIZED_VULNERABILITIES_PATH.read_text())
    except FileNotFoundError:
        load_normalized_vulnerabilities.warning = "normalized vulnerability data not found"
        return []
    except json.JSONDecodeError:
        load_normalized_vulnerabilities.warning = "normalized vulnerability data parse error"
        return []
    except OSError:
        load_normalized_vulnerabilities.warning = "normalized vulnerability data unavailable"
        return []

    if not isinstance(data, list):
        load_normalized_vulnerabilities.warning = "normalized vulnerability data parse error"
        return []

    return data


load_normalized_vulnerabilities.warning = None


def agentops_source_config(source: Optional[str] = "demo"):
    source_mode = (source or "demo").strip().lower() or "demo"
    if source_mode == "demo":
        return {
            "mode": "demo",
            "path": AGENT_RUNS_PATH,
            "source": "demo_agent_runs",
            "missing_warning": "agentops demo data not found",
            "parse_warning": "agentops demo data parse error",
            "unavailable_warning": "agentops demo data unavailable",
        }
    if source_mode == "preview":
        return {
            "mode": "preview",
            "path": AGENT_RUNS_PREVIEW_PATH,
            "source": "agent_runs_preview",
            "missing_warning": "agentops preview data not found",
            "parse_warning": "agentops preview data parse error",
            "unavailable_warning": "agentops preview data unavailable",
        }
    raise HTTPException(status_code=400, detail="Unsupported AgentOps source. Use demo or preview.")


def load_agent_runs(source: Optional[str] = "demo"):
    config = agentops_source_config(source)
    load_agent_runs.warning = None
    load_agent_runs.source = config["source"]
    load_agent_runs.source_mode = config["mode"]

    try:
        data = json.loads(config["path"].read_text())
    except FileNotFoundError:
        load_agent_runs.warning = config["missing_warning"]
        return []
    except json.JSONDecodeError:
        load_agent_runs.warning = config["parse_warning"]
        return []
    except OSError:
        load_agent_runs.warning = config["unavailable_warning"]
        return []

    if not isinstance(data, list):
        load_agent_runs.warning = config["parse_warning"]
        return []

    return [item for item in data if isinstance(item, dict)]


load_agent_runs.warning = None
load_agent_runs.source = "demo_agent_runs"
load_agent_runs.source_mode = "demo"


class TeamAgentOpsFixtureUnavailable(Exception):
    pass


def load_team_agentops_fixture(filename: str) -> dict:
    if (
        filename not in TEAM_AGENTOPS_FIXTURE_FILENAMES
        or ".." in filename
        or Path(filename).is_absolute()
        or Path(filename).name != filename
    ):
        raise TeamAgentOpsFixtureUnavailable

    try:
        data = json.loads((TEAM_AGENTOPS_FIXTURE_DIR / filename).read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        raise TeamAgentOpsFixtureUnavailable

    if not isinstance(data, dict):
        raise TeamAgentOpsFixtureUnavailable
    return data


def load_optional_team_agentops_fixture(filename: str, warnings: list) -> dict:
    try:
        return load_team_agentops_fixture(filename)
    except TeamAgentOpsFixtureUnavailable:
        if TEAM_AGENTOPS_FIXTURE_WARNING not in warnings:
            warnings.append(dict(TEAM_AGENTOPS_FIXTURE_WARNING))
        return {}


def team_agentops_fixture_records(filename: str, warnings: list) -> list:
    data = load_optional_team_agentops_fixture(filename, warnings)
    records = data.get("records", [])
    if not isinstance(records, list):
        if TEAM_AGENTOPS_FIXTURE_WARNING not in warnings:
            warnings.append(dict(TEAM_AGENTOPS_FIXTURE_WARNING))
        return []
    return [item for item in records if isinstance(item, dict)]


def team_agentops_fixture_list(filename: str, key: str, warnings: list) -> list:
    data = load_optional_team_agentops_fixture(filename, warnings)
    items = data.get(key, [])
    if not isinstance(items, list):
        if TEAM_AGENTOPS_FIXTURE_WARNING not in warnings:
            warnings.append(dict(TEAM_AGENTOPS_FIXTURE_WARNING))
        return []
    return [item for item in items if isinstance(item, dict)]


def team_agentops_public_record(item: dict, fields) -> dict:
    return {field: item.get(field) for field in fields}


def team_agentops_int(item: dict, field: str) -> int:
    try:
        return int(item.get(field) or 0)
    except (TypeError, ValueError):
        return 0


def team_agentops_time(value) -> str:
    try:
        return datetime.fromisoformat(str(value)).strftime("%H:%M")
    except ValueError:
        return ""


def team_agentops_timeline_record(item: dict) -> dict:
    return {
        "run_uid": item.get("run_uid"),
        "time": team_agentops_time(item.get("started_at")),
        "agent_name": item.get("agent_name"),
        "project_name": item.get("project_name"),
        "task_title": item.get("task_title"),
        "status": item.get("status"),
        "review_status": item.get("review_status"),
        "output_type": item.get("output_type"),
        "output_ref": item.get("output_ref"),
    }


def agentops_int(item, field: str) -> int:
    try:
        return int(item.get(field) or 0)
    except (TypeError, ValueError):
        return 0


def agentops_text(item, field: str, default: str = "") -> str:
    value = item.get(field)
    if value is None:
        return default
    return str(value)


def normalize_agentops_status(value) -> str:
    status = str(value or "unknown").strip().lower()
    if status in {"success", "failed", "interrupted", "unknown"}:
        return status
    return "unknown"


def agentops_public_run(item, fields, include_preview_quality: bool = False):
    public_item = {field: item.get(field) for field in fields}
    if include_preview_quality:
        public_item["preview_quality"] = agentops_preview_quality_flags(item)
    return public_item


def agentops_sort_started_at(item):
    return agentops_text(item, "started_at")


def agentops_group_status(status_counts):
    active_statuses = [status for status, count in status_counts.items() if count]
    if len(active_statuses) == 1:
        return active_statuses[0]
    if not active_statuses:
        return "unknown"
    return "mixed"


def agentops_is_unknown(item, field: str) -> bool:
    value = item.get(field)
    if value is None:
        return True

    normalized = str(value).strip().lower()
    return normalized in {"", "unknown", "unknown task", "unknown project", "unknown model"}


def agentops_preview_quality_flags(item) -> dict:
    return {
        "unknown_project": agentops_is_unknown(item, "project_name"),
        "unknown_task": agentops_is_unknown(item, "task_number"),
        "unknown_model": agentops_is_unknown(item, "model"),
        "zero_duration": agentops_int(item, "duration_seconds") == 0,
        "large_token_total": agentops_int(item, "total_tokens") >= AGENTOPS_LARGE_TOKEN_THRESHOLD,
    }


def agentops_preview_quality(runs) -> dict:
    quality = {
        "preview": True,
        "review_required": True,
        "review_status": "external",
        "unknown_project_count": 0,
        "unknown_task_count": 0,
        "unknown_model_count": 0,
        "zero_duration_count": 0,
        "large_token_run_count": 0,
        "large_token_threshold": AGENTOPS_LARGE_TOKEN_THRESHOLD,
        "token_estimate_warning": False,
        "notes": AGENTOPS_PREVIEW_QUALITY_NOTES,
    }

    for item in runs:
        flags = agentops_preview_quality_flags(item)
        if flags["unknown_project"]:
            quality["unknown_project_count"] += 1
        if flags["unknown_task"]:
            quality["unknown_task_count"] += 1
        if flags["unknown_model"]:
            quality["unknown_model_count"] += 1
        if flags["zero_duration"]:
            quality["zero_duration_count"] += 1
        if flags["large_token_total"]:
            quality["large_token_run_count"] += 1

    quality["token_estimate_warning"] = quality["large_token_run_count"] > 0
    return quality


# AgentOps API only exposes normalized metadata. It must not expose prompt,
# response, shell output, file contents, credentials or .env values.
def agentops_response_metadata(runs=None) -> dict:
    metadata = {
        "source": load_agent_runs.source,
        "source_mode": load_agent_runs.source_mode,
    }
    if load_agent_runs.source_mode == "preview":
        metadata["warning"] = AGENTOPS_PREVIEW_WARNING
        metadata["quality"] = agentops_preview_quality(runs or [])
        if load_agent_runs.warning:
            metadata["data_warning"] = load_agent_runs.warning
    else:
        metadata["quality"] = {"preview": False}
        if load_agent_runs.warning:
            metadata["warning"] = load_agent_runs.warning
    return metadata


def agentops_summary_response(runs):
    totals = {
        "agent_runs": len(runs),
        "success": 0,
        "failed": 0,
        "interrupted": 0,
        "unknown": 0,
        "total_tokens": 0,
        "cached_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "tool_calls": 0,
        "files_modified": 0,
        "commands_run": 0,
        "error_count": 0,
        "warning_count": 0,
    }
    task_groups = {}
    project_groups = {}
    model_groups = {}
    duration_total = 0

    for item in runs:
        status = normalize_agentops_status(item.get("status"))
        totals[status] += 1
        duration_total += agentops_int(item, "duration_seconds")

        for field in (
            "total_tokens",
            "cached_tokens",
            "input_tokens",
            "output_tokens",
            "reasoning_tokens",
            "tool_calls",
            "files_modified",
            "commands_run",
            "error_count",
            "warning_count",
        ):
            totals[field] += agentops_int(item, field)

        task_number = agentops_text(item, "task_number", "Unknown Task").strip() or "Unknown Task"
        task_name = agentops_text(item, "task_name", "Untitled task").strip() or "Untitled task"
        task_key = (task_number, task_name)
        task_entry = task_groups.setdefault(
            task_key,
            {
                "task_number": task_number,
                "task_name": task_name,
                "project_name": agentops_text(item, "project_name", "Unknown"),
                "runs": 0,
                "total_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "files_modified": 0,
                "status_counts": {
                    "success": 0,
                    "failed": 0,
                    "interrupted": 0,
                    "unknown": 0,
                },
            },
        )
        task_entry["runs"] += 1
        task_entry["total_tokens"] += agentops_int(item, "total_tokens")
        task_entry["output_tokens"] += agentops_int(item, "output_tokens")
        task_entry["reasoning_tokens"] += agentops_int(item, "reasoning_tokens")
        task_entry["files_modified"] += agentops_int(item, "files_modified")
        task_entry["status_counts"][status] += 1

        project_name = agentops_text(item, "project_name", "Unknown").strip() or "Unknown"
        project_entry = project_groups.setdefault(
            project_name,
            {
                "project_name": project_name,
                "runs": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "files_modified": 0,
                "success": 0,
                "failed": 0,
                "interrupted": 0,
            },
        )
        project_entry["runs"] += 1
        project_entry["total_tokens"] += agentops_int(item, "total_tokens")
        project_entry["cached_tokens"] += agentops_int(item, "cached_tokens")
        project_entry["files_modified"] += agentops_int(item, "files_modified")
        if status in {"success", "failed", "interrupted"}:
            project_entry[status] += 1

        model = agentops_text(item, "model", "unknown").strip() or "unknown"
        model_entry = model_groups.setdefault(
            model,
            {
                "model": model,
                "runs": 0,
                "total_tokens": 0,
                "output_tokens": 0,
            },
        )
        model_entry["runs"] += 1
        model_entry["total_tokens"] += agentops_int(item, "total_tokens")
        model_entry["output_tokens"] += agentops_int(item, "output_tokens")

    agent_runs = totals["agent_runs"]
    success_rate = round((totals["success"] / agent_runs * 100), 2) if agent_runs else 0
    avg_duration = round(duration_total / agent_runs) if agent_runs else 0
    cached_to_total_ratio = (
        round(totals["cached_tokens"] / totals["total_tokens"], 2)
        if totals["total_tokens"]
        else 0
    )

    top_tasks = []
    for task_entry in task_groups.values():
        top_tasks.append(
            {
                "task_number": task_entry["task_number"],
                "task_name": task_entry["task_name"],
                "project_name": task_entry["project_name"],
                "runs": task_entry["runs"],
                "total_tokens": task_entry["total_tokens"],
                "output_tokens": task_entry["output_tokens"],
                "reasoning_tokens": task_entry["reasoning_tokens"],
                "files_modified": task_entry["files_modified"],
                "status": agentops_group_status(task_entry["status_counts"]),
            }
        )
    top_tasks.sort(key=lambda item: item["total_tokens"], reverse=True)

    top_projects = sorted(
        project_groups.values(),
        key=lambda item: item["total_tokens"],
        reverse=True,
    )
    top_models = sorted(
        model_groups.values(),
        key=lambda item: item["total_tokens"],
        reverse=True,
    )
    recent_fields = [
        "id",
        "session_id",
        "project_name",
        "task_number",
        "task_name",
        "started_at",
        "ended_at",
        "duration_seconds",
        "status",
        "result",
        "model",
        "total_tokens",
        "cached_tokens",
        "output_tokens",
        "reasoning_tokens",
        "tool_calls",
        "files_modified",
        "commands_run",
    ]
    recent_runs = [
        agentops_public_run(item, recent_fields)
        for item in sorted(runs, key=agentops_sort_started_at, reverse=True)[:5]
    ]

    response = {
        "status": "ok",
        "generated_at": now_utc(),
        "totals": totals,
        "success_rate": success_rate,
        "avg_duration_seconds": avg_duration,
        "cache_efficiency": {
            "cached_tokens": totals["cached_tokens"],
            "total_tokens": totals["total_tokens"],
            "cached_to_total_ratio": cached_to_total_ratio,
        },
        "top_tasks": top_tasks[:5],
        "top_projects": top_projects[:5],
        "top_models": top_models[:5],
        "recent_runs": recent_runs,
    }
    response.update(agentops_response_metadata(runs))
    return response


def vulnerability_host_key(item) -> Optional[str]:
    hostname = str(item.get("hostname") or "").strip()
    if hostname:
        return hostname

    host_id = str(item.get("host_id") or "").strip()
    if host_id:
        return host_id

    return None


def vulnerability_summary_response(items):
    totals = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "unknown": 0,
    }
    affected_hosts = set()
    package_counts = {}
    cve_counts = {}
    host_counts = {}
    remediation_status = {}

    for item in items:
        severity = normalized_severity(item.get("severity"))
        totals[severity] += 1

        host_key = vulnerability_host_key(item)
        if host_key:
            affected_hosts.add(host_key)

        package_name = str(item.get("package_name") or "").strip()
        if package_name:
            package_entry = package_counts.setdefault(
                package_name,
                {
                    "package_name": package_name,
                    "count": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "unknown": 0,
                },
            )
            package_entry["count"] += 1
            package_entry[severity] += 1

        cve_id = str(item.get("cve_id") or "").strip()
        if cve_id:
            cve_entry = cve_counts.setdefault(
                cve_id,
                {
                    "cve_id": cve_id,
                    "count": 0,
                    "highest_severity": "unknown",
                    "affected_hosts": set(),
                },
            )
            cve_entry["count"] += 1
            if SEVERITY_ORDER[severity] < SEVERITY_ORDER[cve_entry["highest_severity"]]:
                cve_entry["highest_severity"] = severity
            if host_key:
                cve_entry["affected_hosts"].add(host_key)

        hostname = str(item.get("hostname") or "").strip()
        if hostname:
            host_entry = host_counts.setdefault(
                hostname,
                {
                    "hostname": hostname,
                    "count": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "unknown": 0,
                },
            )
            host_entry["count"] += 1
            host_entry[severity] += 1

        item_status = str(item.get("remediation_status") or "unknown").strip().lower() or "unknown"
        remediation_status[item_status] = remediation_status.get(item_status, 0) + 1

    totals["total"] = len(items)
    affected_host_count = len(affected_hosts)

    top_packages = sorted(
        package_counts.values(),
        key=lambda entry: (-entry["count"], entry["package_name"]),
    )[:5]
    top_cves = sorted(
        cve_counts.values(),
        key=lambda entry: (-entry["count"], SEVERITY_ORDER[entry["highest_severity"]], entry["cve_id"]),
    )[:5]
    for entry in top_cves:
        entry["affected_hosts"] = len(entry["affected_hosts"])
    top_hosts = sorted(
        host_counts.values(),
        key=lambda entry: (-entry["count"], entry["hostname"]),
    )[:5]

    escalation_required = (
        affected_host_count >= PROJECT_ESCALATION_THRESHOLD["affected_hosts"]
        or totals["critical"] >= PROJECT_ESCALATION_THRESHOLD["critical_count"]
    )
    if escalation_required:
        reason = "Critical vulnerability count reached project escalation threshold."
        if affected_host_count >= PROJECT_ESCALATION_THRESHOLD["affected_hosts"]:
            reason = "Affected host count reached project escalation threshold."
    else:
        reason = "Vulnerability scope can be handled as ServiceOps tickets."

    return {
        "status": "ok",
        "source": "normalized_vulnerabilities",
        "generated_at": now_utc(),
        "totals": totals,
        "affected_hosts": affected_host_count,
        "top_packages": top_packages,
        "top_cves": top_cves,
        "top_hosts": top_hosts,
        "remediation_status": dict(sorted(remediation_status.items())),
        "project_escalation": {
            "required": escalation_required,
            "reason": reason,
            "threshold": PROJECT_ESCALATION_THRESHOLD,
        },
    }


def parse_vulnerability_limit(limit: Optional[str]) -> int:
    if limit is None:
        return 100

    try:
        parsed_limit = int(limit)
    except (TypeError, ValueError):
        return 100

    if parsed_limit < 1:
        return 100

    return min(parsed_limit, 500)


def unique_sorted_values(items, key: str) -> list[str]:
    values = {str(item.get(key) or "").strip() for item in items}
    return sorted(value for value in values if value)


def first_vulnerability_value(items, key: str):
    for item in items:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def highest_vulnerability_severity(items) -> str:
    highest = "unknown"
    for item in items:
        severity = normalized_severity(item.get("severity"))
        if SEVERITY_ORDER[severity] < SEVERITY_ORDER[highest]:
            highest = severity
    return highest


def highest_cvss_score(items):
    scores = []
    for item in items:
        try:
            scores.append(float(item.get("cvss_score")))
        except (TypeError, ValueError):
            continue

    if not scores:
        return None

    score = max(scores)
    return int(score) if score.is_integer() else score


def vulnerability_cve_response(items, requested_cve: str):
    cve_filter = requested_cve.strip().lower()
    cve_items = [
        item for item in items
        if str(item.get("cve_id") or "").strip().lower() == cve_filter
    ]

    if not cve_items:
        raise HTTPException(status_code=404, detail="CVE not found.")

    cve_id = first_vulnerability_value(cve_items, "cve_id") or requested_cve
    packages = unique_sorted_values(cve_items, "package_name")
    reference_urls = sorted({
        str(url).strip()
        for item in cve_items
        for url in (item.get("reference_urls") if isinstance(item.get("reference_urls"), list) else [])
        if str(url).strip()
    })
    affected_host_keys = {
        host_key for host_key in (vulnerability_host_key(item) for item in cve_items)
        if host_key
    }

    affected_hosts = sorted(
        [
            {
                "hostname": item.get("hostname"),
                "host_id": item.get("host_id"),
                "agent_id": item.get("agent_id"),
                "os_name": item.get("os_name"),
                "os_version": item.get("os_version"),
                "package_name": item.get("package_name"),
                "installed_version": item.get("installed_version"),
                "fixed_version": item.get("fixed_version"),
                "detected_at": item.get("detected_at"),
                "last_seen_at": item.get("last_seen_at"),
                "status": item.get("status"),
                "remediation_status": item.get("remediation_status"),
            }
            for item in cve_items
        ],
        key=lambda host: (
            str(host.get("hostname") or ""),
            str(host.get("package_name") or ""),
            str(host.get("detected_at") or ""),
        ),
    )

    return {
        "status": "ok",
        "source": "normalized_vulnerabilities",
        "cve": {
            "cve_id": cve_id,
            "title": first_vulnerability_value(cve_items, "title"),
            "highest_severity": highest_vulnerability_severity(cve_items),
            "cvss_score": highest_cvss_score(cve_items),
            "published_at": first_vulnerability_value(cve_items, "published_at"),
            "modified_at": first_vulnerability_value(cve_items, "modified_at"),
            "affected_host_count": len(affected_host_keys),
            "affected_package_count": len(packages),
            "packages": packages,
            "reference_urls": reference_urls,
            "remediation_hint": first_vulnerability_value(cve_items, "remediation_hint"),
        },
        "affected_hosts": affected_hosts,
    }



VULNERABILITY_SLA_LEVELS = {
    "critical": "urgent",
    "high": "high",
    "medium": "normal",
    "low": "low",
    "unknown": "normal",
}


def vulnerability_field(item, key: str, fallback: str = "unknown"):
    value = item.get(key)
    if value is None:
        return fallback

    text_value = str(value).strip()
    return text_value or fallback


def find_vulnerability_item(cve_id: str, hostname: str, package_name: str):
    cve_filter = cve_id.strip().lower()
    host_filter = hostname.strip().lower()
    package_filter = package_name.strip().lower()

    for item in load_normalized_vulnerabilities():
        if str(item.get("cve_id") or "").strip().lower() != cve_filter:
            continue
        if str(item.get("hostname") or "").strip().lower() != host_filter:
            continue
        if str(item.get("package_name") or "").strip().lower() != package_filter:
            continue
        return item

    return None


def vulnerability_sla_level(severity: Optional[str]) -> str:
    return VULNERABILITY_SLA_LEVELS[normalized_severity(severity)]


def vulnerability_serviceops_task(item, note: Optional[str] = None) -> str:
    os_parts = [
        vulnerability_field(item, "os_name", ""),
        vulnerability_field(item, "os_version", ""),
    ]
    os_text = " ".join(part for part in os_parts if part).strip() or "unknown"
    severity = normalized_severity(item.get("severity"))
    lines = [
        "Vulnerability remediation request",
        "",
        f"CVE: {vulnerability_field(item, 'cve_id')}",
        f"Severity: {severity}",
        f"CVSS: {vulnerability_field(item, 'cvss_score')}",
        f"ServiceOps SLA: {vulnerability_sla_level(severity)}",
        f"Host: {vulnerability_field(item, 'hostname')}",
        f"Agent ID: {vulnerability_field(item, 'agent_id')}",
        f"OS: {os_text}",
        f"Package: {vulnerability_field(item, 'package_name')}",
        f"Installed Version: {vulnerability_field(item, 'installed_version')}",
        f"Fixed Version: {vulnerability_field(item, 'fixed_version')}",
        f"Remediation Hint: {vulnerability_field(item, 'remediation_hint')}",
        f"Source: {vulnerability_field(item, 'source')}",
        f"Source Index: {vulnerability_field(item, 'source_index')}",
        f"Detected At: {vulnerability_field(item, 'detected_at')}",
        f"Last Seen At: {vulnerability_field(item, 'last_seen_at')}",
        "",
        "Recommended action:",
        "Patch package, verify service health, rerun Wazuh vulnerability scan, attach Recovery Evidence.",
    ]

    clean_note = note.strip() if note else ""
    if clean_note:
        lines.extend(["", "Operator note:", clean_note])

    return "\n".join(lines)


def write_vulnerability_ticket_audit(db, action: str, entity_id, summary: str, actor: str) -> None:
    try:
        with db.begin() as conn:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=entity_id,
                action=action,
                summary=summary,
                actor=actor,
            )
    except Exception as exc:
        print(f"Warning: failed to write vulnerability ServiceOps audit log: {exc}")


# Team_AgentOps fixture API v1 is read-only. It reads safe demo fixtures only.
# It does not write files or DB, create audit logs, store prompt / response,
# or mutate AgentOps / ProjectOps / ServiceOps data.
@app.get("/api/team-agentops/dashboard")
def team_agentops_dashboard():
    warnings = []
    runs_data = load_optional_team_agentops_fixture("demo_agent_runs.json", warnings)
    runs = team_agentops_fixture_records("demo_agent_runs.json", warnings)
    projects = team_agentops_fixture_list(
        "demo_project_contribution.json", "projects", warnings
    )
    scorecard = load_optional_team_agentops_fixture("demo_scorecard.json", warnings)
    metrics = scorecard.get("metrics", {})
    notes = scorecard.get("notes", [])
    if not isinstance(metrics, dict):
        metrics = {}
    if not isinstance(notes, list):
        notes = []

    active_agents = {
        item.get("agent_name")
        for item in runs
        if item.get("agent_name")
        and item.get("status") in {"running", "done", "review_needed"}
    }
    pending_review = sum(
        1
        for item in runs
        if item.get("review_status") == "pending"
        or item.get("status") == "review_needed"
    )
    project_progress = [
        team_agentops_int(item, "progress_percent")
        for item in projects
        if item.get("progress_percent") is not None
    ]
    project_impact_percent = (
        round(sum(project_progress) / len(project_progress)) if project_progress else 0
    )

    return {
        "generated_at": runs_data.get("generated_at") or now_utc(),
        "source": "fixture",
        "mode": "read_only",
        "summary": {
            "active_agents": len(active_agents),
            "pending_review": pending_review,
            "project_impact_percent": project_impact_percent,
            "failed_runs": sum(1 for item in runs if item.get("status") == "failed"),
            "usage_cost_tokens": sum(
                team_agentops_int(item, "token_estimate") for item in runs
            ),
        },
        "agent_activity_timeline": [
            team_agentops_timeline_record(item)
            for item in sorted(
                runs, key=lambda item: str(item.get("started_at") or ""), reverse=True
            )[:10]
        ],
        "project_contribution": projects,
        "team_scorecard": {"metrics": metrics, "notes": notes},
        "safety_boundary": dict(TEAM_AGENTOPS_SAFETY_BOUNDARY),
        "warnings": warnings,
    }


@app.get("/api/team-agentops/runs")
def list_team_agentops_runs(
    status: Optional[str] = None,
    review_status: Optional[str] = None,
    project_id: Optional[int] = None,
    agent_name: Optional[str] = None,
):
    warnings = []
    runs = team_agentops_fixture_records("demo_agent_runs.json", warnings)
    filtered = [
        item
        for item in runs
        if (status is None or item.get("status") == status)
        and (review_status is None or item.get("review_status") == review_status)
        and (project_id is None or item.get("project_id") == project_id)
        and (agent_name is None or item.get("agent_name") == agent_name)
    ]
    return {
        "schema_version": "team_agentops_runs_api_v1",
        "source": "fixture",
        "mode": "read_only",
        "records": [
            team_agentops_public_record(item, TEAM_AGENTOPS_RUN_FIELDS)
            for item in filtered
        ],
        "warnings": warnings,
    }


@app.get("/api/team-agentops/runs/{run_uid}")
def get_team_agentops_run(run_uid: str):
    warnings = []
    runs = team_agentops_fixture_records("demo_agent_runs.json", warnings)
    run = next((item for item in runs if item.get("run_uid") == run_uid), None)
    if run is None:
        raise HTTPException(status_code=404, detail="Team_AgentOps run not found.")

    outputs = team_agentops_fixture_records("demo_agent_outputs.json", warnings)
    reviews = team_agentops_fixture_records("demo_agent_reviews.json", warnings)
    return {
        "schema_version": "team_agentops_run_detail_api_v1",
        "source": "fixture",
        "mode": "read_only",
        "run": team_agentops_public_record(run, TEAM_AGENTOPS_RUN_FIELDS),
        "outputs": [
            team_agentops_public_record(item, TEAM_AGENTOPS_OUTPUT_FIELDS)
            for item in outputs
            if item.get("agent_run_uid") == run_uid
        ],
        "reviews": [
            team_agentops_public_record(item, TEAM_AGENTOPS_REVIEW_FIELDS)
            for item in reviews
            if item.get("agent_run_uid") == run_uid
        ],
        "warnings": warnings,
    }


@app.get("/api/team-agentops/reviews/pending")
def list_team_agentops_pending_reviews():
    warnings = []
    runs = team_agentops_fixture_records("demo_agent_runs.json", warnings)
    return {
        "schema_version": "team_agentops_pending_reviews_api_v1",
        "source": "fixture",
        "mode": "read_only",
        "records": [
            team_agentops_public_record(item, TEAM_AGENTOPS_RUN_FIELDS)
            for item in runs
            if item.get("review_status") == "pending"
            or item.get("status") == "review_needed"
        ],
        "warnings": warnings,
    }


@app.get("/api/team-agentops/projects/contribution")
def list_team_agentops_project_contribution():
    warnings = []
    projects = team_agentops_fixture_list(
        "demo_project_contribution.json", "projects", warnings
    )
    return {
        "schema_version": "team_agentops_project_contribution_api_v1",
        "source": "fixture",
        "mode": "read_only",
        "projects": projects,
        "warnings": warnings,
    }


@app.get("/api/team-agentops/scorecard")
def get_team_agentops_scorecard():
    warnings = []
    scorecard = load_optional_team_agentops_fixture("demo_scorecard.json", warnings)
    metrics = scorecard.get("metrics", {})
    notes = scorecard.get("notes", [])
    return {
        "schema_version": "team_agentops_scorecard_api_v1",
        "source": "fixture",
        "mode": "read_only",
        "metrics": metrics if isinstance(metrics, dict) else {},
        "notes": notes if isinstance(notes, list) else [],
        "warnings": warnings,
    }


@app.get("/api/agentops/summary")
def agentops_summary(source: Optional[str] = None):
    runs = load_agent_runs(source)
    return agentops_summary_response(runs)


@app.get("/api/agentops/runs")
def list_agentops_runs(
    project: Optional[str] = None,
    status: Optional[str] = None,
    task: Optional[str] = None,
    model: Optional[str] = None,
    limit: int = 100,
    source: Optional[str] = None,
):
    runs = load_agent_runs(source)

    if limit < 1:
        limit = 100
    limit = min(limit, 500)

    def contains(value, needle: Optional[str]) -> bool:
        if not needle:
            return True
        return needle.strip().lower() in str(value or "").lower()

    filtered = []
    status_filter = status.strip().lower() if status else None
    for item in runs:
        item_status = normalize_agentops_status(item.get("status"))
        task_text = f"{item.get('task_number') or ''} {item.get('task_name') or ''}"
        if not contains(item.get("project_name"), project):
            continue
        if status_filter and item_status != status_filter:
            continue
        if not contains(task_text, task):
            continue
        if not contains(item.get("model"), model):
            continue
        filtered.append(item)

    public_fields = [
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
    ]
    items = [
        agentops_public_run(
            item,
            public_fields,
            include_preview_quality=load_agent_runs.source_mode == "preview",
        )
        for item in sorted(filtered, key=agentops_sort_started_at, reverse=True)[:limit]
    ]

    response = {
        "status": "ok",
        "count": len(filtered),
        "limit": limit,
        "items": items,
    }
    response.update(agentops_response_metadata(runs))
    return response


@app.get("/api/vulnerabilities/summary")
def vulnerabilities_summary():
    items = load_normalized_vulnerabilities()
    response = vulnerability_summary_response(items)
    warning = load_normalized_vulnerabilities.warning
    if warning:
        response["warning"] = warning

    return response


@app.get("/api/vulnerabilities/cves/{cve_id}")
def vulnerability_cve_detail(cve_id: str):
    items = load_normalized_vulnerabilities()
    response = vulnerability_cve_response(items, cve_id)
    warning = load_normalized_vulnerabilities.warning
    if warning:
        response["warning"] = warning

    return response


@app.get("/api/vulnerabilities")
def vulnerabilities(
    severity: Optional[str] = None,
    cve: Optional[str] = None,
    host: Optional[str] = None,
    package: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[str] = None,
):
    items = load_normalized_vulnerabilities()
    requested_limit = parse_vulnerability_limit(limit)

    severity_filter = severity.strip().lower() if severity else None
    cve_filter = cve.strip().lower() if cve else None
    host_filter = host.strip().lower() if host else None
    package_filter = package.strip().lower() if package else None
    status_filter = status.strip().lower() if status else None

    filtered_items = []
    for item in items:
        if severity_filter and normalized_severity(item.get("severity")) != severity_filter:
            continue

        if cve_filter and cve_filter not in str(item.get("cve_id") or "").lower():
            continue

        if host_filter:
            hostname = str(item.get("hostname") or "").lower()
            host_id = str(item.get("host_id") or "").lower()
            if host_filter not in hostname and host_filter not in host_id:
                continue

        if package_filter and package_filter not in str(item.get("package_name") or "").lower():
            continue

        if status_filter:
            remediation = str(item.get("remediation_status") or "").lower()
            item_status = str(item.get("status") or "").lower()
            if status_filter not in remediation and status_filter not in item_status:
                continue

        filtered_items.append(item)

    sorted_items = sorted(
        filtered_items,
        key=lambda item: str(item.get("last_seen_at") or ""),
        reverse=True,
    )
    sorted_items = sorted(
        sorted_items,
        key=lambda item: SEVERITY_ORDER[normalized_severity(item.get("severity"))],
    )

    response = {
        "status": "ok",
        "source": "normalized_vulnerabilities",
        "count": len(filtered_items),
        "limit": requested_limit,
        "items": sorted_items[:requested_limit],
    }
    warning = load_normalized_vulnerabilities.warning
    if warning:
        response["warning"] = warning

    return response



@app.post("/api/vulnerabilities/create-serviceops-ticket")
def create_serviceops_ticket_from_vulnerability(
    payload: VulnerabilityServiceOpsTicketCreate,
    demo_role: str = Header(default="viewer", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    cve_id = payload.cve_id.strip()
    hostname = payload.hostname.strip()
    package_name = payload.package_name.strip()
    assignee = payload.assignee.strip() if payload.assignee else actor
    note = payload.note.strip() if payload.note else None

    vulnerability = find_vulnerability_item(cve_id, hostname, package_name)
    if vulnerability is None:
        raise HTTPException(status_code=404, detail="Vulnerability item not found.")

    db = require_db()
    title = f"Remediate {vulnerability_field(vulnerability, 'cve_id')} on {vulnerability_field(vulnerability, 'hostname')} / {vulnerability_field(vulnerability, 'package_name')}"
    task = vulnerability_serviceops_task(vulnerability, note)
    sla_level = vulnerability_sla_level(vulnerability.get("severity"))
    audit_summary = f"Created vulnerability remediation ticket for {vulnerability_field(vulnerability, 'cve_id')} on {vulnerability_field(vulnerability, 'hostname')}"

    with db.begin() as conn:
        existing = conn.execute(
            text(
                f"""
                SELECT
                    {SERVICEOPS_TICKET_COLUMNS}
                FROM serviceops_tickets
                WHERE deleted_at IS NULL
                  AND lower(status) NOT IN ('done', 'archived', 'deleted')
                  AND lower(task) LIKE :cve_marker
                  AND lower(task) LIKE :host_marker
                  AND lower(task) LIKE :package_marker
                ORDER BY id ASC
                LIMIT 1
                """
            ),
            {
                "cve_marker": f"%cve: {cve_id.lower()}%",
                "host_marker": f"%host: {hostname.lower()}%",
                "package_marker": f"%package: {package_name.lower()}%",
            },
        ).mappings().first()

        if existing is not None:
            ticket = ticket_row_to_dict(existing)
        else:
            max_order = conn.execute(
                text("SELECT COALESCE(MAX(display_order), 0) FROM serviceops_tickets")
            ).scalar_one()

            row = conn.execute(
                text(
                    f"""
                    INSERT INTO serviceops_tickets
                        (
                            title, status, owner, project,
                            estimate_hours, actual_hours, task,
                            assignee, progress_status, sla_level,
                            display_order
                        )
                    VALUES
                        (
                            :title, :status, :owner, :project,
                            :estimate_hours, :actual_hours, :task,
                            :assignee, :progress_status, :sla_level,
                            :display_order
                        )
                    RETURNING
                        {SERVICEOPS_TICKET_COLUMNS}
                    """
                ),
                {
                    "title": title,
                    "status": "pending",
                    "owner": actor,
                    "project": "Vulnerability Remediation",
                    "estimate_hours": 0,
                    "actual_hours": 0,
                    "task": task,
                    "assignee": assignee,
                    "progress_status": "not_started",
                    "sla_level": sla_level,
                    "display_order": int(max_order) + 1,
                },
            ).mappings().first()
            ticket = ticket_row_to_dict(row)

    if existing is not None:
        write_vulnerability_ticket_audit(
            db,
            action="vulnerability_ticket_existing",
            entity_id=ticket["id"],
            summary=f"Existing vulnerability remediation ticket found for {vulnerability_field(vulnerability, 'cve_id')} on {vulnerability_field(vulnerability, 'hostname')}",
            actor=actor,
        )
        return {
            "status": "existing",
            "ticket": ticket,
            "message": "Existing vulnerability remediation ticket found.",
        }

    write_vulnerability_ticket_audit(
        db,
        action="vulnerability_ticket_create",
        entity_id=ticket["id"],
        summary=audit_summary,
        actor=actor,
    )

    return {
        "status": "created",
        "ticket": ticket,
        "vulnerability": vulnerability,
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "enyrax-api",
        "host": socket.gethostname(),
        "time_utc": now_utc(),
        "database": "configured" if engine is not None else "not_configured",
        "modules": {
            "portal": "online",
            "soc": "api-driven",
            "serviceops": "api-driven",
            "projectops": "api-driven",
            "audit": "api-connected",
            "auth": "api-connected",
            "sync": "api-connected",
            "status": "api-connected",
        },
    }


def summarize_sync_health(source_health_summary):
    if source_health_summary.get("error", 0) > 0:
        return "error"
    if source_health_summary.get("stale", 0) > 0:
        return "stale"
    if source_health_summary.get("warning", 0) > 0:
        return "warning"
    if source_health_summary.get("healthy", 0) > 0:
        return "healthy"
    return "unknown"


def check_disk_usage():
    try:
        usage = shutil.disk_usage("/")
        usage_percent = round((usage.used / usage.total) * 100, 1) if usage.total else None
    except OSError as exc:
        return {
            "status": "unknown",
            "usage_percent": None,
            "message": f"Disk usage unavailable: {exc}",
        }

    if usage_percent is None:
        status = "unknown"
    elif usage_percent > 90:
        status = "critical"
    elif usage_percent >= 80:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "usage_percent": usage_percent,
        "message": f"Root filesystem usage is {usage_percent}%",
    }


def check_docker_status():
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.ID}}"],
            capture_output=True,
            check=False,
            text=True,
            timeout=3,
        )
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired, OSError) as exc:
        return {
            "status": "unknown",
            "message": f"Docker status unavailable: {exc}",
        }

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "docker ps returned non-zero status").strip()
        return {
            "status": "unknown",
            "message": f"Docker status unavailable: {detail}",
        }

    running_count = len([line for line in result.stdout.splitlines() if line.strip()])
    return {
        "status": "healthy" if running_count > 0 else "warning",
        "running_count": running_count,
        "message": f"{running_count} running container(s)",
    }


@app.get("/api/system/health-panel")
def system_health_panel():
    checks = {
        "api": {"status": "healthy", "message": "API service alive"},
        "database": {"status": "unknown", "message": "Database is not configured"},
        "sync": {
            "status": "unknown",
            "message": "Sync Gateway health unavailable",
            "source_health_summary": {},
        },
        "soc": {"open_count": 0, "critical_count": 0},
        "serviceops": {"pending_count": 0},
        "disk": check_disk_usage(),
        "docker": check_docker_status(),
        "ssl": {"status": "unknown", "message": "SSL expiry check not configured"},
        "recent_errors": {"status": "healthy", "count": 0, "items": []},
    }

    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).scalar_one()
            checks["database"] = {"status": "healthy", "message": "Database connected"}
        except SQLAlchemyError as exc:
            checks["database"] = {"status": "error", "message": f"Database check failed: {exc}"}

        if checks["database"]["status"] == "healthy":
            try:
                with engine.connect() as conn:
                    source_health_rows = fetch_sync_source_rows(conn)

                source_health_summary = {
                    "healthy": 0,
                    "warning": 0,
                    "stale": 0,
                    "error": 0,
                    "unknown": 0,
                }
                for row in source_health_rows:
                    health = row["health"] if row["health"] in source_health_summary else "unknown"
                    source_health_summary[health] += 1

                sync_status = summarize_sync_health(source_health_summary)
                checks["sync"] = {
                    "status": sync_status,
                    "message": f"Sync Gateway source health is {sync_status}",
                    "source_health_summary": source_health_summary,
                }
            except SQLAlchemyError as exc:
                checks["sync"] = {
                    "status": "unknown",
                    "message": f"Sync Gateway health unavailable: {exc}",
                    "source_health_summary": {},
                }

            try:
                with engine.connect() as conn:
                    soc_counts = conn.execute(
                        text(
                            """
                            SELECT
                                COUNT(*) FILTER (
                                    WHERE lower(status) NOT IN ('closed', 'false_positive')
                                ) AS open_count,
                                COUNT(*) FILTER (
                                    WHERE lower(severity) = 'critical'
                                      AND lower(status) NOT IN ('closed', 'false_positive')
                                ) AS critical_count
                            FROM soc_incidents
                            """
                        )
                    ).mappings().first()
                checks["soc"] = {
                    "open_count": int(soc_counts["open_count"] or 0),
                    "critical_count": int(soc_counts["critical_count"] or 0),
                }
            except SQLAlchemyError:
                checks["soc"] = {"open_count": 0, "critical_count": 0}

            try:
                with engine.connect() as conn:
                    pending_count = conn.execute(
                        text(
                            """
                            SELECT COUNT(*)
                            FROM serviceops_tickets
                            WHERE deleted_at IS NULL
                              AND lower(status) IN ('pending', 'pending_approval')
                            """
                        )
                    ).scalar_one()
                checks["serviceops"] = {"pending_count": int(pending_count or 0)}
            except SQLAlchemyError:
                checks["serviceops"] = {"pending_count": 0}

    return {"status": "ok", "generated_at": now_utc(), "checks": checks}


@app.post("/api/auth/login")
def auth_login(payload: AuthLoginRequest):
    if payload.password != DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    db = require_db()

    with db.connect() as conn:
        user = get_user_by_email(conn, payload.email)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="User is inactive")

    return {
        "status": "ok",
        "token": f"demo-token-{user['role']}",
        "user": auth_user_response(user),
    }


@app.get("/api/auth/me")
def auth_me(authorization: Optional[str] = Header(default=None, alias="Authorization")):
    token = extract_bearer_token(authorization)
    email = token_to_email(token)

    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    db = require_db()

    with db.connect() as conn:
        user = get_user_by_email(conn, email)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="User is inactive")

    return {
        "status": "ok",
        "user": auth_user_response(user),
    }


@app.get("/api/modules")
def modules():
    if engine is None:
        return {
            "status": "ok",
            "service": "enyrax-api",
            "host": socket.gethostname(),
            "time_utc": now_utc(),
            "source": "fallback",
            "modules": MODULES,
        }

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT
                        module_key,
                        name,
                        route,
                        status,
                        description
                    FROM portal_modules
                    ORDER BY display_order ASC
                    """
                )
            ).mappings().all()

        return {
            "status": "ok",
            "service": "enyrax-api",
            "host": socket.gethostname(),
            "time_utc": now_utc(),
            "source": "postgresql",
            "modules": [
                {
                    "key": row["module_key"],
                    "name": row["name"],
                    "route": row["route"],
                    "status": row["status"],
                    "description": row["description"],
                }
                for row in rows
            ],
        }

    except SQLAlchemyError as exc:
        return {
            "status": "degraded",
            "service": "enyrax-api",
            "host": socket.gethostname(),
            "time_utc": now_utc(),
            "source": "fallback",
            "error": str(exc),
            "modules": MODULES,
        }


@app.get("/api/soc/summary")
def soc_summary():
    fallback_incidents = [
        {
            "id": None,
            "title": "Suspicious SSH Brute Force Pattern",
            "severity": "critical",
            "source_ip": "185.220.101.42",
            "target": "web-portal-01",
            "duplicate_count": 36,
            "analysis_type": "failed_login_cluster",
            "mitre": "T1110 Brute Force",
            "status": "open",
            "handled_by": None,
            "handled_at": None,
            "resolution_note": None,
        },
        {
            "id": None,
            "title": "Privilege Escalation After Successful Login",
            "severity": "high",
            "source_ip": "203.0.113.77",
            "target": "infra-node-03",
            "duplicate_count": 8,
            "analysis_type": "attack_story",
            "mitre": "T1068 Privilege Escalation",
            "status": "open",
            "handled_by": None,
            "handled_at": None,
            "resolution_note": None,
        },
        {
            "id": None,
            "title": "Wazuh Agent Disconnected and Reconnected",
            "severity": "medium",
            "source_ip": "10.20.5.17",
            "target": "endpoint-07",
            "duplicate_count": 2,
            "analysis_type": "agent_state_change",
            "mitre": "Defense Evasion Review",
            "status": "open",
            "handled_by": None,
            "handled_at": None,
            "resolution_note": None,
        },
    ]

    source = "fallback"
    hot_incidents = fallback_incidents
    db_error = None

    if engine is not None:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(
                        f"""
                        SELECT
                            {SOC_INCIDENT_COLUMNS}
                        FROM soc_incidents
                        ORDER BY display_order ASC, id ASC
                        """
                    )
                ).mappings().all()

            hot_incidents = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "severity": row["severity"],
                    "source_ip": row["source_ip"],
                    "target": row["target"],
                    "duplicate_count": int(row["duplicate_count"]),
                    "analysis_type": row["analysis_type"],
                    "mitre": row["mitre"],
                    "status": row["status"],
                    "handled_by": row["handled_by"],
                    "handled_at": row["handled_at"].isoformat() if row["handled_at"] else None,
                    "resolution_note": row["resolution_note"],
                }
                for row in rows
            ]
            source = "postgresql"

        except SQLAlchemyError as exc:
            hot_incidents = fallback_incidents
            source = "fallback"
            db_error = str(exc)
    else:
        db_error = "DATABASE_URL not configured"

    critical = sum(1 for item in hot_incidents if item["severity"] == "critical")
    high = sum(1 for item in hot_incidents if item["severity"] == "high")
    medium = sum(1 for item in hot_incidents if item["severity"] == "medium")
    open_incidents = len(hot_incidents)
    correlated_alerts = sum(int(item["duplicate_count"]) for item in hot_incidents)

    response = {
        "status": "ok",
        "service": "enyrax-soc-demo",
        "source": source,
        "time_utc": now_utc(),
        "metrics": {
            "open_incidents": open_incidents,
            "critical": critical,
            "high": high,
            "medium": medium,
            "correlated_alerts": correlated_alerts,
            "ai_confidence": 91,
            "mitre_coverage": len({item["mitre"] for item in hot_incidents}),
        },
        "hot_incidents": hot_incidents,
        "timeline": [
            {
                "time": "07:02",
                "description": "Multiple failed SSH login attempts from external IP.",
            },
            {
                "time": "07:04",
                "description": "Successful login detected after repeated failures.",
            },
            {
                "time": "07:05",
                "description": "Sudo command executed by newly authenticated session.",
            },
            {
                "time": "07:06",
                "description": "Agent heartbeat interruption observed on target host.",
            },
        ],
        "ai_decision": {
            "summary": (
                "The event chain suggests a potential credential-based intrusion followed by "
                "privilege escalation. Confidence is high because login failures, successful "
                "authentication and sudo execution occurred within the same short time window."
            ),
            "recommended_actions": [
                "Temporarily block source IP at firewall layer.",
                "Review successful login session and related commands.",
                "Force password rotation for affected user account.",
                "Preserve logs for incident timeline reconstruction.",
            ],
        },
    }

    if db_error:
        response["db_error"] = db_error

    return response


@app.get("/api/plan-serviceops/dashboard")
def plan_serviceops_dashboard(
    demo_role: str = Header(default="viewer", alias="X-Demo-Role"),
):
    # Task #153 is a read-only aggregation API. It does not mutate ServiceOps or ProjectOps
    # data, create tickets, update statuses, or write audit logs.
    role = normalize_plan_serviceops_role(demo_role)
    generated_at = datetime.now().astimezone()
    tickets = []
    projects = []
    warnings = []

    if engine is None:
        warnings.extend([
            {
                "code": "serviceops_unavailable",
                "message": PLAN_SERVICEOPS_WARNING_MESSAGES["serviceops_unavailable"],
            },
            {
                "code": "projectops_unavailable",
                "message": PLAN_SERVICEOPS_WARNING_MESSAGES["projectops_unavailable"],
            },
        ])
    else:
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(f"""
                    SELECT
                        {SERVICEOPS_TICKET_COLUMNS}
                    FROM serviceops_tickets
                    WHERE deleted_at IS NULL
                """)).mappings().all()
            tickets = [dict(row) for row in rows]
        except SQLAlchemyError:
            warnings.append({
                "code": "serviceops_unavailable",
                "message": PLAN_SERVICEOPS_WARNING_MESSAGES["serviceops_unavailable"],
            })

        try:
            with engine.connect() as conn:
                rows = conn.execute(text(f"""
                    SELECT
                        {PROJECTOPS_PROJECT_COLUMNS}
                    FROM projectops_projects
                    WHERE archived_at IS NULL
                """)).mappings().all()
            projects = [dict(row) for row in rows]
        except SQLAlchemyError:
            warnings.append({
                "code": "projectops_unavailable",
                "message": PLAN_SERVICEOPS_WARNING_MESSAGES["projectops_unavailable"],
            })

    return build_plan_serviceops_dashboard(tickets, projects, role, generated_at, warnings)


@app.get("/api/serviceops/summary")
def serviceops_summary():
    fallback_work_queue = [
        {
            "id": None,
            "title": "VM Request · ERP Test Environment",
            "status": "in_progress",
            "owner": "atn",
            "project": "ERP Upgrade",
            "estimate_hours": 3.5,
            "actual_hours": 2.0,
            "task": "Provision VM, assign network, prepare OS baseline and handover checklist.",
            "assignee": None,
            "progress_status": "not_started",
            "progress_note": None,
            "progress_updated_by": None,
            "progress_updated_at": None,
            "due_at": None,
            "sla_level": "normal",
            "blocked_reason": None,
            "created_at": None,
        },
        {
            "id": None,
            "title": "Firewall Policy Review · Vendor VPN",
            "status": "pending_approval",
            "owner": "Infra Team",
            "project": "Vendor Access Control",
            "estimate_hours": 1.5,
            "actual_hours": 0.5,
            "task": "Review source/destination, service ports, business owner and expiry date.",
            "assignee": None,
            "progress_status": "not_started",
            "progress_note": None,
            "progress_updated_by": None,
            "progress_updated_at": None,
            "due_at": None,
            "sla_level": "normal",
            "blocked_reason": None,
            "created_at": None,
        },
        {
            "id": None,
            "title": "Storage Capacity Alert · Backup Volume",
            "status": "risk",
            "owner": "Storage Admin",
            "project": "Backup Improvement",
            "estimate_hours": 2.0,
            "actual_hours": 4.0,
            "task": "Analyze growth trend, clean expired backup and report expansion risk.",
            "assignee": None,
            "progress_status": "not_started",
            "progress_note": None,
            "progress_updated_by": None,
            "progress_updated_at": None,
            "due_at": None,
            "sla_level": "normal",
            "blocked_reason": None,
            "created_at": None,
        },
        {
            "id": None,
            "title": "Nginx Portal Deployment · ENYRAX Demo",
            "status": "done",
            "owner": "atn",
            "project": "ENYRAX Cloud Demo",
            "estimate_hours": 1.0,
            "actual_hours": 1.0,
            "task": "Deploy portal, verify firewall, confirm public route and status page.",
            "assignee": None,
            "progress_status": "not_started",
            "progress_note": None,
            "progress_updated_by": None,
            "progress_updated_at": None,
            "due_at": None,
            "sla_level": "normal",
            "blocked_reason": None,
            "created_at": None,
        },
    ]

    source = "fallback"
    work_queue = fallback_work_queue
    db_error = None

    if engine is not None:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(
                        f"""
                        SELECT
                            {SERVICEOPS_TICKET_COLUMNS}
                        FROM serviceops_tickets
                        WHERE deleted_at IS NULL
                        ORDER BY display_order ASC, id ASC
                        """
                    )
                ).mappings().all()

            work_queue = [ticket_row_to_dict(row) for row in rows]
            source = "postgresql"

        except SQLAlchemyError as exc:
            work_queue = fallback_work_queue
            source = "fallback"
            db_error = str(exc)
    else:
        db_error = "DATABASE_URL not configured"

    today_tickets = len(work_queue)
    active = sum(1 for item in work_queue if item["status"] == "in_progress")
    pending = sum(1 for item in work_queue if item["status"] == "pending_approval")
    done = sum(1 for item in work_queue if item["status"] == "done")
    risk_items = sum(1 for item in work_queue if item["status"] == "risk")
    team_hours = sum(float(item["actual_hours"]) for item in work_queue)
    project_linked = len({item["project"] for item in work_queue if item["project"]})

    response = {
        "status": "ok",
        "service": "enyrax-serviceops-demo",
        "source": source,
        "time_utc": now_utc(),
        "metrics": {
            "today_tickets": today_tickets,
            "active": active,
            "pending": pending,
            "done": done,
            "team_hours": team_hours,
            "project_linked": project_linked,
            "risk_items": risk_items,
        },
        "work_queue": work_queue,
        "roles": [
            {
                "title": "Infra Member View",
                "description": "Members only see their own tickets, worklog, today's progress, notes and pending reports.",
            },
            {
                "title": "Infra Supervisor View",
                "description": "Supervisors see team workload, member status, total labor hours, blocked tickets and project-linked operation cost.",
            },
            {
                "title": "Executive / Higher-Level View",
                "description": "Higher-level managers review cross-team capacity, project overrun risk and service delivery trends.",
            },
            {
                "title": "ProjectOps Connection",
                "description": "Each ticket can be linked to a project, so infra labor time becomes part of real project cost.",
            },
        ],
        "flow": [
            {
                "step": "Step 01",
                "name": "Request",
                "description": "VM, network, storage, account, firewall or system support request enters the queue.",
            },
            {
                "step": "Step 02",
                "name": "Assign",
                "description": "Supervisor assigns owner, priority, due date and project relationship.",
            },
            {
                "step": "Step 03",
                "name": "Worklog",
                "description": "Member records actions, time spent, blockers and completion notes.",
            },
            {
                "step": "Step 04",
                "name": "Cost Map",
                "description": "Labor time is mapped back to project budget, delivery cost and resource usage.",
            },
            {
                "step": "Step 05",
                "name": "Review",
                "description": "Supervisor reviews team workload, risk items and project operation status.",
            },
        ],
    }

    if db_error:
        response["db_error"] = db_error

    return response


@app.get("/api/projectops/summary")
def projectops_summary():
    fallback_projects = [
        {
            "id": None,
            "title": "ERP Test Environment Upgrade",
            "status": "ontrack",
            "owner": "IT / Infra",
            "budget_hours": 120,
            "actual_hours": 76,
            "linked_tickets": 11,
            "scope": "VM build, network policy, backup baseline, UAT support.",
            "progress": 63,
            "start_date": "2026-05-18",
            "end_date": "2026-06-30",
        },
        {
            "id": None,
            "title": "Vendor VPN Access Control Review",
            "status": "watch",
            "owner": "Security / Infra",
            "budget_hours": 80,
            "actual_hours": 61,
            "linked_tickets": 7,
            "scope": "Firewall rule cleanup, expiry date, owner mapping and audit evidence.",
            "progress": 76,
            "start_date": "2026-05-20",
            "end_date": "2026-06-20",
        },
        {
            "id": None,
            "title": "Backup Storage Improvement",
            "status": "risk",
            "owner": "Infra / Storage",
            "budget_hours": 100,
            "actual_hours": 94,
            "linked_tickets": 9,
            "scope": "Capacity review, retention cleanup, expansion planning and recovery test.",
            "progress": 94,
            "start_date": "2026-05-25",
            "end_date": "2026-07-05",
        },
    ]

    source = "fallback"
    projects = fallback_projects
    db_error = None

    if engine is not None:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(
                        """
                        SELECT
                            id,
                            title,
                            status,
                            owner,
                            budget_hours,
                            actual_hours,
                            linked_tickets,
                            scope,
                            progress,
                            start_date,
                            end_date
                        FROM projectops_projects
                        WHERE archived_at IS NULL
                        ORDER BY display_order ASC, id ASC
                        """
                    )
                ).mappings().all()

            projects = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "status": row["status"],
                    "owner": row["owner"],
                    "budget_hours": float(row["budget_hours"]),
                    "actual_hours": float(row["actual_hours"]),
                    "linked_tickets": int(row["linked_tickets"]),
                    "scope": row["scope"],
                    "progress": int(row["progress"]),
                    "start_date": row["start_date"].isoformat() if row["start_date"] else None,
                    "end_date": row["end_date"].isoformat() if row["end_date"] else None,
                }
                for row in rows
            ]
            source = "postgresql"

        except SQLAlchemyError as exc:
            projects = fallback_projects
            source = "fallback"
            db_error = str(exc)
    else:
        db_error = "DATABASE_URL not configured"

    active_projects = len(projects)
    on_track = sum(1 for item in projects if item["status"] == "ontrack")
    watch = sum(1 for item in projects if item["status"] == "watch")
    risk = sum(1 for item in projects if item["status"] == "risk")
    total_budget = sum(float(item["budget_hours"]) for item in projects)
    total_actual = sum(float(item["actual_hours"]) for item in projects)
    budget_used = round((total_actual / total_budget) * 100) if total_budget else 0
    serviceops_hours = int(total_actual)
    overrun_risk = risk

    response = {
        "status": "ok",
        "service": "enyrax-projectops-demo",
        "source": source,
        "time_utc": now_utc(),
        "metrics": {
            "active_projects": active_projects,
            "on_track": on_track,
            "watch": watch,
            "risk": risk,
            "budget_used": budget_used,
            "serviceops_hours": serviceops_hours,
            "overrun_risk": overrun_risk,
        },
        "projects": projects,
        "gantt": [
            {"phase": "Requirement", "offset": 0, "width": 100, "status": "Done"},
            {"phase": "Infra Build", "offset": 10, "width": 78, "status": "78%"},
            {"phase": "Security Review", "offset": 34, "width": 42, "status": "42%"},
            {"phase": "UAT Support", "offset": 62, "width": 24, "status": "24%"},
            {"phase": "Go-Live", "offset": 82, "width": 8, "status": "Ready"},
        ],
        "cost": {
            "planned_budget": f"{int(total_budget)}h",
            "actual_worklog": f"{int(total_actual)}h",
            "forecast": "346h",
            "risk_signal": "+15%" if risk else "Normal",
            "description": "Potential overrun if unresolved tickets and approvals continue to delay delivery.",
        },
        "flow": [
            {
                "step": "Step 01",
                "name": "Project Card",
                "description": "Project owner creates scope, budget, phase and delivery target.",
            },
            {
                "step": "Step 02",
                "name": "ServiceOps Link",
                "description": "Infra tickets are attached to the project instead of becoming isolated tasks.",
            },
            {
                "step": "Step 03",
                "name": "Worklog Import",
                "description": "Member work hours and notes become real project execution data.",
            },
            {
                "step": "Step 04",
                "name": "Risk Forecast",
                "description": "Budget usage, delay, blockers and approval wait time create overrun signals.",
            },
            {
                "step": "Step 05",
                "name": "Manager View",
                "description": "Supervisors see project health, labor cost and execution risk in one dashboard.",
            },
        ],
    }

    if db_error:
        response["db_error"] = db_error

    return response


@app.get("/api/serviceops/tickets")
def list_serviceops_tickets():
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT
                    {SERVICEOPS_TICKET_COLUMNS}
                FROM serviceops_tickets
                WHERE deleted_at IS NULL
                ORDER BY display_order ASC, id ASC
                """
            )
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "tickets": [ticket_row_to_dict(row) for row in rows],
    }


def list_serviceops_archived_tickets_response(demo_role: str):
    require_role(demo_role, "operator")
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT
                    {SERVICEOPS_TICKET_COLUMNS}
                FROM serviceops_tickets
                WHERE deleted_at IS NOT NULL
                ORDER BY deleted_at DESC, id DESC
                """
            )
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "tickets": [ticket_row_to_dict(row) for row in rows],
    }


@app.get("/api/serviceops/tickets/archive")
def list_serviceops_archive(
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    return list_serviceops_archived_tickets_response(demo_role)


@app.get("/api/serviceops/tickets/trash")
def list_serviceops_trash_compat(
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    return list_serviceops_archived_tickets_response(demo_role)


@app.get("/api/serviceops/tickets/{ticket_id}")
def get_serviceops_ticket(ticket_id: int):
    db = require_db()

    with db.connect() as conn:
        row = conn.execute(
            text(
                f"""
                SELECT
                    {SERVICEOPS_TICKET_COLUMNS}
                FROM serviceops_tickets
                WHERE id = :ticket_id
                """
            ),
            {"ticket_id": ticket_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "status": "ok",
        "ticket": ticket_row_to_dict(row),
    }


@app.get("/api/serviceops/tickets/{ticket_id}/comments")
def list_serviceops_ticket_comments(ticket_id: int):
    db = require_db()

    with db.connect() as conn:
        ticket = conn.execute(
            text(
                """
                SELECT id
                FROM serviceops_tickets
                WHERE id = :ticket_id
                """
            ),
            {"ticket_id": ticket_id},
        ).mappings().first()

        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        rows = conn.execute(
            text(
                """
                SELECT
                    id, ticket_id, actor, role, comment,
                    comment_type, created_at
                FROM serviceops_ticket_comments
                WHERE ticket_id = :ticket_id
                ORDER BY created_at ASC, id ASC
                """
            ),
            {"ticket_id": ticket_id},
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "comments": [serviceops_ticket_comment_row_to_dict(row) for row in rows],
    }


@app.post("/api/serviceops/tickets/{ticket_id}/comments")
def create_serviceops_ticket_comment(
    ticket_id: int,
    payload: ServiceOpsTicketCommentCreate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    comment = payload.comment.strip()
    comment_type = (payload.comment_type or "worklog").strip() or "worklog"
    db = require_db()

    if not comment:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    with db.begin() as conn:
        ticket = conn.execute(
            text(
                """
                SELECT id, title
                FROM serviceops_tickets
                WHERE id = :ticket_id
                """
            ),
            {"ticket_id": ticket_id},
        ).mappings().first()

        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        row = conn.execute(
            text(
                """
                INSERT INTO serviceops_ticket_comments
                    (ticket_id, actor, role, comment, comment_type)
                VALUES
                    (:ticket_id, :actor, :role, :comment, :comment_type)
                RETURNING
                    id, ticket_id, actor, role, comment,
                    comment_type, created_at
                """
            ),
            {
                "ticket_id": ticket_id,
                "actor": actor,
                "role": role,
                "comment": comment,
                "comment_type": comment_type,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="serviceops",
            entity_type="ticket",
            entity_id=ticket_id,
            action="comment",
            summary=f"Added ServiceOps worklog: {ticket['title']}",
            actor=actor,
        )

    return {
        "status": "created",
        "comment": serviceops_ticket_comment_row_to_dict(row),
    }


@app.post("/api/serviceops/tickets")
def create_serviceops_ticket(
    payload: ServiceOpsTicketCreate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM serviceops_tickets")
        ).scalar_one()

        row = conn.execute(
            text(
                f"""
                INSERT INTO serviceops_tickets
                    (title, status, owner, project, estimate_hours, actual_hours, task, display_order)
                VALUES
                    (:title, :status, :owner, :project, :estimate_hours, :actual_hours, :task, :display_order)
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {
                "title": payload.title,
                "status": payload.status,
                "owner": payload.owner,
                "project": payload.project,
                "estimate_hours": payload.estimate_hours,
                "actual_hours": payload.actual_hours,
                "task": payload.task,
                "display_order": int(max_order) + 1,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="serviceops",
            entity_type="ticket",
            entity_id=row["id"],
            action="create",
            summary=f"Created ServiceOps ticket: {row['title']}",
            actor=demo_actor or role,
        )

    return {
        "status": "created",
        "ticket": ticket_row_to_dict(row),
    }


@app.put("/api/serviceops/tickets/{ticket_id}")
def update_serviceops_ticket(
    ticket_id: int,
    payload: ServiceOpsTicketUpdate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    allowed = {
        "title",
        "status",
        "owner",
        "project",
        "estimate_hours",
        "actual_hours",
        "task",
    }

    set_clauses = []
    params = {"ticket_id": ticket_id}

    for key, value in updates.items():
        if key not in allowed:
            continue
        set_clauses.append(f"{key} = :{key}")
        params[key] = value

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    if updates.get("status") == "done":
        actor = demo_actor or role
        set_clauses.extend([
            "progress_status = 'done'",
            "progress_updated_by = :progress_updated_by",
            "progress_updated_at = NOW()",
            "progress_note = CASE WHEN progress_note IS NULL OR btrim(progress_note) = '' THEN 'Marked done.' ELSE progress_note END",
        ])
        params["progress_updated_by"] = actor

    set_sql = ", ".join(set_clauses) + ", updated_at = NOW()"

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE serviceops_tickets
                SET {set_sql}
                WHERE id = :ticket_id
                  AND deleted_at IS NULL
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            params,
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=row["id"],
                action="update",
                summary=f"Updated ServiceOps ticket: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found or archived")

    return {
        "status": "updated",
        "ticket": ticket_row_to_dict(row),
    }


@app.put("/api/serviceops/tickets/{ticket_id}/sla")
def update_serviceops_ticket_sla(
    ticket_id: int,
    payload: ServiceOpsTicketSlaUpdate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    sla_level = (payload.sla_level or "normal").strip().lower()

    if sla_level not in SERVICEOPS_SLA_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid sla_level")

    blocked_reason = payload.blocked_reason.strip() if payload.blocked_reason else None
    if payload.due_at is not None:
        try:
            datetime.fromisoformat(payload.due_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid due_at") from exc

    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE serviceops_tickets
                SET
                    due_at = :due_at,
                    sla_level = :sla_level,
                    blocked_reason = :blocked_reason,
                    updated_at = NOW()
                WHERE id = :ticket_id
                  AND deleted_at IS NULL
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {
                "ticket_id": ticket_id,
                "due_at": payload.due_at,
                "sla_level": sla_level,
                "blocked_reason": blocked_reason,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=row["id"],
                action="sla_update",
                summary=f"Updated ServiceOps SLA: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found or archived")

    return {
        "status": "updated",
        "ticket": ticket_row_to_dict(row),
    }


@app.put("/api/serviceops/tickets/{ticket_id}/take-ownership")
def take_serviceops_ticket_ownership(
    ticket_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    db = require_db()
    progress_note = f"Ticket taken by {actor}."

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE serviceops_tickets
                SET
                    assignee = :actor,
                    progress_status = 'in_progress',
                    progress_note = :progress_note,
                    progress_updated_by = :actor,
                    progress_updated_at = NOW(),
                    updated_at = NOW()
                WHERE id = :ticket_id
                  AND deleted_at IS NULL
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {
                "ticket_id": ticket_id,
                "actor": actor,
                "progress_note": progress_note,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=row["id"],
                action="take_ownership",
                summary=f"Took ownership of ServiceOps ticket: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found or archived")

    return {
        "status": "updated",
        "ticket": ticket_row_to_dict(row),
    }


@app.put("/api/serviceops/tickets/{ticket_id}/progress")
def update_serviceops_ticket_progress(
    ticket_id: int,
    payload: ServiceOpsTicketProgressUpdate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    progress_status = payload.progress_status.strip().lower()

    if progress_status not in SERVICEOPS_PROGRESS_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid progress_status")

    db = require_db()
    status_sql = ", status = 'done'" if progress_status == "done" else ""

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE serviceops_tickets
                SET
                    progress_status = :progress_status,
                    progress_note = :progress_note,
                    progress_updated_by = :progress_updated_by,
                    progress_updated_at = NOW(),
                    updated_at = NOW()
                    {status_sql}
                WHERE id = :ticket_id
                  AND deleted_at IS NULL
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {
                "ticket_id": ticket_id,
                "progress_status": progress_status,
                "progress_note": payload.progress_note,
                "progress_updated_by": actor,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=row["id"],
                action="progress_update",
                summary=f"Updated ServiceOps progress: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found or archived")

    return {
        "status": "updated",
        "ticket": ticket_row_to_dict(row),
    }


@app.put("/api/serviceops/tickets/{ticket_id}/restore")
def restore_serviceops_ticket(
    ticket_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE serviceops_tickets
                SET
                    deleted_at = NULL,
                    deleted_by = NULL,
                    delete_reason = NULL,
                    updated_at = NOW()
                WHERE id = :ticket_id
                  AND deleted_at IS NOT NULL
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {"ticket_id": ticket_id},
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=row["id"],
                action="restore",
                summary=f"Restored ServiceOps ticket from archive: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found or not archived")

    return {
        "status": "restored",
        "ticket": ticket_row_to_dict(row),
    }


@app.delete("/api/serviceops/tickets/{ticket_id}")
def archive_serviceops_ticket(
    ticket_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE serviceops_tickets
                SET
                    deleted_at = NOW(),
                    deleted_by = :deleted_by,
                    delete_reason = :delete_reason,
                    updated_at = NOW()
                WHERE id = :ticket_id
                  AND deleted_at IS NULL
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {
                "ticket_id": ticket_id,
                "deleted_by": role,
                "delete_reason": "Archived from ServiceOps UI",
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="serviceops",
                entity_type="ticket",
                entity_id=row["id"],
                action="archive",
                summary=f"Archived ServiceOps ticket: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found or already archived")

    return {
        "status": "archived",
        "ticket": ticket_row_to_dict(row),
    }


@app.get("/api/projectops/projects")
def list_projectops_projects():
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT
                    {PROJECTOPS_PROJECT_COLUMNS}
                FROM projectops_projects
                WHERE archived_at IS NULL
                ORDER BY display_order ASC, id ASC
                """
            )
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "projects": [project_row_to_dict(row) for row in rows],
    }


@app.get("/api/projectops/projects/archive")
def list_projectops_archive(
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    require_role(demo_role, "operator")
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT
                    {PROJECTOPS_PROJECT_COLUMNS}
                FROM projectops_projects
                WHERE archived_at IS NOT NULL
                ORDER BY archived_at DESC, id DESC
                """
            )
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "projects": [project_row_to_dict(row) for row in rows],
    }


@app.get("/api/projectops/projects/{project_id}")
def get_projectops_project(project_id: int):
    db = require_db()

    with db.connect() as conn:
        row = conn.execute(
            text(
                f"""
                SELECT
                    {PROJECTOPS_PROJECT_COLUMNS}
                FROM projectops_projects
                WHERE id = :project_id
                """
            ),
            {"project_id": project_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "status": "ok",
        "project": project_row_to_dict(row),
    }


@app.post("/api/projectops/projects")
def create_projectops_project(
    payload: ProjectOpsProjectCreate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM projectops_projects")
        ).scalar_one()

        row = conn.execute(
            text(
                f"""
                INSERT INTO projectops_projects
                    (title, status, owner, budget_hours, actual_hours,
                     linked_tickets, scope, progress, start_date, end_date, display_order)
                VALUES
                    (:title, :status, :owner, :budget_hours, :actual_hours,
                     :linked_tickets, :scope, :progress, :start_date, :end_date, :display_order)
                RETURNING
                    {PROJECTOPS_PROJECT_COLUMNS}
                """
            ),
            {
                "title": payload.title,
                "status": payload.status,
                "owner": payload.owner,
                "budget_hours": payload.budget_hours,
                "actual_hours": payload.actual_hours,
                "linked_tickets": payload.linked_tickets,
                "scope": payload.scope,
                "progress": payload.progress,
                "start_date": payload.start_date,
                "end_date": payload.end_date,
                "display_order": int(max_order) + 1,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="projectops",
            entity_type="project",
            entity_id=row["id"],
            action="create",
            summary=f"Created ProjectOps project: {row['title']}",
            actor=demo_actor or role,
        )

    return {
        "status": "created",
        "project": project_row_to_dict(row),
    }


@app.put("/api/projectops/projects/{project_id}")
def update_projectops_project(
    project_id: int,
    payload: ProjectOpsProjectUpdate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    allowed = {
        "title",
        "status",
        "owner",
        "budget_hours",
        "actual_hours",
        "linked_tickets",
        "scope",
        "progress",
        "start_date",
        "end_date",
    }

    set_clauses = []
    params = {"project_id": project_id}

    for key, value in updates.items():
        if key not in allowed:
            continue
        set_clauses.append(f"{key} = :{key}")
        params[key] = value

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    set_sql = ", ".join(set_clauses) + ", updated_at = NOW()"

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE projectops_projects
                SET {set_sql}
                WHERE id = :project_id
                  AND archived_at IS NULL
                RETURNING
                    {PROJECTOPS_PROJECT_COLUMNS}
                """
            ),
            params,
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="projectops",
                entity_type="project",
                entity_id=row["id"],
                action="update",
                summary=f"Updated ProjectOps project: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Project not found or archived")

    return {
        "status": "updated",
        "project": project_row_to_dict(row),
    }


@app.put("/api/projectops/projects/{project_id}/restore")
def restore_projectops_project(
    project_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "supervisor")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE projectops_projects
                SET
                    archived_at = NULL,
                    archived_by = NULL,
                    archive_reason = NULL,
                    updated_at = NOW()
                WHERE id = :project_id
                  AND archived_at IS NOT NULL
                RETURNING
                    {PROJECTOPS_PROJECT_COLUMNS}
                """
            ),
            {"project_id": project_id},
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="projectops",
                entity_type="project",
                entity_id=row["id"],
                action="restore",
                summary=f"Restored ProjectOps project from archive: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Project not found or not archived")

    return {
        "status": "restored",
        "project": project_row_to_dict(row),
    }


@app.delete("/api/projectops/projects/{project_id}")
def archive_projectops_project(
    project_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE projectops_projects
                SET
                    archived_at = NOW(),
                    archived_by = :archived_by,
                    archive_reason = :archive_reason,
                    updated_at = NOW()
                WHERE id = :project_id
                  AND archived_at IS NULL
                RETURNING
                    {PROJECTOPS_PROJECT_COLUMNS}
                """
            ),
            {
                "project_id": project_id,
                "archived_by": role,
                "archive_reason": "Archived from ProjectOps UI",
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="projectops",
                entity_type="project",
                entity_id=row["id"],
                action="archive",
                summary=f"Archived ProjectOps project: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Project not found or already archived")

    return {
        "status": "archived",
        "project": project_row_to_dict(row),
    }


@app.get("/api/soc/incidents")
def list_soc_incidents():
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT
                    {SOC_INCIDENT_COLUMNS}
                FROM soc_incidents
                ORDER BY updated_at DESC NULLS LAST, created_at DESC NULLS LAST, id DESC
                """
            )
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "incidents": [incident_row_to_dict(row) for row in rows],
    }


@app.get("/api/soc/incidents/{incident_id}")
def get_soc_incident(incident_id: int):
    db = require_db()

    with db.connect() as conn:
        row = conn.execute(
            text(
                f"""
                SELECT
                    {SOC_INCIDENT_COLUMNS}
                FROM soc_incidents
                WHERE id = :incident_id
                """
            ),
            {"incident_id": incident_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "ok",
        "incident": incident_row_to_dict(row),
    }


@app.post("/api/soc/incidents/{incident_id}/create-serviceops-ticket")
def create_serviceops_ticket_from_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    db = require_db()

    with db.begin() as conn:
        incident = conn.execute(
            text(
                f"""
                SELECT
                    {SOC_INCIDENT_COLUMNS}
                FROM soc_incidents
                WHERE id = :incident_id
                """
            ),
            {"incident_id": incident_id},
        ).mappings().first()

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        title = f"SOC Follow-up: {incident['title']}"

        existing = conn.execute(
            text(
                f"""
                SELECT
                    {SERVICEOPS_TICKET_COLUMNS}
                FROM serviceops_tickets
                WHERE title = :title
                  AND deleted_at IS NULL
                ORDER BY id ASC
                LIMIT 1
                """
            ),
            {"title": title},
        ).mappings().first()

        if existing is not None:
            return {
                "status": "existing",
                "ticket": ticket_row_to_dict(existing),
            }

        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM serviceops_tickets")
        ).scalar_one()

        row = conn.execute(
            text(
                f"""
                INSERT INTO serviceops_tickets
                    (title, status, owner, project, estimate_hours, actual_hours, task, display_order)
                VALUES
                    (:title, :status, :owner, :project, :estimate_hours, :actual_hours, :task, :display_order)
                RETURNING
                    {SERVICEOPS_TICKET_COLUMNS}
                """
            ),
            {
                "title": title,
                "status": "pending",
                "owner": actor,
                "project": "SOC Incident Response",
                "estimate_hours": 0,
                "actual_hours": 0,
                "task": soc_incident_serviceops_task(incident),
                "display_order": int(max_order) + 1,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="serviceops",
            entity_type="ticket",
            entity_id=row["id"],
            action="create",
            summary=f"Created ServiceOps ticket from SOC incident: {incident['title']}",
            actor=actor,
        )

    return {
        "status": "created",
        "ticket": ticket_row_to_dict(row),
    }


@app.get("/api/soc/incidents/{incident_id}/comments")
def list_soc_incident_comments(incident_id: int):
    db = require_db()

    with db.connect() as conn:
        incident = conn.execute(
            text(
                """
                SELECT id
                FROM soc_incidents
                WHERE id = :incident_id
                """
            ),
            {"incident_id": incident_id},
        ).mappings().first()

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        rows = conn.execute(
            text(
                """
                SELECT
                    id, incident_id, actor, role, comment,
                    comment_type, created_at
                FROM soc_incident_comments
                WHERE incident_id = :incident_id
                ORDER BY created_at ASC, id ASC
                """
            ),
            {"incident_id": incident_id},
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "comments": [incident_comment_row_to_dict(row) for row in rows],
    }


@app.post("/api/soc/incidents/{incident_id}/comments")
def create_soc_incident_comment(
    incident_id: int,
    payload: SocIncidentCommentCreate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    comment = payload.comment.strip()
    comment_type = (payload.comment_type or "note").strip() or "note"
    db = require_db()

    if not comment:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    with db.begin() as conn:
        incident = conn.execute(
            text(
                """
                SELECT id, title
                FROM soc_incidents
                WHERE id = :incident_id
                """
            ),
            {"incident_id": incident_id},
        ).mappings().first()

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        row = conn.execute(
            text(
                """
                INSERT INTO soc_incident_comments
                    (incident_id, actor, role, comment, comment_type)
                VALUES
                    (:incident_id, :actor, :role, :comment, :comment_type)
                RETURNING
                    id, incident_id, actor, role, comment,
                    comment_type, created_at
                """
            ),
            {
                "incident_id": incident_id,
                "actor": actor,
                "role": role,
                "comment": comment,
                "comment_type": comment_type,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="soc",
            entity_type="incident",
            entity_id=incident_id,
            action="comment",
            summary=f"Added SOC incident comment: {incident['title']}",
            actor=actor,
        )

    return {
        "status": "created",
        "comment": incident_comment_row_to_dict(row),
    }


@app.post("/api/soc/incidents")
def create_soc_incident(
    payload: SocIncidentCreate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM soc_incidents")
        ).scalar_one()

        row = conn.execute(
            text(
                f"""
                INSERT INTO soc_incidents
                    (title, severity, source_ip, target, duplicate_count,
                     analysis_type, mitre, status, display_order)
                VALUES
                    (:title, :severity, :source_ip, :target, :duplicate_count,
                     :analysis_type, :mitre, :status, :display_order)
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            {
                "title": payload.title,
                "severity": payload.severity,
                "source_ip": payload.source_ip,
                "target": payload.target,
                "duplicate_count": payload.duplicate_count,
                "analysis_type": payload.analysis_type,
                "mitre": payload.mitre,
                "status": payload.status or "open",
                "display_order": int(max_order) + 1,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="soc",
            entity_type="incident",
            entity_id=row["id"],
            action="create",
            summary=f"Created SOC incident: {row['title']}",
            actor=demo_actor or role,
        )

    return {
        "status": "created",
        "incident": incident_row_to_dict(row),
    }


@app.put("/api/soc/incidents/{incident_id}")
def update_soc_incident(
    incident_id: int,
    payload: SocIncidentUpdate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    db = require_db()
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "status" in updates and not updates["status"]:
        raise HTTPException(status_code=400, detail="Status cannot be empty")

    allowed = {
        "title",
        "severity",
        "source_ip",
        "target",
        "duplicate_count",
        "analysis_type",
        "mitre",
        "status",
        "resolution_note",
    }

    set_clauses = []
    params = {"incident_id": incident_id}
    status_changed = "status" in updates

    for key, value in updates.items():
        if key not in allowed:
            continue
        set_clauses.append(f"{key} = :{key}")
        params[key] = value

    if status_changed:
        set_clauses.append("handled_by = :handled_by")
        set_clauses.append("handled_at = NOW()")
        params["handled_by"] = demo_actor or role

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    set_sql = ", ".join(set_clauses) + ", updated_at = NOW()"

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE soc_incidents
                SET {set_sql}
                WHERE id = :incident_id
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            params,
        ).mappings().first()

        if row is not None:
            summary = f"Updated SOC incident: {row['title']}"
            if status_changed:
                summary = f"Updated SOC incident status to {row['status']}: {row['title']}"

            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="update",
                summary=summary,
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "updated",
        "incident": incident_row_to_dict(row),
    }


def update_soc_incident_status(
    incident_id: int,
    new_status: str,
    minimum_role: str,
    demo_role: str,
    demo_actor: Optional[str],
):
    role = require_role(demo_role, minimum_role)
    actor = demo_actor or role
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE soc_incidents
                SET
                    status = :status,
                    handled_by = :handled_by,
                    handled_at = NOW(),
                    updated_at = NOW()
                WHERE id = :incident_id
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            {
                "incident_id": incident_id,
                "status": new_status,
                "handled_by": actor,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="update",
                summary=f"Updated SOC incident status to {row['status']}: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "updated",
        "incident": incident_row_to_dict(row),
    }


@app.put("/api/soc/incidents/{incident_id}/investigate")
def investigate_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    return update_soc_incident_status(
        incident_id,
        "investigating",
        "operator",
        demo_role,
        demo_actor,
    )


@app.put("/api/soc/incidents/{incident_id}/contain")
def contain_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    return update_soc_incident_status(
        incident_id,
        "contained",
        "operator",
        demo_role,
        demo_actor,
    )


@app.put("/api/soc/incidents/{incident_id}/resolve")
def resolve_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    return update_soc_incident_status(
        incident_id,
        "resolved",
        "operator",
        demo_role,
        demo_actor,
    )


@app.put("/api/soc/incidents/{incident_id}/false-positive")
def mark_soc_incident_false_positive(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    return update_soc_incident_status(
        incident_id,
        "false_positive",
        "supervisor",
        demo_role,
        demo_actor,
    )


@app.put("/api/soc/incidents/{incident_id}/infra-verify")
def start_soc_infra_verification(
    incident_id: int,
    payload: Optional[SocIncidentNoteUpdate] = None,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    note = payload.note if payload else None
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE soc_incidents
                SET
                    status = 'infra_verifying',
                    handled_by = :handled_by,
                    handled_at = NOW(),
                    infra_verification_note = :note,
                    updated_at = NOW()
                WHERE id = :incident_id
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            {
                "incident_id": incident_id,
                "handled_by": actor,
                "note": note,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="infra_verify",
                summary=f"Infra verification started for SOC incident: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "updated",
        "incident": incident_row_to_dict(row),
    }


@app.put("/api/soc/incidents/{incident_id}/infra-confirm")
def confirm_soc_infra_normal(
    incident_id: int,
    payload: Optional[SocIncidentNoteUpdate] = None,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    note = payload.note if payload else None
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE soc_incidents
                SET
                    status = 'infra_confirmed',
                    infra_verified_by = :infra_verified_by,
                    infra_verified_at = NOW(),
                    infra_verification_result = 'normal',
                    infra_verification_note = :note,
                    updated_at = NOW()
                WHERE id = :incident_id
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            {
                "incident_id": incident_id,
                "infra_verified_by": actor,
                "note": note,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="infra_confirm",
                summary=f"Infra confirmed normal for SOC incident: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "updated",
        "incident": incident_row_to_dict(row),
    }


@app.put("/api/soc/incidents/{incident_id}/close")
def close_soc_incident(
    incident_id: int,
    payload: Optional[SocIncidentNoteUpdate] = None,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    note = payload.note if payload else None
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                f"""
                UPDATE soc_incidents
                SET
                    status = 'closed',
                    handled_by = :handled_by,
                    handled_at = NOW(),
                    resolution_note = :note,
                    updated_at = NOW()
                WHERE id = :incident_id
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            {
                "incident_id": incident_id,
                "handled_by": actor,
                "note": note,
            },
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="close",
                summary=f"Closed SOC incident after Infra verification: {row['title']}",
                actor=actor,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "updated",
        "incident": incident_row_to_dict(row),
    }


@app.put("/api/soc/incidents/{incident_id}/reopen")
def reopen_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    return update_soc_incident_status(
        incident_id,
        "open",
        "supervisor",
        demo_role,
        demo_actor,
    )


@app.delete("/api/soc/incidents/{incident_id}")
def delete_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "admin")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                """
                DELETE FROM soc_incidents
                WHERE id = :incident_id
                RETURNING id, title
                """
            ),
            {"incident_id": incident_id},
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="delete",
                summary=f"Deleted SOC incident: {row['title']}",
                actor=demo_actor or role,
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "deleted",
        "incident": {
            "id": row["id"],
            "title": row["title"],
        },
    }


@app.post("/api/sync/events")
def create_local_sync_event(
    payload: LocalSyncEventCreate,
    x_sync_key: Optional[str] = Header(default=None, alias="X-Sync-Key"),
):
    require_sync_key(x_sync_key)
    db = require_db()

    insert_sql = text(
        """
        INSERT INTO local_sync_events
            (source, system, event_type, status, message, payload)
        VALUES
            (:source, :system, :event_type, :status, :message, :payload)
        RETURNING
            id, source, system, event_type, status, message, payload, created_at
        """
    ).bindparams(bindparam("payload", type_=JSONB))

    with db.begin() as conn:
        row = conn.execute(
            insert_sql,
            {
                "source": payload.source,
                "system": payload.system,
                "event_type": payload.event_type,
                "status": payload.status or "ok",
                "message": payload.message,
                "payload": payload.payload or {},
            },
        ).mappings().first()

    return {
        "status": "created",
        "event": sync_event_row_to_dict(row),
    }


@app.get("/api/sync/events")
def list_local_sync_events(
    limit: int = 50,
    source: Optional[str] = None,
    system: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
):
    db = require_db()
    bounded_limit = max(1, min(int(limit), 200))
    filters = []
    params = {"limit": bounded_limit}

    for key, value in {
        "source": source,
        "system": system,
        "event_type": event_type,
        "status": status,
    }.items():
        if value:
            filters.append(f"{key} = :{key}")
            params[key] = value

    where_sql = ""
    if filters:
        where_sql = "WHERE " + " AND ".join(filters)

    with db.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT
                    id, source, system, event_type, status, message, payload, created_at
                FROM local_sync_events
                {where_sql}
                ORDER BY created_at DESC, id DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

    return {
        "status": "ok",
        "count": len(rows),
        "limit": bounded_limit,
        "events": [sync_event_row_to_dict(row) for row in rows],
    }


@app.get("/api/sync/sources")
def list_local_sync_sources():
    db = require_db()

    with db.connect() as conn:
        rows = fetch_sync_source_rows(conn, include_metadata=True)

    sources = [sync_source_row_to_dict(row) for row in rows]

    return {
        "status": "ok",
        "count": len(sources),
        "sources": sources,
    }


@app.put("/api/sync/sources/{source}/metadata")
def update_sync_source_metadata(
    source: str,
    payload: SyncSourceMetadataUpdate,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    normalized_source = source.strip()
    normalized_status = (payload.status or "").strip().lower()
    note = payload.note.strip() if payload.note else None

    if not normalized_source or len(normalized_source) > 160:
        raise HTTPException(status_code=400, detail="Invalid source")

    if normalized_status not in SYNC_SOURCE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid source status")

    archived_by = actor if normalized_status == "archived" else None

    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                """
                INSERT INTO sync_source_metadata
                    (source, status, note, archived_by, archived_at, updated_at)
                VALUES
                    (
                        :source,
                        :status,
                        :note,
                        :archived_by,
                        CASE WHEN :status = 'archived' THEN NOW() ELSE NULL END,
                        NOW()
                    )
                ON CONFLICT (source)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    note = EXCLUDED.note,
                    archived_by = CASE
                        WHEN EXCLUDED.status = 'archived' THEN EXCLUDED.archived_by
                        ELSE NULL
                    END,
                    archived_at = CASE
                        WHEN EXCLUDED.status = 'archived' THEN NOW()
                        ELSE NULL
                    END,
                    updated_at = NOW()
                RETURNING
                    source, status, note, archived_by, archived_at, created_at, updated_at
                """
            ),
            {
                "source": normalized_source,
                "status": normalized_status,
                "note": note,
                "archived_by": archived_by,
            },
        ).mappings().first()

    try:
        with db.begin() as conn:
            write_audit_log(
                conn,
                module="sync",
                entity_type="sync_source",
                entity_id=None,
                action="source_metadata_update",
                summary=f"Updated Sync source metadata: {normalized_source}",
                actor=actor,
            )
    except Exception as exc:
        print(f"Warning: failed to write sync source metadata audit log: {exc}")

    return {
        "status": "updated",
        "source": {
            "source": row["source"],
            "source_status": row["status"],
            "source_note": row["note"],
            "archived_at": row["archived_at"].isoformat() if row["status"] == "archived" and row["archived_at"] else None,
            "archived_by": row["archived_by"] if row["status"] == "archived" else None,
        },
    }


@app.get("/api/sync/incident-candidates")
def list_sync_incident_candidates():
    db = require_db()

    with db.connect() as conn:
        rows = fetch_sync_source_rows(conn)

    candidates = [
        sync_incident_candidate_from_source(row)
        for row in rows
        if row["health"] in {"stale", "error", "unknown"}
    ]

    return {
        "status": "ok",
        "count": len(candidates),
        "candidates": candidates,
    }


@app.post("/api/sync/incident-candidates/{source}/create-soc-incident")
def create_soc_incident_from_sync_candidate(
    source: str,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
    demo_actor: str = Header(default=None, alias="X-Demo-Actor"),
):
    role = require_role(demo_role, "operator")
    actor = demo_actor or role
    db = require_db()

    with db.begin() as conn:
        source_rows = fetch_sync_source_rows(conn)
        source_row = next((row for row in source_rows if row["source"] == source), None)

        if source_row is None or source_row["health"] not in {"stale", "error", "unknown"}:
            raise HTTPException(status_code=400, detail="Source is not an incident candidate.")

        candidate = sync_incident_candidate_from_source(source_row)
        existing = conn.execute(
            text(
                f"""
                SELECT
                    {SOC_INCIDENT_COLUMNS}
                FROM soc_incidents
                WHERE analysis_type = 'local_sync_candidate'
                  AND source_ip = :source
                  AND status NOT IN ('closed', 'false_positive')
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """
            ),
            {"source": source},
        ).mappings().first()

        if existing is not None:
            resolution_note = (
                candidate["reason"]
                + " Recommended action: "
                + candidate["recommended_action"]
            )
            row = conn.execute(
                text(
                    f"""
                    UPDATE soc_incidents
                    SET
                        severity = :severity,
                        resolution_note = :resolution_note,
                        updated_at = NOW()
                    WHERE id = :incident_id
                    RETURNING
                        {SOC_INCIDENT_COLUMNS}
                    """
                ),
                {
                    "incident_id": existing["id"],
                    "severity": candidate["severity"],
                    "resolution_note": resolution_note,
                },
            ).mappings().first()

            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="sync_refresh",
                summary=f"Refreshed SOC incident from sync candidate: {row['title']}",
                actor=actor,
            )

            return {
                "status": "existing_updated",
                "incident": incident_row_to_dict(row),
            }

        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM soc_incidents")
        ).scalar_one()
        resolution_note = (
            candidate["reason"]
            + " Recommended action: "
            + candidate["recommended_action"]
        )
        row = conn.execute(
            text(
                f"""
                INSERT INTO soc_incidents
                    (title, severity, source_ip, target, duplicate_count,
                     analysis_type, mitre, status, resolution_note, display_order)
                VALUES
                    (:title, :severity, :source_ip, :target, :duplicate_count,
                     :analysis_type, :mitre, :status, :resolution_note, :display_order)
                RETURNING
                    {SOC_INCIDENT_COLUMNS}
                """
            ),
            {
                "title": candidate["title"],
                "severity": candidate["severity"],
                "source_ip": candidate["source"],
                "target": "local-sync-gateway",
                "duplicate_count": 1,
                "analysis_type": "local_sync_candidate",
                "mitre": "Operational Monitoring",
                "status": "open",
                "resolution_note": resolution_note,
                "display_order": int(max_order) + 1,
            },
        ).mappings().first()

        write_audit_log(
            conn,
            module="soc",
            entity_type="incident",
            entity_id=row["id"],
            action="create",
            summary=f"Created SOC incident from sync candidate: {row['title']}",
            actor=actor,
        )

    return {
        "status": "created",
        "incident": incident_row_to_dict(row),
    }


@app.get("/api/sync/status")
def local_sync_status():
    db = require_db()

    with db.connect() as conn:
        summary = conn.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_events,
                    MAX(created_at) AS latest_event_at
                FROM local_sync_events
                """
            )
        ).mappings().first()
        sources = conn.execute(
            text(
                """
                SELECT source
                FROM local_sync_events
                GROUP BY source
                ORDER BY source ASC
                """
            )
        ).mappings().all()
        systems = conn.execute(
            text(
                """
                SELECT system
                FROM local_sync_events
                GROUP BY system
                ORDER BY system ASC
                """
            )
        ).mappings().all()
        statuses = conn.execute(
            text(
                """
                SELECT status, COUNT(*) AS count
                FROM local_sync_events
                GROUP BY status
                ORDER BY status ASC
                """
            )
        ).mappings().all()
        recent_rows = conn.execute(
            text(
                """
                SELECT
                    id, source, system, event_type, status, message, payload, created_at
                FROM local_sync_events
                ORDER BY created_at DESC, id DESC
                LIMIT 10
                """
            )
        ).mappings().all()
        source_health_rows = fetch_sync_source_rows(conn)

    latest_event_at = summary["latest_event_at"] if summary else None
    source_health_summary = {
        "healthy": 0,
        "warning": 0,
        "stale": 0,
        "error": 0,
        "unknown": 0,
    }

    for row in source_health_rows:
        health = row["health"] if row["health"] in source_health_summary else "unknown"
        source_health_summary[health] += 1

    return {
        "status": "ok",
        "total_events": int(summary["total_events"] if summary else 0),
        "latest_event_at": latest_event_at.isoformat() if latest_event_at else None,
        "sources": [row["source"] for row in sources],
        "systems": [row["system"] for row in systems],
        "status_counts": {row["status"]: int(row["count"]) for row in statuses},
        "source_health_summary": source_health_summary,
        "recent_events": [sync_event_row_to_dict(row) for row in recent_rows],
    }




@app.get("/api/audit/logs")
def list_audit_logs(
    limit: int = 50,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    require_role(demo_role, "supervisor")

    db = require_db()
    safe_limit = max(1, min(limit, 200))

    with db.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                    id, module, entity_type, entity_id,
                    action, summary, actor, created_at
                FROM audit_logs
                ORDER BY created_at DESC, id DESC
                LIMIT :limit
                """
            ),
            {"limit": safe_limit},
        ).mappings().all()

    return {
        "status": "ok",
        "source": "postgresql",
        "count": len(rows),
        "logs": [
            {
                "id": row["id"],
                "module": row["module"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "action": row["action"],
                "summary": row["summary"],
                "actor": row["actor"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ],
    }
