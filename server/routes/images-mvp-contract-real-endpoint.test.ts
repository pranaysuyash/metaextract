/**
 * Images MVP Contract Drift Guard - REAL ENDPOINT Integration Test
 *
 * This test hits the ACTUAL /api/images_mvp/quote route (not a mock).
 * It will fail if the backend response shape changes.
 *
 * Purpose: Prevent silent contract breaks between backend and frontend.
 * This is the actual "drift guard" - the mock test only validates the validator function.
 */

import request from 'supertest';
import { setupApp } from '../index';
import { IMAGES_MVP_QUOTE_SCHEMA_VERSION } from '../../client/src/lib/images-mvp-quote';
import { describe, it, expect } from '@jest/globals';

describe('Images MVP Contract - Real Endpoint (Integration)', () => {
  let app: any;
  let teardown: (() => Promise<void>) | null = null;

  beforeAll(async () => {
    // Setup app with all routes registered
    const result = await setupApp({ testMode: true });
    app = result.app;
    teardown = result.teardown;
  });

  afterAll(async () => {
    if (teardown) {
      await teardown();
    }
  });
  it('real /api/images_mvp/quote response matches contract v1', async () => {
    const response = await request(app)
      .post('/api/images_mvp/quote')
      .send({
        files: [],
        ops: { embedding: false, ocr: false, forensics: false },
      })
      .expect(200);

    const body = response.body;

    // Validate schemaVersion (exact match)
    expect(body.schemaVersion).toBe(IMAGES_MVP_QUOTE_SCHEMA_VERSION);

    // Required top-level keys and types
    expect(typeof body.quoteId).toBe('string');
    expect(typeof body.expiresAt).toBe('string');
    expect(Array.isArray(body.warnings)).toBe(true);

    // limits object structure
    expect(body).toHaveProperty('limits');
    expect(typeof body.limits.maxFiles).toBe('number');
    expect(typeof body.limits.maxBytes).toBe('number');
    expect(Array.isArray(body.limits.allowedMimes)).toBe(true);

    // creditSchedule object structure
    expect(body).toHaveProperty('creditSchedule');
    expect(typeof body.creditSchedule.base).toBe('number');
    expect(typeof body.creditSchedule.embedding).toBe('number');
    expect(typeof body.creditSchedule.ocr).toBe('number');
    expect(typeof body.creditSchedule.forensics).toBe('number');
    expect(Array.isArray(body.creditSchedule.mpBuckets)).toBe(true);
    expect(typeof body.creditSchedule.standardCreditsPerImage).toBe('number');

    // quote object structure
    expect(body).toHaveProperty('quote');
    expect(Array.isArray(body.quote.perFile)).toBe(true);
    expect(typeof body.quote.totalCredits).toBe('number');
    expect(body.quote.standardEquivalents === null || typeof body.quote.standardEquivalents === 'number').toBe(true);

    // Strict keyset validation (tight coupling choice)
    // If backend adds/removes fields, this test will fail
    // NOTE: Backend includes legacy keys for backwards compat: creditsTotal, perFile, schedule
    const expectedKeys = [
      'schemaVersion',
      'limits',
      'creditSchedule',
      'quote',
      'quoteId',
      'expiresAt',
      'warnings',
      'creditsTotal',  // legacy
      'perFile',       // legacy
      'schedule',      // legacy
    ].sort();
    const actualKeys = Object.keys(body).sort();
    expect(actualKeys).toEqual(expectedKeys);
  });

  it('real /api/images_mvp/quote handles file input correctly', async () => {
    const response = await request(app)
      .post('/api/images_mvp/quote')
      .send({
        files: [
          {
            id: 'test-file-1',
            name: 'test.jpg',
            mime: 'image/jpeg',
            sizeBytes: 1024 * 100, // 100KB
            width: 1920,
            height: 1080,
          },
        ],
        ops: { embedding: false, ocr: false, forensics: false },
      })
      .expect(200);

    const body = response.body;

    // Validate response structure
    expect(body.schemaVersion).toBe(IMAGES_MVP_QUOTE_SCHEMA_VERSION);
    expect(body.quote.perFile.length).toBe(1);
    expect(body.quote.perFile[0].id).toBe('test-file-1');
    expect(typeof body.quote.perFile[0].accepted).toBe('boolean');
    expect(typeof body.quote.totalCredits).toBe('number');
  });

  it('real /api/images_mvp/quote expiresAt is valid future date', async () => {
    const response = await request(app)
      .post('/api/images_mvp/quote')
      .send({
        files: [],
        ops: { embedding: false, ocr: false, forensics: false },
      })
      .expect(200);

    const body = response.body;
    const expiresAt = new Date(body.expiresAt);
    const now = new Date();

    // expiresAt should be a valid date in the future
    expect(expiresAt.toString()).not.toBe('Invalid Date');
    expect(expiresAt.getTime()).toBeGreaterThan(now.getTime());
  });

  it('real /api/images_mvp/quote limits.allowedMimes contains expected types', async () => {
    const response = await request(app)
      .post('/api/images_mvp/quote')
      .send({
        files: [],
        ops: { embedding: false, ocr: false, forensics: false },
      })
      .expect(200);

    const body = response.body;

    // Validate allowed MIME types structure
    expect(Array.isArray(body.limits.allowedMimes)).toBe(true);
    expect(body.limits.allowedMimes.length).toBeGreaterThan(0);
    body.limits.allowedMimes.forEach((mime: unknown) => {
      expect(typeof mime).toBe('string');
    });
  });

  it('real /api/images_mvp/quote creditSchedule.mpBuckets has correct structure', async () => {
    const response = await request(app)
      .post('/api/images_mvp/quote')
      .send({
        files: [],
        ops: { embedding: false, ocr: false, forensics: false },
      })
      .expect(200);

    const body = response.body;

    // Validate mpBuckets structure
    expect(Array.isArray(body.creditSchedule.mpBuckets)).toBe(true);
    expect(body.creditSchedule.mpBuckets.length).toBeGreaterThan(0);

    body.creditSchedule.mpBuckets.forEach((bucket: any) => {
      expect(typeof bucket.label).toBe('string');
      expect(typeof bucket.maxMp).toBe('number');
      expect(typeof bucket.credits).toBe('number');
    });
  });
});
