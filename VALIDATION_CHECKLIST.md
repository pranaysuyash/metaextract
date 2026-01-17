# Remaining Validation Checklist

**Date:** January 17, 2026  
**Status:** Ready for Testing Phase

---

## Critical Validations Needed Before Commit

### A. Code Compilation ⏳ PENDING

- [ ] TypeScript compilation succeeds
- [ ] No ESLint errors
- [ ] Import statements resolve correctly

**How to verify:**

```bash
npm run build
npm run lint
```

---

### B. Unit Tests Pass ⏳ PENDING

- [ ] All 953+ tests pass
- [ ] No new test failures from changes
- [ ] Quota middleware integration tests work

**How to verify:**

```bash
npm run test:ci
```

---

### C. Device_Free Quota Enforcement ⏳ PENDING

**Test scenario:** Anonymous user making 3 extractions

```
1. First extraction → freeQuotaMiddleware checks quota (0 < 2) → PASS
   - Request proceeds to extraction
   - metadata.access.mode = 'device_free'
   - metadata.access.free_used = 1
   - Response: HTTP 200

2. Second extraction → freeQuotaMiddleware checks quota (1 < 2) → PASS
   - Request proceeds to extraction
   - metadata.access.mode = 'device_free'
   - metadata.access.free_used = 2
   - Response: HTTP 200

3. Third extraction → freeQuotaMiddleware checks quota (2 >= 2) → FAIL
   - sendQuotaExceededError() called
   - Response: HTTP 402 (Payment Required)
   - Never reaches extraction handler
```

**Evidence needed:**

- [ ] Cookie with device token generated
- [ ] Extractionswhere succeeds twice
- [ ] Third extraction returns 402
- [ ] Database trial_usages shows 2 uses

---

### D. Quote Lifecycle ⏳ PENDING

**Test scenario:** Quote creation, usage, and replay prevention

```
1. Create quote → /api/images_mvp/quote
   - Response includes quoteId
   - images_mvp_quotes table: status='active', usedAt=NULL

2. Use quote → /api/images_mvp/extract?quoteId=X
   - getImagesMvpQuote(X) checks: status='active' ✓
   - Extraction proceeds
   - markQuoteAsUsed(X) called
   - images_mvp_quotes table: status='used', usedAt=NOW()

3. Replay quote → /api/images_mvp/extract?quoteId=X again
   - getImagesMvpQuote(X) checks: status='active' ✗ (now 'used')
   - Returns undefined
   - Extraction fails gracefully
```

**Evidence needed:**

- [ ] Quote created successfully
- [ ] Quote used and marked as 'used' in DB
- [ ] Replay rejected (quote marked inactive)
- [ ] Expiration prevents very old quotes

---

### E. Quote Expiration ⏳ PENDING

**Test scenario:** Quote expires after 15 minutes

```
1. Create quote
   - expiresAt = NOW() + 15 minutes

2. Within 15 minutes: quote works
   - getImagesMvpQuote checks: new Date() < expiresAt ✓

3. After 15 minutes: quote rejected
   - getImagesMvpQuote checks: new Date() < expiresAt ✗
   - Returns undefined
   - Extraction fails with "expired quote" error
```

**Evidence needed:**

- [ ] Quote response shows correct expiresAt timestamp
- [ ] Expiration check logic verified in code
- [ ] (Functional test requires 15-minute wait or time-mocking)

---

### F. Redaction Applied to device_free ⏳ PENDING

**Test scenario:** Anonymous extraction shows redacted response

```
Expected redactions:
- GPS: rounded to 2 decimals (NOT removed)
  Original: 37.7749295, -122.4194155
  Redacted: 37.77, -122.42

- Extended attributes: keys visible, values NULL

- Filesystem: owner/uid/gid/inode/device removed

- Thumbnails: binary stripped, dimensions kept

- Burned text: extracted_text = NULL, gps removed
```

**Evidence needed:**

- [ ] Extract as anonymous user
- [ ] Verify GPS is rounded (not null, not full precision)
- [ ] Verify filesystem.owner is removed
- [ ] Verify extended_attributes.attributes are nulled
- [ ] Verify thumbnail binary is removed

---

### G. Paid User Credits Work ⏳ PENDING

**Test scenario:** Paid user credit deduction is atomic

```
1. Create paid user with known balance (e.g., 100 credits)

2. Make extraction quote
   - Quote shows actual cost (e.g., 12 credits)

3. Make extraction with quoteId
   - Handler deducts credits
   - Balance becomes 88
   - Database transaction commits

4. Check concurrent safety
   - Multiple requests with same quoteId
   - Only one should succeed (first one)
   - Others should fail (quote already used)
```

**Evidence needed:**

- [ ] Credit balance decreases exactly once
- [ ] No double-charging on concurrent requests
- [ ] Quote marked as used prevents replay

---

### H. Production DB Migration Path ⏳ PENDING

**Documentation needed:**

- [ ] How does init.sql get applied to production?
- [ ] Docker deployments: auto-applied ✓
- [ ] Railway deployments: manual or automatic?
- [ ] Existing production DBs: migration command documented

**Evidence:**

- [ ] Deployment process reviewed
- [ ] Migration step identified or added
- [ ] Plan B if manual: SQL command provided

---

## After All Validations Pass

```
✓ Code compiles
✓ Tests pass (953/953)
✓ Quota enforcement works
✓ Quote lifecycle works
✓ Redaction working
✓ Credits atomic
✓ Production path documented

THEN:
git add -A
git commit -m "CRITICAL FIXES: Device quota enforcement, quote replay prevention, redaction validation

Fixes
- Added freeQuotaMiddleware to /api/images_mvp/extract route
- Implemented markQuoteAsUsed() to prevent quote replay attacks
- Integrated quote lifecycle with extraction success path
- Images MVP now enforces 2-extraction limit for anonymous users
- Quotes can only be used once (prevents double-charging)
- All tests passing, production ready"
```

---

## Blockers

🔴 **BLOCKING:** Tests must pass before commit  
🔴 **BLOCKING:** Code must compile without errors  
🟡 **CRITICAL:** Quota enforcement must be validated  
🟡 **CRITICAL:** Quote lifecycle must be validated

---

## Timeline

- **Immediate:** Build & tests
- **If all pass:** Manual validation of key flows
- **If all validated:** Commit with confidence
