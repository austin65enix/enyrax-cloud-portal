# ENYRAX Local Sync Agent

This directory contains a small local push agent for sending host-side summary events to the ENYRAX Cloud Portal Local Sync Gateway. The design is outbound-only: the local machine sends summaries to Tokyo, and the Tokyo host does not initiate connections back to the local network.

## Environment Variables

- `ENYRAX_SYNC_URL`: sync endpoint URL. Default: `https://portal.soc-monitoring.dev/api/sync/events`
- `ENYRAX_SYNC_KEY`: shared sync key for the `X-Sync-Key` header. Default: `your-demo-sync-key`
- `ENYRAX_SYNC_SOURCE`: source name reported to the cloud. Default: `atn-local-lab`

## Manual Testing

Run all collectors once:

```bash
python3 agents/local_sync_agent.py --once
```

Run a single collector:

```bash
python3 agents/local_sync_agent.py --type heartbeat
python3 agents/local_sync_agent.py --type host
python3 agents/local_sync_agent.py --type docker
python3 agents/local_sync_agent.py --type wazuh
python3 agents/local_sync_agent.py --type all
```

Example with explicit endpoint and key:

```bash
ENYRAX_SYNC_URL="https://portal.soc-monitoring.dev/api/sync/events" \
ENYRAX_SYNC_KEY="replace-with-real-key" \
ENYRAX_SYNC_SOURCE="local-lab-01" \
python3 agents/local_sync_agent.py --once
```

Each POST prints the HTTP status and response body. The sync key is never printed by the agent.

## Cron Example

Run all collectors every five minutes:

```cron
*/5 * * * * ENYRAX_SYNC_KEY=replace-with-real-key ENYRAX_SYNC_SOURCE=local-lab-01 /usr/bin/python3 /var/www/enyrax-portal/agents/local_sync_agent.py --once >> /var/log/enyrax-local-sync.log 2>&1
```

Run heartbeat more frequently:

```cron
* * * * * ENYRAX_SYNC_KEY=replace-with-real-key ENYRAX_SYNC_SOURCE=local-lab-01 /usr/bin/python3 /var/www/enyrax-portal/agents/local_sync_agent.py --type heartbeat >> /var/log/enyrax-local-sync.log 2>&1
```

## Future Work

A systemd service and timer can be added later for cleaner scheduling, restart policy, and centralized journald logs. This task intentionally does not create systemd units.

## Security Notes

- Keep the local side outbound-only. Do not open inbound ports on the local host for Tokyo to poll.
- Set a strong `ENYRAX_SYNC_KEY` and keep it out of shell history, repository files, and public logs.
- Prefer HTTPS endpoints.
- Run the agent with the least privileges needed to read local summaries. Docker and Wazuh access may require group permissions depending on the host.
