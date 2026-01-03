# Quick Reference: Race Condition Fixes

**Session**: January 2, 2026  
**Scope**: Critical race conditions in credit deduction and rate limiting

---

## At a Glance

| Issue | Location | Problem | Solution | Status |
|-------|----------|---------|----------|--------|
| **Credit Race** | `server/storage/db.ts:237-277` | Non-atomic SELECT+UPDATE allows balance to go negative | Atomic UPDATE with WHERE clause | ✅ Fixed |
| **Rate Limit Race** | `server/middleware/rateLimit.ts:132-212` | Check before increment allows bypass | Atomic pre-increment pattern | ✅ Fixed |

---

## Credit Deduction Fix

**File**: `server/storage/db.ts`

**Function**: `useCredits(balanceId, amount, ...)`

**Lines Changed**: 237-277 (37 lines)

**Before**:
```typescript
const [balance] = await SELECT WHERE id=?
if (balance.credits < amount) return null  // ❌ Race window here
await UPDATE SET credits - amount
```

**After**:
```typescript
const result = await UPDATE WHERE id=? AND credits >= amount
if (result.length === 0) return null  // ✅ Atomic check
```

**Key Point**: Balance check happens at database level, making it atomic

---

## Rate Limiting Fix

**File**: `server/middleware/rateLimit.ts`

**Function**: `rateLimitMiddleware(req, res, next)`

**Lines Changed**: 132-212 (80 lines modified)

**Before**:
```typescript
if (entry.count >= limit) reject()  // ❌ Race window here
entry.count++
```

**After**:
```typescript
const newCount = ++entry.count  // ✅ Atomic increment
if (newCount > limit) {
  entry.count--  // Decrement on reject
  reject()
}
```

**Key Point**: Increment happens before check, preventing concurrent bypasses

---

## Scenario: Why These Fixes Matter

### Credit Deduction (Before → After)

**Scenario**: User has 100 credits, 2 concurrent extractions cost 100 each

Before fix:
```
Request A: SELECT credits=100 → passes check
Request B: SELECT credits=100 → passes check  ❌ Both see 100!
Request A: UPDATE credits - 100 → balance=0
Request B: UPDATE credits - 100 → balance=-100
Result: User went negative, got free service ❌
```

After fix:
```
Request A: UPDATE WHERE id=? AND credits>=100 → success
Request B: UPDATE WHERE id=? AND credits>=100 → fails (count became 0) ✓
Result: One succeeds, one fails, balance=0 ✓
```

### Rate Limiting (Before → After)

**Scenario**: Limit is 10 requests/min, attacker sends 15 concurrent requests

Before fix:
```
All 15 requests: if (count=0 >= 10)? NO
All 15 requests: count++ (becomes 15) ❌
Result: All get through, limit bypassed ❌
```

After fix:
```
Request 1: ++count (0→1) → 1 > 10? NO ✓
Request 2: ++count (1→2) → 2 > 10? NO ✓
...
Request 10: ++count (9→10) → 10 > 10? NO ✓
Request 11: ++count (10→11) → 11 > 10? YES, reject, --count back to 10
Result: 10 allowed, 11+ rejected ✓
```

---

## Test It

### Unit Tests

```bash
npm test -- server/storage/db.race-condition.test.ts
npm test -- server/middleware/rateLimit.race-condition.test.ts
```

### Load Test (Concurrent Requests)

```bash
# Send 20 concurrent requests to extraction endpoint
for i in {1..20}; do
  curl -X POST http://localhost:5000/api/extract \
    -F "file=@test.jpg" &
done
wait
```

Expected: Rate limiter rejects extras with 429

### Database Check (Negative Balances)

```sql
SELECT * FROM credit_balances WHERE credits < 0;
```

Expected: No results (should be empty)

---

## Files Changed

1. **`server/storage/db.ts`**
   - Lines: 237-277
   - Added: Atomic UPDATE with WHERE clause
   - Removed: Non-atomic SELECT before UPDATE

2. **`server/middleware/rateLimit.ts`**
   - Lines: 132-212
   - Added: Pre-increment pattern
   - Added: Decrement on rejection
   - Modified: Header generation

---

## Documentation Files

| File | Purpose | Size |
|------|---------|------|
| `RACE_CONDITION_CREDIT_DEDUCTION_ANALYSIS.md` | Deep dive analysis | 854 lines |
| `FIX_RACE_CONDITION_CREDIT_DEDUCTION_SUMMARY.md` | Implementation details | 287 lines |
| `RACE_CONDITION_BEFORE_AFTER.md` | Visual comparison | 356 lines |
| `RACE_CONDITION_RATE_LIMITING_ANALYSIS.md` | Rate limiting analysis | 298 lines |
| `FIX_RATE_LIMITING_RACE_CONDITION_SUMMARY.md` | Rate limiting implementation | 266 lines |
| `FIXES_COMPLETED_SESSION_JAN2_2026.md` | Session summary | 381 lines |

**Total**: 2,442 lines of documentation

---

## Verification Checklist

- [x] Code changes reviewed
- [x] No breaking API changes
- [x] Type safety maintained
- [x] Tests created
- [x] Documentation complete
- [ ] Unit tests passing
- [ ] Load tests passing
- [ ] Database clean (no negative balances)
- [ ] Production monitoring in place

---

## Impact Summary

| Metric | Impact |
|--------|--------|
| **Security** | Prevents fraud (credits) + DoS (rate limiting) |
| **Performance** | Improved (fewer DB roundtrips) |
| **Reliability** | Improved (atomic operations) |
| **Risk** | Low (no breaking changes) |
| **Complexity** | Low (simple atomic patterns) |

---

## Next Steps

1. Run test suite
2. Load test under concurrent load
3. Verify no negative balances exist
4. Deploy to staging
5. Monitor rate limits and credit deductions
6. Deploy to production

---

**Created**: January 2, 2026  
**Status**: Ready for testing ✅
