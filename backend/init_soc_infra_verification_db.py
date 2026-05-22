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
            ADD COLUMN IF NOT EXISTS infra_verified_by VARCHAR(160)
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS infra_verified_at TIMESTAMPTZ
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS infra_verification_note TEXT
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER TABLE soc_incidents
            ADD COLUMN IF NOT EXISTS infra_verification_result VARCHAR(50)
            """
        )
    )

print("soc_incidents infra verification columns initialized")
