#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/enyrax}"
RCLONE_REMOTE="${RCLONE_REMOTE:-enyrax-r2}"
R2_BUCKET="${R2_BUCKET:-enyrax-backups}"
R2_PREFIX="${R2_PREFIX:-tokyo}"

usage() {
  echo "Usage: $0 [--dry-run]"
}

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
elif [ $# -gt 0 ]; then
  usage
  exit 2
fi

if ! command -v rclone >/dev/null 2>&1; then
  echo "ERROR: rclone is not installed. Install rclone and configure remote '${RCLONE_REMOTE}'." >&2
  exit 1
fi

latest_backup=""
latest_mtime=0

shopt -s nullglob
for backup_file in "${BACKUP_DIR}"/enyrax-backup-*.tar.gz; do
  backup_mtime="$(stat -c %Y "$backup_file")"
  if [ "$backup_mtime" -gt "$latest_mtime" ]; then
    latest_mtime="$backup_mtime"
    latest_backup="$backup_file"
  fi
done
shopt -u nullglob

if [ -z "$latest_backup" ]; then
  echo "ERROR: No backup files found in ${BACKUP_DIR} matching enyrax-backup-*.tar.gz." >&2
  exit 1
fi

backup_name="$(basename "$latest_backup")"
backup_size="$(du -h "$latest_backup" | awk '{print $1}')"
r2_prefix="${R2_PREFIX#/}"
r2_prefix="${r2_prefix%/}"
destination="${RCLONE_REMOTE}:${R2_BUCKET}/"
if [ -n "$r2_prefix" ]; then
  destination="${destination}${r2_prefix}/"
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "Cloudflare R2 upload dry run."
  echo "Would upload file: ${backup_name}"
  echo "File size: ${backup_size}"
  echo "Destination: ${destination}"
  exit 0
fi

rclone copyto "$latest_backup" "${destination}${backup_name}"

echo "Cloudflare R2 upload completed."
echo "Uploaded file: ${backup_name}"
echo "File size: ${backup_size}"
echo "Destination: ${destination}"
