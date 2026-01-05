# Local Database + Runtime Setup (Enforced Storage)

Context

- Storage is configured to require a real Postgres when `STORAGE_REQUIRE_DATABASE=true` (default in `.env`, `.env.local`, `.env.production`). When this is set, the server performs an explicit DB connection verification at startup and will _exit immediately_ if Postgres cannot be reached (fail-fast behavior).
- Recent changes: metadata partitioning uses Postgres for summaries and object storage refs; the Images MVP analytics/trials/credits also rely on the DB. The app is intended to run against a real DB in dev and prod; use the in-memory fallback only for short-lived, local debugging when the DB is intentionally disabled.

What blocked setup inside this sandbox

- Docker-based Postgres: `docker compose up -d db` fails with permission denied on the Docker socket.
- Native Postgres initdb: `initdb` fails with `could not create shared memory segment: Operation not permitted` (shmget) even with `shared_memory_type=mmap`; sandbox restriction.
- Port 3000: currently occupied by a node process; kill attempt was denied (EPERM).
- Redis: connection fails (EPERM); rate limiter will crash startup unless disabled.

What you need on your host (outside the sandbox)

1. Postgres running locally (or reachable remotely):
   - Create role: `createuser -s pranay` (or `psql -U postgres -c "CREATE ROLE pranay LOGIN SUPERUSER"`).
   - Create DB: `createdb -O pranay metaextract`.
   - Confirm with: `psql -U pranay -d metaextract -c "select 1;"`.

   Quick check: After setting `DATABASE_URL` run `npm run check:db` to verify connectivity and get a helpful error message.

2. Environment (already set in .env/.env.local/.env.production):
   - `DATABASE_URL=postgresql://pranay@localhost:5432/metaextract`
   - `STORAGE_REQUIRE_DATABASE=true` (enforces DB; remove/false only if you deliberately want in-memory fallback).
   - If Redis isn’t available locally, set `RATE_LIMIT_ENABLED=false` temporarily to avoid startup failures.
3. Port: free 3000 or set `PORT=3001` (update client proxy/dev server if needed).

Optional dev bypass (only if you need to run without DB/Redis briefly)

- Set `STORAGE_REQUIRE_DATABASE=false` to allow in-memory storage.
- Set `RATE_LIMIT_ENABLED=false` to skip Redis.
- Set `PORT=3001` if 3000 is occupied.
- Revert these after you have Postgres/Redis available.

Troubleshooting

- Docker socket permission denied when running `docker compose up -d db`:
  - Ensure your user is in the `docker` group or run `docker compose` with a user that has access to the Docker socket. On some systems (CI/sandbox) Docker socket access is intentionally restricted.
  - As an alternative, use a remote Postgres host (e.g., a cloud instance or an SSH-forwarded port) and set `DATABASE_URL` to that host.
- `initdb` fails with `could not create shared memory segment: Operation not permitted`:
  - This indicates the environment disallows System V shared memory. Use a hosted Postgres or a Docker container on a host where shared memory allocation is permitted.
- Redis `EPERM` on connection or port 3000 already used:
  - Temporarily set `RATE_LIMIT_ENABLED=false` and/or update `PORT` as described above while you fix host issues.

If a local Postgres is not available, using a remote database (or your cloud provider) with `DATABASE_URL` updated is the fastest path to get the server running while retaining `STORAGE_REQUIRE_DATABASE=true`.

How to run after host DB is ready

1. Start Postgres (host or remote) and Redis (or disable rate limit as above).
2. `npm run dev:server` (or your proc manager) — it should connect to Postgres; if not, it will throw on startup because DB is required.
3. `npm run dev:client` (Vite dev server). Ensure client API proxy targets the server port you’re using.

Notes on images MVP

- Unsigned/signed/admin all share the same extraction path; credits/trials/analytics write to Postgres when available. Analytics logging is non-blocking but DB is still expected in normal operation.
- WebSocket progress uses the same server; ensure the API host/port is reachable from the client.

---

## ⚠️ Launch-Critical Database Verification (For Images MVP)

Before launching images_mvp, verify these database components are properly configured:

### Required Tables (Check These Exist)

```sql
-- Check all critical tables for images_mvp
\dt users
\dt subscriptions
\dt extraction_analytics
\dt image_mvp_events
\dt trial_usages
\dt credit_balances
```

### Connection Pool Sizing

**Current**: `max: 10` in `server/db.ts:28`
**Issue**: Will fail at 11 concurrent users
**Action**:

```typescript
// server/db.ts line 27-31
const DEFAULT_POOL_CONFIG = {
  max: 20, // ← Increase from 10 to 20 for launch
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};
```

**Test Before Launch**:

```bash
# Load test with 20 concurrent connections
psql $DATABASE_URL -c "SELECT 1;" # Should succeed

# Verify pool monitoring
NODE_DEBUG=pg npm run dev:server
# Watch for "pool error" messages
```

### Critical Indexes for Performance

Verify these indexes exist (required for high-traffic images_mvp):

```sql
-- Check indexes on high-traffic tables
\d extraction_analytics
-- Should have: idx_requested_at, idx_tier, idx_success

\d image_mvp_events
-- Should have: idx_user_id, idx_event_type, idx_created_at

\d trial_usages
-- Should have: idx_user_id, idx_session_id
```

If missing, add before launch:

