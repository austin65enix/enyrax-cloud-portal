#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

BACKUP_DIR="/home/atn/backups/postgres"
RCLONE_REMOTE="enyrax-soc-backup"
R2_BUCKET="enyrax-soc-backup"
R2_PREFIX="enyrax-soc-tokyo/postgres"
DRY_RUN="${DRY_RUN:-0}"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[ERROR] Required command not found: $1" >&2
    exit 1
  }
}

for command_name in rclone find sort awk basename stat; do
  require_command "$command_name"
done

latest_backup="$(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'enyrax_portal_*.sql' -printf '%T@ %p\n' | sort -nr | awk 'NR==1 {print $2}')"

if [ -z "${latest_backup:-}" ]; then
  echo "[ERROR] No postgres backup found in $BACKUP_DIR" >&2
  exit 1
fi

backup_name="$(basename "$latest_backup")"

if [ ! -s "$latest_backup" ]; then
  echo "[ERROR] Latest postgres backup missing or empty: $latest_backup" >&2
  exit 1
fi

destination="${RCLONE_REMOTE}:${R2_BUCKET}/${R2_PREFIX}/${backup_name}"

echo "[INFO] Latest backup: $latest_backup"
echo "[INFO] Backup size bytes: $(stat -c %s "$latest_backup")"
echo "[INFO] Destination: $destination"

if [ "$DRY_RUN" = "1" ]; then
  echo "[DRY-RUN] Would upload latest PostgreSQL backup: $backup_name -> $destination"
  exit 0
fi

rclone copyto "$latest_backup" "$destination"

echo "[INFO] Cloudflare R2 postgres upload completed: $backup_name -> $destination"
