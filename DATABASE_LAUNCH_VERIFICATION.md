# Images MVP Launch: Database Verification Checklist

**Date**: January 5, 2026  
**Related**: IMAGES_MVP_LAUNCH_CONSULTATION.md, LAUNCH_READINESS_STATUS.md  
**Purpose**: Database validation before images_mvp launch

---

## Quick Summary

Your database configuration has **2 critical issues** that must be fixed before launch:

1. **Connection Pool Too Small** (10 max, fails at 11 users)
2. **Missing Performance Indexes** (queries will slow down)

Both are quick fixes but essential for launch stability.

---

## 🔴 Critical Issue #1: Connection Pool Size

**Location**: `server/db.ts:28`  
**Current Value**: `max: 10`  
**Problem**: Database fails when 11th concurrent user uploads  
**Impact**: 503 "service unavailable" errors at scale  

### Verification
```bash
# Check current pool size
grep -A3 "const DEFAULT_POOL_CONFIG" server/db.ts

# Result should show:
# max: 10  ← THIS IS THE PROBLEM
```

### Fix
```typescript
// server/db.ts line 27-31
const DEFAULT_POOL_CONFIG = {
  max: 20,  // ← Increase from 10 to 20
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};
```

### Test After Change
```bash
# Start server with monitoring
NODE_DEBUG=pg npm run dev:server

# In another terminal, simulate 25 concurrent connections
for i in {1..25}; do
  psql $DATABASE_URL -c "SELECT 1;" &
done
wait

# Check server logs - should NOT see "pool error" messages
```

**Status**: ❌ NOT FIXED (needs implementation)

---

## 🔴 Critical Issue #2: Missing Performance Indexes

**Location**: Database schema  
**Problem**: No indexes on high-traffic tables = slow queries  
**Impact**: Response times degrade as data accumulates

### Verification
```bash
# Connect to database
psql $DATABASE_URL

# Check what indexes exist
\d extraction_analytics
\d image_mvp_events
\d trial_usages
```

**Expected Output**: Should show several indexes with names like:
```
Indexes:
    "extraction_analytics_pkey" PRIMARY KEY
    "idx_extraction_requested_at" 
    "idx_extraction_tier"
    "idx_extraction_success"
```

**If Missing**: Run these SQL commands:

```sql
-- Indexes on extraction_analytics (high-traffic table)
CREATE INDEX IF NOT EXISTS idx_extraction_requested_at 
  ON extraction_analytics(requested_at DESC);
CREATE INDEX IF NOT EXISTS idx_extraction_tier 
  ON extraction_analytics(tier);
CREATE INDEX IF NOT EXISTS idx_extraction_success 
  ON extraction_analytics(success);

-- Indexes on image_mvp_events (analytics table)
CREATE INDEX IF NOT EXISTS idx_image_mvp_events_user 
  ON image_mvp_events(user_id);
CREATE INDEX IF NOT EXISTS idx_image_mvp_events_type 
  ON image_mvp_events(event_type);
CREATE INDEX IF NOT EXISTS idx_image_mvp_events_created 
  ON image_mvp_events(created_at DESC);

-- Indexes on trial_usages (credit system)
CREATE INDEX IF NOT EXISTS idx_trial_usages_user 
  ON trial_usages(user_id);
CREATE INDEX IF NOT EXISTS idx_trial_usages_session 
  ON trial_usages(session_id);
```

**Status**: ❓ UNKNOWN (needs verification)

---

## 🟠 High Priority: Race Condition Prevention

**Issue**: Credit deduction happens concurrently, can cause inconsistency  
**Verification**:

```sql
-- Check credit_balances table structure
\d+ credit_balances

-- Should show:
-- - PRIMARY KEY on (user_id)
-- - NOT NULL on balance column
-- - CHECK constraint: balance >= 0
```

**If Constraints Missing**:
```sql
-- Add constraints
ALTER TABLE credit_balances 
  ADD CONSTRAINT check_balance_nonnegative CHECK (balance >= 0);
```

**Status**: ✅ LIKELY OK (security review shows fix was done)

---

## 🟡 Important: Backup Strategy

**Before Launch**: Test backup/restore process

