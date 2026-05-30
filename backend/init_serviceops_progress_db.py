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
            ADD COLUMN IF NOT EXISTS assignee VARCHAR(160),
            ADD COLUMN IF NOT EXISTS progress_status VARCHAR(50) NOT NULL DEFAULT 'not_started',
            ADD COLUMN IF NOT EXISTS progress_note TEXT,
            ADD COLUMN IF NOT EXISTS progress_updated_by VARCHAR(160),
            ADD COLUMN IF NOT EXISTS progress_updated_at TIMESTAMPTZ
    """))

    conn.execute(text("""
        UPDATE serviceops_tickets
        SET progress_status = 'not_started'
        WHERE progress_status IS NULL
    """))

    conn.execute(text("""
        ALTER TABLE serviceops_tickets
            ALTER COLUMN progress_status SET DEFAULT 'not_started',
            ALTER COLUMN progress_status SET NOT NULL
    """))

print("serviceops_tickets progress columns migrated")
