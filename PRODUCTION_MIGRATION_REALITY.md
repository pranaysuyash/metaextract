# CRITICAL: Production DB Migration Reality Analysis

**Date:** January 17, 2026
**Status:** ⚠️ CRITICAL FINDING

---

## Discovery: Two Deployment Paths

### Path 1: Docker Deployment (Fresh) ✅ SAFE

```
docker-compose.yml mounts:
  ./init.sql:/docker-entrypoint-initdb.d/init.sql

When postgres:15-alpine container starts:
  - PostgreSQL runs all .sql files in /docker-entrypoint-initdb.d/
  - images_mvp_quotes table is CREATED
  - All 4 indexes are CREATED

Result: ✅ Table exists automatically on fresh deploy
```

### Path 2: Railway Production (Existing DB) ⚠️ RISK

```
railway.toml only specifies:
  startCommand = "npm start"
  healthcheckPath = "/api/health"

No migration mechanism defined:
  - init.sql is NOT automatically applied to existing DB
  - No Drizzle migrations configured
  - No SQL initialization in server startup

If production DB is running and init.sql hasn't been applied:
  - Existing DB schema still missing images_mvp_quotes
  - New code references non-existent table
  - Result: ❌ 500 errors in production

When the merged PR was deployed to production:
  - Code expected images_mvp_quotes table
  - If production DB wasn't freshly initialized, table didn't exist
  - Confirmed by 500 errors on /api/images_mvp/* endpoints
```

---

## What Actually Fixes It (In Each Scenario)

### Scenario A: Using Docker (Recommended)

```bash
# Fresh deploy:
docker-compose up -d
# Result: All tables created, including images_mvp_quotes ✅

# Existing container with old DB:
docker-compose down
docker volume rm metaextract_postgres_data  # Wipe old DB
docker-compose up -d
# Result: Fresh schema, all tables created ✅
```

### Scenario B: Railway Production (Current)

```bash
# Need manual schema update via:
# Option 1: Direct psql (not ideal, risky)
psql -U metaextract -d metaextract -f init.sql

# Option 2: Add migration step to deployment
# Option 3: Use Drizzle migrations (recommended)
npm run db:push  # Applies schema changes
```

### Scenario C: Manual/Hybrid Setup

```bash
# Apply init.sql directly
psql $DATABASE_URL -f init.sql
```

---

## Current Production State Check

### Evidence Needed

To prove production is actually fixed, we need:

```sql
-- Query 1: Does table exist?
SELECT to_regclass('public.images_mvp_quotes');
-- Result: MUST return oid (not NULL)

-- Query 2: Do all columns exist?
SELECT column_name FROM information_schema.columns
WHERE table_name = 'images_mvp_quotes';
-- Result: MUST show all 14 columns

-- Query 3: Do all indexes exist?
SELECT indexname FROM pg_indexes
WHERE tablename = 'images_mvp_quotes';
-- Result: MUST show 4 indexes
```

### Verification in Local DB

```bash
psql -U postgres -d metaextract -c "
  SELECT to_regclass('public.images_mvp_quotes');"
# Output should show: "images_mvp_quotes" (oid number)
```

---

## Risk Assessment

### 🔴 HIGH RISK

- Production has existing database
- init.sql changes were only added to source code
- No deployment mechanism applies schema changes to running DB
- **Probability production is still broken: 95%**

### 🟡 MEDIUM RISK

- Docker-based staging environments may not have volume cleared
- Old cached images might have old schema

### 🟢 LOW RISK

- New fresh deployments from scratch (rare)
- Developers running locally (we control environment)

---

## Recommended Fix (For Production)

### Short-term (Immediate)

1. Connect to production database directly
2. Run: `psql $PRODUCTION_DATABASE_URL -f init.sql`
3. Verify: `SELECT to_regclass('public.images_mvp_quotes');`

### Long-term (Next Deploy)

1. Add Drizzle migration system to codebase
2. Use `npm run db:push` in deployment script
3. Or add schema validation to server startup
4. Document deployment checklist

### Example: Server Startup Validation

```typescript
// server/index.ts (add at startup)
async function ensureSchemaExists() {
  const hasTable = await db.query.images_mvp_quotes.findFirst();
  if (!hasTable) {
    console.error('❌ CRITICAL: images_mvp_quotes table missing!');
    console.error('Run: psql $DATABASE_URL -f init.sql');
    process.exit(1);
  }
}

await ensureSchemaExists();
```

---

## Summary

**The Problem:** Code merged with database table references, but table wasn't guaranteed to exist in production.

**The Fix:** init.sql now includes table definition, but production database likely doesn't have it applied yet.

**The Proof Needed:**

1. Connect to production DB
2. Run schema verification query
3. If missing: Apply init.sql directly
4. If present: Move to functionality tests (quota, credits, redaction)

**Next Steps:** Execute production DB check and apply schema if needed.
