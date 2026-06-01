#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

APP_DIR="/var/www/enyrax-portal"
BACKUP_DIR="/home/atn/backups/app"
DRY_RUN="${DRY_RUN:-0}"

RCLONE_REMOTE="enyrax-soc-backup"
R2_BUCKET="enyrax-soc-backup"
R2_PREFIX="enyrax-soc-tokyo/app"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[ERROR] Required command not found: $1" >&2
    exit 1
  }
}

for command_name in tar rclone date mkdir basename stat grep; do
  require_command "$command_name"
done

TS="$(date +%Y%m%d_%H%M%S)"
backup_file="$BACKUP_DIR/enyrax_portal_app_${TS}.tar.gz"
destination="${RCLONE_REMOTE}:${R2_BUCKET}/${R2_PREFIX}/$(basename "$backup_file")"

if [ "$DRY_RUN" = "1" ]; then
  echo "[DRY-RUN] Would create app backup: $backup_file"
  echo "[DRY-RUN] Would upload app backup to: $destination"
  exit 0
fi

mkdir -p "$BACKUP_DIR"

tar \
  --exclude=".env" \
  --exclude="./.env" \
  --exclude="backend/.env" \
  --exclude="./backend/.env" \
  --exclude="backend/venv" \
  --exclude="backend/venv/" \
  --exclude="./backend/venv" \
  --exclude="./backend/venv/" \
  --exclude=".venv" \
  --exclude=".venv/" \
  --exclude="venv" \
  --exclude="venv/" \
  --exclude=".git" \
  --exclude=".git/" \
  --exclude="backups" \
  --exclude="backups/" \
  --exclude="__pycache__" \
  --exclude="*/__pycache__" \
  --exclude="*.pyc" \
  --exclude="*.pyo" \
  --exclude="*.bak" \
  --exclude="*.before-*" \
  --exclude="*.log" \
  --exclude="/tmp" \
  --exclude="tmp" \
  --exclude="data/agentops/snapshots/retention_report.json" \
  -czf "$backup_file" \
  -C "$APP_DIR" \
  .

if [ ! -s "$backup_file" ]; then
  echo "[ERROR] Backup file missing or empty: $backup_file" >&2
  exit 1
fi

if ! tar -tzf "$backup_file" >/dev/null; then
  echo "[ERROR] Backup archive listing failed." >&2
  exit 1
fi

if tar -tzf "$backup_file" |
  grep -E '(^|/)(\.env|backend/\.env|\.git/|backend/venv/|\.venv/|venv/|__pycache__/)' >/dev/null; then
  echo "[ERROR] Backup archive contains excluded sensitive/local files." >&2
  exit 1
fi

echo "[INFO] App backup: $backup_file"
echo "[INFO] Size bytes: $(stat -c %s "$backup_file")"
echo "[INFO] Destination: $destination"

rclone copyto "$backup_file" "$destination"

echo "[INFO] App backup uploaded to R2: $(basename "$backup_file") -> $destination"
