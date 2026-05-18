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

incidents = [
    {
        "title": "Suspicious SSH Brute Force Pattern",
        "severity": "critical",
        "source_ip": "185.220.101.42",
        "target": "web-portal-01",
        "duplicate_count": 36,
        "analysis_type": "failed_login_cluster",
        "mitre": "T1110 Brute Force",
        "display_order": 1,
    },
    {
        "title": "Privilege Escalation After Successful Login",
        "severity": "high",
        "source_ip": "203.0.113.77",
        "target": "infra-node-03",
        "duplicate_count": 8,
        "analysis_type": "attack_story",
        "mitre": "T1068 Privilege Escalation",
        "display_order": 2,
    },
    {
        "title": "Wazuh Agent Disconnected and Reconnected",
        "severity": "medium",
        "source_ip": "10.20.5.17",
        "target": "endpoint-07",
        "duplicate_count": 2,
        "analysis_type": "agent_state_change",
        "mitre": "Defense Evasion Review",
        "display_order": 3,
    },
]

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS soc_incidents (
            id SERIAL PRIMARY KEY,
            title VARCHAR(220) NOT NULL,
            severity VARCHAR(50) NOT NULL,
            source_ip VARCHAR(80) NOT NULL,
            target VARCHAR(120) NOT NULL,
            duplicate_count INTEGER NOT NULL DEFAULT 1,
            analysis_type VARCHAR(120) NOT NULL,
            mitre VARCHAR(160) NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    conn.execute(text("TRUNCATE TABLE soc_incidents RESTART IDENTITY"))

    for incident in incidents:
        conn.execute(
            text("""
                INSERT INTO soc_incidents
                    (title, severity, source_ip, target, duplicate_count, analysis_type, mitre, display_order)
                VALUES
                    (:title, :severity, :source_ip, :target, :duplicate_count, :analysis_type, :mitre, :display_order)
            """),
            incident,
        )

print("soc_incidents initialized")
