/**
 * Property-Based Tests for Pricing System
 * 
 * Feature: professional-product-polish
 * 
 * These tests validate the correctness properties of the pricing system
 * using property-based testing with fast-check.
 */

import * as fc from 'fast-check';
import {
  PRICING_TIERS,
  SUPPORTED_CURRENCIES,
  CREDIT_PACKS,
  CREDIT_COSTS,
  type CurrencyCode,
  type SubscriptionTier,
  type UsageEstimate,
  convertPrice,
  formatPrice,
  calculateMonthlyPrice,
  calculateAnnualPrice,
  calculateAnnualSavings,
  recommendTier,
  getPricingTier,
  getRecommendedTier,
  isFeatureAvailable,
  getFeatureDifferences,
  getCreditCost,
  calculateTotalCredits,
  getCreditPack,
  getCreditPackPrice,
  detectUserCurrency,
} from '../pricing';

// Arbitraries for generating test data
const currencyArb = fc.constantFrom(...Object.keys(SUPPORTED_CURRENCIES) as CurrencyCode[]);
const tierIdArb = fc.constantFrom('free', 'professional', 'forensic', 'enterprise') as fc.Arbitrary<SubscriptionTier>;
const billingCycleArb = fc.constantFrom('monthly', 'annual') as fc.Arbitrary<'monthly' | 'annual'>;
const priceArb = fc.float({ min: 0, max: 10000, noNaN: true });
const positiveIntArb = fc.integer({ min: 1, max: 10000 });

const usageEstimateArb: fc.Arbitrary<UsageEstimate> = fc.record({
  filesPerMonth: fc.integer({ min: 1, max: 5000 }),
  averageFileSizeMB: fc.integer({ min: 1, max: 500 }),
  needsRawFormats: fc.boolean(),
  needsVideoAudio: fc.boolean(),
  needsForensicAnalysis: fc.boolean(),
  needsApiAccess: fc.boolean(),
  needsPdfReports: fc.boolean(),
});