```sql
CREATE INDEX IF NOT EXISTS idx_extraction_requested_at
  ON extraction_analytics(requested_at DESC);
CREATE INDEX IF NOT EXISTS idx_extraction_tier
  ON extraction_analytics(tier);
CREATE INDEX IF NOT EXISTS idx_extraction_success
  ON extraction_analytics(success);

CREATE INDEX IF NOT EXISTS idx_image_mvp_events_user
  ON image_mvp_events(user_id);
CREATE INDEX IF NOT EXISTS idx_image_mvp_events_type
  ON image_mvp_events(event_type);
CREATE INDEX IF NOT EXISTS idx_image_mvp_events_created
  ON image_mvp_events(created_at DESC);
```

### Race Condition Prevention (Credit System)

**Issue**: Concurrent uploads can cause credit deduction race conditions  
**Verify**:

```sql
-- Check that credit updates use atomic transactions
SELECT * FROM credit_balances WHERE user_id = 'test-user';
-- Result should be single row with balance, not multiple pending transactions

-- Verify ACID constraints
\d+ credit_balances
-- Should have: PRIMARY KEY, NOT NULL on balance, CHECK balance >= 0
```

### Backup Strategy Before Launch

**Critical**: Database backups protect against data loss  
**Setup**:

```bash
# Create daily backup (add to crontab)
0 2 * * * pg_dump $DATABASE_URL | gzip > /backup/metaextract-$(date +\%Y\%m\%d).sql.gz

# Test restore (critical!)
gunzip < /backup/metaextract-latest.sql.gz | psql $DATABASE_URL

# Verify: count rows in key tables
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM extraction_analytics;"
```

### Monitoring Database Health

**Before Launch**:

1. Set up connection monitoring:

```sql
-- Monitor active connections
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname;
-- Should not exceed 15-18 (since pool max is 20)
```

2. Monitor slow queries:

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries >1s
SELECT pg_reload_conf();

-- Check slow query log
SELECT query, calls, mean_time FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC;
```

3. Monitor table sizes:

```sql
SELECT schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
-- Watch for extraction_analytics and image_mvp_events growing unexpectedly
```

### Data Retention Policy

**Before Launch**: Define and implement data retention:

```sql
-- Archive old extraction records (after 90 days)
DELETE FROM extraction_analytics
WHERE requested_at < NOW() - INTERVAL '90 days'
AND success = true;  -- Keep failed records longer for debugging

-- Archive analytics events (after 30 days)
DELETE FROM image_mvp_events
WHERE created_at < NOW() - INTERVAL '30 days';
```

### Production Database Checklist

Before public launch, verify:

```
Database Setup:
□ Postgres 13+ running (production version)
□ Backup strategy in place (test restore works)
□ Connection pool set to 20+
□ All critical indexes created
□ Slow query logging enabled
□ Automated maintenance configured (vacuum, analyze)

Data Integrity:
□ Foreign key constraints in place
□ NOT NULL constraints on critical columns
□ Unique constraints prevent duplicates
□ CHECK constraints on balances (no negative)
□ SERIAL/UUID sequences configured

Monitoring:
□ Connection pool monitoring active
□ Table size monitoring active
□ Query performance monitoring active
□ Daily backup verification passing

Security:
□ Database user password strong (>16 chars, alphanumeric+symbols)
□ Role has minimal required permissions
□ SSL connections enabled (if remote DB)
□ Firewall restricts access to DB port
□ No sensitive data in logs

Scaling:
□ Connection pool tested with 20+ concurrent
□ Query plans reviewed for efficiency
□ Partitioning strategy for analytics table (if >1M rows)
□ Read replicas configured (if high availability needed)
```

### Troubleshooting Database Issues

**Problem**: "Too many connections"

```bash
# Increase max_connections in postgresql.conf
max_connections = 200  # Should be >= pool max * number of servers

# Or restart Postgres after change
sudo systemctl restart postgresql
```

**Problem**: Slow extraction queries

```sql
-- Identify slowest queries
SELECT query, calls, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;

-- Analyze specific query
EXPLAIN ANALYZE SELECT * FROM extraction_analytics
WHERE user_id = 'xxx' AND created_at > NOW() - INTERVAL '1 day';
```

**Problem**: Disk space running low

```bash
# Check database size
du -sh /var/lib/postgresql/

# Archive and delete old data
psql $DATABASE_URL -c "DELETE FROM extraction_analytics WHERE requested_at < NOW() - INTERVAL '90 days';"

# Vacuum to reclaim space
psql $DATABASE_URL -c "VACUUM FULL;"
```

---

## Migration Scripts Location

```
server/migrations/
├── 001_add_metadata_storage.sql
├── 002_add_trial_usage_tracking.sql
├── 003_add_trial_usage_count.sql
├── 004_add_ui_events.sql
└── 005_add_credit_system.sql
 └── 006_images_mvp_indexes.sql
```

**To apply migrations**:

```bash
# Drizzle migrations (auto-applied on server start if configured)
npm run db:migrate

# Or manually:
psql $DATABASE_URL < server/migrations/001_add_metadata_storage.sql
psql $DATABASE_URL < server/migrations/002_add_trial_usage_tracking.sql
# ... repeat for all .sql files
```

---

## Production Database Setup (For Deployment)

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for:

- RDS setup (AWS)
- SSL configuration
- Automated backups
- Read replicas
- Scaling to 1000+ concurrent users
