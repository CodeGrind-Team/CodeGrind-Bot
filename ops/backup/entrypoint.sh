#!/bin/bash
# Container entrypoint.
#   schedule  (default) run backup.sh every day at $BACKUP_TIME (UTC, HH:MM)
#   run       take one backup now
#   restore   restore a backup (see restore.sh)
#   health    exit 0 if a backup succeeded within $BACKUP_MAX_AGE_HOURS
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

BACKUP_TIME="${BACKUP_TIME:-03:00}"
BACKUP_STATE_DIR="${BACKUP_STATE_DIR:-/state}"
BACKUP_MAX_AGE_HOURS="${BACKUP_MAX_AGE_HOURS:-26}"

seconds_until_next_run() {
    local now next
    now="$(date -u +%s)"
    next="$(date -u -d "today $BACKUP_TIME" +%s)"
    if ((next <= now)); then
        next="$(date -u -d "tomorrow $BACKUP_TIME" +%s)"
    fi
    echo $((next - now))
}

case "${1:-schedule}" in
schedule)
    # Validate the time once up front so a typo fails loudly.
    date -u -d "today $BACKUP_TIME" >/dev/null
    trap 'log "Stopping scheduler"; exit 0' TERM INT
    log "Scheduler started: daily backups at $BACKUP_TIME UTC"
    # On first start (no successful backup yet) take one immediately, so a
    # misconfiguration shows up now rather than at the first scheduled run.
    if [[ ! -f "$BACKUP_STATE_DIR/last_success" ]]; then
        log "No previous successful backup found, taking one now"
        "$SCRIPT_DIR/backup.sh" || log "Initial backup failed"
    fi
    while true; do
        wait_for="$(seconds_until_next_run)"
        log "Next backup in $((wait_for / 3600))h $(((wait_for % 3600) / 60))m"
        # Sleep in the background so SIGTERM is handled immediately.
        sleep "$wait_for" &
        wait $!
        "$SCRIPT_DIR/backup.sh" || log "Backup run failed, will retry at the next scheduled time"
    done
    ;;
run)
    exec "$SCRIPT_DIR/backup.sh"
    ;;
restore)
    shift
    exec "$SCRIPT_DIR/restore.sh" "$@"
    ;;
health)
    last="$(cat "$BACKUP_STATE_DIR/last_success" 2>/dev/null || echo 0)"
    (($(date -u +%s) - last < BACKUP_MAX_AGE_HOURS * 3600))
    ;;
*)
    exec "$@"
    ;;
esac
