#!/bin/bash
# Runs once, when the MongoDB data volume is first initialised (via the official
# image's /docker-entrypoint-initdb.d hook). Creates least-privilege users:
#   - the bot user can only read and write the `bot` database;
#   - the backup user can only run backups (mongodump).
set -euo pipefail

: "${MONGO_BOT_USERNAME:?MONGO_BOT_USERNAME must be set}"
: "${MONGO_BOT_PASSWORD:?MONGO_BOT_PASSWORD must be set}"
: "${MONGO_BACKUP_USERNAME:?MONGO_BACKUP_USERNAME must be set}"
: "${MONGO_BACKUP_PASSWORD:?MONGO_BACKUP_PASSWORD must be set}"

mongosh --quiet \
    --username "$MONGO_INITDB_ROOT_USERNAME" \
    --password "$MONGO_INITDB_ROOT_PASSWORD" \
    --authenticationDatabase admin \
    admin <<EOF
db.createUser({
  user: process.env.MONGO_BOT_USERNAME,
  pwd: process.env.MONGO_BOT_PASSWORD,
  roles: [{ role: "readWrite", db: "bot" }],
});
db.createUser({
  user: process.env.MONGO_BACKUP_USERNAME,
  pwd: process.env.MONGO_BACKUP_PASSWORD,
  roles: [{ role: "backup", db: "admin" }],
});
print("Created users: " + process.env.MONGO_BOT_USERNAME + ", " + process.env.MONGO_BACKUP_USERNAME);
EOF
