# Fire-and-Forget Issue: Analytics & Credit Logging

**File**: `server/routes/extraction.ts`  
**Lines**: 202-229  
**Severity**: HIGH  
**Impact**: Data loss, billing inconsistency, analytics gaps, silent failures

---

## The Problem

Two critical async operations are **fire-and-forget** - started but not awaited:

```typescript
// Line 202-218: Fire-and-forget analytics logging
storage
  .logExtractionUsage({...})
  .catch((err) => console.error('Failed to log usage:', err));

// Line 220-228: Fire-and-forget credit deduction
if (chargeCredits && creditBalanceId) {
  storage
    .useCredits(
      creditBalanceId,
      creditCost,
      `Extraction: ${fileExt}`,
      mimeType
    )
    .catch((err) => console.error('Failed to use credits:', err));
}
```

### Why This Is Broken

The response is sent BEFORE these operations complete:

```typescript
// Response already sent above
res.json({ metadata });  // ← User gets response immediately

// These still running in background
storage.logExtractionUsage(...).catch(...);  // ← May fail after response
storage.useCredits(...).catch(...);           // ← May fail after response
```

**Scenarios where this breaks**:

1. **Database connection drops during logging**
   - User gets "success" response
   - Analytics log never reaches database
   - No record that extraction happened
   - Business metrics are wrong

2. **Credit deduction fails**
   - User gets "success" response
   - Credits NOT deducted
   - User got free extraction
   - Billing is wrong

3. **Process crashes during logging**
   - PM2/systemd restarts the service
   - Promise is lost
   - Analytics/credits lost forever

4. **Database timeout**
   - Operation takes 30 seconds
   - Process killed at 10 seconds
   - Partial writes possible
   - Data inconsistency

---

## Comparison to Working Code

Line 231-243 handles trial recording correctly with `await`:

```typescript
// ✅ CORRECT: Await and handle error
if (!bypassCredits && hasTrialAvailable && trialEmail) {
  try {
    await storage.recordTrialUsage({...});  // ← Waits for completion
  } catch (err) {
    console.error('Failed to record trial usage:', err);
  }
}

// ✅ CORRECT: Persist results
try {
  const savedRecord = await storage.saveMetadata({...});  // ← Waits
  metadata.id = savedRecord.id;
} catch (dbError) {
  console.error('[Extraction] Failed to save metadata to DB:', dbError);
}
```

But analytics and credits use fire-and-forget ❌

---

## The Fix

**Two approaches:**

### Option A: Await & Handle (Simple, Recommended)

```typescript
// Log analytics (must complete)
try {
  await storage.logExtractionUsage({
    tier: normalizedTier,
    fileExtension: fileExt,
    mimeType,
    fileSizeBytes: req.file.size,
    isVideo: mimeType.startsWith('video/'),
    isImage: mimeType.startsWith('image/'),
    isPdf: mimeType === 'application/pdf',
    isAudio: mimeType.startsWith('audio/'),
    fieldsExtracted: metadata.fields_extracted || 0,
    processingMs,
    success: true,
    ipAddress: req.ip || req.socket.remoteAddress || null,
    userAgent: req.headers['user-agent'] || null,
  });
} catch (err) {
  console.error('[Extraction] Failed to log usage:', err);
  // Log but continue - analytics is not blocking
}

// Deduct credits (MUST complete before responding)
if (chargeCredits && creditBalanceId) {
  try {
    const txn = await storage.useCredits(
      creditBalanceId,
      creditCost,
      `Extraction: ${fileExt}`,
      mimeType
    );
    
    if (!txn) {
      // useCredits returns null if balance insufficient
      return sendQuotaExceededError(
        res,
        'Credit deduction failed (balance may have changed)'
      );
    }
  } catch (err) {
    console.error('[Extraction] Failed to deduct credits:', err);
    return sendInternalServerError(
      res,
      'Failed to process credit transaction'
    );
  }
}
```

### Option B: Parallel with Timeout (Advanced)

If you need to avoid blocking the response, use `Promise.allSettled()`:

```typescript
// Start all background operations but don't wait for response
const backgroundOps = Promise.allSettled([
  storage.logExtractionUsage({...}),
  chargeCredits && creditBalanceId
    ? storage.useCredits(creditBalanceId, creditCost, ...)
    : Promise.resolve(null),
]).then((results) => {
  results.forEach((result, idx) => {
    if (result.status === 'rejected') {
      const op = ['usage', 'credits'][idx];
      console.error(`[Extraction] Background ${op} failed:`, result.reason);
      // Could send alert/metric here
    }
  });
}).catch((err) => {
  console.error('[Extraction] Background ops error:', err);
});

// Send response to user immediately
res.json({ metadata });

// DON'T await backgroundOps, but log if they fail
backgroundOps.catch(() => {});
```

**⚠️ Problem with Option B**: Still loses data if process crashes. Only use if analytics/logging is non-critical.

