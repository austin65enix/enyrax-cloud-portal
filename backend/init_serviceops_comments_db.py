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
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS serviceops_ticket_comments (
              id SERIAL PRIMARY KEY,
              ticket_id INTEGER NOT NULL,
              actor VARCHAR(160),
              role VARCHAR(50),
              comment TEXT NOT NULL,
              comment_type VARCHAR(50) DEFAULT 'worklog',
              created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_serviceops_ticket_comments_ticket_id
            ON serviceops_ticket_comments (ticket_id)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_serviceops_ticket_comments_created_at
            ON serviceops_ticket_comments (created_at)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_serviceops_ticket_comments_comment_type
            ON serviceops_ticket_comments (comment_type)
            """
        )
    )

print("serviceops_ticket_comments table initialized")
