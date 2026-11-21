# 🛠️ Operations, Resilience & Disaster Recovery — The Last Blog in the World

> **English** | [Versão em Português](../operations.md)

This operational runbook covers backup routines, disaster recovery procedures, rollback strategies, and free-tier dormancy mitigation.

---

## 1. Free-Tier Cloud Limits & Mitigations

Operating modern cloud architecture at **permanent zero cost** requires proactive handling of free-tier provider policies:

| Provider | Free-Tier Restriction | Project Impact | Mitigation Implemented |
|---|---|---|---|
| **Render** | Spin-down after 15 min of HTTP inactivity | ~45s cold start on first request after dormancy | Scheduled GitHub Actions workflow `.github/workflows/keep_alive.yml` pings every 3h |
| **Supabase** | Database pauses after 7 days of inactivity | DB enters dormancy and requires manual unpause | Keep-alive queries `/healthz` and weekly `backup.yml` maintain active queries |
| **Render** | Container filesystem is 100% ephemeral | Locally-written files are lost on container restart | All media uploads are stored directly in Supabase Storage via S3 |

### How Keep-Alive Works (`.github/workflows/keep_alive.yml`)
- Runs every 3 hours via GitHub Actions cron (and can be triggered manually).
- Sends an HTTP `GET` request to the `/healthz` endpoint.
- The endpoint actively validates PostgreSQL connectivity (`SELECT 1`) and Redis (`SET/GET`), keeping both providers awake.

---

## 2. Backup Routines

### 2.1 Automated Weekly Backup (`.github/workflows/backup.yml`)
A scheduled workflow runs every Sunday at 03:00 UTC in GitHub Actions:
1. Connects securely to Supabase PostgreSQL using the `DATABASE_URL` secret.
2. Executes `pg_dump` in compressed custom binary format (`-Fc`).
3. Uploads the encrypted artifact to GitHub Actions with a **30-day retention period**.

### 2.2 Manual Database Dump
To extract a local database dump instantly:

```bash
# Set Supabase connection string
export DATABASE_URL="postgresql://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# Create local backups directory (gitignored)
mkdir -p backups

# Generate timestamped dump
pg_dump "$DATABASE_URL" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --file="backups/backup_$(date +%Y%m%d_%H%M%S).dump"
```

---

## 3. Disaster Recovery

To restore a backup into a fresh PostgreSQL instance:

```bash
# 1. Target database URL
export TARGET_DATABASE_URL="postgresql://postgres.<new-ref>:<password>@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# 2. Run restoration with pg_restore
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --dbname="$TARGET_DATABASE_URL" \
  backups/backup_YYYYMMDD_HHMMSS.dump

# 3. Validate schema migrations
python manage.py migrate
```

---

## 4. Media Storage Backup (Supabase S3)

Because post covers and media are stored in a public S3 bucket, synchronization is straightforward with the AWS CLI:

```bash
# Configure Supabase S3 credentials
export AWS_ACCESS_KEY_ID="<SUPABASE_S3_ACCESS_KEY>"
export AWS_SECRET_ACCESS_KEY="<SUPABASE_S3_SECRET_KEY>"
export AWS_ENDPOINT_URL="https://<project-ref>.supabase.co/storage/v1/s3"

# Sync all media files to local folder
aws s3 sync s3://media ./backups/media/
```

---

## 5. Deployment Rollback Procedures

If a deployment introduces unintended regressions:

1. **Rollback via GitHub Container Registry (GHCR)**:
   - On every commit to `main`, CI pushes an immutable image tagged with the commit SHA (`ghcr.io/luiz-edu0202/o-ultimo-blog-do-mundo:sha-<commit>`).
   - In the Render dashboard, navigate to **Settings** > **Image URL** and point to the previous stable commit SHA.
2. **Rollback via Git**:
   ```bash
   git revert <commit-hash>
   git push origin main
   # CI runs the test suite and automatically triggers the deploy hook
   ```