```bash
# Create test backup
pg_dump $DATABASE_URL > /tmp/backup-$(date +%Y%m%d).sql

# Test restore (critical!)
# First, create a test database
createdb metaextract_test

# Restore into test DB
psql metaextract_test < /tmp/backup-$(date +%Y%m%d).sql

# Verify (count rows)
psql metaextract_test -c "
  SELECT 
    (SELECT COUNT(*) FROM users) as user_count,
    (SELECT COUNT(*) FROM extraction_analytics) as extraction_count,
    (SELECT COUNT(*) FROM image_mvp_events) as event_count;
"

# Cleanup
dropdb metaextract_test
```

**Action**: Add to crontab for daily backups:
```bash
0 2 * * * pg_dump $DATABASE_URL | gzip > /backup/metaextract-$(date +\%Y\%m\%d).sql.gz
```

**Status**: ⚠️ NEEDS SETUP

---

## 🟡 Important: Migration Verification

**Verify all migrations applied**:

```bash
# Check migrations directory
ls -la server/migrations/

# Should show:
# 001_add_metadata_storage.sql
# 002_add_trial_usage_tracking.sql
# 003_add_trial_usage_count.sql
# 004_add_ui_events.sql
# 005_add_credit_system.sql

# Check database for these tables
psql $DATABASE_URL -c "
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema='public' 
  ORDER BY table_name;
"

# Should include:
# - users
# - subscriptions
# - extraction_analytics
# - image_mvp_events (or ui_events)
# - trial_usages
# - credit_balances
```

**If Any Missing**: Apply manually:
```bash
psql $DATABASE_URL < server/migrations/001_add_metadata_storage.sql
psql $DATABASE_URL < server/migrations/002_add_trial_usage_tracking.sql
# ... etc for all files
```

**Status**: ⚠️ NEEDS VERIFICATION

---

## Database Health Monitoring

### Before Launch: Enable Monitoring

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
SELECT pg_reload_conf();

-- Enable pg_stat_statements extension (for query analysis)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### Daily Monitoring Queries

```bash
# Add these to a monitoring script (run daily)

# 1. Check connection count
psql $DATABASE_URL -c "
  SELECT datname, count(*) as connections 
  FROM pg_stat_activity 
  GROUP BY datname
  ORDER BY connections DESC;"

# 2. Check slowest queries
psql $DATABASE_URL -c "
  SELECT query, calls, mean_time 
  FROM pg_stat_statements 
  WHERE mean_time > 100  -- queries slower than 100ms
  ORDER BY mean_time DESC 
  LIMIT 10;"

# 3. Check table sizes
psql $DATABASE_URL -c "
  SELECT schemaname, tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
  FROM pg_tables 
  WHERE schemaname='public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# 4. Check database size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size('metaextract'));"
```

---

## Pre-Launch Database Checklist

```
CONNECTION & POOL
□ Pool max set to 20+ (currently 10 - FIX THIS)
□ Test with 20 concurrent connections passes
□ No "pool error" or "too many connections" errors

INDEXES
□ extraction_analytics has indexes (VERIFY)
□ image_mvp_events has indexes (VERIFY)
□ trial_usages has indexes (VERIFY)
□ Query plans use indexes (VERIFY with EXPLAIN)

MIGRATIONS
□ All 5 migrations applied
□ All required tables exist
□ Table structures match schema.ts

DATA INTEGRITY
□ Foreign keys in place
□ NOT NULL constraints on critical columns
□ Unique constraints prevent duplicates
□ CHECK constraints on balances (balance >= 0)

PERFORMANCE
□ Slow query logging enabled
□ pg_stat_statements available
□ Query execution plans reviewed

BACKUPS
□ Daily backup script configured
□ Backup restore tested (end-to-end)
□ Backup storage on separate disk/server

MONITORING
□ Connection count monitoring ready
□ Table size monitoring ready
□ Slow query monitoring ready
□ Alert thresholds defined
```

---

## Specific Images MVP Database Concerns

### 1. User Identification
**Tables**: `users`, `subscriptions`, `credit_balances`  
**Concern**: User A should not see User B's data  
**Verification**:
```sql
-- Verify foreign key constraints
SELECT 
  constraint_name, 
  table_name, 
  referenced_table_name 
FROM information_schema.referential_constraints 
WHERE table_schema = 'public';

-- Should show: credit_balances → users.id
```

