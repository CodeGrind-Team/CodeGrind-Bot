# Self-hosted MongoDB and backups

Optional Docker Compose services for running the bot's database on the same
machine as the bot, with nightly encrypted off-site backups.

| Service  | Profile  | What it does |
|----------|----------|--------------|
| `mongo`  | `mongo`  | MongoDB 8.0. No published port: only the other containers can reach it. Authentication is always on. |
| `backup` | `backup` | Every night: `mongodump` → gzip → [age](https://github.com/FiloSottile/age) encryption → local copy → upload with [rclone](https://rclone.org) → retention. |

Without these profiles enabled, nothing changes: the bot uses whatever
`MONGODB_URI` points at (e.g. MongoDB Atlas).

## How it's secured

- **Network:** MongoDB is only on the internal Docker network. Never add a
  `ports:` entry for it. To reach it from your machine, use an SSH tunnel.
- **Users:** each client gets only what it needs.
  - root: admin and restores only
  - `codegrind` (the bot): read/write on the `bot` database only
  - `backup`: MongoDB's `backup` role only (read-only)
- **Fail-safe start:** the container refuses to start without root
  credentials, and `--auth` is always passed, so a missing `.env` value can't
  start an open database.
- **Backups:** each backup is encrypted with your age **public** key before
  it is written or uploaded. The **private** key never goes on the server. So
  neither a leaked bucket nor a compromised server exposes old backups.
- **At rest:** the data volume relies on the host disk's encryption (Oracle
  Cloud encrypts block volumes by default).

## Retention policy

Defaults, all configurable in `.env`:

| Where | Kept |
|-------|------|
| Off-site (rclone remote) | The newest backup of each of the last **14** days, **8** weeks (ISO weeks) and **12** months: at most 34 backups. |
| On the server | The last **7** days, for quick restores. |

- **What a "day" means:** counts are of periods *that have a backup*, the
  same rule restic uses. A gap, say after an outage, never causes older
  backups to be pruned faster.
- **Weekly and monthly backups** are picked from the existing nightly
  backups, so there are no duplicate uploads, and a missed Sunday never
  leaves that week empty.
- **When pruning happens:** only after the new backup has been written and
  uploaded (with the uploaded size checked). The newest backup is never
  deleted. Files that aren't backups are never touched.
- **On failure:** if a backup fails, nothing is deleted and an optional
  Discord webhook is notified. The container also reports `unhealthy` in
  `docker compose ps` if no backup has succeeded in 26 hours.

## One-time setup

### 1. Create the encryption key (on your own machine, not the server)

```bash
age-keygen -o codegrind-backup.key
# Public key: age1...   <- goes in .env on the server (safe to share)
```

Store `codegrind-backup.key` (the **private** key) somewhere durable and
offline, such as a password manager, then delete it from disk. **Without it,
backups can't be decrypted.** You can list several public keys, separated by
spaces, so that more than one person can restore.

### 2. Create a bucket and an rclone remote

rclone supports most storage providers. Two good free-tier options:

**Oracle Cloud Object Storage** (20 GB free; no credentials on the server):

1. Create a **private** bucket, e.g. `codegrind-backups`.
2. Create a dynamic group matching the instance, e.g.
   `instance.id = '<instance OCID>'`, and a policy:
   `Allow dynamic-group <group> to manage objects in compartment <compartment> where target.bucket.name = 'codegrind-backups'`
3. Create `ops/backup/config/rclone.conf` (git-ignored):

   ```ini
   [oci]
   type = oracleobjectstorage
   provider = instance_principal_auth
   namespace = <object storage namespace>
   compartment = <compartment OCID>
   region = <region, e.g. uk-london-1>
   ```

4. Set `BACKUP_RCLONE_REMOTE=oci:codegrind-backups`.

**Google Cloud Storage:** create a bucket and a service account with
*Storage Object Admin* on that bucket only. Save its key as
`ops/backup/config/gcs-key.json`, and write `ops/backup/config/rclone.conf`:

```ini
[gcs]
type = google cloud storage
service_account_file = /config/gcs-key.json
bucket_policy_only = true
```

Then set `BACKUP_RCLONE_REMOTE=gcs:<bucket-name>`.

Set `chmod 600 ops/backup/config/*` either way.

### 3. Add to `.env` on the server

Use passwords without URL-special characters, e.g. `openssl rand -hex 24`.

