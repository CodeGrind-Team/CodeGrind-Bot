#!/bin/bash
# Shared helpers for the backup scripts.

# Backup filenames embed a UTC timestamp so they sort chronologically, e.g.
# codegrind-bot-2026-11-08T030000Z.archive.gz.age
BACKUP_PREFIX="codegrind-bot-"
# shellcheck disable=SC2034 # used by scripts that source this file
BACKUP_SUFFIX=".archive.gz.age"
BACKUP_NAME_REGEX="^${BACKUP_PREFIX}[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}Z\\.archive\\.gz\\.age$"

log() {
    printf '%s [backup] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"
}

# Prints the date (YYYY-MM-DD) embedded in a backup filename.
backup_date() {
    local name="${1#"$BACKUP_PREFIX"}"
    printf '%s\n' "${name:0:10}"
}

# Reads backup filenames on stdin and prints the ones the retention policy says
# to DELETE, one per line. Unrecognised filenames are ignored (never deleted).
#
# Grandfather-father-son policy: keep the newest backup of each of the last
# $1 days, of each of the last $2 ISO weeks, and of each of the last $3 months.
# The newest backup is always kept. A backup kept for any reason is not deleted.
#
# Weekly and monthly backups are chosen from the existing daily backups, so a
# missed run never leaves a period without a backup if one exists for it.
retention_deletions() {
    local keep_daily="$1" keep_weekly="$2" keep_monthly="$3"
    local -A seen_day=() seen_week=() seen_month=()
    local days=0 weeks=0 months=0 first=1
    local name d week month keep

    while IFS= read -r name; do
        [[ "$name" =~ $BACKUP_NAME_REGEX ]] || continue
        d="$(backup_date "$name")"
        week="$(date -u -d "$d" +%G-W%V)"
        month="${d:0:7}"
        keep=0

        if ((first)); then
            keep=1
            first=0
        fi
        if [[ -z "${seen_day[$d]:-}" ]] && ((days < keep_daily)); then
            seen_day[$d]=1
            days=$((days + 1))
            keep=1
        fi
        if [[ -z "${seen_week[$week]:-}" ]] && ((weeks < keep_weekly)); then
            seen_week[$week]=1
            weeks=$((weeks + 1))
            keep=1
        fi
        if [[ -z "${seen_month[$month]:-}" ]] && ((months < keep_monthly)); then
            seen_month[$month]=1
            months=$((months + 1))
            keep=1
        fi

        ((keep)) || printf '%s\n' "$name"
    done < <(sort -r)
}