### 2. Credit Deduction Atomicity
**Tables**: `credit_balances`, `trial_usages`  
**Concern**: Credits deducted exactly once, even with concurrent uploads  
**Verification**:
```sql
-- Create test user and verify transaction isolation
BEGIN;
UPDATE credit_balances SET balance = balance - 1 
  WHERE user_id = 'test-user';
SELECT balance FROM credit_balances WHERE user_id = 'test-user';
ROLLBACK;

-- Balance should NOT change after ROLLBACK
SELECT balance FROM credit_balances WHERE user_id = 'test-user';
```

### 3. Analytics Event Tracking
**Tables**: `image_mvp_events`, `extraction_analytics`  
**Concern**: Events recorded correctly for conversion funnel analysis  
**Verification**:
```sql
-- Check event structure
\d image_mvp_events

-- Sample events
SELECT event_type, COUNT(*) as count 
FROM image_mvp_events 
GROUP BY event_type;

-- Should show events like: 
-- - landing_viewed
-- - upload_selected
-- - analysis_started
-- - analysis_completed
-- - paywall_viewed
-- - purchase_completed
```

### 4. Trial User Tracking
**Tables**: `trial_usages`, `users`  
**Concern**: Free tier users only get 2 extractions, then must pay  
**Verification**:
```sql
-- Check trial tracking
\d trial_usages

-- Columns should include:
-- - user_id
-- - extraction_count or similar
-- - tier (free, professional, etc)
-- - created_at

-- Verify user tier defaults to 'free'
SELECT tier, COUNT(*) FROM users GROUP BY tier;
-- Should show most users with tier='free'
```

---

## Post-Launch Monitoring

### Daily Tasks
```bash
# 1. Check backup completed
ls -lh /backup/metaextract-$(date +%Y%m%d).sql.gz

# 2. Check database size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size('metaextract'));"

# 3. Check connection count
psql $DATABASE_URL -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# 4. Check for errors
grep ERROR /var/log/postgresql/postgresql.log | tail -20
```

### Weekly Tasks
```bash
# 1. Review slow queries
psql $DATABASE_URL -c "
  SELECT query, calls, mean_time 
  FROM pg_stat_statements 
  WHERE mean_time > 1000 
  ORDER BY mean_time DESC LIMIT 10;"

# 2. Analyze table growth
psql $DATABASE_URL -c "
  SELECT tablename, pg_size_pretty(pg_total_relation_size('public.'||tablename))
  FROM pg_tables WHERE schemaname='public'
  ORDER BY pg_total_relation_size('public.'||tablename) DESC;"

# 3. Verify backups
gunzip < /backup/metaextract-$(date -d '7 days ago' +%Y%m%d).sql.gz | psql metaextract_test
# (on separate test DB)
```

---

## Troubleshooting

### If: "too many connections"
```bash
# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Increase pool size (see Fix #1 above)
# Then restart server
```

### If: Slow extraction queries
```bash
# Check indexes
psql $DATABASE_URL -c "\d extraction_analytics"

# Create missing indexes (see Fix #2 above)

# Analyze slow query
psql $DATABASE_URL -c "
  EXPLAIN ANALYZE 
  SELECT * FROM extraction_analytics 
  WHERE user_id = 'xxx' 
  AND requested_at > NOW() - INTERVAL '1 day';"
```

### If: Backup restore fails
```bash
# Check backup file size
ls -lh /backup/metaextract-*.sql.gz

# Verify backup integrity
gunzip -t /backup/metaextract-latest.sql.gz

# Try restore with verbose output
psql $DATABASE_URL -v ON_ERROR_STOP=on < backup-file.sql
```

---

## Success Criteria

✅ **Database Ready for Launch When**:
- [ ] Pool size: 20+ (currently 10 - NEEDS FIX)
- [ ] Performance indexes created (NEEDS VERIFICATION)
- [ ] All migrations applied
- [ ] Backup/restore tested and working
- [ ] Monitoring queries return data
- [ ] No "pool error" messages in logs
- [ ] Credit system race condition fixed (✅ already done)

---

## Related Documents

- `docs/LOCAL_DB_SETUP.md` - Local development setup
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Production deployment
- `IMAGES_MVP_LAUNCH_CONSULTATION.md` - Full launch analysis
- `LAUNCH_READINESS_STATUS.md` - Security review completed
- `shared/schema.ts` - Database schema definitions

---

**Status**: Database setup is ~80% ready. Need to fix connection pool size and verify indexes before launch.