```bash
# Enables the services, so a plain `docker compose up -d --build` runs everything.
COMPOSE_PROFILES=mongo,backup,datadog

MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=<random>
MONGO_BOT_PASSWORD=<random>
MONGO_BACKUP_PASSWORD=<random>

BACKUP_AGE_RECIPIENTS=age1...            # public key from step 1
BACKUP_RCLONE_REMOTE=oci:codegrind-backups
# Optional:
# BACKUP_TIME=03:00                      # UTC
# BACKUP_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
# BACKUP_KEEP_DAILY=14  BACKUP_KEEP_WEEKLY=8  BACKUP_KEEP_MONTHLY=12  BACKUP_KEEP_LOCAL=7
```

The users are created the first time the `mongo` volume is initialised.
Changing the passwords later means changing them in MongoDB too
(`db.changeUserPassword`).

## Migrating from Atlas

The downtime is a few minutes. Keep the Atlas cluster (paused) for a week
afterwards as a fallback.

```bash
cd ~/CodeGrind-Bot
git pull --ff-only

# 1. Start only the database (creates the users on first start).
docker compose up -d mongo
docker compose ps mongo             # wait for "healthy"

# 2. Stop the bot so nothing writes during the copy.
docker compose stop app

# 3. Copy Atlas -> local (paste the Atlas URI when prompted).
read -rs ATLAS_URI && export ATLAS_URI
docker compose run --rm --no-deps -e ATLAS_URI backup bash -c \
  'mongodump --quiet --uri "$ATLAS_URI" --db bot --gzip --archive=/backups/atlas-migration.archive'
docker compose run --rm backup bash -c \
  'mongorestore --quiet --uri "$BACKUP_RESTORE_URI" --gzip --archive=/backups/atlas-migration.archive --nsInclude "bot.*"'

# 4. Check every document arrived (must print "ALL MATCH").
export SRC_URI="$ATLAS_URI"
# paste: mongodb://root:<MONGO_ROOT_PASSWORD>@mongo:27017/?authSource=admin
read -rs DST_URI && export DST_URI
docker compose run --rm --no-deps -e SRC_URI -e DST_URI \
  -v "$PWD/ops/mongo/compare_databases.py:/compare.py:ro" app python /compare.py

# 5. Remove the unencrypted migration dump.
docker compose run --rm --no-deps backup rm /backups/atlas-migration.archive

# 6. Point the bot at the local database: in .env set
#    MONGODB_URI=mongodb://codegrind:<MONGO_BOT_PASSWORD>@mongo:27017/?authSource=admin
docker compose up -d --build        # starts app + backup (+ datadog)
docker compose logs -f app backup
```

The backup service takes a backup straight away on its first start, so step 6
also checks that encryption and upload work. Then in Atlas, pause the cluster,
and delete it after a week.

**Rollback:** put the Atlas `MONGODB_URI` back in `.env`, then run
`docker compose up -d app`. Anything written after the switch exists only in
the local database.

## Day-to-day

```bash
docker compose ps                                     # backup shows (healthy) after a success
docker compose logs --tail 50 backup
docker compose exec backup /opt/backup/entrypoint.sh run           # take a backup now
docker compose exec backup sh -c 'rclone lsf "$BACKUP_RCLONE_REMOTE"'   # list off-site backups
```

### Restore drill (do this every few months)

This restores into a separate `bot_restored` database, so live data is not
touched. The private key is mounted only for this one command.

```bash
# copy the private key to the server temporarily, e.g. ~/codegrind-backup.key
docker compose run --rm -v ~/codegrind-backup.key:/run/secrets/age-identity:ro backup restore latest
shred -u ~/codegrind-backup.key
# check the printed document counts, then clean up:
docker compose exec mongo sh -c \
  'mongosh -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --quiet --eval "db.getSiblingDB(\"bot_restored\").dropDatabase()"'
```

`restore` takes `latest` or a file name from the listing above. Files that
aren't on the server are downloaded from the remote.

### Real restore (data loss)

```bash
docker compose stop app
docker compose run --rm -v ~/codegrind-backup.key:/run/secrets/age-identity:ro \
  backup restore <file name | latest> --replace     # drops and replaces the live `bot` database
shred -u ~/codegrind-backup.key
docker compose start app
```

### Restore without the server

Any machine with `age` and the MongoDB Database Tools can restore a downloaded
backup:

```bash
age -d -i codegrind-backup.key codegrind-bot-<timestamp>.archive.gz.age \
  | mongorestore --uri "<target URI>" --gzip --archive --nsInclude 'bot.*'
```
