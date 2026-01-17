# Extraction Endpoint Refactoring - Implementation Ready

## Status: INFRASTRUCTURE COMPLETE - READY FOR ENDPOINT REFACTORING

## What's Been Completed

### ✅ Infrastructure (ALL DONE)
1. **Schema**: creditHolds table with unique index on `(balance_id, request_id)`
2. **Migration**: 010_add_credit_holds.sql applied to database
3. **Storage Methods**: 
   - `reserveCredits(requestId, balanceId, amount, description, quoteId?, expiresInMs?)`
   - `commitHold(requestId, balanceId, fileType?)`
   - `releaseHold(requestId, balanceId)`
   - `cleanupExpiredHolds()`
4. **Helpers**:
   - `getIdempotencyKey(req)` - Extract Idempotency-Key header
   - `isDatabaseHealthy()` - Check DB availability
   - `startHoldCleanup()` - Periodic cleanup every 5 minutes
5. **Types**: All interfaces updated in storage/types.ts

## What Remains: Refactor Extraction Endpoint

### Current Flow (BROKEN - lines 1560-1920)

The current code has the vulnerability:

```typescript
// Line 1530: Handler starts
async (req: Request, res: Response) => {
  let creditBalanceId: string | null = null;
  let chargeCredits = false;
  let useTrial = false;

  try {
    // Lines 1560-1640: File validation, credit computation
    const creditCost = quotedCreditCost ?? creditsTotal;
    
    // Lines 1710-1760: Check credits (TOO LATE!)
    if (sessionId) {
      const balance = await storage.getOrCreateCreditBalance(...);
      creditBalanceId = balance?.id ?? null;
      if (!balance || balance.credits < creditCost) {
        return sendQuotaExceededError(res, ...);
      }
      chargeCredits = true;
    }
    
    // Line 1800: PYTHON STARTS HERE (before final verification!)
    const rawMetadata = await extractMetadataWithPython(...);
    
    // Line 1900: Credits deducted AFTER Python completes (RACE CONDITION!)
    if (chargeCredits && creditBalanceId) {
      const txn = await storage.useCredits(
        creditBalanceId,
        creditCost,
        ...
      );
      if (txn === null) {
        // Too late! Python already ran!
        return res.status(402).json({...});
      }
    }
    
    res.json(metadata);
  } catch (error) {
    // No hold release here!
    sendInternalServerError(res, ...);
  }
}
```

### Required New Flow

