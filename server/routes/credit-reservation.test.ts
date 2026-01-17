/** @jest-environment node */

/**
 * Critical Money-Path Tests for Credit Reservation System
 * 
 * These tests verify that the reserve-commit-release pattern correctly prevents:
 * 1. Concurrent overspending (race conditions)
 * 2. Double-charging on retries (idempotency)
 * 3. Free extractions during DB outages (fail-closed)
 * 4. Extraction results without successful charging (commit before response)
 */

import request from 'supertest';
import express from 'express';
import { createServer } from 'http';
import { registerRoutes } from '../routes';
import { storage } from '../storage';
import * as db from '../db';

describe('Credit Reservation - Money Path Safety Tests', () => {
  let app: ReturnType<typeof express>;
  let server: ReturnType<typeof createServer>;

  beforeAll(() => {
    app = express();
    server = createServer(app);
    registerRoutes(server, app);
  });

  beforeEach(async () => {
    // Setup test database state
    if (typeof (storage as any).clearAll === 'function') {
      await (storage as any).clearAll();
    }
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  /**
   * Test 1: Concurrency Overspend Protection
   * 
   * Scenario: User has exactly 1 extraction worth of credits
   * Action: Fire 10 concurrent requests with different idempotency keys
   * Expected: Only 1 succeeds, others get 402 Insufficient Credits
   */
  it('should prevent concurrent overspending via atomic reservation', async () => {
    // Setup: Create user with exactly 1 extraction worth of credits
    const testBalanceId = 'test-balance-concurrent';
    const creditCost = 10; // Assume 10 credits per extraction
    
    // Create the balance first, then add credits
    await storage.getOrCreateCreditBalance(`session:${testBalanceId}`);
    await storage.addCredits(
      testBalanceId,
      creditCost,
      'Test setup - single extraction',
      'test'
    );

    // Mock session/auth to use this balance
    const sessionId = 'test-session-concurrent';
    
    // Fire 10 concurrent requests with DIFFERENT idempotency keys
    const requests = Array.from({ length: 10 }, (_, i) =>
      request(app)
        .post('/api/images_mvp/extract')
        .set('Cookie', `metaextract_session=${sessionId}`)
        .set('Idempotency-Key', `test-concurrent-${i}`)
        .attach('file', Buffer.from('fake-image-data'), 'test.jpg')
        .field('ops', JSON.stringify({ ocr: false, forensics: false, embedding: false }))
    );

    const responses = await Promise.all(requests);

    // Assert: Exactly 1 success (200), rest are 402 or 503
    const successCount = responses.filter(r => r.status === 200).length;
    const insufficientCreditsCount = responses.filter(r => r.status === 402).length;
    const unavailableCount = responses.filter(r => r.status === 503).length;

    expect(successCount).toBe(1);
    expect(insufficientCreditsCount + unavailableCount).toBe(9);

    // Verify: Only 1 hold was committed
    const finalBalance = await storage.getOrCreateCreditBalance(testBalanceId, undefined);
    expect(finalBalance?.credits).toBe(0); // All credits consumed by the 1 successful request
  }, 30000); // 30 second timeout for concurrent requests

  /**
   * Test 2: Retry Idempotency Protection
   * 
   * Scenario: Same request sent twice with same Idempotency-Key
   * Expected: Second request returns existing hold, no double-charge
   */
  it('should not double-charge on retry with same Idempotency-Key', async () => {
    const testBalanceId = 'test-balance-idempotency';
    const creditCost = 10;
    
    await storage.addCredits(
      testBalanceId,
      creditCost * 2, // Enough for 2 extractions
      'Test setup - idempotency',
      'test'
    );

    const sessionId = 'test-session-idempotency';
    const idempotencyKey = 'test-retry-same-key';

    // First request
    const response1 = await request(app)
      .post('/api/images_mvp/extract')
      .set('Cookie', `metaextract_session=${sessionId}`)
      .set('Idempotency-Key', idempotencyKey)
      .attach('file', Buffer.from('fake-image-data'), 'test.jpg')
      .field('ops', JSON.stringify({ ocr: false, forensics: false, embedding: false }));

    expect(response1.status).toBe(200);

    // Second request - SAME idempotency key (simulates retry)
    const response2 = await request(app)
      .post('/api/images_mvp/extract')
      .set('Cookie', `metaextract_session=${sessionId}`)
      .set('Idempotency-Key', idempotencyKey) // Same key!
      .attach('file', Buffer.from('fake-image-data'), 'test.jpg')
      .field('ops', JSON.stringify({ ocr: false, forensics: false, embedding: false }));

    // Should succeed (idempotent) but not double-charge
    expect(response2.status).toBe(200);

    // Verify: Only charged once
    const finalBalance = await storage.getOrCreateCreditBalance(testBalanceId, undefined);
    expect(finalBalance?.credits).toBe(creditCost); // Still have 1 extraction worth left
  }, 20000);

  /**
   * Test 3: DB Outage Fail-Closed Protection
   * 
   * Scenario: Database becomes unavailable during paid extraction
   * Expected: 503 Service Unavailable, Python extraction never invoked
   */
  it('should fail closed on DB outage and not run Python extraction', async () => {
    // Mock isDatabaseConnected to return false (simulates DB outage)
    const isDatabaseConnectedSpy = jest.spyOn(db, 'isDatabaseConnected');
    isDatabaseConnectedSpy.mockReturnValue(false);

    // Track if Python was invoked
    let pythonInvoked = false;
    const extractionHelpers = require('../utils/extraction-helpers');
    const extractMetadataSpy = jest.spyOn(
      extractionHelpers,
      'extractMetadataWithPython'
    );
    extractMetadataSpy.mockImplementation(async () => {
      pythonInvoked = true;
      return { /* mock metadata */ };
    });

    const sessionId = 'test-session-db-outage';

    const response = await request(app)
      .post('/api/images_mvp/extract')
      .set('Cookie', `metaextract_session=${sessionId}`)
      .set('Idempotency-Key', 'test-db-outage')
      .attach('file', Buffer.from('fake-image-data'), 'test.jpg')
      .field('ops', JSON.stringify({ ocr: false, forensics: false, embedding: false }));

    // Assert: 503 response, Python was NEVER invoked
    expect(response.status).toBe(503);
    expect(response.body.error).toMatch(/unavailable/i);
    expect(pythonInvoked).toBe(false);
  }, 10000);

  /**
   * Test 4: Commit Failure Protection
   * 
   * Scenario: Python succeeds but commitHold fails
   * Expected: 503 response, no extraction result returned, hold released
   */
  it('should not return extraction result if commit fails', async () => {
    const testBalanceId = 'test-balance-commit-fail';
    const creditCost = 10;
    
    await storage.addCredits(
      testBalanceId,
      creditCost,
      'Test setup - commit failure',
      'test'
    );

    const sessionId = 'test-session-commit-fail';

    // Mock commitHold to fail
    const commitHoldSpy = jest.spyOn(storage, 'commitHold');
    commitHoldSpy.mockRejectedValueOnce(new Error('Commit failed - simulated'));

    const response = await request(app)
      .post('/api/images_mvp/extract')
      .set('Cookie', `metaextract_session=${sessionId}`)
      .set('Idempotency-Key', 'test-commit-fail')
      .attach('file', Buffer.from('fake-image-data'), 'test.jpg')
      .field('ops', JSON.stringify({ ocr: false, forensics: false, embedding: false }));

    // Assert: 503 response (not 200), no extraction data returned
    expect(response.status).toBe(503);
    expect(response.body.error).toBeDefined();
    expect(response.body.metadata).toBeUndefined(); // No extraction result

    // Verify: Hold was released (credits refunded)
    const finalBalance = await storage.getOrCreateCreditBalance(testBalanceId, undefined);
    expect(finalBalance?.credits).toBe(creditCost); // Credits refunded
  }, 15000);

  /**
   * Test 5: Missing Idempotency-Key Rejection
   * 
   * Scenario: Paid extraction without Idempotency-Key header
   * Expected: 400 Bad Request
   */
  it('should require Idempotency-Key header for paid extractions', async () => {
    const sessionId = 'test-session-no-idem-key';

    const response = await request(app)
      .post('/api/images_mvp/extract')
      .set('Cookie', `metaextract_session=${sessionId}`)
      // Intentionally omit Idempotency-Key header
      .attach('file', Buffer.from('fake-image-data'), 'test.jpg')
      .field('ops', JSON.stringify({ ocr: false, forensics: false, embedding: false }));

    // Assert: 400 response requiring idempotency key
    expect(response.status).toBe(400);
    expect(response.body.error).toMatch(/Idempotency-Key/i);
  });

  /**
   * Test 6: Hold Expiry and Cleanup
   * 
   * Scenario: Hold expires without being committed
   * Expected: Cleanup job releases hold and refunds credits
   */
  it('should automatically release expired holds', async () => {
    const testBalanceId = 'test-balance-expiry';
    const creditCost = 10;
    
    await storage.addCredits(
      testBalanceId,
      creditCost,
      'Test setup - expiry',
      'test'
    );

    // Create a hold with very short expiry (1 second)
    const requestId = 'test-expiry-hold';
    await storage.reserveCredits(
      requestId,
      testBalanceId,
      creditCost,
      'Test hold for expiry',
      undefined,
      1000 // 1 second expiry
    );

    // Verify hold was created and credits deducted
    const balanceAfterReserve = await storage.getOrCreateCreditBalance(testBalanceId, undefined);
    expect(balanceAfterReserve?.credits).toBe(0);

    // Wait for expiry
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Run cleanup
    const releasedCount = await storage.cleanupExpiredHolds();
    expect(releasedCount).toBeGreaterThan(0);

    // Verify credits were refunded
    const balanceAfterCleanup = await storage.getOrCreateCreditBalance(testBalanceId, undefined);
    expect(balanceAfterCleanup?.credits).toBe(creditCost);
  }, 10000);
});
