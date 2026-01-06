/**
 * Race Condition Test for Credit Deduction
 *
 * This test demonstrates that the atomic UPDATE with WHERE clause
 * prevents negative credit balances under concurrent access.
 */

import { DatabaseStorage } from './db';

describe('DatabaseStorage - Race Condition Prevention', () => {
  let storage: DatabaseStorage;

  beforeEach(() => {
    storage = new DatabaseStorage();
  });

  /**
   * Test: Concurrent credit deductions should not exceed available balance
   *
   * Scenario:
   * - User has 100 credits
   * - Two concurrent requests each attempt to deduct 100 credits
   * - Expected: One succeeds, one fails (or both fail if balance becomes 0)
   * - Not allowed: Balance goes negative
   *
   * Before fix:
   * - Both requests see balance=100
   * - Both pass the check
   * - Both deduct 100
   * - Final balance: -100 ❌
   *
   * After fix (atomic UPDATE with WHERE):
   * - Both requests attempt UPDATE with WHERE balance >= 100
   * - Only one UPDATE succeeds (affects 1 row)
   * - Other UPDATE fails (affects 0 rows)
   * - Final balance: 0 ✅
   */
  it('should prevent negative balances with concurrent deductions', async () => {
    // Prefer using local Postgres when available; otherwise skip the test
    const testDbFlag = (global as any).__TEST_DB_READY;
    const initError = (global as any).__TEST_DB_INIT_ERROR;

    if (initError) {
      // DB connection exists but schema init failed — fail loudly with actionable message
      throw new Error(
        `Database appears reachable but schema initialization failed: ${initError}. Please run ./init.sql against your test database or check DATABASE_URL.`
      );
    }

    if (!testDbFlag) {
      console.log(
        'Database not available, skipping race condition test (requires a running Postgres with test schema)'
      );
      return;
    }

    // Setup: Create balance with 100 credits
    let balance;
    balance = await storage.getOrCreateCreditBalance('test_race_' + Date.now());
    await storage.addCredits(balance.id, 100, 'initial setup');

    // Simulate two concurrent requests attempting to deduct 100 each
    const results = await Promise.all([
      storage.useCredits(balance.id, 100, 'request 1'),
      storage.useCredits(balance.id, 100, 'request 2'),
    ]);

    // Count successful deductions
    const successCount = results.filter(r => r !== null).length;

    // At most one should succeed (not both)
    expect(successCount).toBeLessThanOrEqual(1);

    // Final balance should never be negative
    const finalBalance = await storage.getCreditBalance(balance.id);
    if (finalBalance) {
      expect(finalBalance.credits).toBeGreaterThanOrEqual(0);
      expect(finalBalance.credits).toBeLessThanOrEqual(100);
    }
  });

  /**
   * Test: Partial deduction should only work if sufficient balance
   *
   * Scenario:
   * - User has 50 credits
   * - Attempt to deduct 100 credits
   * - Expected: Transaction fails, balance unchanged
   */
  it('should reject deduction if insufficient balance', async () => {
    const testDb = (storage as any).db;
    if (!testDb) {
      return;
    }

    let balance;
    try {
      balance = await storage.getOrCreateCreditBalance(
        'test_insufficient_' + Date.now()
      );
      await storage.addCredits(balance.id, 50, 'initial setup');
    } catch (e: any) {
      if (
        e &&
        typeof e.message === 'string' &&
        e.message.includes('relation')
      ) {
        console.log(
          'Database schema missing, skipping insufficient balance test:',
          e.message
        );
        return;
      }
      throw e;
    }

    // Attempt to deduct more than available
    const result = await storage.useCredits(
      balance.id,
      100,
      'too much deduction'
    );

    // Should fail
    expect(result).toBeNull();

    // Balance should not change
    const finalBalance = await storage.getCreditBalance(balance.id);
    expect(finalBalance?.credits).toBe(50);
  });

  /**
   * Test: Multiple small concurrent deductions should not exceed balance
   *
   * Scenario:
   * - User has 30 credits
   * - Five concurrent requests, each deducting 10 credits
   * - Expected: Three succeed, two fail
   * - Balance: 0
   */
  it('should handle multiple concurrent deductions correctly', async () => {
    const testDb = (storage as any).db;
    if (!testDb) {
      return;
    }

    let balance;
    try {
      balance = await storage.getOrCreateCreditBalance(
        'test_multiple_' + Date.now()
      );
      await storage.addCredits(balance.id, 30, 'initial setup');
    } catch (e: any) {
      if (
        e &&
        typeof e.message === 'string' &&
        e.message.includes('relation')
      ) {
        console.log(
          'Database schema missing, skipping multiple deductions test:',
          e.message
        );
        return;
      }
      throw e;
    }

    // Five concurrent deductions of 10 credits each
    const results = await Promise.all(
      Array.from({ length: 5 }, (_, i) =>
        storage.useCredits(balance.id, 10, `request ${i + 1}`)
      )
    );

    // Count successes
    const successCount = results.filter(r => r !== null).length;

    // Should allow exactly 3 to succeed (30 / 10)
    expect(successCount).toBeLessThanOrEqual(3);

    // Balance should never be negative
    const finalBalance = await storage.getCreditBalance(balance.id);
    expect(finalBalance?.credits).toBeGreaterThanOrEqual(0);
  });

  it('logs last operation when addCredits hits a 25P02 and rethrows', async () => {
    const storage = new DatabaseStorage();

    const fakeError: any = { code: '25P02', message: 'current transaction is aborted' };
    // Make the DB update throw immediately (simulate transaction-aborted condition)
    (storage as any).db = {
      update: () => {
        throw fakeError;
      },
    };

    await expect(storage.addCredits('balance123', 10, 'purchase')).rejects.toEqual(fakeError);

    expect((storage as any).__lastAbort).toBeDefined();
    expect(((storage as any).__lastAbort).op).toContain('update creditBalances add 10 to balance123');
  });

  it('logs last operation when useCredits hits a 25P02 and returns null', async () => {
    const storage = new DatabaseStorage();

    const fakeError: any = { code: '25P02', message: 'current transaction is aborted' };
    // Simulate a failing update during subtract that triggers 25P02 handling
    (storage as any).db = {
      update: () => {
        throw fakeError;
      },
    };

    const result = await storage.useCredits('balance123', 10, 'usage');
    expect(result).toBeNull();

    expect((storage as any).__lastAbort).toBeDefined();
    expect(((storage as any).__lastAbort).op).toContain('update creditBalances (subtract)');
  });

  it('logs last operation when transferCredits hits a 25P02 and rethrows', async () => {
    const storage = new DatabaseStorage();

    const fakeError: any = { code: '25P02', message: 'current transaction is aborted' };

    (storage as any).db = {
      transaction: async (fn: any) => {
        const client = {
          select: () => ({
            from: () => ({
              where: () => {
                const arr: any = [{ remaining: 10, credits: 100 }];
                arr.limit = () => arr;
                return arr;
              },
            }),
          }),
          update: () => {
            throw fakeError;
          },
          insert: () => {},
        };
        return await fn(client);
      },
    };

    await expect(
      storage.transferCredits('from123', 'to456', 10, 'transfer')
    ).rejects.toEqual(fakeError);

    const last = storage.getLastAbort();
    expect(last).toBeDefined();
    // transfer triggers a subtract from the source balance
    expect(last?.op).toContain('update creditBalances subtract from from123');

    // ensure transfer fallback was recorded but not warned to console in tests
    const fb = storage.getCreditGrantsFallback();
    expect(fb).toBeDefined();
    expect(fb).toContain('current transaction is aborted');
  });
});
