from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import os
import socket

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


class ServiceOpsTicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    status: str = Field(default="pending_approval", max_length=50)
    owner: str = Field(..., min_length=1, max_length=100)
    project: str = Field(..., min_length=1, max_length=120)
    estimate_hours: float = 0
    actual_hours: float = 0
    task: str = Field(..., min_length=1)


class ServiceOpsTicketUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, max_length=50)
    owner: Optional[str] = Field(default=None, max_length=100)
    project: Optional[str] = Field(default=None, max_length=120)
    estimate_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    task: Optional[str] = None


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


class LocalSyncEventCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=120)
    system: str = Field(..., min_length=1, max_length=80)
    event_type: str = Field(..., min_length=1, max_length=120)
    status: str = Field(default="ok", max_length=50)
    message: Optional[str] = None
    payload: dict = Field(default_factory=dict)


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


def sync_source_row_to_dict(row):
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


def fetch_sync_source_rows(conn):
    return conn.execute(
        text(
            """
            WITH ranked_events AS (
                SELECT
                    source, system, event_type, status, message, created_at, id,
                    ROW_NUMBER() OVER (
                        PARTITION BY source
                        ORDER BY created_at DESC, id DESC
                    ) AS source_rank
                FROM local_sync_events
            ),
            source_rollup AS (
                SELECT
                    source,
                    MAX(created_at) AS latest_event_at,
                    MAX(created_at) FILTER (WHERE event_type = 'heartbeat') AS latest_heartbeat_at,
                    ARRAY_AGG(DISTINCT system ORDER BY system) AS systems,
                    COUNT(*) AS total_events,
                    COUNT(*) FILTER (WHERE status = 'ok') AS ok_count,
                    COUNT(*) FILTER (WHERE status = 'warning') AS warning_count,
                    COUNT(*) FILTER (WHERE status = 'error') AS error_count,
                    (ARRAY_AGG(message ORDER BY created_at DESC, id DESC))[1] AS latest_message
                FROM local_sync_events
                GROUP BY source
            ),
            recent_errors AS (
                SELECT
                    source,
                    BOOL_OR(status = 'error') AS has_recent_error
                FROM ranked_events
                WHERE source_rank <= 30
                GROUP BY source
            )
            SELECT
                source_rollup.source,
                CASE
                    WHEN COALESCE(recent_errors.has_recent_error, FALSE) THEN 'error'
                    WHEN source_rollup.latest_heartbeat_at IS NULL THEN 'unknown'
                    WHEN source_rollup.latest_heartbeat_at >= NOW() - INTERVAL '10 minutes' THEN 'healthy'
                    WHEN source_rollup.latest_heartbeat_at >= NOW() - INTERVAL '30 minutes' THEN 'warning'
                    ELSE 'stale'
                END AS health,
                source_rollup.latest_event_at,
                source_rollup.latest_heartbeat_at,
                source_rollup.systems,
                source_rollup.total_events,
                source_rollup.ok_count,
                source_rollup.warning_count,
                source_rollup.error_count,
                source_rollup.latest_message
            FROM source_rollup
            LEFT JOIN recent_errors ON recent_errors.source = source_rollup.source
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
    display_order, created_at, updated_at,
    deleted_at, deleted_by, delete_reason
"""


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


def write_audit_log(
    conn,
    module: str,
    entity_type: str,
    entity_id: Optional[int],
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
                        """
                        SELECT
                            id,
                            title,
                            status,
                            owner,
                            project,
                            estimate_hours,
                            actual_hours,
                            task
                        FROM serviceops_tickets
                        WHERE deleted_at IS NULL
                        ORDER BY display_order ASC, id ASC
                        """
                    )
                ).mappings().all()

            work_queue = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "status": row["status"],
                    "owner": row["owner"],
                    "project": row["project"],
                    "estimate_hours": float(row["estimate_hours"]),
                    "actual_hours": float(row["actual_hours"]),
                    "task": row["task"],
                }
                for row in rows
            ]
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
                ORDER BY display_order ASC, id ASC
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
        rows = fetch_sync_source_rows(conn)

    sources = [sync_source_row_to_dict(row) for row in rows]

    return {
        "status": "ok",
        "count": len(sources),
        "sources": sources,
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
            return {
                "status": "existing",
                "incident": incident_row_to_dict(existing),
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
