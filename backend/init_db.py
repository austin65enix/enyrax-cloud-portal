from sqlalchemy import create_engine, text
from pathlib import Path
import os


def load_env():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
      return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)

modules = [
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
        "key": "status",
        "name": "Server Status",
        "route": "/status/",
        "status": "api-connected",
        "description": "Cloud host, Nginx, HTTPS, API health and deployment checkpoint.",
    },
]

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS portal_modules (
            id SERIAL PRIMARY KEY,
            module_key VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(120) NOT NULL,
            route VARCHAR(120) NOT NULL,
            status VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    for idx, m in enumerate(modules, start=1):
        conn.execute(
            text("""
                INSERT INTO portal_modules
                    (module_key, name, route, status, description, display_order)
                VALUES
                    (:module_key, :name, :route, :status, :description, :display_order)
                ON CONFLICT (module_key)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    route = EXCLUDED.route,
                    status = EXCLUDED.status,
                    description = EXCLUDED.description,
                    display_order = EXCLUDED.display_order,
                    updated_at = NOW()
            """),
            {
                "module_key": m["key"],
                "name": m["name"],
                "route": m["route"],
                "status": m["status"],
                "description": m["description"],
                "display_order": idx,
            },
        )

print("portal_modules initialized")
