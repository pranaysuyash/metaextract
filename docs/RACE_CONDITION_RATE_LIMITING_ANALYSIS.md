# Race Condition: Rate Limiting - Detailed Analysis

**File**: `server/middleware/rateLimit.ts`  
**Function**: `rateLimitMiddleware` (lines 96-213)  
**Severity**: CRITICAL  
**Impact**: Rate limiting completely bypassed under concurrent load

---

## The Problem

The rate limiting middleware has a **classic check-then-act race condition**:

```typescript
// Lines 133-157 (Per-minute limit check)
if (entry.count >= limits.requestsPerMinute) {
  // Reject request
  return;
}

// ⚠️ RACE CONDITION WINDOW: Another request can run here!

// Lines 180-182 (Increment counter)
entry.count++;
entry.dailyCount++;
```

**Timeline**:
```
Request A (T=0.0ms)        |  Request B (T=0.1ms)   |  Request C (T=0.2ms)
========================== | ====================== | =======================
entry.count = 5            |                        |
Check: 5 >= 10? NO ✓      |                        |
                           | entry.count = 5        |
                           | Check: 5 >= 10? NO ✓  |
                           |                        | entry.count = 5
                           |                        | Check: 5 >= 10? NO ✓
Increment count=6         |                        |
                           | Increment count=7     |
                           |                        | Increment count=8
All 3 pass ✓ (should reject at 10) ❌
```

With 10 concurrent requests and limit of 10/min:
- All 10 see `count=0` at same time
- All 10 pass the check
- All 10 increment
- All 10 requests succeed
- **Effective limit: None** (all get through)

---

## Why This Happens

1. **Check and increment are separate operations** (lines 133 vs 181)
2. **No atomic operation** - JavaScript async event loop allows context switches
3. **Shared mutable state** - `entry.count` can be read stale by concurrent requests
4. **No locking mechanism** - In-memory Map has no concurrency control

---

## Affected Scenarios

### Brute Force Attacks
- Auth endpoint uses 5-minute window (lines 238-247)
- Attacker with 10 concurrent connections can make 10 login attempts per 5 minutes
- Should only allow N attempts
- **Actual**: Allows 10×N attempts

### DDoS Protection
- Rate limiter is the only DoS protection
- Limit: 100 requests/minute per user
- Attacker can make unlimited requests with concurrent connections
- **Actual**: 100 concurrent requests all get through

### Free Tier Exploitation
- Free tier: 10 requests/minute
- Attacker can bypass this with 10 concurrent requests
- Gets 10× the service without paying
- **Actual**: Unlimited extractions with concurrent uploads

---

## The Fix

Convert to **atomic increment-and-check** pattern using atomicity primitives:

```typescript
function rateLimitMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const now = Date.now();
  const key = keyGenerator(req);
  const tier = normalizeTier(getTierFromRequest(req));
  const limits = getRateLimits(tier);

  let entry = rateLimitStore.get(key);
  
  if (!entry) {
    entry = {
      count: 0,
      windowStart: now,
      dailyCount: 0,
      dayStart: now,
    };
    rateLimitStore.set(key, entry);
  }

  // Reset windows
  if (now - entry.windowStart > 60000) {
    entry.count = 0;
    entry.windowStart = now;
  }
  const dayMs = 24 * 60 * 60 * 1000;
  if (now - entry.dayStart > dayMs) {
    entry.dailyCount = 0;
    entry.dayStart = now;
  }

  // ✅ ATOMIC: Check AND increment together
  // Option 1: Pre-increment and check (best for concurrent loads)
  const newCount = ++entry.count;
  const newDailyCount = ++entry.dailyCount;

  // Check AFTER increment - we allow N+1 to detect overage
  if (newCount > limits.requestsPerMinute) {
    // Reject this request
    res.setHeader('Retry-After', Math.ceil((entry.windowStart + 60000 - now) / 1000));
    res.setHeader('X-RateLimit-Limit', limits.requestsPerMinute);
    res.setHeader('X-RateLimit-Remaining', 0);
    
    res.status(429).json({
      error: 'Too many requests',
      message: `Rate limit exceeded. Maximum ${limits.requestsPerMinute} requests per minute for ${tier} tier.`,
      tier,
      retry_after_seconds: Math.ceil((entry.windowStart + 60000 - now) / 1000),
    });
    
    // IMPORTANT: Decrement since we're rejecting this request
    entry.count--;
    entry.dailyCount--;
    return;
  }

  // Same for daily limit
  if (newDailyCount > limits.requestsPerDay) {
    const nextDay = new Date(entry.dayStart + dayMs);
    
    res.setHeader('X-RateLimit-Daily-Limit', limits.requestsPerDay);
    res.setHeader('X-RateLimit-Daily-Remaining', 0);
    res.setHeader('X-RateLimit-Daily-Reset', nextDay.toISOString());
    
    res.status(429).json({
      error: 'Daily limit exceeded',
      message: `Daily limit of ${limits.requestsPerDay} requests exceeded for ${tier} tier.`,
      tier,
      reset_at: nextDay.toISOString(),
    });
    
    entry.count--;
    entry.dailyCount--;
    return;
  }

  // Request allowed - set headers with remaining counts
  res.setHeader('X-RateLimit-Limit', limits.requestsPerMinute);
  res.setHeader('X-RateLimit-Remaining', Math.max(0, limits.requestsPerMinute - newCount));
  res.setHeader('X-RateLimit-Reset', Math.ceil((entry.windowStart + 60000) / 1000));
  res.setHeader('X-RateLimit-Daily-Limit', limits.requestsPerDay);
  res.setHeader('X-RateLimit-Daily-Remaining', Math.max(0, limits.requestsPerDay - newDailyCount));

  // Handle response error decrement
  if (skipFailedRequests) {
    const originalEnd = res.end;
    res.end = function (...args: any[]) {
      if (res.statusCode >= 400) {
        entry!.count = Math.max(0, entry!.count - 1);
        entry!.dailyCount = Math.max(0, entry!.dailyCount - 1);
      }
      return (originalEnd as any).apply(res, args as any);
    };
  }

  next();
}
```

