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
            CREATE TABLE IF NOT EXISTS sync_source_metadata (
                id SERIAL PRIMARY KEY,
                source VARCHAR(160) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                note TEXT NULL,
                archived_by VARCHAR(160) NULL,
                archived_at TIMESTAMPTZ NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )
    count = conn.execute(text("SELECT COUNT(*) FROM sync_source_metadata")).scalar_one()

print(f"sync_source_metadata table ready; count={count}")
