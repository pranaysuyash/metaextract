/**
 * Pricing Module Tests
 *
 * Tests for pricing calculations, currency conversion, tier utilities
 */

import {
  SUPPORTED_CURRENCIES,
  type CurrencyCode,
  type CurrencyInfo,
  type SubscriptionTier,
  type PricingTier,
  type PricingFeature,
  PRICING_TIERS,
  CREDIT_PACKS,
  CREDIT_COSTS,
  getDefaultCreditCost,
  getCreditCost,
  calculateTotalCredits,
  formatPrice,
  convertPrice,
  detectUserCurrency,
  getPricingTier,
  getRecommendedTier,
  calculateMonthlyPrice,
  calculateAnnualPrice,
  calculateAnnualSavings,
  recommendTier,
  calculateEstimatedCost,
  isFeatureAvailable,
  getFeatureDifferences,
  compareFeatureAcrossTiers,
  getCreditPack,
  getCreditPackPrice,
  FEATURE_CATEGORIES,
} from '../pricing';

describe('Pricing Module', () => {
  describe('SUPPORTED_CURRENCIES', () => {
    it('should have USD as base currency with rate 1', () => {
      expect(SUPPORTED_CURRENCIES.USD.rate).toBe(1);
      expect(SUPPORTED_CURRENCIES.USD.symbol).toBe('$');
    });

    it('should have all major currencies defined', () => {
      const currencies = Object.keys(SUPPORTED_CURRENCIES);
      expect(currencies).toContain('USD');
      expect(currencies).toContain('EUR');
      expect(currencies).toContain('GBP');
      expect(currencies).toContain('CAD');
      expect(currencies).toContain('AUD');
      expect(currencies).toContain('JPY');
      expect(currencies).toContain('INR');
    });

    it('should have correct currency symbols', () => {
      expect(SUPPORTED_CURRENCIES.EUR.symbol).toBe('€');
      expect(SUPPORTED_CURRENCIES.GBP.symbol).toBe('£');
      expect(SUPPORTED_CURRENCIES.JPY.symbol).toBe('¥');
    });

    it('should have valid exchange rates', () => {
      const currencies = Object.values(SUPPORTED_CURRENCIES) as CurrencyInfo[];
      currencies.forEach(currency => {
        expect(currency.rate).toBeGreaterThan(0);
        expect(typeof currency.name).toBe('string');
        expect(typeof currency.locale).toBe('string');
      });
    });
  });

  describe('FEATURE_CATEGORIES', () => {
    it('should have all expected categories', () => {
      expect(FEATURE_CATEGORIES).toContain('file-support');
      expect(FEATURE_CATEGORIES).toContain('metadata-extraction');
      expect(FEATURE_CATEGORIES).toContain('forensic-analysis');
      expect(FEATURE_CATEGORIES).toContain('processing');
      expect(FEATURE_CATEGORIES).toContain('export-support');
    });
  });

  describe('PRICING_TIERS', () => {
    it('should have 4 tiers', () => {
      expect(PRICING_TIERS.length).toBe(4);
    });

    it('should have free tier with basePrice 0', () => {
      const freeTier = PRICING_TIERS.find(t => t.id === 'free');
      expect(freeTier).toBeDefined();
      expect(freeTier?.basePrice).toBe(0);
    });

    it('should have professional tier', () => {
      const proTier = PRICING_TIERS.find(t => t.id === 'professional');
      expect(proTier).toBeDefined();
      expect(proTier?.basePrice).toBe(19);
    });

    it('should have forensic tier marked as recommended', () => {
      const forensicTier = PRICING_TIERS.find(t => t.id === 'forensic');
      expect(forensicTier).toBeDefined();
      expect(forensicTier?.recommended).toBe(true);
      expect(forensicTier?.basePrice).toBe(49);
    });

    it('should have enterprise tier with unlimited uploads', () => {
      const enterpriseTier = PRICING_TIERS.find(t => t.id === 'enterprise');
      expect(enterpriseTier).toBeDefined();
      expect(enterpriseTier?.limits.monthlyUploads).toBe(-1);
      expect(enterpriseTier?.basePrice).toBe(149);
    });

    it('should have correct support levels', () => {
      expect(PRICING_TIERS[0].limits.supportLevel).toBe('community');
      expect(PRICING_TIERS[1].limits.supportLevel).toBe('email');
      expect(PRICING_TIERS[2].limits.supportLevel).toBe('priority');
      expect(PRICING_TIERS[3].limits.supportLevel).toBe('dedicated');
    });

    it('should have valid feature arrays for each tier', () => {
      PRICING_TIERS.forEach((tier: PricingTier) => {
        expect(Array.isArray(tier.features)).toBe(true);
        expect(tier.features.length).toBeGreaterThan(0);
        tier.features.forEach((feature: PricingFeature) => {
          expect(typeof feature.id).toBe('string');
          expect(typeof feature.name).toBe('string');
          expect(typeof feature.included).toBe('boolean');
        });
      });
    });

    it('should have correct annual discounts', () => {
      const freeTier = PRICING_TIERS.find(t => t.id === 'free');
      const proTier = PRICING_TIERS.find(t => t.id === 'professional');
      const forensicTier = PRICING_TIERS.find(t => t.id === 'forensic');
      const enterpriseTier = PRICING_TIERS.find(t => t.id === 'enterprise');

      expect(freeTier?.annualDiscount).toBe(0);
      expect(proTier?.annualDiscount).toBe(20);
      expect(forensicTier?.annualDiscount).toBe(20);
      expect(enterpriseTier?.annualDiscount).toBe(0);
    });
  });

  describe('CREDIT_PACKS', () => {
    it('should have 4 credit packs', () => {
      expect(CREDIT_PACKS.length).toBe(4);
    });

    it('should have single pack with 1 credit', () => {
      const single = CREDIT_PACKS.find(p => p.id === 'single');
      expect(single).toBeDefined();
      expect(single?.credits).toBe(1);
      expect(single?.basePrice).toBe(2);
    });

    it('should have investigation pack marked as popular', () => {
      const investigation = CREDIT_PACKS.find(p => p.id === 'investigation');
      expect(investigation).toBeDefined();
      expect(investigation?.popular).toBe(true);
      expect(investigation?.credits).toBe(10);
    });

    it('should have case pack with 50 credits', () => {
      const casePack = CREDIT_PACKS.find(p => p.id === 'case');
      expect(casePack).toBeDefined();
      expect(casePack?.credits).toBe(50);
    });

    it('should have agency pack with bulk discount', () => {
      const agency = CREDIT_PACKS.find(p => p.id === 'agency');
      expect(agency).toBeDefined();
      expect(agency?.credits).toBe(200);
      expect(agency?.perCreditPrice).toBe(0.75);
    });

    it('should calculate correct perCreditPrice for all packs', () => {
      CREDIT_PACKS.forEach(pack => {
        const expectedPerCreditPrice = pack.basePrice / pack.credits;
        expect(pack.perCreditPrice).toBeCloseTo(expectedPerCreditPrice, 2);
      });
    });
  });

  describe('CREDIT_COSTS', () => {
    it('should have costs for standard image formats', () => {
      expect(CREDIT_COSTS['image/jpeg']).toBe(1);
      expect(CREDIT_COSTS['image/png']).toBe(1);
      expect(CREDIT_COSTS['image/gif']).toBe(1);
      expect(CREDIT_COSTS['image/webp']).toBe(1);
    });

    it('should have higher costs for RAW formats', () => {
      expect(CREDIT_COSTS['image/x-canon-cr2']).toBe(2);
      expect(CREDIT_COSTS['image/x-nikon-nef']).toBe(2);
      expect(CREDIT_COSTS['image/x-sony-arw']).toBe(2);
      expect(CREDIT_COSTS['image/x-adobe-dng']).toBe(2);
    });

    it('should have higher costs for video formats', () => {
      expect(CREDIT_COSTS['video/mp4']).toBe(5);
      expect(CREDIT_COSTS['video/quicktime']).toBe(5);
    });

    it('should have costs for audio formats', () => {
      expect(CREDIT_COSTS['audio/mpeg']).toBe(2);
      expect(CREDIT_COSTS['audio/flac']).toBe(2);
      expect(CREDIT_COSTS['audio/wav']).toBe(2);
    });
  });

  describe('getDefaultCreditCost', () => {
    it('should return 2 for unknown file types', () => {
      expect(getDefaultCreditCost()).toBe(2);
    });
  });

  describe('getCreditCost', () => {
    it('should return correct cost for known mime types', () => {
      expect(getCreditCost('image/jpeg')).toBe(1);
      expect(getCreditCost('image/png')).toBe(1);
      expect(getCreditCost('video/mp4')).toBe(5);
    });

    it('should return default cost for unknown mime types', () => {
      expect(getCreditCost('unknown/type')).toBe(2);
      expect(getCreditCost('application/octet-stream')).toBe(2);
    });

    it('should handle HEIC formats', () => {
      expect(getCreditCost('image/heic')).toBe(2);
      expect(getCreditCost('image/heif')).toBe(2);
    });
  });

  describe('calculateTotalCredits', () => {
    it('should calculate credits for single file', () => {
      const files = [{ type: 'image/jpeg' }];
      expect(calculateTotalCredits(files)).toBe(1);
    });

    it('should calculate credits for multiple files', () => {
      const files = [
        { type: 'image/jpeg' },
        { type: 'image/png' },
        { type: 'video/mp4' },
      ];
      expect(calculateTotalCredits(files)).toBe(1 + 1 + 5);
    });

    it('should handle mixed file types', () => {
      const files = [
        { type: 'image/jpeg' },
        { type: 'image/x-canon-cr2' },
        { type: 'audio/mpeg' },
      ];
      expect(calculateTotalCredits(files)).toBe(1 + 2 + 2);
    });

    it('should handle empty array', () => {
      expect(calculateTotalCredits([])).toBe(0);
    });

    it('should handle files with unknown types', () => {
      const files = [{ type: 'image/jpeg' }, { type: 'unknown/type' }];
      expect(calculateTotalCredits(files)).toBe(1 + 2);
    });
  });

  describe('convertPrice', () => {
    it('should return same price for USD', () => {
      expect(convertPrice(100, 'USD')).toBe(100);
    });

    it('should convert to EUR', () => {
      const eurPrice = convertPrice(100, 'EUR');
      expect(eurPrice).toBeCloseTo(92, 0);
    });

    it('should convert to GBP', () => {
      const gbpPrice = convertPrice(100, 'GBP');
      expect(gbpPrice).toBeCloseTo(79, 0);
    });

    it('should convert to JPY', () => {
      const jpyPrice = convertPrice(100, 'JPY');
      expect(jpyPrice).toBeCloseTo(14950, 0);
    });
  });

  describe('formatPrice', () => {
    it('should format USD price correctly', () => {
      const result = formatPrice(19, 'USD');
      expect(result).toContain('$');
    });

    it('should format EUR with € symbol', () => {
      const result = formatPrice(19, 'EUR');
      expect(result).toContain('€');
    });

    it('should format GBP with £ symbol', () => {
      const result = formatPrice(19, 'GBP');
      expect(result).toContain('£');
    });

    it('should handle compact notation', () => {
      const result = formatPrice(1500, 'USD', { compact: true });
      expect(result).toContain('$');
    });
  });

  describe('getPricingTier', () => {
    it('should return undefined (deprecated function)', () => {
      const tier = getPricingTier('professional');
      expect(tier).toBeUndefined();
    });
  });

  describe('getRecommendedTier', () => {
    it('should return undefined (deprecated function)', () => {
      const tier = getRecommendedTier();
      expect(tier).toBeUndefined();
    });
  });

  describe('calculateMonthlyPrice', () => {
    it('should calculate monthly price for monthly billing', () => {
      const freeTier = PRICING_TIERS.find(t => t.id === 'free');
      if (freeTier) {
        const price = calculateMonthlyPrice(freeTier, 'monthly');
        expect(price).toBe(0);
      }
    });

    it('should apply annual discount', () => {
      const proTier = PRICING_TIERS.find(t => t.id === 'professional');
      if (proTier) {
        const price = calculateMonthlyPrice(proTier, 'annual');
        expect(price).toBeLessThan(proTier.basePrice);
      }
    });
  });

  describe('calculateAnnualPrice', () => {
    it('should calculate annual price correctly', () => {
      const freeTier = PRICING_TIERS.find(t => t.id === 'free');
      if (freeTier) {
        const annualPrice = calculateAnnualPrice(freeTier);
        expect(annualPrice).toBe(0);
      }
    });

    it('should apply annual discount for applicable tiers', () => {
      const proTier = PRICING_TIERS.find(t => t.id === 'professional');
      if (proTier) {
        const annualPrice = calculateAnnualPrice(proTier);
        const expectedPrice =
          proTier.basePrice * 12 * (1 - proTier.annualDiscount / 100);
        expect(annualPrice).toBeCloseTo(expectedPrice, 0);
      }
    });
  });

  describe('calculateAnnualSavings', () => {
    it('should calculate savings for professional tier', () => {
      const proTier = PRICING_TIERS.find(t => t.id === 'professional');
      if (proTier) {
        const savings = calculateAnnualSavings(proTier);
        expect(savings).toBeGreaterThan(0);
      }
    });
  });

  describe('getCreditPack', () => {
    it('should return undefined (deprecated function)', () => {
      const pack = getCreditPack('investigation');
      expect(pack).toBeUndefined();
    });

    it('should return undefined for invalid id', () => {
      const pack = getCreditPack('invalid');
      expect(pack).toBeUndefined();
    });
  });

  describe('getCreditPackPrice', () => {
    it('should return 0 for valid pack (deprecated - calls getCreditPack)', () => {
      const price = getCreditPackPrice('single');
      expect(price).toBe(0);
    });

    it('should return 0 for invalid pack', () => {
      const price = getCreditPackPrice('invalid');
      expect(price).toBe(0);
    });
  });

  describe('isFeatureAvailable', () => {
    it('should return false when tier lookup fails (deprecated)', () => {
      expect(isFeatureAvailable('forensic', 'forensic-analysis')).toBe(false);
    });

    it('should return false for excluded features', () => {
      expect(isFeatureAvailable('free', 'forensic-analysis')).toBe(false);
    });
  });

  describe('getFeatureDifferences', () => {
    it('should return empty arrays (deprecated - tier lookup fails)', () => {
      const differences = getFeatureDifferences('free', 'professional');
      expect(differences).toEqual({ gained: [], lost: [] });
    });
  });

  describe('compareFeatureAcrossTiers', () => {
    it('should return empty object (deprecated - tier lookup fails)', () => {
      const comparison = compareFeatureAcrossTiers('forensic-analysis');
      expect(comparison).toEqual({});
    });
  });
});
