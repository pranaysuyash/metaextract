# Race Condition: Credit Deduction - Detailed Analysis

**File**: `server/storage/db.ts`  
**Functions**: `useCredits()` (lines 235-273)  
**Severity**: CRITICAL  
**Impact**: Negative credit balances, revenue loss, user abuse

---

## The Problem

The `useCredits()` function has a **classic race condition** between the balance check and the deduction:

```typescript
// Lines 235-273
async useCredits(
  balanceId: string,
  amount: number,
  description: string,
  fileType?: string
): Promise<CreditTransaction | null> {
  if (!this.db) return null;
  try {
    // ❌ RACE CONDITION STARTS HERE
    const [balance] = await this.db
      .select()
      .from(creditBalances)
      .where(eq(creditBalances.id, balanceId))
      .limit(1);

    if (!balance || balance.credits < amount) return null;  // ← Balance check

    // ⚠️ Time window: Another request can check balance here too!

    await this.db
      .update(creditBalances)
      .set({
        credits: sql`${creditBalances.credits} - ${amount}`,
        updatedAt: new Date(),
      })
      .where(eq(creditBalances.id, balanceId));  // ← Deduction happens
    // ❌ RACE CONDITION ENDS HERE

    // ... transaction creation ...
  }
}
```

---

## Race Condition Scenario

**Initial state**: User has 100 credits

**Concurrent requests**: Two extraction requests, each costing 100 credits

```
Request A (T=0.0ms)          |  Request B (T=0.1ms)
============================|============================
SELECT credits = 100        |
✓ Check: 100 >= 100         |
                             | SELECT credits = 100
                             | ✓ Check: 100 >= 100
UPDATE credits - 100        |
                             | UPDATE credits - 100
                             |
Final balance: -100 ❌      |
```

Both requests see 100 credits, both pass the check, both deduct 100. Result: **-100 credits**.

---

## Why This Happens

1. **Non-atomic operations**: The SELECT and UPDATE are separate database calls
2. **No locking**: No database transaction or row lock prevents concurrent reads
3. **No idempotency**: Multiple requests can race to modify the same row
4. **Async/await gap**: JavaScript's async nature gives other requests time to run between SELECT and UPDATE

---

## Affected Callsites

This function is called in:
- `server/routes/extraction.ts` (line 210-214)
- `server/routes/images-mvp.ts` (line 322-326)

When users submit concurrent extraction requests, both can bypass the balance check.

---

## The Fix

Convert the operation into a **single atomic database statement** using a WHERE clause that validates the balance:

```typescript
async useCredits(
  balanceId: string,
  amount: number,
  description: string,
  fileType?: string
): Promise<CreditTransaction | null> {
  if (!this.db) return null;
  try {
    // ✅ ATOMIC: Check and update in one statement
    const result = await this.db
      .update(creditBalances)
      .set({
        credits: sql`${creditBalances.credits} - ${amount}`,
        updatedAt: new Date(),
      })
      // Critical: Only update if balance is sufficient
      .where(
        sql`${eq(creditBalances.id, balanceId)} AND ${creditBalances.credits} >= ${amount}`
      )
      .returning();

    // If no rows updated, balance was insufficient
    if (result.length === 0) return null;

    // Only now create the transaction record
    const [tx] = await this.db
      .insert(creditTransactions)
      .values({
        balanceId,
        type: 'usage',
        amount: -amount,
        description,
        fileType,
      })
      .returning();
    return tx;
  } catch (error) {
    console.error('Failed to use credits:', error);
    return null;
  }
}
```

### Why This Works

1. **Single SQL statement**: Database executes atomically
2. **WHERE clause prevents negative**: Only updates if balance >= amount
3. **Returns updated count**: We can check if update succeeded
4. **No SELECT needed**: We don't need to pre-check the balance

### Database Implementation

Modern SQL databases (PostgreSQL, MySQL) support atomic conditional updates:

```sql
-- PostgreSQL (what Drizzle uses)
UPDATE credit_balances 
SET credits = credits - 100, updated_at = NOW()
WHERE id = 'bal_123' 
  AND credits >= 100
RETURNING *;
```

If balance is 50 and we try to deduct 100, the UPDATE affects 0 rows. Transaction creation is skipped.

---

## Alternative: Database Transaction

If you need multiple operations atomically, use a database transaction:

```typescript
async useCredits(...): Promise<CreditTransaction | null> {
  if (!this.db) return null;
  try {
    return await this.db.transaction(async (tx) => {
      // Lock the row for this transaction
      const [balance] = await tx
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.id, balanceId))
        .for(sql`update`);  // Row-level lock

      if (!balance || balance.credits < amount) return null;

      // Now deduct (no other transaction can read stale balance)
      await tx
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} - ${amount}`,
          updatedAt: new Date(),
        })
        .where(eq(creditBalances.id, balanceId));

      const [tx] = await tx
        .insert(creditTransactions)
        .values({...})
        .returning();
      return tx;
    });
  } catch (error) {
    console.error('Failed to use credits:', error);
    return null;
  }
}
```

**Note**: Requires Drizzle ORM to support `.for(sql\`update\`)`. Check Drizzle documentation.

---

## Recommended Solution

**Use atomic UPDATE with WHERE clause** (Option 1) because:
- ✅ Simpler, no transaction overhead
- ✅ Better performance under high concurrency
- ✅ Works with any database (PostgreSQL, MySQL, SQLite)
- ✅ Single roundtrip to database

---

## Testing the Fix

Create a test to verify race condition is fixed:

```typescript
// Add to server/storage/db.test.ts
describe('useCredits - Race Condition', () => {
  it('should prevent concurrent credit deductions exceeding balance', async () => {
    const balanceId = 'test_balance';
    
    // Setup: User has 100 credits
    await storage.getOrCreateCreditBalance(balanceId);
    await storage.addCredits(balanceId, 100, 'initial');

    // Simulate concurrent requests with Promise.all
    const results = await Promise.all([
      storage.useCredits(balanceId, 100, 'request 1'),
      storage.useCredits(balanceId, 100, 'request 2'),
    ]);

    // One should succeed, one should fail
    const successes = results.filter((r) => r !== null).length;
    expect(successes).toBe(1);  // ✅ Only one request gets credits

    // Final balance should be 0, not -100
    const finalBalance = await storage.getCreditBalance(balanceId);
    expect(finalBalance?.credits).toBe(0);
  });
});
```

---

## Summary

| Aspect | Current | Fixed |
|--------|---------|-------|
| **Consistency** | ❌ Negative balances possible | ✅ Always non-negative |
| **Query count** | 2 (SELECT + UPDATE) | 1 (UPDATE with WHERE) |
| **Concurrency** | ❌ Race condition | ✅ Atomic operation |
| **Performance** | Medium (2 roundtrips) | Better (1 roundtrip) |
| **Complexity** | Simple but broken | Simple and correct |

This fix is **urgent** as it directly enables revenue fraud.
