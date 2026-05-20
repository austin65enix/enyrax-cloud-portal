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
    raise SystemExit("DATABASE_URL is not configured. Please check backend/.env")

engine = create_engine(DATABASE_URL)


CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(160) UNIQUE NOT NULL,
  display_name VARCHAR(120) NOT NULL,
  role VARCHAR(50) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_users_role
ON users(role);
"""


SEED_USERS_SQL = """
INSERT INTO users
  (email, display_name, role, is_active)
VALUES
  ('viewer@enyrax.local', 'Viewer Demo User', 'viewer', TRUE),
  ('operator@enyrax.local', 'Operator Demo User', 'operator', TRUE),
  ('supervisor@enyrax.local', 'Supervisor Demo User', 'supervisor', TRUE),
  ('admin@enyrax.local', 'Admin Demo User', 'admin', TRUE)
ON CONFLICT (email)
DO UPDATE SET
  display_name = EXCLUDED.display_name,
  role = EXCLUDED.role,
  is_active = EXCLUDED.is_active,
  updated_at = NOW();
"""


VERIFY_SQL = """
SELECT
  id,
  email,
  display_name,
  role,
  is_active,
  created_at,
  updated_at
FROM users
ORDER BY
  CASE role
    WHEN 'viewer' THEN 1
    WHEN 'operator' THEN 2
    WHEN 'supervisor' THEN 3
    WHEN 'admin' THEN 4
    ELSE 99
  END,
  id;
"""


def main() -> None:
    with engine.begin() as conn:
        conn.execute(text(CREATE_USERS_TABLE_SQL))
        conn.execute(text(CREATE_INDEX_SQL))
        conn.execute(text(SEED_USERS_SQL))

        rows = conn.execute(text(VERIFY_SQL)).mappings().all()

    print("Users table initialized.")
    print()
    print("Demo users:")
    for row in rows:
        print(
            f"- {row['id']:>2} | {row['email']:<24} | "
            f"{row['display_name']:<22} | {row['role']:<10} | "
            f"active={row['is_active']}"
        )


if __name__ == "__main__":
    main()
