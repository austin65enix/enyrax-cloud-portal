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

tickets = [
    {
        "title": "VM Request · ERP Test Environment",
        "status": "in_progress",
        "owner": "atn",
        "project": "ERP Upgrade",
        "estimate_hours": 3.5,
        "actual_hours": 2.0,
        "task": "Provision VM, assign network, prepare OS baseline and handover checklist.",
        "display_order": 1,
    },
    {
        "title": "Firewall Policy Review · Vendor VPN",
        "status": "pending_approval",
        "owner": "Infra Team",
        "project": "Vendor Access Control",
        "estimate_hours": 1.5,
        "actual_hours": 0.5,
        "task": "Review source/destination, service ports, business owner and expiry date.",
        "display_order": 2,
    },
    {
        "title": "Storage Capacity Alert · Backup Volume",
        "status": "risk",
        "owner": "Storage Admin",
        "project": "Backup Improvement",
        "estimate_hours": 2.0,
        "actual_hours": 4.0,
        "task": "Analyze growth trend, clean expired backup and report expansion risk.",
        "display_order": 3,
    },
    {
        "title": "Nginx Portal Deployment · ENYRAX Demo",
        "status": "done",
        "owner": "atn",
        "project": "ENYRAX Cloud Demo",
        "estimate_hours": 1.0,
        "actual_hours": 1.0,
        "task": "Deploy portal, verify firewall, confirm public route and status page.",
        "display_order": 4,
    },
]

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS serviceops_tickets (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            status VARCHAR(50) NOT NULL,
            owner VARCHAR(100) NOT NULL,
            project VARCHAR(120) NOT NULL,
            estimate_hours NUMERIC(6,2) NOT NULL DEFAULT 0,
            actual_hours NUMERIC(6,2) NOT NULL DEFAULT 0,
            task TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    conn.execute(text("TRUNCATE TABLE serviceops_tickets RESTART IDENTITY"))

    for ticket in tickets:
        conn.execute(
            text("""
                INSERT INTO serviceops_tickets
                    (title, status, owner, project, estimate_hours, actual_hours, task, display_order)
                VALUES
                    (:title, :status, :owner, :project, :estimate_hours, :actual_hours, :task, :display_order)
            """),
            ticket,
        )

print("serviceops_tickets initialized")
