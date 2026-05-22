from pathlib import Path
import os

from sqlalchemy import create_engine, text


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

with engine.begin() as conn:
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'open'
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS handled_by VARCHAR(160)
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS handled_at TIMESTAMPTZ
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS resolution_note TEXT
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_soc_incidents_status
            ON soc_incidents (status)
            """
        )
    )

print("soc_incidents lifecycle columns initialized")
