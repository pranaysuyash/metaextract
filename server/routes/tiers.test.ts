/** @jest-environment node */

/**
 * Tier Configuration API Tests
 *
 * Tests tier configuration and validation endpoints:
 * - GET /api/tiers
 * - GET /api/tiers/:tier
 * - Tier-based file type restrictions
 * - Tier-based file size limits
 * - Tier feature availability
 */

import request from 'supertest';
import express from 'express';
import { createServer, type Server } from 'http';
import { registerRoutes } from '../routes';
import {
  getTierConfig,
  getCreditCost,
  getRequiredTierForFileType,
  isFileSizeAllowed,
  isFileTypeAllowed,
  normalizeTier,
  toPythonTier,
} from '@shared/tierConfig';

describe('Tier Configuration API Tests', () => {
  let app: ReturnType<typeof express>;
  let httpServer: Server;

  beforeAll(async () => {
    app = express();
    app.use(express.json());

    httpServer = createServer(app);
    await registerRoutes(httpServer, app);
  });

  afterAll((done) => {
    // In these tests we never call `httpServer.listen()`. Node throws
    // ERR_SERVER_NOT_RUNNING if `close()` is called while not listening.
    if (httpServer.listening) {
      httpServer.close(done);
      return;
    }

    done();
  });

  describe('GET /api/tiers - List All Tiers', () => {
    it('should return all tier configurations', async () => {
      const response = await request(app).get('/api/tiers').expect(200);

      expect(response.body).toBeInstanceOf(Object);
      expect(response.body).toHaveProperty('free');
      expect(response.body).toHaveProperty('professional');
      expect(response.body).toHaveProperty('forensic');
      expect(response.body).toHaveProperty('enterprise');
    });

    it('should include complete tier configuration details', async () => {
      const response = await request(app).get('/api/tiers').expect(200);

      const freeTier = response.body.free;
      expect(freeTier).toHaveProperty('displayName');
      expect(freeTier).toHaveProperty('maxFileSizeMB');
      expect(freeTier).toHaveProperty('price');
      expect(freeTier).toHaveProperty('features');
      expect(freeTier).toHaveProperty('allowedFileTypes');
    });

    it('should structure tier data correctly for frontend consumption', async () => {
      const response = await request(app).get('/api/tiers').expect(200);

      const enterpriseTier = response.body.enterprise;
      expect(enterpriseTier.features).toHaveProperty('batchUpload', true);
      expect(enterpriseTier.features).toHaveProperty('apiAccess', true);
      expect(enterpriseTier.features).toHaveProperty(
        'manipulationDetection',
        true
      );
      expect(enterpriseTier.maxFileSizeMB).toBe(5000);
    });
  });

  describe('GET /api/tiers/:tier - Get Specific Tier', () => {
    it('should return free tier configuration', async () => {
      const response = await request(app).get('/api/tiers/free').expect(200);

      expect(response.body).toHaveProperty('displayName');
      expect(response.body).toHaveProperty('maxFileSizeMB', 10);
      expect(response.body).toHaveProperty('price', 0);
      expect(response.body.features).toHaveProperty('batchUpload', false);
    });

    it('should return professional tier configuration', async () => {
      const response = await request(app)
        .get('/api/tiers/professional')
        .expect(200);

      expect(response.body).toHaveProperty('maxFileSizeMB', 500);
      expect(response.body).toHaveProperty('price', 19);
      expect(response.body.features).toHaveProperty('batchUpload', false);
    });

    it('should return forensic tier configuration', async () => {
      const response = await request(app)
        .get('/api/tiers/forensic')
        .expect(200);

      expect(response.body).toHaveProperty('maxFileSizeMB', 2000);
      expect(response.body).toHaveProperty('price', 49);
      expect(response.body.features).toHaveProperty('batchUpload', true);
    });

    it('should return enterprise tier configuration', async () => {
      const response = await request(app)
        .get('/api/tiers/enterprise')
        .expect(200);

      expect(response.body).toHaveProperty('maxFileSizeMB', 5000);
      expect(response.body).toHaveProperty('price', 149);
      expect(response.body.features).toHaveProperty('batchUpload', true);
      expect(response.body.features).toHaveProperty('apiAccess', true);
    });

    it('should handle invalid tier names gracefully', async () => {
      const response = await request(app).get('/api/tiers/invalid').expect(200);

      expect(response.body).toBeDefined();
    });
  });

  describe('Tier-based File Type Restrictions', () => {
    it('should allow basic image types for free tier', () => {
      expect(isFileTypeAllowed('free', 'image/jpeg')).toBe(true);
      expect(isFileTypeAllowed('free', 'image/png')).toBe(true);
      expect(isFileTypeAllowed('free', 'image/gif')).toBe(true);
      expect(isFileTypeAllowed('free', 'image/webp')).toBe(true);
    });

    it('should restrict advanced formats for free tier', () => {
      expect(isFileTypeAllowed('free', 'video/mp4')).toBe(false);
      expect(isFileTypeAllowed('free', 'audio/mpeg')).toBe(false);
      expect(isFileTypeAllowed('free', 'application/pdf')).toBe(false);
      expect(isFileTypeAllowed('free', 'image/x-canon-cr2')).toBe(false);
    });

    it('should allow RAW formats for professional tier', () => {
      expect(isFileTypeAllowed('professional', 'image/x-canon-cr2')).toBe(true);
      expect(isFileTypeAllowed('professional', 'image/x-nikon-nef')).toBe(true);
      expect(isFileTypeAllowed('professional', 'image/x-sony-arw')).toBe(true);
      expect(isFileTypeAllowed('professional', 'image/heif')).toBe(true);
    });

    it('should allow video/audio for forensic tier', () => {
      expect(isFileTypeAllowed('forensic', 'video/mp4')).toBe(true);
      expect(isFileTypeAllowed('forensic', 'video/quicktime')).toBe(true);
      expect(isFileTypeAllowed('forensic', 'audio/mpeg')).toBe(true);
      expect(isFileTypeAllowed('forensic', 'audio/wav')).toBe(true);
      expect(isFileTypeAllowed('forensic', 'application/pdf')).toBe(true);
    });

    it('should allow all file types for enterprise tier', () => {
      expect(isFileTypeAllowed('enterprise', 'video/mp4')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'audio/mpeg')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'application/pdf')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'image/x-canon-cr2')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'application/zip')).toBe(true);
    });
  });

  describe('Tier-based File Size Limits', () => {
    it('should enforce free tier 10MB limit', () => {
      expect(isFileSizeAllowed('free', 10 * 1024 * 1024)).toBe(true);
      expect(isFileSizeAllowed('free', 11 * 1024 * 1024)).toBe(false);
      expect(isFileSizeAllowed('free', 100 * 1024 * 1024)).toBe(false);
    });

    it('should enforce professional tier 500MB limit', () => {
      expect(isFileSizeAllowed('professional', 500 * 1024 * 1024)).toBe(true);
      expect(isFileSizeAllowed('professional', 501 * 1024 * 1024)).toBe(false);
      expect(isFileSizeAllowed('professional', 600 * 1024 * 1024)).toBe(false);
    });

    it('should enforce forensic tier 2GB limit', () => {
      expect(isFileSizeAllowed('forensic', 2000 * 1024 * 1024)).toBe(true);
      expect(isFileSizeAllowed('forensic', 2001 * 1024 * 1024)).toBe(false);
    });

    it('should enforce enterprise tier 5GB limit', () => {
      expect(isFileSizeAllowed('enterprise', 5000 * 1024 * 1024)).toBe(true);
      expect(isFileSizeAllowed('enterprise', 5100 * 1024 * 1024)).toBe(false);
    });
  });

  describe('Tier Feature Availability', () => {
    it('should restrict batch upload to forensic+ tiers', () => {
      expect(getTierConfig('free').features.batchUpload).toBe(false);
      expect(getTierConfig('professional').features.batchUpload).toBe(false);
      expect(getTierConfig('forensic').features.batchUpload).toBe(true);
      expect(getTierConfig('enterprise').features.batchUpload).toBe(true);
    });

    it('should restrict manipulation detection to forensic+ tiers', () => {
      expect(getTierConfig('free').features.manipulationDetection).toBe(false);
      expect(getTierConfig('professional').features.manipulationDetection).toBe(
        false
      );
      expect(getTierConfig('forensic').features.manipulationDetection).toBe(
        true
      );
      expect(getTierConfig('enterprise').features.manipulationDetection).toBe(
        true
      );
    });

    it('should restrict API access to forensic+ tiers', () => {
      expect(getTierConfig('free').features.apiAccess).toBe(false);
      expect(getTierConfig('professional').features.apiAccess).toBe(false);
      expect(getTierConfig('forensic').features.apiAccess).toBe(true);
      expect(getTierConfig('enterprise').features.apiAccess).toBe(true);
    });

    it('should allow basic EXIF extraction for all tiers', () => {
      expect(getTierConfig('free').features.basicExif).toBe(true);
      expect(getTierConfig('professional').features.basicExif).toBe(true);
      expect(getTierConfig('forensic').features.basicExif).toBe(true);
      expect(getTierConfig('enterprise').features.basicExif).toBe(true);
    });
  });

  describe('Tier Normalization', () => {
    it('should normalize various tier names correctly', () => {
      expect(normalizeTier('free')).toBe('free');
      expect(normalizeTier('Free')).toBe('free');
      expect(normalizeTier('FREE')).toBe('free');
      expect(normalizeTier('starter')).toBe('professional');

      expect(normalizeTier('professional')).toBe('professional');
      expect(normalizeTier('pro')).toBe('forensic');
      expect(normalizeTier('Professional')).toBe('professional');

      expect(normalizeTier('forensic')).toBe('forensic');
      expect(normalizeTier('Forensic')).toBe('forensic');

      expect(normalizeTier('enterprise')).toBe('enterprise');
      expect(normalizeTier('Enterprise')).toBe('enterprise');
      expect(normalizeTier('super')).toBe('enterprise');
    });

    it('should default to enterprise for invalid tier names', () => {
      expect(normalizeTier('invalid')).toBe('enterprise');
      expect(normalizeTier('')).toBe('enterprise');
      expect(normalizeTier(undefined)).toBe('enterprise');
    });
  });

  describe('Required Tier Determination', () => {
    it('should return required tier for restricted file types', () => {
      expect(getRequiredTierForFileType('video/mp4')).toBe('forensic');
      expect(getRequiredTierForFileType('audio/mpeg')).toBe('forensic');
      expect(getRequiredTierForFileType('application/pdf')).toBe('forensic');
      expect(getRequiredTierForFileType('image/x-canon-cr2')).toBe(
        'professional'
      );
    });

    it('should return free for basic image types', () => {
      expect(getRequiredTierForFileType('image/jpeg')).toBe('free');
      expect(getRequiredTierForFileType('image/png')).toBe('free');
      expect(getRequiredTierForFileType('image/gif')).toBe('free');
    });
  });

  describe('Credit System Integration', () => {
    it('should calculate correct credit costs for different file types', () => {
      expect(getCreditCost('image/jpeg')).toBeDefined();
      expect(getCreditCost('video/mp4')).toBeDefined();
      expect(getCreditCost('application/pdf')).toBeDefined();
      expect(typeof getCreditCost('image/jpeg')).toBe('number');
    });

    it('should handle unknown file types gracefully', () => {
      expect(getCreditCost('application/octet-stream')).toBeDefined();
      expect(getCreditCost('unknown/type')).toBeDefined();
    });
  });

  describe('Python Tier Mapping', () => {
    it('should map frontend tiers to Python tiers correctly', () => {
      expect(toPythonTier('free')).toBe('free');
      expect(toPythonTier('professional')).toBe('starter');
      expect(toPythonTier('forensic')).toBe('premium');
      expect(toPythonTier('enterprise')).toBe('super');
    });

    it('should handle normalized tier names', () => {
      expect(toPythonTier('starter')).toBe('starter');
      expect(toPythonTier('pro')).toBe('premium');
      expect(toPythonTier('super')).toBe('super');
    });
  });
});
