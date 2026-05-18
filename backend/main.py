from fastapi import FastAPI
from datetime import datetime, timezone
import socket

app = FastAPI(
    title="ENYRAX Cloud API",
    version="0.2.0",
)

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
        "status": "static-demo",
        "description": "Security alerts, incident timeline and AI-assisted investigation demo.",
    },
    {
        "key": "serviceops",
        "name": "ServiceOps",
        "route": "/serviceops/",
        "status": "static-demo",
        "description": "Infra work orders, labor time, supervisor view and operation workflow.",
    },
    {
        "key": "projectops",
        "name": "ProjectOps",
        "route": "/projectops/",
        "status": "static-demo",
        "description": "Project timeline, worklog cost mapping and overrun risk view.",
    },
    {
        "key": "status",
        "name": "Server Status",
        "route": "/status/",
        "status": "api-connected",
        "description": "Cloud host, Nginx, HTTPS, API health and deployment checkpoint.",
    },
]


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "enyrax-api",
        "host": socket.gethostname(),
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "modules": {
            "portal": "online",
            "soc": "static-demo",
            "serviceops": "static-demo",
            "projectops": "static-demo",
            "status": "api-connected",
        },
    }


@app.get("/api/modules")
def modules():
    return {
        "status": "ok",
        "service": "enyrax-api",
        "host": socket.gethostname(),
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "modules": MODULES,
    }


@app.get("/api/soc/summary")
def soc_summary():
    return {
        "status": "ok",
        "service": "enyrax-soc-demo",
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "open_incidents": 12,
            "critical": 3,
            "high": 5,
            "medium": 4,
            "correlated_alerts": 428,
            "ai_confidence": 91,
            "mitre_coverage": 7,
        },
        "hot_incidents": [
            {
                "title": "Suspicious SSH Brute Force Pattern",
                "severity": "critical",
                "source_ip": "185.220.101.42",
                "target": "web-portal-01",
                "duplicate_count": 36,
                "analysis_type": "failed_login_cluster",
                "mitre": "T1110 Brute Force",
            },
            {
                "title": "Privilege Escalation After Successful Login",
                "severity": "high",
                "source_ip": "203.0.113.77",
                "target": "infra-node-03",
                "duplicate_count": 8,
                "analysis_type": "attack_story",
                "mitre": "T1068 Privilege Escalation",
            },
            {
                "title": "Wazuh Agent Disconnected and Reconnected",
                "severity": "medium",
                "source_ip": "10.20.5.17",
                "target": "endpoint-07",
                "duplicate_count": 2,
                "analysis_type": "agent_state_change",
                "mitre": "Defense Evasion Review",
            },
        ],
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


@app.get("/api/serviceops/summary")
def serviceops_summary():
    return {
        "status": "ok",
        "service": "enyrax-serviceops-demo",
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "today_tickets": 18,
            "active": 6,
            "pending": 9,
            "done": 3,
            "team_hours": 42.5,
            "project_linked": 11,
            "risk_items": 3,
        },
        "work_queue": [
            {
                "title": "VM Request · ERP Test Environment",
                "status": "in_progress",
                "owner": "atn",
                "project": "ERP Upgrade",
                "estimate_hours": 3.5,
                "actual_hours": 2.0,
                "task": "Provision VM, assign network, prepare OS baseline and handover checklist.",
            },
            {
                "title": "Firewall Policy Review · Vendor VPN",
                "status": "pending_approval",
                "owner": "Infra Team",
                "project": "Vendor Access Control",
                "estimate_hours": 1.5,
                "actual_hours": 0.5,
                "task": "Review source/destination, service ports, business owner and expiry date.",
            },
            {
                "title": "Storage Capacity Alert · Backup Volume",
                "status": "risk",
                "owner": "Storage Admin",
                "project": "Backup Improvement",
                "estimate_hours": 2.0,
                "actual_hours": 4.0,
                "task": "Analyze growth trend, clean expired backup and report expansion risk.",
            },
            {
                "title": "Nginx Portal Deployment · ENYRAX Demo",
                "status": "done",
                "owner": "atn",
                "project": "ENYRAX Cloud Demo",
                "estimate_hours": 1.0,
                "actual_hours": 1.0,
                "task": "Deploy portal, verify firewall, confirm public route and status page.",
            },
        ],
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

@app.get("/api/projectops/summary")
def projectops_summary():
    return {
        "status": "ok",
        "service": "enyrax-projectops-demo",
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "active_projects": 7,
            "on_track": 3,
            "watch": 2,
            "risk": 2,
            "budget_used": 68,
            "serviceops_hours": 126,
            "overrun_risk": 2,
        },
        "projects": [
            {
                "title": "ERP Test Environment Upgrade",
                "status": "ontrack",
                "owner": "IT / Infra",
                "budget_hours": 120,
                "actual_hours": 76,
                "linked_tickets": 11,
                "scope": "VM build, network policy, backup baseline, UAT support.",
                "progress": 63,
            },
            {
                "title": "Vendor VPN Access Control Review",
                "status": "watch",
                "owner": "Security / Infra",
                "budget_hours": 80,
                "actual_hours": 61,
                "linked_tickets": 7,
                "scope": "Firewall rule cleanup, expiry date, owner mapping and audit evidence.",
                "progress": 76,
            },
            {
                "title": "Backup Storage Improvement",
                "status": "risk",
                "owner": "Infra / Storage",
                "budget_hours": 100,
                "actual_hours": 94,
                "linked_tickets": 9,
                "scope": "Capacity review, retention cleanup, expansion planning and recovery test.",
                "progress": 94,
            },
        ],
        "gantt": [
            {"phase": "Requirement", "offset": 0, "width": 100, "status": "Done"},
            {"phase": "Infra Build", "offset": 10, "width": 78, "status": "78%"},
            {"phase": "Security Review", "offset": 34, "width": 42, "status": "42%"},
            {"phase": "UAT Support", "offset": 62, "width": 24, "status": "24%"},
            {"phase": "Go-Live", "offset": 82, "width": 8, "status": "Ready"},
        ],
        "cost": {
            "planned_budget": "300h",
            "actual_worklog": "231h",
            "forecast": "346h",
            "risk_signal": "+15%",
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
