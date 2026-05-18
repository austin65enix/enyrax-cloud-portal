#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/enyrax-portal"
BACKUP_DIR="${APP_DIR}/backups"
ENV_FILE="${APP_DIR}/backend/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: Missing env file: $ENV_FILE"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set"
  exit 1
fi

if [ $# -ne 1 ]; then
  echo "Usage:"
  echo "  ./scripts/restore_db.sh backups/<backup-file>.sql.gz"
  echo
  echo "Available backups:"
  ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || true
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "== ENYRAX DB Restore =="
echo "Backup: $BACKUP_FILE"
echo
echo "WARNING: This will restore data into the configured database."
echo "Press Ctrl+C within 5 seconds to cancel..."
sleep 5

if [[ "$BACKUP_FILE" == *.gz ]]; then
  gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"
else
  psql "$DATABASE_URL" < "$BACKUP_FILE"
fi

echo
echo "Restore completed."
