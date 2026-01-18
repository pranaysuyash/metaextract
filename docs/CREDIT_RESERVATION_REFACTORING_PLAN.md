# Credit Reservation Refactoring Plan

## Status: IN PROGRESS

## Objective

Fix HIGH-risk credit enforcement issues by implementing reserve-commit-release pattern.

## Completed Steps

### ✅ 1. Schema & Migration (DONE)

- Added `creditHolds` table to shared/schema.ts
- Created migration 010_add_credit_holds.sql
- Applied migration to database
- Added unique index on requestId for idempotency

### ✅ 2. Storage Layer Methods (DONE)

- Implemented `reserveCredits()` with SELECT FOR UPDATE locking
- Implemented `commitHold()` to finalize charges
- Implemented `releaseHold()` to refund on failure
- Implemented `cleanupExpiredHolds()` for maintenance
- Added methods to IStorage interface in types.ts
- Added CreditHold type exports

### ✅ 3. Health Check Helper (DONE)

- Added `isDatabaseHealthy()` function to images-mvp.ts

## Remaining Work

### 4. Refactor Extraction Endpoint (IN PROGRESS)

Current problematic flow (lines 1530-1900):

```
1530: Start handler
1540: File validation (mime + extension)
1600: Compute credit cost
1630: Check trial status
1650: Check credit balance (TOO LATE - happens after upload)
1710: Python extraction begins (BEFORE final credit verification!)
1867: Credit deduction with useCredits() (RACE CONDITION WINDOW)
1900: Record trial usage
2010: Response
```

Required new flow:

```
1530: Start handler
1531: Generate extractionId = crypto.randomUUID() for idempotency
1532: Check DB health - FAIL CLOSED if unhealthy
1540: File validation (mime + extension)
1600: Compute credit cost
1630: Check trial status
1650: Determine access mode (trial/paid/device_free)
1660: **RESERVE CREDITS HERE** (before Python!)
      - If paid mode: storage.reserveCredits(extractionId, balanceId, cost, desc, quoteId)
      - If trial: validate trial availability (fail closed if DB down)
      - If device_free: validate free quota
1710: Python extraction (only runs if entitlement verified)
1780: **COMMIT HOLD** storage.commitHold(extractionId, mimeType)
1900: Record trial usage
2010: Response
CATCH: **RELEASE HOLD** storage.releaseHold(extractionId) on error
```

### Code Changes Required

#### A. Early Initialization (after line 1530)

```typescript
const startTime = Date.now();
const extractionId = crypto.randomUUID(); // Idempotency key
let holdReserved = false; // Track if we need to release
let tempPath: string | null = null;
let sessionId: string | null = null;
let creditBalanceId: string | null = null;
let useTrial = false;
let chargeCredits = false;
```

#### B. Add DB Health Check (after line 1540)

```typescript
// Fail closed if database is unavailable (money-path safety)
if (process.env.NODE_ENV !== 'development') {
  const dbHealthy = await isDatabaseHealthy();
  if (!dbHealthy) {
    return sendServiceUnavailableError(
      res,
      'Database temporarily unavailable. Please try again shortly.'
    );
  }
}
```

#### C. Move Credit Reservation (replace lines 1650-1708)

Current location: AFTER file upload, BEFORE Python
New logic:

