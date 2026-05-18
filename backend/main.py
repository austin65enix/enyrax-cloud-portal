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
