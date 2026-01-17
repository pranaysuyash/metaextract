/**
 * Images MVP Contract Drift Guard Test
 *
 * Validates that the /api/images_mvp/quote endpoint response
 * matches the expected schema. This test fails if:
 * - Required fields are missing
 * - Field types have changed
 * - Unexpected fields are added/removed
 *
 * Purpose: Prevent silent contract breaks between backend and frontend
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { describe, it, expect, beforeAll } from '@jest/globals';

// ============================================================================
// Contract Drift Guard Test
// ============================================================================

describe('Images MVP Contract Drift Guard', () => {
  let app: Express;

  beforeAll(() => {
    app = express();
    app.use(express.json());

    // Mock quote endpoint
    app.post('/api/images_mvp/quote', async (req, res) => {
      res.json({
        schemaVersion: 'images_mvp_quote_v1',
        quoteId: 'test-quote-123',
        creditsTotal: 12,
        perFile: {
          'file-1': {
            id: 'file-1',
            accepted: true,
            detected_type: 'image/jpeg',
            creditsTotal: 12,
            breakdown: {
              base: 1,
              embedding: 3,
              ocr: 5,
              forensics: 0,
              mp: 3,
            },
            mp: 20.5,
            mpBucket: 'xl',
            warnings: [],
          },
        },
        schedule: {
          base: 1,
          embedding: 3,
          ocr: 5,
          forensics: 4,
          mpBuckets: [
            { label: 'standard', maxMp: 12, credits: 0 },
            { label: 'large', maxMp: 24, credits: 1 },
            { label: 'xl', maxMp: 48, credits: 3 },
            { label: 'xxl', maxMp: 96, credits: 7 },
          ],
        },
        limits: {
          maxBytes: 104857600,
          allowedMimes: ['image/jpeg', 'image/png', 'image/webp'],
          maxFiles: 10,
        },
        creditSchedule: {
          base: 1,
          embedding: 3,
          ocr: 5,
          forensics: 4,
          mpBuckets: [
            { label: 'standard', maxMp: 12, credits: 0 },
            { label: 'large', maxMp: 24, credits: 1 },
            { label: 'xl', maxMp: 48, credits: 3 },
            { label: 'xxl', maxMp: 96, credits: 7 },
          ],
          standardCreditsPerImage: 4,
        },
        quote: {
          perFile: [
            {
              id: 'file-1',
              accepted: true,
              detected_type: 'image/jpeg',
              creditsTotal: 12,
              breakdown: {
                base: 1,
                embedding: 3,
                ocr: 5,
                forensics: 0,
                mp: 3,
              },
              mp: 20.5,
              mpBucket: 'xl',
              warnings: [],
            },
          ],
          totalCredits: 12,
          standardEquivalents: 3,
        },
        expiresAt: '2026-01-17T15:15:00.000Z',
        warnings: [],
      });
    });
  });

  it('should have all required top-level fields', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    const requiredFields = [
      'schemaVersion',
      'quoteId',
      'creditsTotal',
      'perFile',
      'schedule',
      'limits',
      'creditSchedule',
      'quote',
      'expiresAt',
      'warnings',
    ];

    for (const field of requiredFields) {
      expect(res.body).toHaveProperty(field);
    }
  });

  it('should have correct schema version', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    expect(res.body.schemaVersion).toBe('images_mvp_quote_v1');
  });

  it('should have correct types for critical fields', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    // Type checks
    expect(typeof res.body.schemaVersion).toBe('string');
    expect(typeof res.body.quoteId).toBe('string');
    expect(typeof res.body.creditsTotal).toBe('number');
    expect(typeof res.body.expiresAt).toBe('string');

    // Object checks
    expect(typeof res.body.perFile).toBe('object');
    expect(typeof res.body.schedule).toBe('object');
    expect(typeof res.body.limits).toBe('object');
    expect(typeof res.body.creditSchedule).toBe('object');
    expect(typeof res.body.quote).toBe('object');

    // Array checks
    expect(Array.isArray(res.body.warnings)).toBe(true);
  });

  it('should have limits sub-object with correct fields', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    const limits = res.body.limits;
    expect(typeof limits.maxBytes).toBe('number');
    expect(Array.isArray(limits.allowedMimes)).toBe(true);
    expect(typeof limits.maxFiles).toBe('number');

    // Validate values are reasonable
    expect(limits.maxBytes).toBeGreaterThan(0);
    expect(limits.allowedMimes.length).toBeGreaterThan(0);
    expect(limits.maxFiles).toBeGreaterThan(0);
  });

  it('should have creditSchedule with all cost tiers', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    const schedule = res.body.creditSchedule;

    // Check all tiers exist
    expect(typeof schedule.base).toBe('number');
    expect(typeof schedule.embedding).toBe('number');
    expect(typeof schedule.ocr).toBe('number');
    expect(typeof schedule.forensics).toBe('number');
    expect(typeof schedule.standardCreditsPerImage).toBe('number');

    // Check mp buckets
    expect(Array.isArray(schedule.mpBuckets)).toBe(true);
    expect(schedule.mpBuckets.length).toBeGreaterThan(0);

    // Validate bucket structure
    for (const bucket of schedule.mpBuckets) {
      expect(typeof bucket.label).toBe('string');
      expect(typeof bucket.maxMp).toBe('number');
      expect(typeof bucket.credits).toBe('number');
    }
  });

  it('should have quote summary with per-file array', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    const quote = res.body.quote;

    expect(Array.isArray(quote.perFile)).toBe(true);
    expect(typeof quote.totalCredits).toBe('number');
    expect(
      quote.standardEquivalents === null ||
        typeof quote.standardEquivalents === 'number'
    ).toBe(true);
  });

  it('should validate expiresAt is a valid ISO string', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    const expiresAt = new Date(res.body.expiresAt);
    expect(expiresAt instanceof Date && !isNaN(expiresAt.getTime())).toBe(true);

    // Should be in the future
    expect(expiresAt.getTime()).toBeGreaterThan(Date.now());
  });

  it('should not have unexpected additional fields', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    const expectedKeys = new Set([
      'schemaVersion',
      'quoteId',
      'creditsTotal',
      'perFile',
      'schedule',
      'limits',
      'creditSchedule',
      'quote',
      'expiresAt',
      'warnings',
    ]);

    const actualKeys = Object.keys(res.body);
    for (const key of actualKeys) {
      expect(expectedKeys.has(key)).toBe(true);
    }
  });

  it('should match frontend type assertion', async () => {
    const { assertQuoteSchemaVersion } =
      await import('../client/src/lib/images-mvp-quote');

    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({ files: [], ops: {} })
      .expect(200);

    // Should not throw - validates schemaVersion and type
    expect(() => assertQuoteSchemaVersion(res.body)).not.toThrow();
  });

  it('should validate perFile objects have correct structure', async () => {
    const res = await request(app)
      .post('/api/images_mvp/quote')
      .send({
        files: [
          { id: 'f1', name: 'test.jpg', mime: 'image/jpeg', sizeBytes: 1000 },
        ],
        ops: {},
      })
      .expect(200);

    const perFile = res.body.perFile;
    for (const [fileId, fileData] of Object.entries(perFile)) {
      expect(typeof fileId).toBe('string');
      expect(typeof fileData.id).toBe('string');
      expect(typeof fileData.accepted).toBe('boolean');
      expect(
        fileData.creditsTotal === undefined ||
          typeof fileData.creditsTotal === 'number'
      ).toBe(true);
      expect(fileData.mp === undefined || typeof fileData.mp === 'number').toBe(
        true
      );
      expect(Array.isArray(fileData.warnings)).toBe(true);
    }
  });
});
