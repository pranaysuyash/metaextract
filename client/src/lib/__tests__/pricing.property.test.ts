/**
 * Property-Based Tests for Pricing System
 *
 * Feature: professional-product-polish
 *
 * DEPRECATION NOTICE:
 * These tests are OBSOLETE because the tier-based pricing system is deprecated.
 * The Images MVP uses credit-based pricing (IMAGES_MVP_CREDIT_PACKS) instead.
 *
 * This file is preserved for historical reference only.
 */

import * as fc from 'fast-check';
// import {
//   PRICING_TIERS,
//   SUPPORTED_CURRENCIES,
//   CREDIT_PACKS,
//   CREDIT_COSTS,
//   type CurrencyCode,
//   type SubscriptionTier,
//   type UsageEstimate,
//   convertPrice,
//   formatPrice,
//   calculateMonthlyPrice,
//   calculateAnnualPrice,
//   calculateAnnualSavings,
//   recommendTier,
//   getPricingTier,
//   getRecommendedTier,
//   isFeatureAvailable,
//   getFeatureDifferences,
//   getCreditCost,
//   calculateTotalCredits,
//   getCreditPack,
//   getCreditPackPrice,
//   detectUserCurrency,
// } from '../pricing';

// ============================================================================
// SKIPPED: OBSOLETE TESTS
// ============================================================================
// All tier-based pricing tests are skipped because PRICING_TIERS and CREDIT_PACKS
// are now obsolete. The MVP uses credit-based pricing instead.
//
// To re-enable these tests, uncomment the imports above and restore the test code.
// ============================================================================

describe.skip('OBSOLETE: Pricing System Property Tests', () => {
  /**
   * All tests in this suite are OBSOLETE.
   *
   * The original tests validated:
   * - Pricing calculation accuracy
   * - Currency localization
   * - Plan change handling
   * - Tier recommendation properties
   * - Credit system properties
   * - Pricing tier invariants
   *
   * These are no longer relevant for the credit-based MVP pricing model.
   */
  it('obsolete tests - tier-based pricing deprecated', () => {
    expect(true).toBe(true);
  });
});