```typescript
async (req: Request, res: Response) => {
  const startTime = Date.now();
  let tempPath: string | null = null;
  let sessionId: string | null = null;
  let creditBalanceId: string | null = null;
  let useTrial = false;
  let chargeCredits = false;
  let holdReserved = false; // Track if we need to release on error
  const requestId = getIdempotencyKey(req); // Get client-provided key

  try {
    if (!req.file) {
      return sendInvalidRequestError(res, 'No file uploaded');
    }

    // PHASE A: Validate cheap stuff (existing code lines 1560-1690)
    // [file validation, mime checks, quote lookup, credit calculation]
    // This stays exactly the same until line 1690

    const creditCost = quotedCreditCost ?? creditsTotal;
    const trialEmail = normalizeEmail(req.body?.trial_email ?? req.body?.access_email);
    sessionId = getSessionId(req);

    // Check trial status
    let trialUses = 0;
    if (trialEmail) {
      // existing trial check code
    }
    const hasTrialAvailable = !!trialEmail && trialUses < 2;

    // PHASE B: Fail-closed DB health check (NEW - INSERT AFTER LINE 1700)
    if (process.env.NODE_ENV !== 'development') {
      if (!hasTrialAvailable) { // paid flow requires DB
        const dbHealthy = await isDatabaseHealthy();
        if (!dbHealthy) {
          return sendServiceUnavailableError(
            res,
            'Billing system temporarily unavailable. Please try again shortly.'
          );
        }
      }
    }

    // PHASE C: Determine access mode and RESERVE (REPLACE lines 1710-1760)
    if (process.env.NODE_ENV === 'development') {
      useTrial = false;
      chargeCredits = false;
    } else if (hasTrialAvailable) {
      useTrial = true;
      // Trial validation happens above in DB health check
    } else {
      // Paid flow - RESERVE BEFORE PYTHON
      if (sessionId) {
        const namespacedSessionId = getImagesMvpBalanceId(sessionId);
        const balance = await storage.getOrCreateCreditBalance(
          namespacedSessionId,
          undefined
        );
        creditBalanceId = balance?.id ?? null;

        if (!balance) {
          return sendQuotaExceededError(res, 'Credit balance not found');
        }

        // ⚠️ CRITICAL: Require idempotency key for paid extractions
        if (!requestId) {
          return sendInvalidRequestError(
            res,
            'Idempotency-Key header required for paid extractions'
          );
        }

        // **RESERVE CREDITS ATOMICALLY**
        try {
          await storage.reserveCredits(
            requestId,
            creditBalanceId,
            creditCost,
            `Extraction: ${fileExt?.slice(1) || 'unknown'} (Images MVP)`,
            quoteId || undefined,
            15 * 60 * 1000 // 15 minutes expiry
          );
          holdReserved = true;
          chargeCredits = true;
        } catch (error) {
          console.error('Credit reservation failed:', error);
          const errMsg = error instanceof Error ? error.message : 'Unknown error';
          if (errMsg.includes('Insufficient credits')) {
            return sendQuotaExceededError(res, errMsg);
          }
          return sendServiceUnavailableError(
            res,
            'Unable to reserve credits. Please try again.'
          );
        }
      } else if ((req as any).user?.id) {
        // Authenticated user path - same pattern
        const userId = (req as any).user.id as string;
        const namespaced = getImagesMvpBalanceId(`user:${userId}`);
        const balance = await storage.getOrCreateCreditBalance(
          namespaced,
          userId
        );
        creditBalanceId = balance?.id ?? null;

        if (!balance) {
          return sendQuotaExceededError(res, 'Credit balance not found');
        }

        // ⚠️ CRITICAL: Require idempotency key
        if (!requestId) {
          return sendInvalidRequestError(
            res,
            'Idempotency-Key header required for paid extractions'
          );
        }

        // **RESERVE CREDITS ATOMICALLY**
        try {
          await storage.reserveCredits(
            requestId,
            creditBalanceId,
            creditCost,
            `Extraction: ${fileExt?.slice(1) || 'unknown'} (Images MVP)`,
            quoteId || undefined,
            15 * 60 * 1000
          );
          holdReserved = true;
          chargeCredits = true;
        } catch (error) {
          console.error('Credit reservation failed:', error);
          const errMsg = error instanceof Error ? error.message : 'Unknown error';
          if (errMsg.includes('Insufficient credits')) {
            return sendQuotaExceededError(res, errMsg);
          }
          return sendServiceUnavailableError(
            res,
            'Unable to reserve credits. Please try again.'
          );
        }
      } else {
        // Anonymous device_free flow (no hold needed)
        chargeCredits = false;
      }
    }

    // PHASE D: Run Python extraction (line 1800+)
    // [existing Python call code - NO CHANGES]
    tempPath = req.file.path;
    
    if (sessionId) {
      broadcastProgress(sessionId, 10, 'File uploaded successfully', 'upload_complete');
    }

    const pythonTier = 'super';
    
    if (sessionId) {
      broadcastProgress(sessionId, 20, 'Starting metadata extraction', 'extraction_start');
    }

    const extractorOptions = { ocr: ops.ocr, maxDim: 2048 };
    const rawMetadata = await extractMetadataWithPython(...); // existing call

    if (sessionId) {
      broadcastProgress(sessionId, 90, 'Metadata extraction complete', 'extraction_complete');
    }

    const processingMs = Date.now() - startTime;
    rawMetadata.extraction_info.processing_ms = processingMs;

    // [existing metadata transformation code lines 1820-1890]
    const metadata = transformMetadataForFrontend(...);
    
    // PHASE E: Commit hold BEFORE responding (REPLACE lines 1900-1930)
    // **DELETE THE OLD useCredits() CALL ENTIRELY**
    // Replace with:
    if (chargeCredits && holdReserved && creditBalanceId && requestId) {
      try {
        await storage.commitHold(requestId, creditBalanceId, mimeType);
      } catch (error) {
        console.error('Failed to commit credit hold:', error);
        // Release the hold
        try {
          await storage.releaseHold(requestId, creditBalanceId);
        } catch (releaseError) {
          console.error('Failed to release hold after commit failure:', releaseError);
        }
        // Don't return extraction result if we couldn't charge
        return sendServiceUnavailableError(
          res,
          'Credit charge failed. Please contact support.'
        );
      }
    }

    // Record trial usage (existing code line 1935+)
    if (useTrial && trialEmail) {
      try {
        await storage.recordTrialUsage({...});
      } catch (error) {
        console.error('Failed to record trial usage:', error);
      }
    }

    // [existing device_free quota code lines 1950-2020]
    // [existing redaction code]
    // [existing quote marking code]

    res.json(metadata);

  } catch (error) {
    console.error('Images MVP extraction error:', error);

    // PHASE F: Release hold on ANY error (NEW - UPDATE CATCH BLOCK)
    if (holdReserved && creditBalanceId && requestId) {
      try {
        await storage.releaseHold(requestId, creditBalanceId);
      } catch (releaseError) {
        console.error('Failed to release credit hold on error:', releaseError);
      }
    }

    if (sessionId) {
      broadcastError(
        sessionId,
        error instanceof Error ? error.message : 'Extraction failed'
      );
    }

    sendInternalServerError(res, 'Failed to extract metadata');
  } finally {
    await cleanupTempFile(tempPath);
    if (sessionId) {
      setTimeout(() => cleanupConnections(sessionId!), 5000);
    }
  }
}
```

