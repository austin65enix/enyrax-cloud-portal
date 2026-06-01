# Tokyo Portal Backup Scripts Deployment Notes

Operational notes for ENYRAX Tokyo portal app and PostgreSQL backups

## Overview

This document describes how to deploy, verify, schedule, and monitor the Tokyo portal backup scripts for ENYRAX. It covers application archive backup, PostgreSQL local dump, and upload of the latest PostgreSQL backup to Cloudflare R2.

本文件說明 ENYRAX Tokyo Portal 備份腳本的部署、驗證、排程與監控方式。範圍包含應用程式封存備份、PostgreSQL 本機 dump，以及將最新 PostgreSQL 備份上傳至 Cloudflare R2。

This document contains deployment notes only. It does not store Cloudflare R2 credentials or database passwords. Keep rclone credentials in the host-local rclone config. Do not commit `.env` files to Git. Backup scripts must not print secrets.

## Scripts Covered

| Script | Purpose |
| --- | --- |
| `scripts/backup_app_to_r2.sh` | Create application archive and upload to R2 app prefix |
| `scripts/backup_postgres_local.sh` | Create local PostgreSQL dump |
| `scripts/upload_latest_postgres_to_r2.sh` | Upload latest PostgreSQL dump to R2 postgres prefix |

這三支腳本分別處理 app tarball、PostgreSQL dump、以及 PostgreSQL dump 的 R2 上傳。它們應該分開驗證，避免 app 備份與 database 備份互相影響。

## Prerequisites

- Ubuntu host with ENYRAX portal deployed.
- Repository path: `/var/www/enyrax-portal`
- Application directory: `/var/www/enyrax-portal`
- `rclone` installed.
- Cloudflare R2 remote configured locally.
- PostgreSQL client tools installed.
- `DATABASE_URL` available in `/var/www/enyrax-portal/backend/.env` for the PostgreSQL dump script.
- Backup target directories writable by the execution user or root.
- Logs writable by the scheduled task.

Do not store R2 access keys, database passwords, or API tokens inside scripts or Git-tracked files.

不要把 R2 access key、database password、API token 寫進 scripts 或任何 Git-tracked 檔案。

## Environment and Configuration

The current scripts define these values directly and do not implement environment overrides. If overrides are added later, document and verify them before deployment. Credentials are intentionally not listed here.

| Variable / Setting | Default / Example | Purpose |
| --- | --- | --- |
| `APP_DIR` | `/var/www/enyrax-portal` | Application directory used by the app and PostgreSQL backup scripts |
| `BACKUP_DIR` | `/home/atn/backups/app` | Local app archive directory |
| `BACKUP_DIR` | `/home/atn/backups/postgres` | Local PostgreSQL dump directory |
| `RCLONE_REMOTE` | `enyrax-soc-backup` | rclone remote name |
| `R2_BUCKET` | `enyrax-soc-backup` | Cloudflare R2 bucket |
| App `R2_PREFIX` | `enyrax-soc-tokyo/app` | R2 path prefix for app archives |
| PostgreSQL `R2_PREFIX` | `enyrax-soc-tokyo/postgres` | R2 path prefix for PostgreSQL dumps |
| `DATABASE_URL` | Do not print or commit the value. | PostgreSQL connection string loaded from `backend/.env` |
| Timestamp format | `date +%Y%m%d_%H%M%S` | Backup file timestamp |

## Hardening Behavior

- All three scripts use `set -euo pipefail`, a conservative `IFS`, and required-command checks.
- App archives exclude `.env`, `backend/.env`, `.git`, virtualenv directories, Python caches, local backup artifacts, logs, temporary paths, and `data/agentops/snapshots/retention_report.json`.
- The app script verifies the completed archive listing before upload and aborts if excluded sensitive or local paths remain.
- Created or uploaded backup files must exist and be non-empty.
- The PostgreSQL local dump requires `DATABASE_URL` from `backend/.env`, but never prints its value. It writes a temporary file and moves it into place only after a non-empty dump succeeds.
- R2 upload scripts rely on the execution user host-local rclone config and use normal `rclone copyto` verbosity. The former `-vv` flag was removed to reduce log exposure.
- `DRY_RUN=1` performs dependency and configuration checks without creating an archive, invoking `pg_dump`, or uploading to R2. The PostgreSQL upload dry-run still selects and validates the latest local dump.

## Manual Verification Commands

### Check scripts

```bash
cd /var/www/enyrax-portal

ls -la \
  scripts/backup_app_to_r2.sh \
  scripts/backup_postgres_local.sh \
  scripts/upload_latest_postgres_to_r2.sh
```

### Syntax check

```bash
bash -n scripts/backup_app_to_r2.sh
bash -n scripts/backup_postgres_local.sh
bash -n scripts/upload_latest_postgres_to_r2.sh
```

### Dry-run checks

Run these before cron installation. They must not create backups or upload files. The PostgreSQL upload dry-run requires an existing non-empty local dump.

```bash
DRY_RUN=1 scripts/backup_app_to_r2.sh
DRY_RUN=1 scripts/backup_postgres_local.sh
DRY_RUN=1 scripts/upload_latest_postgres_to_r2.sh
```

