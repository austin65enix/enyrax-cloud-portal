from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import os
import socket

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


app = FastAPI(
    title="ENYRAX Cloud API",
    version="1.1.0",
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


class SocIncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=220)
    severity: Optional[str] = Field(default=None, max_length=50)
    source_ip: Optional[str] = Field(default=None, max_length=80)
    target: Optional[str] = Field(default=None, max_length=120)
    duplicate_count: Optional[int] = None
    analysis_type: Optional[str] = Field(default=None, max_length=120)
    mitre: Optional[str] = Field(default=None, max_length=160)


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
        "description": "Operation trail for SOC, ServiceOps and ProjectOps create / update / delete actions.",
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


def ticket_row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "status": row["status"],
        "owner": row["owner"],
        "project": row["project"],
        "estimate_hours": float(row["estimate_hours"]),
        "actual_hours": float(row["actual_hours"]),
        "task": row["task"],
        "display_order": row["display_order"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def project_row_to_dict(row):
    return {
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
        "display_order": row["display_order"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
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
            "status": "api-connected",
        },
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
                        """
                        SELECT
                            id,
                            title,
                            severity,
                            source_ip,
                            target,
                            duplicate_count,
                            analysis_type,
                            mitre
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
                """
                SELECT
                    id, title, status, owner, project,
                    estimate_hours, actual_hours, task,
                    display_order, created_at, updated_at
                FROM serviceops_tickets
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


@app.get("/api/serviceops/tickets/{ticket_id}")
def get_serviceops_ticket(ticket_id: int):
    db = require_db()

    with db.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    id, title, status, owner, project,
                    estimate_hours, actual_hours, task,
                    display_order, created_at, updated_at
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
):
    require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM serviceops_tickets")
        ).scalar_one()

        row = conn.execute(
            text(
                """
                INSERT INTO serviceops_tickets
                    (title, status, owner, project, estimate_hours, actual_hours, task, display_order)
                VALUES
                    (:title, :status, :owner, :project, :estimate_hours, :actual_hours, :task, :display_order)
                RETURNING
                    id, title, status, owner, project,
                    estimate_hours, actual_hours, task,
                    display_order, created_at, updated_at
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
):
    require_role(demo_role, "operator")
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
                RETURNING
                    id, title, status, owner, project,
                    estimate_hours, actual_hours, task,
                    display_order, created_at, updated_at
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
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "status": "updated",
        "ticket": ticket_row_to_dict(row),
    }


@app.delete("/api/serviceops/tickets/{ticket_id}")
def delete_serviceops_ticket(
    ticket_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    require_role(demo_role, "admin")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                """
                DELETE FROM serviceops_tickets
                WHERE id = :ticket_id
                RETURNING id, title
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
                action="delete",
                summary=f"Deleted ServiceOps ticket: {row['title']}",
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "status": "deleted",
        "ticket": {
            "id": row["id"],
            "title": row["title"],
        },
    }


@app.get("/api/projectops/projects")
def list_projectops_projects():
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                    id, title, status, owner,
                    budget_hours, actual_hours, linked_tickets,
                    scope, progress, start_date, end_date,
                    display_order, created_at, updated_at
                FROM projectops_projects
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


@app.get("/api/projectops/projects/{project_id}")
def get_projectops_project(project_id: int):
    db = require_db()

    with db.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    id, title, status, owner,
                    budget_hours, actual_hours, linked_tickets,
                    scope, progress, start_date, end_date,
                    display_order, created_at, updated_at
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
):
    require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM projectops_projects")
        ).scalar_one()

        row = conn.execute(
            text(
                """
                INSERT INTO projectops_projects
                    (title, status, owner, budget_hours, actual_hours,
                     linked_tickets, scope, progress, start_date, end_date, display_order)
                VALUES
                    (:title, :status, :owner, :budget_hours, :actual_hours,
                     :linked_tickets, :scope, :progress, :start_date, :end_date, :display_order)
                RETURNING
                    id, title, status, owner,
                    budget_hours, actual_hours, linked_tickets,
                    scope, progress, start_date, end_date,
                    display_order, created_at, updated_at
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
):
    require_role(demo_role, "operator")
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
                RETURNING
                    id, title, status, owner,
                    budget_hours, actual_hours, linked_tickets,
                    scope, progress, start_date, end_date,
                    display_order, created_at, updated_at
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
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "status": "updated",
        "project": project_row_to_dict(row),
    }


@app.delete("/api/projectops/projects/{project_id}")
def delete_projectops_project(
    project_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    require_role(demo_role, "admin")
    db = require_db()

    with db.begin() as conn:
        row = conn.execute(
            text(
                """
                DELETE FROM projectops_projects
                WHERE id = :project_id
                RETURNING id, title
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
                action="delete",
                summary=f"Deleted ProjectOps project: {row['title']}",
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "status": "deleted",
        "project": {
            "id": row["id"],
            "title": row["title"],
        },
    }


@app.get("/api/soc/incidents")
def list_soc_incidents():
    db = require_db()

    with db.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                    id, title, severity, source_ip, target,
                    duplicate_count, analysis_type, mitre,
                    display_order, created_at, updated_at
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
                """
                SELECT
                    id, title, severity, source_ip, target,
                    duplicate_count, analysis_type, mitre,
                    display_order, created_at, updated_at
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
):
    require_role(demo_role, "operator")
    db = require_db()

    with db.begin() as conn:
        max_order = conn.execute(
            text("SELECT COALESCE(MAX(display_order), 0) FROM soc_incidents")
        ).scalar_one()

        row = conn.execute(
            text(
                """
                INSERT INTO soc_incidents
                    (title, severity, source_ip, target, duplicate_count,
                     analysis_type, mitre, display_order)
                VALUES
                    (:title, :severity, :source_ip, :target, :duplicate_count,
                     :analysis_type, :mitre, :display_order)
                RETURNING
                    id, title, severity, source_ip, target,
                    duplicate_count, analysis_type, mitre,
                    display_order, created_at, updated_at
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
):
    require_role(demo_role, "operator")
    db = require_db()
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    allowed = {
        "title",
        "severity",
        "source_ip",
        "target",
        "duplicate_count",
        "analysis_type",
        "mitre",
    }

    set_clauses = []
    params = {"incident_id": incident_id}

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
                UPDATE soc_incidents
                SET {set_sql}
                WHERE id = :incident_id
                RETURNING
                    id, title, severity, source_ip, target,
                    duplicate_count, analysis_type, mitre,
                    display_order, created_at, updated_at
                """
            ),
            params,
        ).mappings().first()

        if row is not None:
            write_audit_log(
                conn,
                module="soc",
                entity_type="incident",
                entity_id=row["id"],
                action="update",
                summary=f"Updated SOC incident: {row['title']}",
            )

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "status": "updated",
        "incident": incident_row_to_dict(row),
    }


@app.delete("/api/soc/incidents/{incident_id}")
def delete_soc_incident(
    incident_id: int,
    demo_role: str = Header(default="admin", alias="X-Demo-Role"),
):
    require_role(demo_role, "admin")
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
