#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/enyrax-portal"
BACKUP_DIR="/var/backups/enyrax"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
SYSTEMD_SERVICE="/etc/systemd/system/enyrax-api.service"
ENV_FILES=(
  "${APP_DIR}/backend/.env"
  "${APP_DIR}/.env"
)

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

timestamp="$(date -u +%Y%m%d-%H%M)"
staging_dir="/tmp/enyrax-backup-${timestamp}"
archive_path="${BACKUP_DIR}/enyrax-backup-${timestamp}.tar.gz"

load_env_file() {
  local env_file="$1"

  if [ -r "$env_file" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
}

detect_db_source() {
  if [ -n "${DATABASE_URL:-}" ]; then
    echo "DATABASE_URL"
  elif [ -n "${DB_NAME:-}" ]; then
    echo "DB_NAME/DB_USER/DB_HOST/DB_PORT"
  else
    echo "not configured"
  fi
}

print_sources() {
  echo "== ENYRAX Tokyo Portal Backup Dry Run =="
  echo "Would back up:"
  echo "  Project directory: ${APP_DIR}"
  echo "  PostgreSQL dump: $(detect_db_source)"
  echo "  Nginx sites-available: ${NGINX_AVAILABLE}"
  echo "  Nginx sites-enabled: ${NGINX_ENABLED}"
  echo "  systemd service: ${SYSTEMD_SERVICE}"

  for env_file in "${ENV_FILES[@]}"; do
    if [ -e "$env_file" ]; then
      echo "  env file: ${env_file}"
    fi
  done

  echo
  echo "Would write archive to: ${archive_path}"
  echo "Would delete local archives older than 7 days from: ${BACKUP_DIR}"
}

run_pg_dump() {
  local output_file="$1"

  if [ -n "${DATABASE_URL:-}" ]; then
    pg_dump "$DATABASE_URL" > "$output_file"
    return
  fi

  if [ -z "${DB_NAME:-}" ]; then
    echo "ERROR: Database configuration missing. Set DATABASE_URL or DB_NAME." >&2
    exit 1
  fi

  local pg_args=()
  if [ -n "${DB_USER:-}" ]; then
    pg_args+=("-U" "$DB_USER")
  fi
  if [ -n "${DB_HOST:-}" ]; then
    pg_args+=("-h" "$DB_HOST")
  fi
  if [ -n "${DB_PORT:-}" ]; then
    pg_args+=("-p" "$DB_PORT")
  fi

  pg_dump "${pg_args[@]}" -d "$DB_NAME" > "$output_file"
}

copy_if_exists() {
  local source_path="$1"
  local target_path="$2"

  if [ -e "$source_path" ]; then
    mkdir -p "$(dirname "$target_path")"
    cp -a "$source_path" "$target_path"
  fi
}

cleanup() {
  if [ -n "${staging_dir:-}" ] && [ -d "$staging_dir" ]; then
    rm -rf "$staging_dir"
  fi
}

for env_file in "${ENV_FILES[@]}"; do
  load_env_file "$env_file"
done

if [ "$DRY_RUN" -eq 1 ]; then
  print_sources
  exit 0
fi

trap cleanup EXIT

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

rm -rf "$staging_dir"
mkdir -p "$staging_dir"
chmod 700 "$staging_dir"

mkdir -p "${staging_dir}/project" "${staging_dir}/postgres" "${staging_dir}/nginx" "${staging_dir}/systemd" "${staging_dir}/env"

cp -a "$APP_DIR" "${staging_dir}/project/enyrax-portal"

run_pg_dump "${staging_dir}/postgres/enyrax-postgres.sql"

copy_if_exists "$NGINX_AVAILABLE" "${staging_dir}/nginx/sites-available"
copy_if_exists "$NGINX_ENABLED" "${staging_dir}/nginx/sites-enabled"
copy_if_exists "$SYSTEMD_SERVICE" "${staging_dir}/systemd/enyrax-api.service"

for env_file in "${ENV_FILES[@]}"; do
  if [ -e "$env_file" ]; then
    env_target="${staging_dir}/env/${env_file#${APP_DIR}/}"
    copy_if_exists "$env_file" "$env_target"
  fi
done

tar -C "$staging_dir" -czf "$archive_path" .
chmod 600 "$archive_path"

find "$BACKUP_DIR" -name "enyrax-backup-*.tar.gz" -mtime +7 -delete

backup_size="$(du -h "$archive_path" | awk '{print $1}')"

echo "Backup completed."
echo "Path: ${archive_path}"
echo "Size: ${backup_size}"
