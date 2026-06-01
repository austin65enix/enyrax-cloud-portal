#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/home/atn/backups/postgres"
RCLONE_REMOTE="enyrax-soc-backup"
R2_BUCKET="enyrax-soc-backup"
R2_PREFIX="enyrax-soc-tokyo/postgres"

latest_backup="$(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'enyrax_portal_*.sql' -printf '%T@ %p\n' | sort -nr | awk 'NR==1 {print $2}')"

if [ -z "${latest_backup:-}" ]; then
  echo "ERROR: no postgres backup found in $BACKUP_DIR" >&2
  exit 1
fi

backup_name="$(basename "$latest_backup")"
backup_size_bytes="$(stat -c %s "$latest_backup")"

if [ "$backup_size_bytes" -le 0 ]; then
  echo "ERROR: latest postgres backup is empty: $latest_backup" >&2
  exit 1
fi

destination="${RCLONE_REMOTE}:${R2_BUCKET}/${R2_PREFIX}/"

echo "[INFO] Latest backup: $latest_backup"
echo "[INFO] Backup size: $(du -h "$latest_backup" | awk '{print $1}')"
echo "[INFO] Destination: ${destination}"

rclone copyto "$latest_backup" "${destination}${backup_name}" -vv

echo "[INFO] Cloudflare R2 postgres upload completed."
