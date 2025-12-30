/**
 * Unit tests for tier configuration
 */
import {
  getTierConfig,
  isFileTypeAllowed,
  isFileSizeAllowed,
  getRequiredTierForFileType,
  normalizeTier,
  toPythonTier,
  TIER_CONFIGS,
  CREDIT_PACKS,
  getRateLimits,
} from '@shared/tierConfig';

describe('Tier Configuration', () => {
  describe('normalizeTier', () => {
    it('should normalize tier names correctly', () => {
      expect(normalizeTier('free')).toBe('free');
      expect(normalizeTier('FREE')).toBe('free');
      expect(normalizeTier('professional')).toBe('professional');
      expect(normalizeTier('forensic')).toBe('forensic');
      expect(normalizeTier('enterprise')).toBe('enterprise');
    });

    it('should handle legacy tier names', () => {
      expect(normalizeTier('starter')).toBe('professional');
      expect(normalizeTier('premium')).toBe('forensic');
      expect(normalizeTier('super')).toBe('enterprise');
    });

    it('should default to enterprise for unknown tiers', () => {
      expect(normalizeTier('unknown')).toBe('enterprise');
      expect(normalizeTier('')).toBe('enterprise');
    });
  });

  describe('toPythonTier', () => {
    it('should convert tier names for Python engine', () => {
      expect(toPythonTier('free')).toBe('free');
      expect(toPythonTier('professional')).toBe('starter');
      expect(toPythonTier('forensic')).toBe('premium');
      expect(toPythonTier('enterprise')).toBe('super');
    });
  });

  describe('getTierConfig', () => {
    it('should return correct config for each tier', () => {
      const freeConfig = getTierConfig('free');
      expect(freeConfig.maxFileSizeMB).toBe(10);
      expect(freeConfig.fieldsPerFile).toBe(200);

      const proConfig = getTierConfig('professional');
      expect(proConfig.maxFileSizeMB).toBe(100);
      expect(proConfig.fieldsPerFile).toBe(1000);

      const forensicConfig = getTierConfig('forensic');
      expect(forensicConfig.maxFileSizeMB).toBe(500);
      expect(forensicConfig.fieldsPerFile).toBe(15000);

      const enterpriseConfig = getTierConfig('enterprise');
      expect(enterpriseConfig.maxFileSizeMB).toBe(2000);
      expect(enterpriseConfig.fieldsPerFile).toBe(45000);
    });
  });

  describe('isFileTypeAllowed', () => {
    it('should allow common image types for free tier', () => {
      expect(isFileTypeAllowed('free', 'image/jpeg')).toBe(true);
      expect(isFileTypeAllowed('free', 'image/png')).toBe(true);
      expect(isFileTypeAllowed('free', 'image/gif')).toBe(true);
      expect(isFileTypeAllowed('free', 'image/webp')).toBe(true);
    });

    it('should restrict video/audio for free tier', () => {
      expect(isFileTypeAllowed('free', 'video/mp4')).toBe(false);
      expect(isFileTypeAllowed('free', 'audio/mpeg')).toBe(false);
      expect(isFileTypeAllowed('free', 'application/pdf')).toBe(false);
    });

    it('should allow more types for professional tier', () => {
      expect(isFileTypeAllowed('professional', 'image/heic')).toBe(true);
      expect(isFileTypeAllowed('professional', 'image/x-canon-cr2')).toBe(true);
    });

    it('should allow video/audio for forensic tier', () => {
      expect(isFileTypeAllowed('forensic', 'video/mp4')).toBe(true);
      expect(isFileTypeAllowed('forensic', 'audio/mpeg')).toBe(true);
      expect(isFileTypeAllowed('forensic', 'application/pdf')).toBe(true);
    });

    it('should allow all types for enterprise tier', () => {
      expect(isFileTypeAllowed('enterprise', 'video/mp4')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'audio/mpeg')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'application/pdf')).toBe(true);
      expect(isFileTypeAllowed('enterprise', 'application/dicom')).toBe(true);
    });
  });

  describe('isFileSizeAllowed', () => {
    it('should enforce file size limits per tier', () => {
      const MB = 1024 * 1024;

      // Free tier: 10MB limit
      expect(isFileSizeAllowed('free', 5 * MB)).toBe(true);
      expect(isFileSizeAllowed('free', 15 * MB)).toBe(false);

      // Professional tier: 100MB limit
      expect(isFileSizeAllowed('professional', 50 * MB)).toBe(true);
      expect(isFileSizeAllowed('professional', 150 * MB)).toBe(false);

      // Forensic tier: 500MB limit
      expect(isFileSizeAllowed('forensic', 250 * MB)).toBe(true);
      expect(isFileSizeAllowed('forensic', 600 * MB)).toBe(false);

      // Enterprise tier: 2000MB limit
      expect(isFileSizeAllowed('enterprise', 1000 * MB)).toBe(true);
      expect(isFileSizeAllowed('enterprise', 2500 * MB)).toBe(false);
    });
  });

  describe('getRequiredTierForFileType', () => {
    it('should return correct tier for file types', () => {
      expect(getRequiredTierForFileType('image/jpeg')).toBe('free');
      expect(getRequiredTierForFileType('image/heic')).toBe('professional');
      expect(getRequiredTierForFileType('video/mp4')).toBe('forensic');
      expect(getRequiredTierForFileType('application/dicom')).toBe('enterprise');
    });
  });

  describe('getRateLimits', () => {
    it('should return rate limits for each tier', () => {
      const freeLimits = getRateLimits('free');
      expect(freeLimits.requestsPerMinute).toBeDefined();
      expect(freeLimits.requestsPerDay).toBeDefined();

      const enterpriseLimits = getRateLimits('enterprise');
      expect(enterpriseLimits.requestsPerMinute).toBeGreaterThan(freeLimits.requestsPerMinute);
    });
  });

  describe('TIER_CONFIGS structure', () => {
    it('should have all required tiers', () => {
      expect(TIER_CONFIGS).toHaveProperty('free');
      expect(TIER_CONFIGS).toHaveProperty('professional');
      expect(TIER_CONFIGS).toHaveProperty('forensic');
      expect(TIER_CONFIGS).toHaveProperty('enterprise');
    });

    it('should have required properties for each tier', () => {
      Object.values(TIER_CONFIGS).forEach((config) => {
        expect(config).toHaveProperty('displayName');
        expect(config).toHaveProperty('priceLabel');
        expect(config).toHaveProperty('maxFileSizeMB');
        expect(config).toHaveProperty('fieldsPerFile');
        expect(config).toHaveProperty('features');
      });
    });
  });

  describe('CREDIT_PACKS structure', () => {
    it('should have credit pack options', () => {
      expect(Array.isArray(CREDIT_PACKS)).toBe(true);
      expect(CREDIT_PACKS.length).toBeGreaterThan(0);
    });

    it('should have required properties for each pack', () => {
      CREDIT_PACKS.forEach((pack) => {
        expect(pack).toHaveProperty('id');
        expect(pack).toHaveProperty('credits');
        expect(pack).toHaveProperty('price');
      });
    });
  });
});
