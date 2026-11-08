#!/bin/bash
# Wraps the official image's entrypoint and refuses to start without root
# credentials, so a missing .env value can never start an open database.
# (`--auth` is also passed explicitly in docker-compose.yml, because the image
# only enables it when these variables are set.)
set -euo pipefail

if [[ -z "${MONGO_INITDB_ROOT_USERNAME:-}" || -z "${MONGO_INITDB_ROOT_PASSWORD:-}" ]]; then
    echo "MONGO_ROOT_USERNAME and MONGO_ROOT_PASSWORD must be set in .env" >&2
    exit 1
fi

exec docker-entrypoint.sh "$@"
