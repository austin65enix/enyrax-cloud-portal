#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/enyrax-portal"
BACKUP_DIR="/home/atn/backups/app"
TS="$(date +%Y%m%d_%H%M%S)"

RCLONE_REMOTE="enyrax-soc-backup"
R2_BUCKET="enyrax-soc-backup"
R2_PREFIX="enyrax-soc-tokyo/app"

mkdir -p "$BACKUP_DIR"

backup_file="$BACKUP_DIR/enyrax_portal_app_${TS}.tar.gz"

tar \
  --exclude="$APP_DIR/.git" \
  --exclude="$APP_DIR/__pycache__" \
  --exclude="$APP_DIR/backups" \
  -czf "$backup_file" \
  -C "$APP_DIR" .

backup_size_bytes="$(stat -c %s "$backup_file")"

if [ "$backup_size_bytes" -le 0 ]; then
  echo "ERROR: app backup is empty: $backup_file" >&2
  exit 1
fi

destination="${RCLONE_REMOTE}:${R2_BUCKET}/${R2_PREFIX}/"

echo "[INFO] App backup: $backup_file"
echo "[INFO] Size: $(du -h "$backup_file" | awk '{print $1}')"
echo "[INFO] Destination: $destination"

rclone copyto "$backup_file" "${destination}$(basename "$backup_file")" -vv

echo "[INFO] App backup uploaded to R2."
