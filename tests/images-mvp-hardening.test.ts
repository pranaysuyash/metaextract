/**
 * Images MVP Hardening Tests
 *
 * Tests for two critical production fixes:
 * 1. Quote endpoint rate limiting (Gate C)
 * 2. Quote response schema versioning (Gate E)
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import { MemStorage } from '../server/storage/mem';
import { createRateLimiter } from '../server/middleware/rateLimit';

// ============================================================================
// Test App Setup
// ============================================================================

let app: Express;
let storage: MemStorage;

beforeAll(() => {
  app = express();
  storage = new MemStorage();

  app.use(express.json());

  // Route-specific rate limiter for quote endpoint (same as production)
  const quoteLimiter = createRateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: 30,
    keyGenerator: req => req.ip || 'test-ip',
  } as any);

  // Quote endpoint (simplified for testing)
  app.post('/api/images_mvp/quote', quoteLimiter, async (req, res) => {
    try {
      const quote = await storage.createImagesMvpQuote({
        sessionId: req.get('x-session-id') || 'test-session',
        files: req.body.files || [],
        ops: req.body.ops || {},
        creditsTotal: 4,
        perFileCredits: {},
        perFile: {},
        schedule: {},
        expiresAt: new Date(Date.now() + 15 * 60 * 1000),
      });

      res.json({
        schemaVersion: 'images_mvp_quote_v1', // GATE E: Schema version
        quoteId: quote.id,
        creditsTotal: quote.creditsTotal,
        expiresAt: quote.expiresAt.toISOString(),
        limits: { maxBytes: 100 * 1024 * 1024, allowedMimes: [], maxFiles: 10 },
        creditSchedule: {
          base: 1,
          embedding: 3,
          ocr: 5,
          forensics: 4,
          mpBuckets: [],
          standardCreditsPerImage: 4,
        },
        quote: { perFile: [], totalCredits: 4, standardEquivalents: 1 },
        warnings: [],
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to create quote' });
    }
  });
});

// ============================================================================
// GATE C: Quote Endpoint Rate Limiting
// ============================================================================

describe('Gate C: Quote Endpoint Abuse Control', () => {
  it('should accept normal request rate (under limit)', async () => {
    // Make 15 requests (under 30/min limit)
    for (let i = 0; i < 15; i++) {
      const res = await request(app)
        .post('/api/images_mvp/quote')
        .set('x-session-id', `session-${i}`)
        .send({ files: [], ops: {} });

      expect(res.status).toBe(200);
      expect(res.body.quoteId).toBeDefined();
    }
  });

  it('should reject requests exceeding rate limit', async () => {
    // Make 35 requests rapidly (exceeds 30/min limit)
    const results = [];
    for (let i = 0; i < 35; i++) {
      const res = await request(app)
        .post('/api/images_mvp/quote')
        .set('x-session-id', `burst-test-${i}`)
        .send({ files: [], ops: {} });

      results.push(res.status);
    }

    // Some requests should be rejected with 429
    const rejected = results.filter(status => status === 429);
    expect(rejected.length).toBeGreaterThan(0);

    // Count successful requests (should be ~30 or less)
    const accepted = results.filter(status => status === 200);
    expect(accepted.length).toBeLessThanOrEqual(30);
  });

  it('should return 429 Too Many Requests when rate limit exceeded', async () => {
    // Exhaust rate limit
    for (let i = 0; i < 30; i++) {
      await request(app)
        .post('/api/images_mvp/quote')
        .set('x-session-id', `exhaust-${i}`)
        .send({ files: [], ops: {} });
    }

    // Next request should be rejected
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .set('x-session-id', 'final-request')
      .send({ files: [], ops: {} });

    expect(res.status).toBe(429);
  });
});

// ============================================================================
// GATE E: Quote Response Schema Versioning
// ============================================================================

describe('Gate E: Frontend Contract Stability', () => {
  it('should include schemaVersion in quote response', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .set('x-session-id', 'schema-test')
      .send({ files: [], ops: {} });

    expect(res.status).toBe(200);
    expect(res.body.schemaVersion).toBe('images_mvp_quote_v1');
  });

  it('should have all required top-level fields', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .set('x-session-id', 'required-fields-test')
      .send({ files: [], ops: {} });

    expect(res.status).toBe(200);

    // Check exact top-level keys match expected schema
    const expectedKeys = [
      'schemaVersion',
      'quoteId',
      'creditsTotal',
      'expiresAt',
      'limits',
      'creditSchedule',
      'quote',
      'warnings',
    ];

    const actualKeys = Object.keys(res.body).sort();
    const expectedKeysSort = expectedKeys.sort();

    expect(actualKeys).toEqual(expectedKeysSort);
  });

  it('should have correct types for critical fields', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .set('x-session-id', 'type-check-test')
      .send({ files: [], ops: {} });

    expect(res.status).toBe(200);

    // Type validations
    expect(typeof res.body.schemaVersion).toBe('string');
    expect(typeof res.body.quoteId).toBe('string');
    expect(typeof res.body.creditsTotal).toBe('number');
    expect(typeof res.body.expiresAt).toBe('string');
    expect(typeof res.body.limits.maxBytes).toBe('number');
    expect(typeof res.body.limits.maxFiles).toBe('number');
    expect(Array.isArray(res.body.limits.allowedMimes)).toBe(true);
    expect(typeof res.body.creditSchedule.base).toBe('number');
    expect(Array.isArray(res.body.quote.perFile)).toBe(true);
    expect(Array.isArray(res.body.warnings)).toBe(true);
  });

  it('should reject if schemaVersion is missing (simulated)', async () => {
    // Test the validation function from frontend
    const { assertQuoteSchemaVersion } =
      await import('../client/src/lib/images-mvp-quote');

    const invalidResponse = {
      quoteId: 'test',
      creditsTotal: 4,
      // Missing schemaVersion!
    };

    expect(() => assertQuoteSchemaVersion(invalidResponse)).toThrow(
      /Unsupported quote schemaVersion/
    );
  });

  it('should reject if schemaVersion is wrong (simulated)', async () => {
    const { assertQuoteSchemaVersion } =
      await import('../client/src/lib/images-mvp-quote');

    const invalidResponse = {
      schemaVersion: 'images_mvp_quote_v2', // Wrong version!
      quoteId: 'test',
      creditsTotal: 4,
    };

    expect(() => assertQuoteSchemaVersion(invalidResponse)).toThrow(
      /Unsupported quote schemaVersion: images_mvp_quote_v2/
    );
  });

  it('should accept valid schemaVersion (simulated)', async () => {
    const { assertQuoteSchemaVersion, IMAGES_MVP_QUOTE_SCHEMA_VERSION } =
      await import('../client/src/lib/images-mvp-quote');

    const validResponse = {
      schemaVersion: IMAGES_MVP_QUOTE_SCHEMA_VERSION,
      quoteId: 'test',
      creditsTotal: 4,
      expiresAt: '2026-01-17T15:00:00Z',
      limits: { maxBytes: 100000000, allowedMimes: [], maxFiles: 10 },
      creditSchedule: {
        base: 1,
        embedding: 3,
        ocr: 5,
        forensics: 4,
        mpBuckets: [],
        standardCreditsPerImage: 4,
      },
      quote: { perFile: [], totalCredits: 4, standardEquivalents: 1 },
      warnings: [],
    };

    // Should not throw
    assertQuoteSchemaVersion(validResponse);
    expect(validResponse.schemaVersion).toBe('images_mvp_quote_v1');
  });
});

// ============================================================================
// Quote Cleanup Test
// ============================================================================

describe('Quote Cleanup (Prevents DB growth)', () => {
  it('should cleanup expired quotes on demand', async () => {
    // Create multiple quotes
    const now = Date.now();
    const expiredTime = new Date(now - 1000); // Expired 1 second ago

    const quote1 = await storage.createImagesMvpQuote({
      sessionId: 'cleanup-test-1',
      files: [],
      ops: {},
      creditsTotal: 4,
      perFileCredits: {},
      perFile: {},
      schedule: {},
      expiresAt: expiredTime, // Expired
    });

    const quote2 = await storage.createImagesMvpQuote({
      sessionId: 'cleanup-test-2',
      files: [],
      ops: {},
      creditsTotal: 4,
      perFileCredits: {},
      perFile: {},
      schedule: {},
      expiresAt: new Date(now + 15 * 60 * 1000), // Still valid
    });

    // Verify both exist before cleanup
    const before1 = await storage.getImagesMvpQuote(quote1.id);
    const before2 = await storage.getImagesMvpQuote(quote2.id);
    expect(before1).toBeDefined();
    expect(before2).toBeDefined();

    // Run cleanup
    const result = await storage.cleanupExpiredQuotes();

    // Verify result
    expect(result).toBeGreaterThan(0); // At least one quote was deleted

    // Verify expired quote is gone
    const after1 = await storage.getImagesMvpQuote(quote1.id);
    expect(after1).toBeUndefined();

    // Verify non-expired quote still exists
    const after2 = await storage.getImagesMvpQuote(quote2.id);
    expect(after2).toBeDefined();
  });

  it('should return count of deleted quotes', async () => {
    // Create 5 expired quotes
    const expiredTime = new Date(Date.now() - 1000);

    const ids = [];
    for (let i = 0; i < 5; i++) {
      const quote = await storage.createImagesMvpQuote({
        sessionId: `cleanup-count-${i}`,
        files: [],
        ops: {},
        creditsTotal: 4,
        perFileCredits: {},
        perFile: {},
        schedule: {},
        expiresAt: expiredTime,
      });
      ids.push(quote.id);
    }

    // Run cleanup
    const result = await storage.cleanupExpiredQuotes();

    // Should report deleting 5 quotes
    expect(result).toBeGreaterThanOrEqual(5);

    // All should be gone
    for (const id of ids) {
      const quote = await storage.getImagesMvpQuote(id);
      expect(quote).toBeUndefined();
    }
  });
});