```typescript
// Determine Access Mode
if (process.env.NODE_ENV === 'development') {
  useTrial = false;
  chargeCredits = false;
} else if (hasTrialAvailable) {
  useTrial = true;
  // Fail closed: if DB is down, reject trial (don't give free extraction)
  if (!isDatabaseConnected()) {
    return sendServiceUnavailableError(
      res,
      'Trial system temporarily unavailable'
    );
  }
} else {
  // Paid or device_free path
  if (sessionId) {
    const namespacedSessionId = getImagesMvpBalanceId(sessionId);
    const balance = await storage.getOrCreateCreditBalance(
      namespacedSessionId,
      undefined
    );
    creditBalanceId = balance?.id ?? null;

    if (!balance || balance.credits < creditCost) {
      return sendQuotaExceededError(
        res,
        `Insufficient credits (required: ${creditCost}, available: ${balance?.credits ?? 0})`
      );
    }
    chargeCredits = true;

    // **RESERVE CREDITS ATOMICALLY**
    try {
      await storage.reserveCredits(
        extractionId,
        creditBalanceId,
        creditCost,
        `Extraction: ${fileExt?.slice(1) || 'unknown'} (Images MVP)`,
        quoteId || undefined
      );
      holdReserved = true;
    } catch (error) {
      console.error('Credit reservation failed:', error);
      return sendQuotaExceededError(
        res,
        'Unable to reserve credits. Please try again.'
      );
    }
  } else if ((req as any).user?.id) {
    // Authenticated user path - same pattern
    const userId = (req as any).user.id as string;
    const namespaced = getImagesMvpBalanceId(`user:${userId}`);
    const balance = await storage.getOrCreateCreditBalance(namespaced, userId);
    creditBalanceId = balance?.id ?? null;

    if (!balance || balance.credits < creditCost) {
      return sendQuotaExceededError(
        res,
        `Insufficient credits (required: ${creditCost}, available: ${balance?.credits ?? 0})`
      );
    }
    chargeCredits = true;

    // **RESERVE CREDITS ATOMICALLY**
    try {
      await storage.reserveCredits(
        extractionId,
        creditBalanceId,
        creditCost,
        `Extraction: ${fileExt?.slice(1) || 'unknown'} (Images MVP)`,
        quoteId || undefined
      );
      holdReserved = true;
    } catch (error) {
      console.error('Credit reservation failed:', error);
      return sendQuotaExceededError(
        res,
        'Unable to reserve credits. Please try again.'
      );
    }
  } else {
    // Anonymous device_free flow
    chargeCredits = false;
  }
}
```

#### D. Remove Old Credit Deduction (delete lines 1867-1891)

The old `storage.useCredits()` call must be REMOVED - we now use commitHold instead.

#### E. Add Commit Hold (after line 1780, after extraction succeeds)

```typescript
// Commit the credit hold (finalize charge)
if (chargeCredits && holdReserved) {
  try {
    await storage.commitHold(extractionId, mimeType);
  } catch (error) {
    console.error('Failed to commit credit hold:', error);
    // Hold will auto-expire if we fail to commit
    // Log but don't block response (extraction already succeeded)
  }
}
```

#### F. Update Error Handler (in catch block, line 2015)

```typescript
} catch (error) {
  console.error('Images MVP extraction error:', error);

  // Release credit hold on error
  if (holdReserved) {
    try {
      await storage.releaseHold(extractionId);
    } catch (releaseError) {
      console.error('Failed to release credit hold:', releaseError);
    }
  }

  // Send error notification via WebSocket
  if (sessionId) {
    broadcastError(
      sessionId,
      error instanceof Error ? error.message : 'Extraction failed'
    );
  }

  sendInternalServerError(res, 'Failed to extract metadata');
}
```

### 5. Update Tests

- Add concurrency test (10 parallel requests, 1 balance, verify single charge)
- Add idempotency test (retry with same extractionId, verify no double charge)
- Add DB outage test (simulate DB down, verify 503 with no Python call)

### 6. Regression Testing

- Run full test suite
- Verify no existing functionality broken
- Check trial flow still works
- Check device_free flow still works

## Files Modified

- ✅ shared/schema.ts (credit_holds table)
- ✅ migrations/010_add_credit_holds.sql
- ✅ server/storage/db.ts (reservation methods)
- ✅ server/storage/types.ts (interface updates)
- ✅ server/routes/images-mvp.ts (health check helper)
- ⏳ server/routes/images-mvp.ts (extraction endpoint refactor) - IN PROGRESS
- ⏳ tests/... (new tests) - PENDING

## Safety Checklist

- [ ] Extraction ID generated early for idempotency
- [ ] DB health checked before expensive work
- [ ] Credits reserved BEFORE Python extraction
- [ ] Hold committed on success
- [ ] Hold released on error
- [ ] Fail closed on DB outage
- [ ] No race conditions in credit checks
- [ ] Idempotency via requestId unique constraint
- [ ] Tests verify concurrent requests don't double-charge
- [ ] Tests verify retry with same ID is idempotent
- [ ] Tests verify DB outage fails gracefully

## Notes

- This is a critical money-path change - test thoroughly
- The reserve-commit-release pattern eliminates the race condition window
- Idempotency via requestId prevents double-charging on retries
- SELECT FOR UPDATE in reserveCredits ensures atomic reservation
- Fail-closed behavior prevents giving away free extractions during outages
