# Action Plan: From Verified Code to Verified Production

**Status:** Code fixes staged, tests passing locally. Production deployment unverified.

---

## Phase 1: Pre-Deployment Verification (Next 2 Hours)

### Task 1: Run Integration Tests

**Owner:** QA/Dev
**Time:** 30 minutes
**What:** Execute the 5 must-run validation scenarios

```bash
# Test 1: Device_free quota enforcement
# Make 3 extractions on same device
# Expect: 1st OK, 2nd OK, 3rd = 402 Payment Required

# Test 2: Quote replay prevention
# Use same quoteId twice
# Expect: Either rejected or marked as 'used' (prevent double-charge)

# Test 3: Credit atomicity
# Parallel extractions with insufficient balance
# Expect: No negative balances, no double-charging

# Test 4: GPS redaction
# Compare device_free vs paid extraction of same image
# Expect: device_free GPS rounded (37.77, -122.42)

# Test 5: Quote expiration
# Create quote, wait 15min, try to use
# Expect: Expired quote rejected
```

**Blocker:** If any test fails, return to code review before deployment.

---

### Task 2: Verify Cleanup Job Deployment

**Owner:** Ops/DevOps
**Time:** 15 minutes
**What:** Confirm quote cleanup is scheduled

```bash
# Verify cleanup job exists in production cron/scheduler
# Expected: Job runs hourly or every 15 minutes
# Action: Check logs for "Cleaned up X expired quotes" messages
# Risk: Without cleanup, images_mvp_quotes table grows indefinitely
```

**Success Criteria:** Cleanup job is running and deleting expired quotes.

---

### Task 3: Database Migration Verification

**Owner:** Ops/DevOps  
**Time:** 10 minutes
**What:** Confirm schema in production

```sql
-- Connect to production DB
-- Run verification query:
SELECT to_regclass('public.images_mvp_quotes') AS table_exists;
-- Expected: Returns table OID (not NULL)

-- Verify indexes:
SELECT indexname FROM pg_indexes
WHERE tablename = 'images_mvp_quotes';
-- Expected: 4 indexes
--   - idx_images_mvp_quotes_session_id
--   - idx_images_mvp_quotes_user_id
--   - idx_images_mvp_quotes_status
--   - idx_images_mvp_quotes_expires_at

-- Verify structure:
\d public.images_mvp_quotes
-- Expected: 14 columns, correct types
```

**Blocker:** If table doesn't exist, deploy schema migration before proceeding.

---

## Phase 2: Production Deployment (2-4 Hours)

### Task 4: Deploy Code Changes

**Owner:** DevOps
**Time:** 30 minutes
**What:** Deploy fixed code to production

**Files to deploy:**

- `server/routes/images-mvp.ts` (37 lines changed)
- `init.sql` (table definition, already in repo)

**Deployment steps:**

```bash
# 1. Merge PR to main (if not already merged)
# 2. Tag release: v2.0.1-hotfix
# 3. Deploy to production:
git checkout main
git pull
npm ci
npm run build
npm run db:push  # If migrations pending

# 4. Restart services
# (use your deployment tool)

# 5. Verify deployment
curl https://api.metaextract.com/api/health
# Expected: 200 OK, service online
```

**Rollback Plan:** If issues, revert to previous commit and redeploy.

---

### Task 5: Smoke Test Production Endpoints

**Owner:** QA
**Time:** 15 minutes
**What:** Quick verification that endpoints are responding

```bash
# Test 1: Health check
curl https://api.metaextract.com/api/health
# Expected: {"status":"ok"}

# Test 2: Quote endpoint (unauthenticated)
curl -X POST https://api.metaextract.com/api/images_mvp/quote \
  -H "Content-Type: application/json" \
  -d '{"files":[],"ops":{}}'
# Expected: 200 OK with quoteId

# Test 3: Analytics tracking
curl -X POST https://api.metaextract.com/api/images_mvp/analytics/track \
  -H "Content-Type: application/json" \
  -d '{"event":"test","data":{}}'
# Expected: 204 No Content

# Test 4: No 500 errors in logs
tail -100 /var/log/api.log | grep "500"
# Expected: No 500 errors (or only pre-deployment ones)
```

**Success:** All endpoints responding, no new errors.

---

## Phase 3: Monitoring (First 24 Hours)

### Task 6: Monitor Critical Metrics

**Owner:** Ops/DevOps
**Time:** Ongoing (first 24 hours)
**What:** Watch the alert thresholds

**Metrics Dashboard:**

```
Quote endpoint:
  - Response time (p95 < 100ms) ✅
  - Error rate (< 0.1%) ✅
  - Request count (baseline + X%) ✅

Extraction endpoint:
  - Response time (p95 < 2s) ✅
  - Error rate (< 0.1%) ✅
  - 402 responses (device_free quota blocks) → should see some

Database:
  - Connection pool usage (< 80%) ✅
  - Quote table row count (growing as expected) ✅
  - Index hit rate (> 90%) ✅

Background jobs:
  - Cleanup job execution (hourly) ✅
  - Rows deleted by cleanup (> 0) ✅

Rate limiting:
  - Reject count on /quote (verify limiting works) ✅
```

**Alert Thresholds (Set These):**

```
CRITICAL:
  - Quote endpoint error rate > 0.1%
  - Database connection pool exhaustion
  - Cleanup job fails for 2+ hours
  - Zero 402 responses after 1 hour (quota not enforcing)

WARNING:
  - Quote endpoint response time > 100ms
  - Images_mvp_quotes table > 1M rows (cleanup not working)
  - Rate limiting errors on non-rate-limited IPs
```

---

### Task 7: Validate Business Logic (Manual)

**Owner:** QA/Product
**Time:** 30 minutes after go-live
**What:** Spot-check that features work as intended

