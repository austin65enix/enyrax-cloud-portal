# ENYRAX Backup Upload to Cloudflare R2

## Purpose

Upload local backups from the Tokyo host to Cloudflare R2 for offsite backup storage.

The local backup archive is expected to be created by:

```bash
scripts/backup_tokyo_portal.sh
```

The upload script sends the latest matching archive from `/var/backups/enyrax` to the configured Cloudflare R2 bucket path.

## Prerequisites

- Install `rclone` on the Tokyo host.
- Create a Cloudflare R2 bucket.
- Create a Cloudflare R2 API token / access key.
- Use `rclone config` to create the remote:

```text
enyrax-r2
```

Do not put Cloudflare R2 access keys or secrets in the upload script. Store them only in the local `rclone` configuration.

Default upload settings:

```text
BACKUP_DIR=/var/backups/enyrax
RCLONE_REMOTE=enyrax-r2
R2_BUCKET=enyrax-backups
R2_PREFIX=tokyo
```

## Testing

Check that the Cloudflare R2 remote is visible:

```bash
rclone lsd enyrax-r2:
```

Preview the upload target without uploading:

```bash
sudo scripts/upload_backup_to_r2.sh --dry-run
```

Upload the latest backup:

```bash
sudo scripts/upload_backup_to_r2.sh
```

## Cron

Run the Cloudflare R2 upload 10 minutes after the daily local backup. For example:

```cron
40 18 * * * /var/www/enyrax-portal/scripts/upload_backup_to_r2.sh >> /var/log/enyrax-r2-upload.log 2>&1
```

## Restore Reminder

Cloudflare R2 is only the backup repository. A restore still requires:

- Download backup.
- Extract project.
- Restore PostgreSQL dump.
- Restore nginx / systemd configuration.
- Restart services.

## Related Backup Scripts

For Tokyo Portal app and PostgreSQL backup deployment notes, see:

- `docs/tokyo_portal_backup_deployment_notes.md`
