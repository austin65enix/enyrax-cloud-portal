#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/enyrax-portal"
BACKUP_DIR="${APP_DIR}/backups"
ENV_FILE="${APP_DIR}/backend/.env"

mkdir -p "$BACKUP_DIR"

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

TS="$(date -u +%Y%m%d_%H%M%S)"
OUT="${BACKUP_DIR}/enyrax_portal_${TS}.sql"

echo "== ENYRAX DB Backup =="
echo "Output: $OUT"

pg_dump "$DATABASE_URL" > "$OUT"

gzip "$OUT"

echo "Backup completed:"
echo "${OUT}.gz"

echo
echo "Latest backups:"
ls -lh "$BACKUP_DIR" | tail -n 10
