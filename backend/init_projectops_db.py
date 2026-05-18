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

projects = [
    {
        "title": "ERP Test Environment Upgrade",
        "status": "ontrack",
        "owner": "IT / Infra",
        "budget_hours": 120,
        "actual_hours": 76,
        "linked_tickets": 11,
        "scope": "VM build, network policy, backup baseline, UAT support.",
        "progress": 63,
        "display_order": 1,
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
        "display_order": 2,
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
        "display_order": 3,
    },
]

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS projectops_projects (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            status VARCHAR(50) NOT NULL,
            owner VARCHAR(120) NOT NULL,
            budget_hours NUMERIC(8,2) NOT NULL DEFAULT 0,
            actual_hours NUMERIC(8,2) NOT NULL DEFAULT 0,
            linked_tickets INTEGER NOT NULL DEFAULT 0,
            scope TEXT NOT NULL,
            progress INTEGER NOT NULL DEFAULT 0,
            display_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    conn.execute(text("TRUNCATE TABLE projectops_projects RESTART IDENTITY"))

    for project in projects:
        conn.execute(
            text("""
                INSERT INTO projectops_projects
                    (title, status, owner, budget_hours, actual_hours, linked_tickets, scope, progress, display_order)
                VALUES
                    (:title, :status, :owner, :budget_hours, :actual_hours, :linked_tickets, :scope, :progress, :display_order)
            """),
            project,
        )

print("projectops_projects initialized")