---

## Recommended Fix (Option A)

Apply these changes:

1. **Move credit check earlier** (already done at line 146-151)
2. **Await credit deduction** before sending response
3. **Await analytics logging** before sending response (non-blocking error)
4. **Return error if deduction fails**

**Logic flow**:
```
1. Validate file → Extract metadata
2. ✅ AWAIT: logExtractionUsage (analytics)
3. ✅ AWAIT: useCredits (billing) - MUST NOT FAIL SILENTLY
4. ✅ AWAIT: saveMetadata (database)
5. ✅ SEND: res.json(metadata)
```

---

## Code Changes Required

**Current** (Lines 199-229):
```typescript
// Log analytics
const fileExt = path.extname(req.file.originalname).toLowerCase().slice(1) || 'unknown';
storage
  .logExtractionUsage({...})
  .catch((err) => console.error('Failed to log usage:', err));

if (chargeCredits && creditBalanceId) {
  storage
    .useCredits(creditBalanceId, creditCost, ...)
    .catch((err) => console.error('Failed to use credits:', err));
}
```

**Fixed** (Same lines):
```typescript
// Log analytics (non-critical, error doesn't block response)
const fileExt = path.extname(req.file.originalname).toLowerCase().slice(1) || 'unknown';
try {
  await storage.logExtractionUsage({...});
} catch (err) {
  console.error('[Extraction] Failed to log usage:', err);
  // Don't block on analytics failure
}

// Deduct credits (CRITICAL, must succeed)
if (chargeCredits && creditBalanceId) {
  try {
    const txn = await storage.useCredits(
      creditBalanceId,
      creditCost,
      `Extraction: ${fileExt}`,
      mimeType
    );
    
    if (!txn) {
      return sendQuotaExceededError(
        res,
        'Credit deduction failed (insufficient balance)'
      );
    }
  } catch (err) {
    console.error('[Extraction] Failed to deduct credits:', err);
    return sendInternalServerError(
      res,
      'Unable to process credit transaction. Please try again.'
    );
  }
}
```

---

## Impact

### Before Fix
- User can exploit by crashing the process mid-extraction
- Analytics lost if database slow
- Credits never deducted
- Billing metrics wrong
- Silent failures, no alerts

### After Fix
- Credits guaranteed to deduct or request rejected
- Analytics logged reliably
- Errors returned to user if critical ops fail
- Billing accurate
- Visible failures in logs

---

## Testing

Create test case in `server/routes/extraction.test.ts`:

```typescript
describe('Credit deduction and analytics logging', () => {
  it('should deduct credits before responding to user', async () => {
    // Mock storage
    const useCreditsspy = jest.spyOn(storage, 'useCredits')
      .mockResolvedValue({ id: 'tx_1', amount: 10, ...});
    
    // Make extraction request
    const res = await request(app)
      .post('/api/extract')
      .attach('file', testImagePath);
    
    // Should have awaited useCredits
    expect(useCreditsSpy).toHaveBeenCalled();
    expect(res.status).toBe(200);
    expect(res.body.access.credits_charged).toBe(10);
  });

  it('should return error if credit deduction fails', async () => {
    jest.spyOn(storage, 'useCredits')
      .mockRejectedValue(new Error('DB timeout'));
    
    const res = await request(app)
      .post('/api/extract')
      .attach('file', testImagePath);
    
    // Should reject the request
    expect(res.status).toBeGreaterThanOrEqual(400);
    expect(res.body.error).toBeTruthy();
  });

  it('should not fail on analytics logging errors', async () => {
    jest.spyOn(storage, 'logExtractionUsage')
      .mockRejectedValue(new Error('DB down'));
    jest.spyOn(storage, 'useCredits')
      .mockResolvedValue({ id: 'tx_1' });
    
    const res = await request(app)
      .post('/api/extract')
      .attach('file', testImagePath);
    
    // Should still succeed even if analytics fails
    expect(res.status).toBe(200);
    expect(res.body.metadata).toBeTruthy();
  });
});
```

---

## Related Issues

This is part of a larger pattern in the codebase:
- **Similar issue in batch extraction** - check routes/forensic.ts
- **Similar issue in trial recording** - partially fixed (line 233 uses await)
- **Similar issue in metadata saving** - partially fixed (line 246 uses await)

---

## Summary

| Aspect | Current | Fixed |
|--------|---------|-------|
| **Credit deduction guarantee** | ❌ Silent failure possible | ✅ Must complete or reject |
| **Analytics logging** | ❌ Lost if DB slow/crashes | ✅ Logged but non-blocking |
| **Error visibility** | ❌ Hidden in console logs | ✅ Returned to user |
| **Billing accuracy** | ❌ Credits not deducted | ✅ Credits guaranteed deducted |
| **Data loss risk** | ❌ High (process crash) | ✅ Low (synchronous ops) |

---

**Status**: Ready for implementation ✅
