#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

APP_DIR="/var/www/enyrax-portal"
ENV_FILE="${APP_DIR}/backend/.env"
BACKUP_DIR="/home/atn/backups/postgres"
DRY_RUN="${DRY_RUN:-0}"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[ERROR] Required command not found: $1" >&2
    exit 1
  }
}

for command_name in pg_dump date mkdir mv stat rm; do
  require_command "$command_name"
done

TS="$(date +%Y%m%d_%H%M%S)"

if [ ! -f "$ENV_FILE" ]; then
  echo "[ERROR] Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
  echo "[ERROR] DATABASE_URL is required but will not be printed." >&2
  exit 1
fi

tmp_file="$BACKUP_DIR/enyrax_portal_${TS}.sql.tmp"
final_file="$BACKUP_DIR/enyrax_portal_${TS}.sql"

if [ "$DRY_RUN" = "1" ]; then
  echo "[DRY-RUN] DATABASE_URL is set and will not be printed."
  echo "[DRY-RUN] Would create PostgreSQL backup: $final_file"
  exit 0
fi

mkdir -p "$BACKUP_DIR"
trap 'rm -f "$tmp_file"' EXIT

echo "[INFO] PostgreSQL backup started: $(date)"
echo "[INFO] Output: $final_file"

pg_dump "$DATABASE_URL" > "$tmp_file"

if [ ! -s "$tmp_file" ]; then
  echo "[ERROR] PostgreSQL backup file missing or empty. Abort." >&2
  exit 1
fi

mv "$tmp_file" "$final_file"
trap - EXIT

echo "[INFO] PostgreSQL backup completed."
echo "[INFO] Size bytes: $(stat -c %s "$final_file")"
echo "[INFO] File: $final_file"
