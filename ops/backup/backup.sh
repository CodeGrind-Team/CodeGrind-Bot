#!/bin/bash
# Takes one encrypted backup of the `bot` database, uploads it off-box, then
# applies the retention policy locally and remotely.
#
#   mongodump (gzip) -> age (public key only) -> $BACKUP_DIR -> rclone remote
#
# Retention is only applied after the new backup has been written (and
# uploaded, when a remote is configured), so a failing backup never causes old
# backups to be deleted.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

: "${BACKUP_MONGO_URI:?BACKUP_MONGO_URI must be set}"
: "${BACKUP_AGE_RECIPIENTS:?BACKUP_AGE_RECIPIENTS must be set (age public key(s))}"
BACKUP_DB="${BACKUP_DB:-bot}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_STATE_DIR="${BACKUP_STATE_DIR:-/state}"
BACKUP_RCLONE_REMOTE="${BACKUP_RCLONE_REMOTE:-}"
BACKUP_KEEP_LOCAL="${BACKUP_KEEP_LOCAL:-7}"
BACKUP_KEEP_DAILY="${BACKUP_KEEP_DAILY:-14}"
BACKUP_KEEP_WEEKLY="${BACKUP_KEEP_WEEKLY:-8}"
BACKUP_KEEP_MONTHLY="${BACKUP_KEEP_MONTHLY:-12}"
BACKUP_DISCORD_WEBHOOK_URL="${BACKUP_DISCORD_WEBHOOK_URL:-}"

notify_failure() {
    local message="$1"
    log "FAILED: $message"
    if [[ -n "$BACKUP_DISCORD_WEBHOOK_URL" ]]; then
        curl -fsS -m 15 -H "Content-Type: application/json" \
            -d "{\"content\": \"⚠️ CodeGrind database backup failed: ${message//\"/\\\"}\"}" \
            "$BACKUP_DISCORD_WEBHOOK_URL" >/dev/null ||
            log "Could not send Discord failure notification"
    fi
}

step="starting"
trap 'notify_failure "$step (line $LINENO)"' ERR

mkdir -p "$BACKUP_DIR" "$BACKUP_STATE_DIR"

# Never run two backups at once (e.g. a manual run during a scheduled one).
exec 9>"$BACKUP_STATE_DIR/backup.lock"
flock -n 9 || {
    log "Another backup is already running, skipping"
    exit 0
}

recipients=()
for key in $BACKUP_AGE_RECIPIENTS; do
    recipients+=(-r "$key")
done

name="${BACKUP_PREFIX}$(date -u +%Y-%m-%dT%H%M%SZ)${BACKUP_SUFFIX}"
path="$BACKUP_DIR/$name"
partial="$path.partial"
# Remove the half-written file if anything below fails.
trap 'rm -f "$partial"' EXIT

step="dump and encrypt"
log "Creating $name"
mongodump --quiet --uri="$BACKUP_MONGO_URI" --db="$BACKUP_DB" --gzip --archive |
    age "${recipients[@]}" >"$partial"

step="verify backup file"
size="$(stat -c %s "$partial")"
header="$(head -c 21 "$partial")"
if [[ "$header" != "age-encryption.org/v1" ]] || ((size < 1024)); then
    rm -f "$partial"
    false # triggers the ERR trap
fi
mv "$partial" "$path"
log "Wrote $name ($((size / 1024)) KiB)"

if [[ -n "$BACKUP_RCLONE_REMOTE" ]]; then
    step="upload to $BACKUP_RCLONE_REMOTE"
    rclone copyto "$path" "$BACKUP_RCLONE_REMOTE/$name"
    # Confirm the object exists remotely with the same size before pruning.
    remote_size="$(rclone size --json "$BACKUP_RCLONE_REMOTE/$name" | grep -o '"bytes":[0-9]*' | cut -d: -f2)"
    [[ "$remote_size" == "$size" ]]
    log "Uploaded to $BACKUP_RCLONE_REMOTE"

    step="remote retention"
    rclone lsf --files-only "$BACKUP_RCLONE_REMOTE" |
        retention_deletions "$BACKUP_KEEP_DAILY" "$BACKUP_KEEP_WEEKLY" "$BACKUP_KEEP_MONTHLY" |
        while IFS= read -r old; do
            rclone deletefile "$BACKUP_RCLONE_REMOTE/$old"
            log "Deleted remote $old"
        done
else
    log "BACKUP_RCLONE_REMOTE not set: keeping the backup on this machine only"
fi

step="local retention"
# Locally, keep only the newest $BACKUP_KEEP_LOCAL days of backups (the off-box
# copy holds the long-term history).
find "$BACKUP_DIR" -maxdepth 1 -type f -printf '%f\n' |
    retention_deletions "$BACKUP_KEEP_LOCAL" 0 0 |
    while IFS= read -r old; do
        rm -f "$BACKUP_DIR/$old"
        log "Deleted local $old"
    done
# Leftovers from interrupted runs.
find "$BACKUP_DIR" -maxdepth 1 -type f -name '*.partial' -mmin +60 -delete

date -u +%s >"$BACKUP_STATE_DIR/last_success"
log "Backup completed"
