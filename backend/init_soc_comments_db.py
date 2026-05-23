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
            CREATE TABLE IF NOT EXISTS soc_incident_comments (
              id SERIAL PRIMARY KEY,
              incident_id INTEGER NOT NULL,
              actor VARCHAR(160) NOT NULL,
              role VARCHAR(50) NOT NULL,
              comment TEXT NOT NULL,
              comment_type VARCHAR(50) NOT NULL DEFAULT 'note',
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_soc_incident_comments_incident_id
            ON soc_incident_comments (incident_id)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_soc_incident_comments_created_at
            ON soc_incident_comments (created_at)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_soc_incident_comments_actor
            ON soc_incident_comments (actor)
            """
        )
    )

print("soc_incident_comments table initialized")
