#!/usr/bin/env bash
set -euo pipefail

LOCAL_SYNC_DIR="${LOCAL_SYNC_DIR:-${HOME}/enyrax-local-sync}"
AGENT_PATH="${AGENT_PATH:-${LOCAL_SYNC_DIR}/local_sync_agent.py}"
ENV_FILE="${ENV_FILE:-${LOCAL_SYNC_DIR}/.env}"
LOG_FILE="${LOG_FILE:-${LOCAL_SYNC_DIR}/logs/local_sync_agent.log}"
LOCK_DIR="${LOCK_DIR:-${LOCAL_SYNC_DIR}/locks}"
MARKER_BEGIN="# BEGIN enyrax-local-sync"
MARKER_END="# END enyrax-local-sync"

print_env_example() {
  cat <<EOF
Create ${ENV_FILE} before installing cron:

export ENYRAX_SYNC_URL=https://portal.soc-monitoring.dev/api/sync/events
export ENYRAX_SYNC_KEY=your-demo-sync-key
export ENYRAX_SYNC_SOURCE=local-wazuh-lab-01
EOF
}

if [ ! -f "$AGENT_PATH" ]; then
  echo "ERROR: local_sync_agent.py not found: ${AGENT_PATH}" >&2
  echo "Place the local sync agent at ${AGENT_PATH}, then run this script again." >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: env file not found: ${ENV_FILE}" >&2
  print_env_example >&2
  exit 1
fi

mkdir -p "$(dirname "$LOG_FILE")" "$LOCK_DIR"

tmp_cron="$(mktemp)"
tmp_new="$(mktemp)"
cleanup() {
  rm -f "$tmp_cron" "$tmp_new"
}
trap cleanup EXIT

if crontab -l > "$tmp_cron" 2>/dev/null; then
  :
else
  : > "$tmp_cron"
fi

awk -v begin="$MARKER_BEGIN" -v end="$MARKER_END" '
  $0 == begin { skip = 1; next }
  $0 == end { skip = 0; next }
  skip == 0 { print }
' "$tmp_cron" > "$tmp_new"

cat >> "$tmp_new" <<EOF
${MARKER_BEGIN}
*/5 * * * * flock -n "${LOCK_DIR}/heartbeat.lock" bash -lc 'cd "${LOCAL_SYNC_DIR}" && set -a && source "${ENV_FILE}" && set +a && python3 "${AGENT_PATH}" --type heartbeat >> "${LOG_FILE}" 2>&1'
*/15 * * * * flock -n "${LOCK_DIR}/host.lock" bash -lc 'cd "${LOCAL_SYNC_DIR}" && set -a && source "${ENV_FILE}" && set +a && python3 "${AGENT_PATH}" --type host >> "${LOG_FILE}" 2>&1'
*/15 * * * * flock -n "${LOCK_DIR}/docker.lock" bash -lc 'cd "${LOCAL_SYNC_DIR}" && set -a && source "${ENV_FILE}" && set +a && python3 "${AGENT_PATH}" --type docker >> "${LOG_FILE}" 2>&1'
*/10 * * * * flock -n "${LOCK_DIR}/wazuh.lock" bash -lc 'cd "${LOCAL_SYNC_DIR}" && set -a && source "${ENV_FILE}" && set +a && python3 "${AGENT_PATH}" --type wazuh >> "${LOG_FILE}" 2>&1'
${MARKER_END}
EOF

crontab "$tmp_new"

echo "Installed enyrax local sync cron jobs."
echo "Relevant crontab lines:"
crontab -l | grep -n "enyrax-local-sync\|local_sync_agent.py\|ENYRAX_SYNC_SOURCE\|heartbeat\|wazuh" || true
