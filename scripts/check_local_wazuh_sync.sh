#!/usr/bin/env bash
set -euo pipefail

LOCAL_SYNC_DIR="${LOCAL_SYNC_DIR:-${HOME}/enyrax-local-sync}"
AGENT_PATH="${AGENT_PATH:-${LOCAL_SYNC_DIR}/local_sync_agent.py}"
ENV_FILE="${ENV_FILE:-${LOCAL_SYNC_DIR}/.env}"
ALERTS_PATH="/var/ossec/logs/alerts/alerts.json"
WAZUH_CONTAINERS=(
  "single-node-wazuh.manager"
  "single-node-wazuh.indexer"
  "single-node-wazuh.dashboard"
)

ok() {
  echo "OK: $*"
}

warn() {
  echo "WARN: $*"
}

fail() {
  echo "ERROR: $*" >&2
}

echo "== ENYRAX Local Wazuh Sync Check =="

if [ -d "$LOCAL_SYNC_DIR" ]; then
  ok "local sync directory exists: ${LOCAL_SYNC_DIR}"
else
  fail "local sync directory missing: ${LOCAL_SYNC_DIR}"
  exit 1
fi

if [ -f "$AGENT_PATH" ]; then
  ok "local_sync_agent.py exists: ${AGENT_PATH}"
else
  fail "local_sync_agent.py missing: ${AGENT_PATH}"
  exit 1
fi

if [ -f "$ENV_FILE" ]; then
  ok ".env exists: ${ENV_FILE}"
else
  fail ".env missing: ${ENV_FILE}"
  exit 1
fi

if command -v docker >/dev/null 2>&1; then
  ok "docker command exists"
else
  fail "docker command not found"
  exit 1
fi

echo
echo "== Wazuh containers =="
for container in "${WAZUH_CONTAINERS[@]}"; do
  if docker ps -a --format '{{.Names}}' | grep -Fx "$container" >/dev/null 2>&1; then
    status="$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || true)"
    health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container" 2>/dev/null || true)"
    ok "${container} exists; status=${status:-unknown}; health=${health:-unknown}"
  else
    warn "${container} missing"
  fi
done

echo
echo "== Wazuh alerts.json =="
if docker ps -a --format '{{.Names}}' | grep -Fx "single-node-wazuh.manager" >/dev/null 2>&1; then
  if docker exec single-node-wazuh.manager sh -lc "test -f '${ALERTS_PATH}'" >/dev/null 2>&1; then
    alerts_size="$(docker exec single-node-wazuh.manager sh -lc "wc -c < '${ALERTS_PATH}'" 2>/dev/null | tr -d '[:space:]')"
    ok "manager ${ALERTS_PATH} exists"
    echo "alerts.json size: ${alerts_size:-unknown} bytes"
  else
    warn "manager ${ALERTS_PATH} missing"
  fi
else
  warn "single-node-wazuh.manager missing; skipped docker exec alerts.json check"
fi

echo
echo "== Heartbeat test =="
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [ -n "${ENYRAX_SYNC_SOURCE:-}" ]; then
  echo "sync source: ${ENYRAX_SYNC_SOURCE}"
fi
if [ -n "${ENYRAX_SYNC_URL:-}" ]; then
  echo "sync url: ${ENYRAX_SYNC_URL}"
fi
if [ -n "${ENYRAX_SYNC_KEY:-}" ]; then
  echo "sync key: configured"
else
  warn "sync key: not configured"
fi

cd "$LOCAL_SYNC_DIR"
python3 "$AGENT_PATH" --type heartbeat
