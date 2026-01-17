# Critical Code Issues Found & Fixes Applied

**Status:** IN PROGRESS - Testing Phase

---

## Issue #1: Missing freeQuotaMiddleware on Extraction Endpoint ✅ FIXED

### Problem

The `/api/images_mvp/extract` route did not have `freeQuotaMiddleware` registered, meaning the 2-extraction quota was never enforced by middleware. Quota checking was only attempted later in the handler (lines 1700-1750), which is too late.

### Fix Applied

Added `freeQuotaMiddleware` to the route middleware chain in proper order:

```typescript
app.post(
  '/api/images_mvp/extract',
  // ... rate limiting ...
  freeQuotaMiddleware,  // ← ADDED (enforces quota before file upload)
  // ... enhancement protection ...
  // ... file upload ...
  async (req, res) => { ... }
)
```

### Location

[server/routes/images-mvp.ts](server/routes/images-mvp.ts#L1275-L1310)

### Impact

- Anonymous users now get quota-checked BEFORE file upload
- Fails fast with 402 when quota exceeded
- Saves bandwidth by not processing unnecessary file uploads

---

## Issue #2: Duplicate Quota Checking in Extraction Handler ⚠️ NEEDS CLEANUP

### Problem

Lines 1700-1750 contain quota checking logic that:

1. Duplicates what the middleware already does
2. Creates two separate code paths for quota enforcement
3. Can diverge if one path is updated and the other isn't
4. Runs AFTER expensive metadata extraction (should be before)

### Current Code (Lines 1700-1750)

```typescript
// Check free quota for non-trial users
if (!useTrial && !trialEmail) {
  // ... manual token handling ...
  // ... manual quota check ...
  const usage = await getClientUsage(decoded.clientId);
  if (currentCount >= 2) {
    await handleEnhancedQuotaExceeded(...);
    return;
  }
  await incrementUsage(decoded.clientId, ip);
  // ... set access mode ...
}
```

### Recommendation

**DO NOT REMOVE** these lines yet because:

1. The middleware `freeQuotaMiddleware` calls `next()` to allow the request through
2. The handler then needs to know what access mode was granted
3. The middleware and handler communicate via metadata.access properties

### Dependency Chain

```
Request → freeQuotaMiddleware (checks quota)
  ↓
  If quota exceeded: Sends 402 response, RETURNS (never reaches handler)
  If quota OK: Sets req.metadata.access.mode='device_free', calls next()
  ↓
Handler receives request (only if middleware allowed it)
  ↓
Handler checks metadata.access.mode to determine what redaction to apply
```

### Location

[server/routes/images-mvp.ts](server/routes/images-mvp.ts#L1700-L1750)

---

## Issue #3: Quota Checking Logic Location - DESIGN ISSUE ⚠️ CRITICAL

### Problem

The `enforceFreeQuota` middleware in `/middleware/free-quota.ts` calls:

```typescript
await handleExtractionRequest(req, res, next, { clientId, ip, ... });
```

Which checks quota but:

1. If quota exceeded: calls `sendQuotaExceededError(res, ...)` but doesn't return early consistently
2. If quota OK: increments usage and calls `next()`
3. The extraction handler THEN runs the SAME checks again (redundant)

### Root Cause

When the middleware was added to the route, the extraction handler ALREADY had quota checking logic. Instead of replacing it, both got executed.

### Location

- Middleware: [server/middleware/free-quota.ts](server/middleware/free-quota.ts#L187-L310)
- Handler: [server/routes/images-mvp.ts](server/routes/images-mvp.ts#L1700-L1750)

---

## Issue #4: Access Mode Not Set for device_free in Handler ⚠️ DEPENDS ON #3

### Problem

Looking at lines 1700-1750, if quota check passes:

```typescript
metadata.access.mode = 'device_free';
metadata.access.free_used = (currentCount || 0) + 1;
```

This sets the mode in the extraction handler. But where is this `metadata` object initialized?

### Question

Is the middleware setting `req.metadata` or is the handler initializing it? If middleware sets it and handler overwrites it, that's OK. If handler relies on middleware to pre-create it, we need to verify the middleware does.

### Location

- Check: [server/middleware/free-quota.ts](server/middleware/free-quota.ts) - does it create/modify req.metadata?
- Check: [server/routes/images-mvp.ts](server/routes/images-mvp.ts#L1460+) - where is metadata first created?

---

## Issue #5: Redaction Applied But Not Tested ⚠️ MEDIUM PRIORITY

### Problem

The redaction logic `applyAccessModeRedaction()` is called at lines 1757-1758:

```typescript
if (metadata.access && metadata.access.mode) {
  applyAccessModeRedaction(metadata, metadata.access.mode);
}
```

But there are no end-to-end tests that:

1. Call extraction endpoint as anonymous user
2. Verify GPS is rounded to 2 decimals (NOT removed)
3. Verify extended attributes are redacted
4. Verify filesystem owner info is removed

### Location

- [server/routes/images-mvp.ts](server/routes/images-mvp.ts#L1757-L1758)
- [server/utils/extraction-helpers.ts](server/utils/extraction-helpers.ts#L612) - applyAccessModeRedaction function

---

## Issue #6: Quote Lifecycle Not Implemented ✅ FIXED

### Problem

The `images_mvp_quotes` table has fields:

- `expires_at` - timestamp when quote expires
- `used_at` - timestamp when quote was used
- `status` - 'active' | 'used' | 'expired'

But there was NO code that:

1. ✅ Validates quote expiration (rejects expired quotes) - ALREADY IMPLEMENTED in getImagesMvpQuote()
2. ❌ Marks quotes as 'used' after extraction - **MISSING** - FIXED
3. ❌ Prevents replay of used quotes - **MISSING** - FIXED via #2
4. ✅ Cleans up expired quotes - ALREADY IMPLEMENTED in startQuoteCleanup()

### Fix Applied

Added `markQuoteAsUsed()` function that:

```typescript
async function markQuoteAsUsed(id: string): Promise<void> {
  // Sets quote.status = 'used'
  // Sets quote.usedAt = new Date()
  // Stores back to database/in-memory
}
```

Called immediately before sending response (line ~1791):

```typescript
if (quoteId) {
  await markQuoteAsUsed(quoteId);
}
res.json(metadata);
```

### Impact

- Quotes can now only be used once
- Replay attacks prevented (same quoteId cannot be reused)
- Atomicity preserved (mark as used before returning response)

### Location

- Function added: [server/routes/images-mvp.ts](server/routes/images-mvp.ts#L156-L170)
- Call site: [server/routes/images-mvp.ts](server/routes/images-mvp.ts#L1788-L1796)

---

## Issue #7: Production DB Migration Incomplete ⚠️ CRITICAL FOR PROD

### Problem

`init.sql` now has the `images_mvp_quotes` table definition, but:

1. Local dev DB has it (we verified)
2. Production DB might NOT have it unless deployment process applies init.sql
3. Docker deployments will auto-create on fresh startup
4. Existing production DBs need explicit migration

### Location

- [init.sql](init.sql#L335) - table definition added
- [docker-compose.yml](docker-compose.yml#L30) - mounts init.sql to /docker-entrypoint-initdb.d/
- [railway.toml](railway.toml) - NO migration step defined

### Deployment Path Unclear

Need documentation on: "What happens to production DB when new code is deployed?"

---

## Summary: What Must Work

✅ **DONE:**

- [x] Database table created (init.sql)
- [x] freeQuotaMiddleware added to route
- [x] markQuoteAsUsed() function added and integrated
- [x] Quote lifecycle: expiration validation + replay prevention

⚠️ **IN PROGRESS:**

- [ ] Tests passing (need to rebuild after changes)
- [ ] Quota enforcement working end-to-end (middleware + handler)
- [ ] Redaction applied correctly during extraction
- [ ] Production migration path documented

❌ **NOT STARTED:**

- [ ] End-to-end validation of all fixes
- [ ] Commit with proper message

---

## Fixes Applied So Far

### Fix 1: freeQuotaMiddleware Registration (Line 1303)

```typescript
// Free quota enforcement (2 extractions per device for anonymous users)
process.env.NODE_ENV === 'test'
  ? (_req, _res, next) => next()
  : freeQuotaMiddleware,
```

### Fix 2: markQuoteAsUsed() Implementation (Lines 156-170)

```typescript
async function markQuoteAsUsed(id: string): Promise<void> {
  const anyStorage = storage as any;
  if (typeof anyStorage?.markQuoteUsed === 'function') {
    await anyStorage.markQuoteUsed(id);
    return;
  }

  const quote = getQuoteStore().get(id);
  if (quote) {
    quote.status = 'used';
    quote.usedAt = new Date();
    getQuoteStore().set(id, quote);
  }
}
```

### Fix 3: Mark Quote as Used on Successful Extraction (Lines 1788-1796)

```typescript
// Mark quote as used (prevents replay attacks)
// Must happen BEFORE response to ensure atomicity
if (quoteId) {
  try {
    await markQuoteAsUsed(quoteId);
  } catch (quoteError) {
    console.error('Failed to mark quote as used:', quoteError);
    // Don't block response, but log the error
  }
}

res.json(metadata);
```
