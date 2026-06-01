#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/enyrax-portal"
ENV_FILE="${APP_DIR}/backend/.env"
BACKUP_DIR="/home/atn/backups/postgres"
TS="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set in $ENV_FILE" >&2
  exit 1
fi

tmp_file="$BACKUP_DIR/enyrax_portal_${TS}.sql.tmp"
final_file="$BACKUP_DIR/enyrax_portal_${TS}.sql"

echo "[INFO] PostgreSQL backup started: $(date)"
echo "[INFO] Output: $final_file"

pg_dump "$DATABASE_URL" > "$tmp_file"

backup_size_bytes="$(stat -c %s "$tmp_file")"

if [ "$backup_size_bytes" -le 0 ]; then
  rm -f "$tmp_file"
  echo "ERROR: PostgreSQL backup is empty. Abort." >&2
  exit 1
fi

mv "$tmp_file" "$final_file"

echo "[INFO] PostgreSQL backup completed."
echo "[INFO] Size: $(du -h "$final_file" | awk '{print $1}')"
echo "[INFO] File: $final_file"
