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
            CREATE TABLE IF NOT EXISTS local_sync_events (
                id SERIAL PRIMARY KEY,
                source VARCHAR(120) NOT NULL,
                system VARCHAR(80) NOT NULL,
                event_type VARCHAR(120) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'ok',
                message TEXT,
                payload JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_local_sync_events_created_at
            ON local_sync_events (created_at)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_local_sync_events_source
            ON local_sync_events (source)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_local_sync_events_system
            ON local_sync_events (system)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_local_sync_events_event_type
            ON local_sync_events (event_type)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_local_sync_events_status
            ON local_sync_events (status)
            """
        )
    )
    count = conn.execute(text("SELECT COUNT(*) FROM local_sync_events")).scalar_one()

print(f"local_sync_events table ready; count={count}")
