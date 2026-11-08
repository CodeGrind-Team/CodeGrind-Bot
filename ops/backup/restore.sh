#!/bin/bash
# Decrypts and restores a backup.
#
# Usage: restore.sh <backup-file-name | latest> [--replace]
#
#   By default the backup is restored into a separate `bot_restored` database,
#   so restore drills never touch live data. With --replace it is restored over
#   the live `bot` database (existing collections are dropped first).
#
# Needs the age PRIVATE key at $BACKUP_AGE_IDENTITY_FILE (mount it only for the
# restore; it should never be stored on the server) and a MongoDB URI with the
# `restore` role in $BACKUP_RESTORE_URI (e.g. the root user).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

: "${BACKUP_RESTORE_URI:?BACKUP_RESTORE_URI must be set}"
BACKUP_AGE_IDENTITY_FILE="${BACKUP_AGE_IDENTITY_FILE:-/run/secrets/age-identity}"
BACKUP_DB="${BACKUP_DB:-bot}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_RCLONE_REMOTE="${BACKUP_RCLONE_REMOTE:-}"

usage() {
    echo "Usage: $0 <backup-file-name | latest> [--replace]" >&2
    exit 2
}

[[ $# -ge 1 ]] || usage
target="$1"
replace=0
[[ "${2:-}" == "--replace" ]] && replace=1
[[ -r "$BACKUP_AGE_IDENTITY_FILE" ]] || {
    echo "Private key not readable at $BACKUP_AGE_IDENTITY_FILE" >&2
    exit 1
}

list_backups() {
    {
        find "$BACKUP_DIR" -maxdepth 1 -type f -printf '%f\n' 2>/dev/null || true
        [[ -n "$BACKUP_RCLONE_REMOTE" ]] && rclone lsf --files-only "$BACKUP_RCLONE_REMOTE"
    } | grep -E "$BACKUP_NAME_REGEX" | sort -u
}

if [[ "$target" == "latest" ]]; then
    target="$(list_backups | tail -n 1)"
    [[ -n "$target" ]] || {
        echo "No backups found" >&2
        exit 1
    }
fi
[[ "$target" =~ $BACKUP_NAME_REGEX ]] || {
    echo "Not a backup file name: $target" >&2
    exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if [[ -f "$BACKUP_DIR/$target" ]]; then
    file="$BACKUP_DIR/$target"
elif [[ -n "$BACKUP_RCLONE_REMOTE" ]]; then
    log "Downloading $target from $BACKUP_RCLONE_REMOTE"
    rclone copyto "$BACKUP_RCLONE_REMOTE/$target" "$tmp/$target"
    file="$tmp/$target"
else
    echo "Backup $target not found locally and no remote configured" >&2
    exit 1
fi

if ((replace)); then
    restore_db="$BACKUP_DB"
    ns_args=(--drop)
    log "Restoring $target over the LIVE '$restore_db' database"
else
    restore_db="${BACKUP_DB}_restored"
    ns_args=(--drop --nsFrom="${BACKUP_DB}.*" --nsTo="${restore_db}.*")
    log "Restoring $target into '$restore_db' (live data untouched)"
fi

age -d -i "$BACKUP_AGE_IDENTITY_FILE" "$file" |
    mongorestore --quiet --uri="$BACKUP_RESTORE_URI" --gzip --archive \
        --nsInclude="${BACKUP_DB}.*" "${ns_args[@]}"

log "Restored. Document counts in '$restore_db':"
mongosh --quiet "$BACKUP_RESTORE_URI" --eval "
const d = db.getSiblingDB('$restore_db');
d.getCollectionNames().filter(n => !n.startsWith('system.')).sort()
  .forEach(n => print('  ' + n + ': ' + d.getCollection(n).countDocuments()));
"