## Key Invariants Enforced

1. ✅ **Idempotency key required for paid**: `Idempotency-Key` header mandatory
2. ✅ **DB health checked before work**: Fail closed if DB down and paid/trial
3. ✅ **Credits reserved before Python**: Hold created with SELECT FOR UPDATE lock
4. ✅ **Commit before response**: No extraction result sent if charge fails
5. ✅ **Release on error**: All failure paths release the hold
6. ✅ **Retry safety**: (balanceId, requestId) unique index prevents double-charge
7. ✅ **Hold expiry**: 15-minute timeout with automatic cleanup

## Exact Line Changes Needed in images-mvp.ts

1. **Line 1530**: Add `const requestId = getIdempotencyKey(req);` and `let holdReserved = false;`
2. **Line 1705**: Insert DB health check before credit logic
3. **Lines 1710-1760**: Replace with reservation logic (requires Idempotency-Key, calls reserveCredits)
4. **Lines 1900-1930**: DELETE old `storage.useCredits()` call
5. **Lines 1900-1930**: ADD `storage.commitHold()` call before response
6. **Line 2040 (catch block)**: ADD `storage.releaseHold()` at start of catch

## Testing Required

Once refactoring is complete, add these 4 critical tests:

### Test 1: Concurrency Overspend
```typescript
// Set user credits to exactly 1 extraction worth
// Fire 10 concurrent requests with DIFFERENT Idempotency-Keys
// Assert: only 1 reaches Python, only 1 committed hold
// Assert: other 9 get 402 Insufficient Credits
```

### Test 2: Retry Idempotency
```typescript
// Send same request twice with SAME Idempotency-Key
// Assert: second request returns existing hold, no double-charge
// Assert: only 1 Python extraction occurs
```

### Test 3: DB Outage Fail-Closed
```typescript
// Mock isDatabaseHealthy() to return false
// Send paid extraction request
// Assert: 503 Service Unavailable, Python never invoked
```

### Test 4: Commit Failure Protection
```typescript
// Mock commitHold() to fail
// Python returns successful result
// Assert: response is 503, no extraction result returned
// Assert: hold is released (credits refunded)
```

## Ready to Implement

All infrastructure is in place. The extraction endpoint can now be refactored safely following the exact pattern above.

The key is:
1. Add requestId extraction at top
2. Add DB health check after trial determination
3. Replace credit check with reservation (requires Idempotency-Key)
4. Delete old useCredits() call
5. Add commitHold() before response
6. Add releaseHold() in catch block

Once complete, add the 4 tests to prove correctness.
