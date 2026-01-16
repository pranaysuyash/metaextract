import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { storage } from './index';
import { ImagesMvpQuote, InsertImagesMvpQuote } from '../../shared/schema';

describe('Quote Storage', () => {
  let testQuote: InsertImagesMvpQuote;
  let createdQuote: ImagesMvpQuote;

  beforeEach(() => {
    // Create test quote data
    const expiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes from now
    
    testQuote = {
      sessionId: 'test-session-123',
      files: [
        {
          id: 'file-1',
          name: 'test-image.jpg',
          mime: 'image/jpeg',
          sizeBytes: 1024 * 1024, // 1MB
          width: 1920,
          height: 1080,
        },
      ],
      ops: {
        embedding: true,
        ocr: false,
        forensics: false,
      },
      creditsTotal: 5,
      perFileCredits: {
        'file-1': 5,
      },
      perFile: {
        'file-1': {
          id: 'file-1',
          accepted: true,
          detected_type: 'image/jpeg',
          creditsTotal: 5,
          mp: 2.07,
          mpBucket: 'standard',
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
        ],
        standardCreditsPerImage: 4,
      },
      expiresAt,
    };
  });

  afterEach(async () => {
    // Clean up test data
    if (createdQuote?.id) {
      try {
        await storage.expireQuote(createdQuote.id);
      } catch (error) {
        // Ignore cleanup errors
      }
    }
  });

  describe('createQuote', () => {
    it('should create a new quote with all required fields', async () => {
      createdQuote = await storage.createQuote(testQuote);

      expect(createdQuote).toBeDefined();
      expect(createdQuote.id).toBeDefined();
      expect(createdQuote.sessionId).toBe(testQuote.sessionId);
      expect(createdQuote.creditsTotal).toBe(testQuote.creditsTotal);
      expect(createdQuote.status).toBe('active');
      expect(createdQuote.createdAt).toBeDefined();
      expect(createdQuote.updatedAt).toBeDefined();
    });

    it('should generate UUID if not provided', async () => {
      const quoteWithoutId = { ...testQuote };
      delete (quoteWithoutId as any).id;
      
      createdQuote = await storage.createQuote(quoteWithoutId);
      
      expect(createdQuote.id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
    });
  });

  describe('getQuote', () => {
    beforeEach(async () => {
      createdQuote = await storage.createQuote(testQuote);
    });

    it('should retrieve an existing quote by ID', async () => {
      const retrievedQuote = await storage.getQuote(createdQuote.id);

      expect(retrievedQuote).toBeDefined();
      expect(retrievedQuote?.id).toBe(createdQuote.id);
      expect(retrievedQuote?.sessionId).toBe(testQuote.sessionId);
      expect(retrievedQuote?.creditsTotal).toBe(testQuote.creditsTotal);
    });

    it('should return undefined for non-existent quote', async () => {
      const retrievedQuote = await storage.getQuote('non-existent-id');
      expect(retrievedQuote).toBeUndefined();
    });

    it('should return undefined for expired quotes', async () => {
      // Create a quote that expires immediately
      const expiredQuote = await storage.createQuote({
        ...testQuote,
        expiresAt: new Date(Date.now() - 1000), // 1 second ago
      });

      const retrievedQuote = await storage.getQuote(expiredQuote.id);
      expect(retrievedQuote).toBeUndefined();
    });
  });

  describe('getQuoteBySessionId', () => {
    beforeEach(async () => {
      createdQuote = await storage.createQuote(testQuote);
    });

    it('should retrieve the most recent active quote for a session', async () => {
      const retrievedQuote = await storage.getQuoteBySessionId(testQuote.sessionId);

      expect(retrievedQuote).toBeDefined();
      expect(retrievedQuote?.id).toBe(createdQuote.id);
      expect(retrievedQuote?.sessionId).toBe(testQuote.sessionId);
    });

    it('should return undefined for non-existent session', async () => {
      const retrievedQuote = await storage.getQuoteBySessionId('non-existent-session');
      expect(retrievedQuote).toBeUndefined();
    });

    it('should return the most recent quote when multiple exist', async () => {
      // Create a second quote for the same session
      const newerQuote = await storage.createQuote({
        ...testQuote,
        files: [
          {
            id: 'file-2',
            name: 'test-image-2.jpg',
            mime: 'image/jpeg',
            sizeBytes: 2048 * 1024, // 2MB
            width: 2560,
            height: 1440,
          },
        ],
        creditsTotal: 8,
      });

      const retrievedQuote = await storage.getQuoteBySessionId(testQuote.sessionId);
      expect(retrievedQuote?.id).toBe(newerQuote.id);
      expect(retrievedQuote?.creditsTotal).toBe(8);
    });
  });

  describe('updateQuote', () => {
    beforeEach(async () => {
      createdQuote = await storage.createQuote(testQuote);
    });

    it('should update quote fields', async () => {
      const updates = {
        status: 'used' as const,
        usedAt: new Date(),
      };

      await storage.updateQuote(createdQuote.id, updates);
      const updatedQuote = await storage.getQuote(createdQuote.id);

      expect(updatedQuote?.status).toBe('used');
      expect(updatedQuote?.usedAt).toBeDefined();
      expect(updatedQuote?.updatedAt.getTime()).toBeGreaterThan(createdQuote.updatedAt.getTime());
    });

    it('should throw error for non-existent quote', async () => {
      await expect(
        storage.updateQuote('non-existent-id', { status: 'used' })
      ).rejects.toThrow('Quote not found');
    });
  });

  describe('expireQuote', () => {
    beforeEach(async () => {
      createdQuote = await storage.createQuote(testQuote);
    });

    it('should mark quote as expired', async () => {
      await storage.expireQuote(createdQuote.id);
      const expiredQuote = await storage.getQuote(createdQuote.id);

      expect(expiredQuote?.status).toBe('expired');
      expect(expiredQuote?.updatedAt.getTime()).toBeGreaterThan(createdQuote.updatedAt.getTime());
    });

    it('should throw error for non-existent quote', async () => {
      await expect(
        storage.expireQuote('non-existent-id')
      ).rejects.toThrow('Quote not found');
    });
  });

  describe('cleanupExpiredQuotes', () => {
    it('should clean up expired quotes and return count', async () => {
      // Create quotes that will expire
      const expiredQuote1 = await storage.createQuote({
        ...testQuote,
        expiresAt: new Date(Date.now() - 10000), // 10 seconds ago
      });

      const expiredQuote2 = await storage.createQuote({
        ...testQuote,
        sessionId: 'test-session-456',
        expiresAt: new Date(Date.now() - 5000), // 5 seconds ago
      });

      // Create a quote that won't expire
      const activeQuote = await storage.createQuote({
        ...testQuote,
        sessionId: 'test-session-789',
        expiresAt: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes from now
      });

      const cleanedCount = await storage.cleanupExpiredQuotes();
      expect(cleanedCount).toBe(2);

      // Verify expired quotes are no longer retrievable
      expect(await storage.getQuote(expiredQuote1.id)).toBeUndefined();
      expect(await storage.getQuote(expiredQuote2.id)).toBeUndefined();
      expect(await storage.getQuote(activeQuote.id)).toBeDefined();
    });

    it('should return 0 when no quotes need cleanup', async () => {
      const cleanedCount = await storage.cleanupExpiredQuotes();
      expect(cleanedCount).toBe(0);
    });
  });

  describe('Integration with Images MVP flow', () => {
    it('should support the complete quote lifecycle', async () => {
      // 1. Create quote (simulating /api/images_mvp/quote)
      createdQuote = await storage.createQuote(testQuote);
      expect(createdQuote.status).toBe('active');

      // 2. Retrieve quote for extraction (simulating /api/images_mvp/extract)
      const quoteForExtraction = await storage.getQuote(createdQuote.id);
      expect(quoteForExtraction).toBeDefined();
      expect(quoteForExtraction?.ops.embedding).toBe(true);
      expect(quoteForExtraction?.perFileCredits['file-1']).toBe(5);

      // 3. Mark quote as used after successful extraction
      await storage.updateQuote(createdQuote.id, {
        status: 'used',
        usedAt: new Date(),
      });

      const usedQuote = await storage.getQuote(createdQuote.id);
      expect(usedQuote?.status).toBe('used');
      expect(usedQuote?.usedAt).toBeDefined();
    });
  });
});