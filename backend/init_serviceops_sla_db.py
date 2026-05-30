from pathlib import Path
import os

from sqlalchemy import create_engine, text


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


load_env()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE serviceops_tickets
            ADD COLUMN IF NOT EXISTS due_at TIMESTAMPTZ NULL,
            ADD COLUMN IF NOT EXISTS sla_level VARCHAR(50) DEFAULT 'normal',
            ADD COLUMN IF NOT EXISTS blocked_reason TEXT NULL
    """))

    conn.execute(text("""
        UPDATE serviceops_tickets
        SET sla_level = 'normal'
        WHERE sla_level IS NULL
    """))

    conn.execute(text("""
        ALTER TABLE serviceops_tickets
            ALTER COLUMN sla_level SET DEFAULT 'normal'
    """))

print("serviceops_tickets SLA columns migrated")