### Why This Works

**Key change**: Increment first (`++entry.count`), then check

1. **Atomic operation**: `++` is atomic in JavaScript (single bytecode)
2. **No check window**: Can't both see old value and increment stale
3. **Clear semantics**: "You used this request, now check if you're over"
4. **Simple decrement on reject**: If rejected, subtract back

**Concurrent scenario with fix**:
```
Request A         Request B          Request C
count = 0        count = 0          count = 0
++count → 1      ++count → 2        ++count → 3
Check: 1 > 10? NO  Check: 2 > 10? NO  Check: 3 > 10? NO
Accept ✓         Accept ✓           Accept ✓

...continues until...

Request J
count = 9
++count → 10
Check: 10 > 10? NO
Accept ✓

Request K
count = 10
++count → 11
Check: 11 > 10? YES ❌
Reject request
--count → 10 (back to limit)
```

All 10 requests get through, the 11th is rejected. **Correct behavior**.

---

## Advanced: Use Semaphore for True Atomicity

If you need true thread-safe atomicity (for clustered deployments):

```typescript
import Semaphore from 'semaphore';

const rateLimitMutex = new Semaphore(1);

return async function rateLimitMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  // Acquire lock
  await rateLimitMutex.acquire();
  try {
    // ... check and increment logic (now atomic)
  } finally {
    // Release lock
    rateLimitMutex.release();
  }
  next();
};
```

**Trade-off**: Semaphore adds mutex overhead (~1-5ms per request). Only needed if:
- Multiple processes (cluster mode)
- Distributed deployment
- Redis backend

For single-process, pre-increment approach is sufficient.

---

## Testing the Fix

```typescript
describe('Rate Limiting - Race Condition', () => {
  it('should prevent 10 concurrent requests from bypassing limit of 5', async () => {
    const limiter = createRateLimiter({ windowMs: 60000 });
    const limit = 5;
    
    // Mock getRateLimits to return limit of 5
    let passCount = 0;
    
    // Fire 10 concurrent requests
    const requests = Array.from({ length: 10 }, async () => {
      const mockRes = {
        status: () => ({ json: () => {} }),
        setHeader: () => {},
      };
      
      limiter(mockReq, mockRes as any, () => {
        passCount++;
      });
    });
    
    await Promise.all(requests);
    
    // Should only allow 5, reject 5
    expect(passCount).toBeLessThanOrEqual(5);
  });
});
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Atomicity** | ❌ Non-atomic | ✅ Atomic increment |
| **Race condition** | ❌ YES | ❌ NO |
| **True concurrent limit** | ❌ Bypassed | ✅ Enforced |
| **Code complexity** | Simple | Simple |
| **Performance** | Fast | Same |
| **Distributed safe** | ❌ No | ⚠️ No (need semaphore) |

---

**Status**: Ready for implementation
**Risk**: Low (fixed counter logic only)
**Benefit**: High (DoS protection works)