### rclone remote check

```bash
rclone listremotes
rclone lsd <remote>:
```

## Manual Run Procedure

Run each script separately and verify its result before continuing. Prefer a regular user when that user has the required filesystem and rclone config permissions. Use `sudo -E` only when required; note that the current PostgreSQL script loads `DATABASE_URL` from `backend/.env`.

### 1. PostgreSQL local backup

```bash
cd /var/www/enyrax-portal
sudo -E scripts/backup_postgres_local.sh
```

After completion, confirm that the expected backup file was created under `/home/atn/backups/postgres`.

### 2. Upload latest PostgreSQL backup to R2

```bash
cd /var/www/enyrax-portal
sudo -E scripts/upload_latest_postgres_to_r2.sh
```

Confirm that the latest PostgreSQL dump is the expected file and that the rclone remote path is correct.

### 3. App backup to R2

```bash
cd /var/www/enyrax-portal
sudo -E scripts/backup_app_to_r2.sh
```

The app backup creates a tarball and uploads it to the R2 app prefix. Its tar exclusions are relative to `APP_DIR`, including `.env`, `backend/.env`, `.git`, virtualenv directories, caches, logs, temporary paths, and backup artifacts. Before upload, the script scans the archive listing and aborts if excluded sensitive or local paths remain.

## Post-run Verification

Check the R2 app backup:

```bash
rclone lsf <remote>:enyrax-soc-backup/enyrax-soc-tokyo/app/ | tail -20
```

Check the R2 PostgreSQL backup:

```bash
rclone lsf <remote>:enyrax-soc-backup/enyrax-soc-tokyo/postgres/ | tail -20
```

Check local backups using the paths configured by the current scripts:

```bash
ls -lh /home/atn/backups/app /home/atn/backups/postgres 2>/dev/null || true
```

## Suggested Cron Schedule

This is a recommendation only. Do not install it until manual verification succeeds.

```cron
# PostgreSQL local backup
30 22 * * * cd /var/www/enyrax-portal && scripts/backup_postgres_local.sh >> /var/log/enyrax-postgres-backup.log 2>&1

# Upload latest PostgreSQL backup to Cloudflare R2
40 22 * * * cd /var/www/enyrax-portal && scripts/upload_latest_postgres_to_r2.sh >> /var/log/enyrax-postgres-r2-upload.log 2>&1

# App backup to Cloudflare R2
50 22 * * * cd /var/www/enyrax-portal && scripts/backup_app_to_r2.sh >> /var/log/enyrax-app-r2-backup.log 2>&1
```

Escape `%` as `\%` if a cron command includes `date`. The cron user must be able to read the app, database configuration, and rclone config, and write backup directories and logs. Root cron uses root's rclone config; an `atn` user cron uses `atn`'s rclone config. Verify the selected execution user explicitly.

## Restore Notes

This is not a complete restore runbook. It records the minimum direction for a controlled restore.

### App restore

- Download the app tarball from R2.
- Extract it into a temporary directory.
- Inspect the extracted content.
- Do not overwrite production directly.
- Compare config, static files, and backend code.
- Restore `.env` from a secure host source, not from the repository.

### PostgreSQL restore

- Download the SQL dump from R2.
- Test the restore against a staging database.
- Do not restore directly into production.
- Verify schema, row counts, and critical tables.
- Require a maintenance window and rollback plan.

Never restore directly into production without a verified staging restore and rollback plan.

未經 staging 還原驗證與 rollback plan，不要直接還原到 production。

## Monitoring and Logs

Recommended log checks:

```bash
tail -n 100 /var/log/enyrax-postgres-backup.log
tail -n 100 /var/log/enyrax-postgres-r2-upload.log
tail -n 100 /var/log/enyrax-app-r2-backup.log
```

Record and monitor:

- start time
- end time
- backup file name
- file size
- upload destination prefix
- success / failure
- non-zero exit codes

Cron should monitor exit codes. Backup logs can contain sensitive operational metadata and must not be exposed publicly. A future task can connect failures to Status, AgentOps, or ServiceOps notifications.

## Security Boundary

- Do not commit `.env`.
- Do not commit rclone config.
- Do not commit database credentials.
- Do not print `DATABASE_URL`.
- Do not print access keys.
- Do not store R2 secrets in scripts.
- Do not include backups in Git.
- Backup archives may contain sensitive data and must be protected.
- R2 bucket permissions should follow least privilege.
- Restore access should be limited to authorized operators.

備份檔本身可能包含敏感資料，因此即使 scripts 沒有 secrets，備份產物也必須視為敏感資產。

## Known Cautions

- App archive exclusions and the archive safety scan must remain aligned when local runtime paths change.
- PostgreSQL dumps may contain sensitive data.
- rclone remote identity depends on the execution user.
- Cron has a smaller environment than an interactive shell.
- R2 upload success does not equal restore readiness.
- This document does not replace a full restore drill.

## Completed Hardening

- Task #160: Tokyo Portal Backup Script Hardening

## Future Tasks
- Task #161: Tokyo Portal Restore Drill Plan
- Task #162: Backup Monitoring / Status Integration
- Task #163: Backup Retention Policy
- Task #164: Backup Encryption Review
