import { describe, it, expect, beforeEach } from '@jest/globals';
import { eq } from 'drizzle-orm';
import { trialUsages } from '@shared/schema';
import { getDatabase } from '../db';
import { storage } from '../storage/index';
import { randomUUID } from 'crypto';
import {
  generateClientToken,
  verifyClientToken,
} from './free-quota-enforcement';
import { resolveAccessDecision, redactMetadata } from './access-control';
import type { Request } from 'express';
import type { FrontendMetadataResponse } from './extraction-helpers';

describe('AccessControl - Entitlement Resolver', () => {
  let mockReq: Partial<Request>;

  beforeEach(() => {
    mockReq = {
      body: {},
      cookies: {},
      headers: {},
    };
  });

  describe('Trial Users', () => {
    it('should allow trial with 0 previous uses', async () => {
      const email = `test+trial0-${randomUUID()}@example.com`;
      mockReq.body = { trial_email: email };

      const db = getDatabase();
      await db.delete(trialUsages).where(eq(trialUsages.email, email));

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(true);
      expect(decision.mode).toBe('full');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('TRIAL_FULL');
      expect(decision.freeQuotaUsed).toBe(0);
    });

    it('should allow trial with 1 previous use', async () => {
      const email = `test+trial1-${randomUUID()}@example.com`;
      mockReq.body = { trial_email: email };

      const db = getDatabase();
      await db.delete(trialUsages).where(eq(trialUsages.email, email));
      await db.insert(trialUsages).values({ email, uses: 1 });

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(true);
      expect(decision.mode).toBe('full');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('TRIAL_FULL');
      expect(decision.freeQuotaUsed).toBe(1);
    });

    it('should block trial with 2 previous uses', async () => {
      const email = `test+trial2-${randomUUID()}@example.com`;
      mockReq.body = { trial_email: email };

      const db = getDatabase();
      await db.delete(trialUsages).where(eq(trialUsages.email, email));
      await db.insert(trialUsages).values({ email, uses: 2 });

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(false);
      expect(decision.mode).toBe('redacted');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('BLOCKED_NO_CREDITS');
      expect(decision.freeQuotaUsed).toBe(2);
    });
  });

  describe('Authenticated Users', () => {
    it('should allow authenticated user with credits', async () => {
      const userId = `user123-${randomUUID()}`;
      (mockReq as any).user = { id: userId };

      const sessionId = `images_mvp:user:${userId}`;
      const balance = await storage.getOrCreateCreditBalance(sessionId, userId);
      await storage.addCredits(balance.id, 5, 'test credits');

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(true);
      expect(decision.mode).toBe('full');
      expect(decision.chargeCredits).toBe(true);
      expect(decision.reason).toBe('PAID_FULL');
      expect(decision.creditsRemaining).toBe(4);
      expect(decision.userId).toBe(userId);
    });

    it('should block authenticated user with 0 credits', async () => {
      const userId = `user123-${randomUUID()}`;
      (mockReq as any).user = { id: userId };

      const sessionId = `images_mvp:user:${userId}`;
      await storage.getOrCreateCreditBalance(sessionId, userId);

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(false);
      expect(decision.mode).toBe('redacted');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('BLOCKED_NO_CREDITS');
      expect(decision.creditsRemaining).toBe(0);
      expect(decision.userId).toBe(userId);
    });
  });

  describe('Anonymous Users (Free Quota)', () => {
    it('should allow anonymous user on first request', async () => {
      const token = generateClientToken();
      const decoded = verifyClientToken(token);
      if (!decoded) throw new Error('Test token decode failed');

      await storage.set(`quota:${decoded.clientId}`, JSON.stringify({ freeUsed: 0 }));

      mockReq.cookies = { metaextract_client: token };

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(true);
      expect(decision.mode).toBe('redacted');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('FREE_REDACTED');
      expect(decision.freeQuotaUsed).toBe(0);
      expect(decision.userId).toBeNull();
    });

    it('should allow anonymous user with 1 previous request', async () => {
      const token = generateClientToken();
      const decoded = verifyClientToken(token);
      if (!decoded) throw new Error('Test token decode failed');

      await storage.set(`quota:${decoded.clientId}`, JSON.stringify({ freeUsed: 1 }));

      mockReq.cookies = { metaextract_client: token };

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(true);
      expect(decision.mode).toBe('redacted');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('FREE_REDACTED');
      expect(decision.freeQuotaUsed).toBe(1);
      expect(decision.userId).toBeNull();
    });

    it('should block anonymous user with 2 previous requests', async () => {
      const token = generateClientToken();
      const decoded = verifyClientToken(token);
      if (!decoded) throw new Error('Test token decode failed');

      await storage.set(`quota:${decoded.clientId}`, JSON.stringify({ freeUsed: 2 }));

      mockReq.cookies = { metaextract_client: token };

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(false);
      expect(decision.mode).toBe('redacted');
      expect(decision.chargeCredits).toBe(false);
      expect(decision.reason).toBe('BLOCKED_NO_CREDITS');
      expect(decision.freeQuotaUsed).toBe(2);
      expect(decision.userId).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('should prioritize paid over free when both available', async () => {
      const userId = `user123-${randomUUID()}`;
      (mockReq as any).user = { id: userId };

      const sessionId = `images_mvp:user:${userId}`;
      const balance = await storage.getOrCreateCreditBalance(sessionId, userId);
      await storage.addCredits(balance.id, 5, 'test credits');

      const decision = await resolveAccessDecision(mockReq as Request);

      expect(decision.allowed).toBe(true);
      expect(decision.mode).toBe('full');
      expect(decision.chargeCredits).toBe(true);
      expect(decision.reason).toBe('PAID_FULL');
      expect(decision.creditsRemaining).toBe(4);
      expect(decision.freeQuotaUsed).toBe(0);
    });
  });
});

describe('AccessControl - Redaction', () => {
  let mockReport: FrontendMetadataResponse;

  beforeEach(() => {
    mockReport = {
      filename: 'test.jpg',
      filesize: '1024',
      filetype: 'jpg',
      mime_type: 'image/jpeg',
      gps: {
        latitude: 37.774929,
        longitude: -122.419418,
        google_maps_url: 'https://maps.google.com/?q=37.774929,-122.419418',
      },
      exif: {},
      filesystem: {
        created: '2024-01-01T00:00:00Z',
        modified: '2024-01-01T00:00:00Z',
        owner: 'user123',
        permissions_octal: '0644',
      },
      thumbnail: {
        has_embedded: true,
        width: 640,
        height: 480,
        data: 'base64data...',
      },
      burned_metadata: {
        has_burned_metadata: true,
        extracted_text: 'Secret text burned into image',
        confidence: 'high',
        parsed_data: {
          gps: { latitude: 37.774929, longitude: -122.419418 },
          plus_code: '849V+FQ',
          location: {
            city: 'San Francisco',
            state: 'CA',
            country: 'USA',
            street: '123 Main St',
          },
        },
      },
      extended_attributes: {
        available: true,
        count: 5,
        attributes: {
          attr1: 'value1',
          attr2: 'value2',
        },
      },
      perceptual_hashes: {
        phash: 'abc123',
        dhash: 'def456',
        ahash: 'ghi789',
        whash: 'jkl012',
        md5: 'md5hash',
        sha256: 'sha256hash',
      },
    } as any;
  });

  it('should not modify report when mode is full', () => {
    const result = redactMetadata(mockReport, 'full');

    expect(result.gps?.latitude).toBe(37.774929);
    expect(result.gps?.longitude).toBe(-122.419418);
    expect(result.gps?.google_maps_url).toBeDefined();
    expect(result.burned_metadata?.extracted_text).toBe(
      'Secret text burned into image'
    );
  });

  it('should redact GPS coordinates when mode is redacted', () => {
    const result = redactMetadata(mockReport, 'redacted');

    expect(result.gps?.latitude).toBe(37.77);
    expect(result.gps?.longitude).toBe(-122.42);
    expect(result.gps?.google_maps_url).toBeUndefined();
  });

  it('should redact burned metadata text and precise location when mode is redacted', () => {
    const result = redactMetadata(mockReport, 'redacted');

    expect(result.burned_metadata?.extracted_text).toBeNull();
    expect(result.burned_metadata?.parsed_data?.gps).toBeUndefined();
    expect(result.burned_metadata?.parsed_data?.plus_code).toBeUndefined();
    expect(result.burned_metadata?.parsed_data?.location).toEqual({
      city: 'San Francisco',
      state: 'CA',
      country: 'USA',
    });
  });

  it('should redact filesystem sensitive fields when mode is redacted', () => {
    const result = redactMetadata(mockReport, 'redacted');

    expect(result.filesystem?.owner).toBeUndefined();
    expect(result.filesystem?.permissions_octal).toBeUndefined();
    expect(result.filesystem?.created).toBeDefined();
    expect(result.filesystem?.modified).toBeDefined();
  });

  it('should redact thumbnail data when mode is redacted', () => {
    const result = redactMetadata(mockReport, 'redacted');

    expect(result.thumbnail?.has_embedded).toBe(true);
    expect(result.thumbnail?.width).toBe(640);
    expect(result.thumbnail?.height).toBe(480);
    expect((result.thumbnail as any)?.data).toBeUndefined();
  });

  it('should redact extended attribute values when mode is redacted', () => {
    const result = redactMetadata(mockReport, 'redacted');

    expect(result.extended_attributes?.available).toBe(true);
    expect(result.extended_attributes?.count).toBe(5);
    expect(result.extended_attributes?.attributes?.attr1).toBeNull();
    expect(result.extended_attributes?.attributes?.attr2).toBeNull();
  });

  it('should redact extra perceptual hashes when mode is redacted', () => {
    const result = redactMetadata(mockReport, 'redacted');

    expect(result.perceptual_hashes?.phash).toBe('abc123');
    expect(result.perceptual_hashes?.dhash).toBe('def456');
    expect(result.perceptual_hashes?.ahash).toBe('ghi789');
    expect(result.perceptual_hashes?.whash).toBe('jkl012');
    expect((result.perceptual_hashes as any)?.md5).toBeUndefined();
    expect((result.perceptual_hashes as any)?.sha256).toBeUndefined();
  });
});