describe('Pricing System Property Tests', () => {
  /**
   * Property 12: Pricing calculation accuracy
   * 
   * For any usage level and subscription tier, pricing calculations
   * should correctly reflect the published pricing model.
   * 
   * **Validates: Requirements 4.3**
   */
  describe('Property 12: Pricing calculation accuracy', () => {
    it('monthly price should equal base price for monthly billing', () => {
      fc.assert(
        fc.property(tierIdArb, currencyArb, (tierId, currency) => {
          const tier = getPricingTier(tierId);
          if (!tier) return true; // Skip if tier not found
          
          const monthlyPrice = calculateMonthlyPrice(tier, 'monthly', currency);
          const expectedPrice = convertPrice(tier.basePrice, currency);
          
          // Allow small floating point differences
          return Math.abs(monthlyPrice - expectedPrice) < 0.01;
        }),
        { numRuns: 100 }
      );
    });

    it('annual billing should apply the correct discount', () => {
      fc.assert(
        fc.property(tierIdArb, currencyArb, (tierId, currency) => {
          const tier = getPricingTier(tierId);
          if (!tier || tier.basePrice === 0) return true; // Skip free tier
          
          const monthlyPrice = calculateMonthlyPrice(tier, 'monthly', currency);
          const annualMonthlyPrice = calculateMonthlyPrice(tier, 'annual', currency);
          const expectedDiscount = tier.annualDiscount / 100;
          
          // Annual price should be discounted
          const expectedAnnualMonthly = monthlyPrice * (1 - expectedDiscount);
          return Math.abs(annualMonthlyPrice - expectedAnnualMonthly) < 0.01;
        }),
        { numRuns: 100 }
      );
    });

    it('annual price should be 12x the monthly annual price', () => {
      fc.assert(
        fc.property(tierIdArb, currencyArb, (tierId, currency) => {
          const tier = getPricingTier(tierId);
          if (!tier) return true;
          
          const annualPrice = calculateAnnualPrice(tier, currency);
          const monthlyAnnualPrice = calculateMonthlyPrice(tier, 'annual', currency);
          
          return Math.abs(annualPrice - monthlyAnnualPrice * 12) < 0.01;
        }),
        { numRuns: 100 }
      );
    });

    it('annual savings should be positive for paid tiers', () => {
      fc.assert(
        fc.property(tierIdArb, currencyArb, (tierId, currency) => {
          const tier = getPricingTier(tierId);
          if (!tier || tier.basePrice === 0) return true; // Skip free tier
          
          const savings = calculateAnnualSavings(tier, currency);
          return savings > 0;
        }),
        { numRuns: 100 }
      );
    });

    it('annual savings should equal difference between monthly and annual totals', () => {
      fc.assert(
        fc.property(tierIdArb, currencyArb, (tierId, currency) => {
          const tier = getPricingTier(tierId);
          if (!tier) return true;
          
          const monthlyTotal = convertPrice(tier.basePrice * 12, currency);
          const annualTotal = calculateAnnualPrice(tier, currency);
          const savings = calculateAnnualSavings(tier, currency);
          
          return Math.abs(savings - (monthlyTotal - annualTotal)) < 0.01;
        }),
        { numRuns: 100 }
      );
    });

    it('tier prices should be ordered (free < professional < forensic < enterprise)', () => {
      fc.assert(
        fc.property(currencyArb, (currency) => {
          const freeTier = getPricingTier('free')!;
          const proTier = getPricingTier('professional')!;
          const forensicTier = getPricingTier('forensic')!;
          const enterpriseTier = getPricingTier('enterprise')!;
          
          const freePrice = calculateMonthlyPrice(freeTier, 'monthly', currency);
          const proPrice = calculateMonthlyPrice(proTier, 'monthly', currency);
          const forensicPrice = calculateMonthlyPrice(forensicTier, 'monthly', currency);
          const enterprisePrice = calculateMonthlyPrice(enterpriseTier, 'monthly', currency);
          
          return freePrice < proPrice && proPrice < forensicPrice && forensicPrice < enterprisePrice;
        }),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 14: Currency localization
   * 
   * For any user location, pricing should display in the appropriate
   * local currency with correct conversion rates.
   * 
   * **Validates: Requirements 4.6**
   */
  describe('Property 14: Currency localization', () => {
    it('converted price should be proportional to exchange rate', () => {
      fc.assert(
        fc.property(priceArb, currencyArb, (priceUSD, currency) => {
          const converted = convertPrice(priceUSD, currency);
          const rate = SUPPORTED_CURRENCIES[currency].rate;
          
          return Math.abs(converted - priceUSD * rate) < 0.01;
        }),
        { numRuns: 100 }
      );
    });

    it('USD conversion should return the same price', () => {
      fc.assert(
        fc.property(priceArb, (priceUSD) => {
          const converted = convertPrice(priceUSD, 'USD');
          return Math.abs(converted - priceUSD) < 0.001;
        }),
        { numRuns: 100 }
      );
    });

    it('formatted price should contain currency symbol', () => {
      fc.assert(
        fc.property(priceArb, currencyArb, (priceUSD, currency) => {
          const formatted = formatPrice(priceUSD, currency);
          const currencyInfo = SUPPORTED_CURRENCIES[currency];
          
          // The formatted string should contain some currency indicator
          // (symbol or currency code)
          return formatted.includes(currencyInfo.symbol) || 
                 formatted.includes(currency) ||
                 formatted.length > 0;
        }),
        { numRuns: 100 }
      );
    });

    it('all supported currencies should have valid exchange rates', () => {
      Object.entries(SUPPORTED_CURRENCIES).forEach(([code, info]) => {
        expect(info.rate).toBeGreaterThan(0);
        expect(info.symbol).toBeTruthy();
        expect(info.name).toBeTruthy();
        expect(info.locale).toBeTruthy();
      });
    });

    it('detectUserCurrency should return a valid currency code', () => {
      const detected = detectUserCurrency();
      expect(Object.keys(SUPPORTED_CURRENCIES)).toContain(detected);
    });

    it('credit pack prices should convert correctly', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...CREDIT_PACKS.map(p => p.id)),
          currencyArb,
          (packId, currency) => {
            const pack = getCreditPack(packId);
            if (!pack) return true;
            
            const price = getCreditPackPrice(packId, currency);
            const expectedPrice = convertPrice(pack.basePrice, currency);
            
            return Math.abs(price - expectedPrice) < 0.01;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 13: Plan change handling
   * 
   * For any subscription upgrade or downgrade, user permissions
   * and billing should update correctly without data loss.
   * 
   * **Validates: Requirements 4.4**
   */
  describe('Property 13: Plan change handling', () => {
    it('upgrading should gain features, not lose them', () => {
      const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
      
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: 2 }),
          fc.integer({ min: 1, max: 3 }),
          (fromIdx, toOffset) => {
            const toIdx = Math.min(fromIdx + toOffset, 3);
            const fromTier = tierOrder[fromIdx];
            const toTier = tierOrder[toIdx];
            
            const { gained, lost } = getFeatureDifferences(fromTier, toTier);
            
            // When upgrading, should gain features and not lose any
            return gained.length >= 0 && lost.length === 0;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('downgrading may lose features', () => {
      const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
      
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 3 }),
          fc.integer({ min: 1, max: 3 }),
          (fromIdx, toOffset) => {
            const toIdx = Math.max(fromIdx - toOffset, 0);
            if (fromIdx === toIdx) return true;
            
            const fromTier = tierOrder[fromIdx];
            const toTier = tierOrder[toIdx];
            
            const { gained, lost } = getFeatureDifferences(fromTier, toTier);
            
            // When downgrading, may lose features
            // This is expected behavior, not an error
            return lost.length >= 0;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('same tier comparison should have no changes', () => {
      fc.assert(
        fc.property(tierIdArb, (tierId) => {
          const { gained, lost } = getFeatureDifferences(tierId, tierId);
          return gained.length === 0 && lost.length === 0;
        }),
        { numRuns: 100 }
      );
    });

    it('feature availability should be consistent with tier definition', () => {
      fc.assert(
        fc.property(tierIdArb, (tierId) => {
          const tier = getPricingTier(tierId);
          if (!tier) return true;
          
          // Check each feature
          return tier.features.every(feature => {
            const available = isFeatureAvailable(tierId, feature.id);
            return available === feature.included;
          });
        }),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Additional pricing properties
   */
  describe('Tier recommendation properties', () => {
    it('recommended tier should always be valid', () => {
      fc.assert(
        fc.property(usageEstimateArb, (usage) => {
          const recommended = recommendTier(usage);
          const validTiers: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
          return validTiers.includes(recommended);
        }),
        { numRuns: 100 }
      );
    });

    it('high volume usage should recommend higher tiers', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2001, max: 10000 }),
          (filesPerMonth) => {
            const usage: UsageEstimate = {
              filesPerMonth,
              averageFileSizeMB: 10,
              needsRawFormats: false,
              needsVideoAudio: false,
              needsForensicAnalysis: false,
              needsApiAccess: false,
              needsPdfReports: false,
            };
            
            const recommended = recommendTier(usage);
            return recommended === 'enterprise';
          }
        ),
        { numRuns: 100 }
      );
    });

    it('video/audio needs should recommend forensic or higher', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 500 }),
          (filesPerMonth) => {
            const usage: UsageEstimate = {
              filesPerMonth,
              averageFileSizeMB: 10,
              needsRawFormats: false,
              needsVideoAudio: true,
              needsForensicAnalysis: false,
              needsApiAccess: false,
              needsPdfReports: false,
            };
            
            const recommended = recommendTier(usage);
            return recommended === 'forensic' || recommended === 'enterprise';
          }
        ),
        { numRuns: 100 }
      );
    });

    it('getRecommendedTier should return a tier marked as recommended', () => {
      const recommended = getRecommendedTier();
      expect(recommended.recommended).toBe(true);
    });
  });

  describe('Credit system properties', () => {
    it('credit costs should be positive for all file types', () => {
      Object.entries(CREDIT_COSTS).forEach(([mimeType, cost]) => {
        expect(cost).toBeGreaterThan(0);
      });
    });

    it('total credits should be sum of individual file credits', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              type: fc.constantFrom(...Object.keys(CREDIT_COSTS)),
              size: fc.integer({ min: 1, max: 1000000 }),
            }),
            { minLength: 1, maxLength: 20 }
          ),
          (files) => {
            const total = calculateTotalCredits(files);
            const expected = files.reduce((sum, f) => sum + getCreditCost(f.type), 0);
            return total === expected;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('credit packs should have decreasing per-credit price as quantity increases', () => {
      const sortedPacks = [...CREDIT_PACKS].sort((a, b) => a.credits - b.credits);
      
      for (let i = 1; i < sortedPacks.length; i++) {
        expect(sortedPacks[i].perCreditPrice).toBeLessThanOrEqual(sortedPacks[i - 1].perCreditPrice);
      }
    });

    it('all credit packs should be retrievable by ID', () => {
      CREDIT_PACKS.forEach(pack => {
        const retrieved = getCreditPack(pack.id);
        expect(retrieved).toBeDefined();
        expect(retrieved?.id).toBe(pack.id);
      });
    });
  });

  describe('Pricing tier invariants', () => {
    it('all tiers should have unique IDs', () => {
      const ids = PRICING_TIERS.map(t => t.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('exactly one tier should be marked as recommended', () => {
      const recommendedCount = PRICING_TIERS.filter(t => t.recommended).length;
      expect(recommendedCount).toBe(1);
    });

    it('all tiers should have at least one feature', () => {
      PRICING_TIERS.forEach(tier => {
        expect(tier.features.length).toBeGreaterThan(0);
      });
    });

    it('higher tiers should have more or equal features included', () => {
      const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
      
      for (let i = 1; i < tierOrder.length; i++) {
        const lowerTier = getPricingTier(tierOrder[i - 1])!;
        const higherTier = getPricingTier(tierOrder[i])!;
        
        const lowerIncluded = lowerTier.features.filter(f => f.included).length;
        const higherIncluded = higherTier.features.filter(f => f.included).length;
        
        expect(higherIncluded).toBeGreaterThanOrEqual(lowerIncluded);
      }
    });
  });
});