```bash
# Test 1: Device_free quota
# As anonymous user:
#   1. Extract file (device_free credit 1/2)
#   2. Extract file (device_free credit 2/2)
#   3. Extract file (should get 402 PAYMENT REQUIRED)
# Verify: Response says "quota exceeded"

# Test 2: Paid user works normally
# As authenticated user with credits:
#   1. Extract file (credits decremented)
#   2. Verify: Account balance decreased
#   3. Extract 10+ times (should all succeed until balance depleted)

# Test 3: GPS rounding
# As device_free user:
#   1. Extract an image with GPS
#   2. Sample response: check GPS field
#   3. Verify: Rounded to 2 decimals (37.77, -122.42 not 37.7749295, -122.4194155)

# Test 4: No negative balances
# Check database:
SELECT COUNT(*) FROM users WHERE credits < 0;
# Expected: 0 (no negative balances)

# Test 5: Cleanup job working
# Check logs:
grep "Cleaned up.*expired quotes" /var/log/background-jobs.log | tail -3
# Expected: Recent entries showing quotes deleted
```

---

## Phase 4: Final Sign-Off (End of Day 1)

### Task 8: Verify All Checklist Items

**Owner:** Tech Lead
**Time:** 15 minutes
**What:** Go through deployment checklist

```
SCHEMA DEPLOYMENT:
  ✅ images_mvp_quotes table exists in production
  ✅ All 14 fields present and correct type
  ✅ 4 indexes created (session_id, user_id, status, expires_at)

CODE DEPLOYMENT:
  ✅ All 953 tests passed before deployment
  ✅ Code compiled without errors
  ✅ No breaking API changes
  ✅ Backward compatible with existing clients

BUSINESS LOGIC:
  ✅ Quota enforcement working (3rd extraction = 402)
  ✅ GPS rounding applied (device_free only)
  ✅ Cleanup job running (quotes deleted)
  ✅ No negative credit balances
  ✅ Quote expiration enforced (15 min TTL)

OPERATIONS:
  ✅ Rate limiting active on /quote (50 req/15min)
  ✅ Alert thresholds configured
  ✅ Monitoring dashboard live
  ✅ Team trained on runbook

COMPLIANCE:
  ✅ GPS rounding verified against privacy policy
  ✅ GDPR compliance documented
  ✅ Redaction logic matches product spec
```

**Sign-Off:** If all checked, deployment is successful.

---

## Risk Mitigation

### If Test Failures Occur

**Scenario 1: 402 not returned on 3rd extraction**

- Check: freeQuotaMiddleware registered on route?
- Check: Device token being set in cookies?
- Check: Session counter incrementing correctly?
- Rollback: Revert code changes, redeploy previous version

**Scenario 2: GPS rounding not applied**

- Check: applyAccessModeRedaction called?
- Check: Access mode correctly set to 'device_free'?
- Check: Rounding function using Math.round(val \* 100) / 100?
- Rollback: Revert code changes

**Scenario 3: Cleanup job not deleting quotes**

- Check: Job is scheduled and running?
- Check: TTL index exists on expiresAt?
- Check: DELETE query completing without errors?
- Mitigation: Run manual cleanup: DELETE FROM images_mvp_quotes WHERE expiresAt < NOW();

**Scenario 4: Negative credit balance exists**

- Check: Extraction locked balance before charging?
- Check: No race conditions on concurrent requests?
- Mitigation: Contact affected users, credit their accounts

---

## Communication Template

**For Stakeholders:**

```
DEPLOYMENT SUMMARY
Date: 2026-01-17
Status: ✅ SUCCESSFUL (or ❌ ROLLBACK INITIATED)

WHAT WAS FIXED:
- Fixed 500 errors caused by missing database table
- Added quota enforcement (device_free: 2 free extractions per device)
- Implemented quote replay prevention
- Applied GPS rounding for privacy

WHAT WAS VALIDATED:
✅ 953 unit tests passing
✅ Integration tests verified quota enforcement
✅ Cleanup job confirmed running
✅ Zero negative credit balances
✅ Rate limiting active

MONITORING:
We will monitor:
- Quote endpoint response time
- Quota enforcement effectiveness (verify 402 responses)
- Cleanup job execution (quotes deleted hourly)
- Database performance
- Error rates

ISSUES ADDRESSED:
- Tests passing locally but business logic untested → Added integration tests
- Production deployment unverified → Verified schema, cleanup job, endpoints
- GPS privacy unclear → Documented rounding precision and privacy implications
- No end-to-end validation → Manual spot-checks performed

NEXT STEPS:
1. Monitor for 24 hours
2. Review metrics dashboard daily for 1 week
3. Update runbook with lessons learned
4. Plan for additional integration test coverage
```

---

## Success Criteria

✅ **Deployment is successful when:**

1. All 953 tests passing before deployment
2. Schema migrated to production (table + indexes verified)
3. Cleanup job running and deleting expired quotes
4. 3rd device_free extraction returns 402 (quota enforced)
5. GPS rounding applied correctly
6. No negative credit balances in database
7. Rate limiting active on /quote endpoint
8. Zero 500 errors in production logs
9. All manual validation tests pass
10. Monitoring alerts configured and functioning

❌ **Roll back if:**

1. Tests fail before deployment
2. Schema migration fails
3. Quota enforcement not working (3rd extraction doesn't return 402)
4. Cleanup job not running
5. GPS not rounding correctly
6. Negative balances appear in database
7. Production shows increased error rate (> 0.1%)
8. Monitoring indicates system degradation

---

**Owner:** Deployment Lead
**Timeline:** 2026-01-17 (today, in phases)
**Status:** READY FOR DEPLOYMENT (pending Task 1-3)
