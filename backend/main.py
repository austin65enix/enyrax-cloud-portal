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
