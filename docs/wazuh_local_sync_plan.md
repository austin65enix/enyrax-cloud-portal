# Wazuh Local Sync Recovery Plan

## 1. 目標

讓地端 Wazuh / Docker / Host / Agent 狀態定期回拋東京 Portal，讓 Sync Gateway 能判斷：

- healthy
- warning
- stale
- error
- unknown

## 2. 目前資料流

```text
Local Wazuh Lab
  -> local_sync_agent.py
  -> POST /api/sync/events
  -> Sync Gateway
  -> SOC Incident Candidate
  -> SOC Incident
  -> Infra Verify / Recovery Evidence
  -> ServiceOps Ticket
```

## 3. 地端 source

source name:

```text
local-wazuh-lab-01
```

systems:

- agent
- host
- docker
- wazuh

## 4. 建議回拋頻率

- heartbeat：每 5 分鐘
- host summary：每 15 分鐘
- docker status：每 15 分鐘
- wazuh alert summary：每 10 分鐘

## 5. stale 判斷

Portal 端目前依 heartbeat 與 latest event 判斷：

- heartbeat <= 10 min：healthy
- heartbeat > 10 min：warning
- heartbeat > 30 min：stale
- no heartbeat：unknown
- latest event error：error
- latest event warning：warning

## 6. Wazuh alerts.json 注意事項

Wazuh Docker 內 alerts.json 可能位於：

```text
/var/ossec/logs/alerts/alerts.json
```

但 host 上不一定存在：

```text
/var/ossec/logs/alerts/alerts.json
```

因此 local_sync_agent.py 應該支援：

- host path mode
- docker exec mode
- fallback warning if file missing

## 7. 現階段建議

短期：

- 用 cron 定期執行 local_sync_agent.py
- 先確保 heartbeat 不 stale
- 再補 wazuh summary

中期：

- 包成 systemd timer
- 加入 local log
- 加入 retry
- 加入 agent self-check

長期：

- agent installer
- sync key rotation
- multi-site source registration
- source-level dashboard

## 8. 地端 cron 安裝

地端主機先準備 local sync 目錄：

```bash
mkdir -p ~/enyrax-local-sync/logs
cd ~/enyrax-local-sync
```

確認 `local_sync_agent.py` 已放在：

```text
~/enyrax-local-sync/local_sync_agent.py
```

建立環境檔：

```bash
cat > ~/enyrax-local-sync/.env <<'EOF'
export ENYRAX_SYNC_URL=https://portal.soc-monitoring.dev/api/sync/events
export ENYRAX_SYNC_KEY=your-demo-sync-key
export ENYRAX_SYNC_SOURCE=local-wazuh-lab-01
EOF
chmod 600 ~/enyrax-local-sync/.env
```

安裝 cron：

```bash
/var/www/enyrax-portal/scripts/install_local_sync_cron.sh
```

cron 預期頻率：

- heartbeat：每 5 分鐘
- host：每 15 分鐘
- docker：每 15 分鐘
- wazuh：每 10 分鐘

## 9. 手動測試指令

地端測試：

```bash
cd ~/enyrax-local-sync

source .env

python3 local_sync_agent.py --type heartbeat
python3 local_sync_agent.py --type host
python3 local_sync_agent.py --type docker
python3 local_sync_agent.py --type wazuh
```

東京端驗證：

```bash
curl -s "https://portal.soc-monitoring.dev/api/sync/sources" \
  | jq '.sources[] | select(.source=="local-wazuh-lab-01")'

curl -s "https://portal.soc-monitoring.dev/api/sync/events?source=local-wazuh-lab-01&limit=5" | jq
```

## 10. 快速檢查

地端主機可執行：

```bash
/var/www/enyrax-portal/scripts/check_local_wazuh_sync.sh
```

檢查重點：

- local sync directory 是否存在
- local_sync_agent.py 是否存在
- `.env` 是否存在
- Docker 與 Wazuh containers 是否存在
- manager container 內 `/var/ossec/logs/alerts/alerts.json` 是否存在
- heartbeat 是否能成功回拋

## 11. Troubleshooting

如果 `echo $ENYRAX_SYNC_SOURCE` 正確，但 Python event source 仍 fallback 成 `atn-local-lab`，
請確認 `.env` 使用 `export`，因為 Python `os.environ` 只讀 exported environment variables。
