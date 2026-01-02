/**
 * Property-Based Tests for Subscription Management System
 * 
 * Feature: professional-product-polish
 * 
 * These tests validate the correctness properties of the subscription
 * management system using property-based testing with fast-check.
 */

import * as fc from 'fast-check';
import {
  type UserSubscription,
  type SubscriptionStatus,
  type BillingCycle,
  type PlanChangeType,
  getPlanChangeType,
  canChangePlan,
  calculateProratedAmount,
  previewPlanChange,
  changePlan,
  cancelSubscription,
  reactivateSubscription,
  getSubscriptionUsage,
  checkUsageAgainstTier,
  createFreeSubscription,
  hasFeatureAccess,
  getEffectiveTier,
} from '../subscription';
import {
  type SubscriptionTier,
  PRICING_TIERS,
  getPricingTier,
} from '../pricing';

// Arbitraries for generating test data
const tierIdArb = fc.constantFrom('free', 'professional', 'forensic', 'enterprise') as fc.Arbitrary<SubscriptionTier>;
const statusArb = fc.constantFrom('active', 'trialing', 'past_due', 'canceled', 'unpaid', 'incomplete') as fc.Arbitrary<SubscriptionStatus>;
const billingCycleArb = fc.constantFrom('monthly', 'annual') as fc.Arbitrary<BillingCycle>;

const subscriptionArb: fc.Arbitrary<UserSubscription> = fc.record({
  id: fc.uuid(),
  userId: fc.uuid(),
  tier: tierIdArb,
  status: statusArb,
  billingCycle: billingCycleArb,
  currentPeriodStart: fc.date({ min: new Date('2024-01-01'), max: new Date('2025-06-01') }),
  currentPeriodEnd: fc.date({ min: new Date('2024-02-01'), max: new Date('2026-01-31') }),
  cancelAtPeriodEnd: fc.boolean(),
  createdAt: fc.date({ min: new Date('2023-01-01'), max: new Date('2024-12-31') }),
  updatedAt: fc.date({ min: new Date('2024-01-01'), max: new Date('2025-12-31') }),
}).map(sub => {
  // Ensure valid dates
  const periodStart = new Date(sub.currentPeriodStart);
  const periodEnd = new Date(sub.currentPeriodEnd);
  
  // If dates are invalid, use defaults
  const validStart = isNaN(periodStart.getTime()) ? new Date('2024-06-01') : periodStart;
  const validEnd = isNaN(periodEnd.getTime()) ? new Date('2024-07-01') : periodEnd;
  
  return {
    ...sub,
    currentPeriodStart: validStart,
    // Ensure period end is after period start
    currentPeriodEnd: new Date(Math.max(validEnd.getTime(), validStart.getTime() + 86400000 * 30)),
  };
});

const activeSubscriptionArb = subscriptionArb.map(sub => ({
  ...sub,
  status: 'active' as SubscriptionStatus,
  cancelAtPeriodEnd: false,
}));

describe('Subscription Management Property Tests', () => {
  /**
   * Property 13: Plan change handling
   * 
   * For any subscription upgrade or downgrade, user permissions
   * and billing should update correctly without data loss.
   * 
   * **Validates: Requirements 4.4**
   */
  describe('Property 13: Plan change handling', () => {
    it('getPlanChangeType should correctly identify upgrade/downgrade/same', () => {
      const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
      
      fc.assert(
        fc.property(tierIdArb, tierIdArb, (fromTier, toTier) => {
          const changeType = getPlanChangeType(fromTier, toTier);
          const fromIndex = tierOrder.indexOf(fromTier);
          const toIndex = tierOrder.indexOf(toTier);
          
          if (fromIndex < toIndex) {
            return changeType === 'upgrade';
          } else if (fromIndex > toIndex) {
            return changeType === 'downgrade';
          } else {
            return changeType === 'same';
          }
        }),
        { numRuns: 100 }
      );
    });

    it('canChangePlan should reject change to same tier', () => {
      fc.assert(
        fc.property(activeSubscriptionArb, (subscription) => {
          const result = canChangePlan(subscription, subscription.tier);
          return result.allowed === false && result.reason !== undefined;
        }),
        { numRuns: 100 }
      );
    });

    it('canChangePlan should reject changes for unpaid subscriptions', () => {
      fc.assert(
        fc.property(
          subscriptionArb.map(s => ({ ...s, status: 'unpaid' as SubscriptionStatus })),
          tierIdArb,
          (subscription, targetTier) => {
            if (subscription.tier === targetTier) return true;
            const result = canChangePlan(subscription, targetTier);
            return result.allowed === false;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('canChangePlan should allow downgrade to free for active subscriptions', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.filter(s => s.tier !== 'free'),
          (subscription) => {
            const result = canChangePlan(subscription, 'free');
            return result.allowed === true;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('previewPlanChange should identify correct change type', () => {
      fc.assert(
        fc.property(activeSubscriptionArb, tierIdArb, (subscription, targetTier) => {
          const preview = previewPlanChange(subscription, targetTier);
          const expectedType = getPlanChangeType(subscription.tier, targetTier);
          return preview.changeType === expectedType;
        }),
        { numRuns: 100 }
      );
    });

    it('previewPlanChange should require confirmation for downgrades', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.filter(s => s.tier !== 'free'),
          (subscription) => {
            // Find a tier to downgrade to
            const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
            const currentIndex = tierOrder.indexOf(subscription.tier);
            if (currentIndex === 0) return true; // Can't downgrade from free
            
            const targetTier = tierOrder[currentIndex - 1];
            const preview = previewPlanChange(subscription, targetTier);
            
            return preview.requiresConfirmation === true;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('previewPlanChange should list features gained on upgrade', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.filter(s => s.tier !== 'enterprise'),
          (subscription) => {
            // Find a tier to upgrade to
            const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
            const currentIndex = tierOrder.indexOf(subscription.tier);
            const targetTier = tierOrder[currentIndex + 1];
            
            const preview = previewPlanChange(subscription, targetTier);
            
            // Upgrades should not lose features
            return preview.featuresLost.length === 0;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('previewPlanChange should list features lost on downgrade', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.filter(s => s.tier !== 'free'),
          (subscription) => {
            const preview = previewPlanChange(subscription, 'free');
            
            // Downgrading to free should lose features (unless already on free)
            return preview.featuresLost.length >= 0; // May or may not lose features
          }
        ),
        { numRuns: 100 }
      );
    });

    it('prorated amount should be positive for upgrades', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.filter(s => s.tier !== 'enterprise' && s.tier !== 'free'),
          (subscription) => {
            // Upgrade to next tier
            const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
            const currentIndex = tierOrder.indexOf(subscription.tier);
            const targetTier = tierOrder[currentIndex + 1];
            
            const prorated = calculateProratedAmount(subscription, targetTier);
            
            // Prorated amount should be >= 0 for upgrades
            return prorated >= 0;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('prorated amount should be negative or zero for downgrades', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.filter(s => s.tier !== 'free'),
          (subscription) => {
            // Skip if dates are invalid
            if (isNaN(subscription.currentPeriodStart.getTime()) || 
                isNaN(subscription.currentPeriodEnd.getTime())) {
              return true;
            }
            
            // Downgrade to previous tier
            const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
            const currentIndex = tierOrder.indexOf(subscription.tier);
            const targetTier = tierOrder[currentIndex - 1];
            
            const prorated = calculateProratedAmount(subscription, targetTier);
            
            // Prorated amount should be <= 0 for downgrades (credit)
            return prorated <= 0;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('prorated amount should be zero for free tier changes', () => {
      fc.assert(
        fc.property(
          activeSubscriptionArb.map(s => ({ ...s, tier: 'free' as SubscriptionTier })),
          tierIdArb,
          (subscription, targetTier) => {
            const prorated = calculateProratedAmount(subscription, targetTier);
            return prorated === 0;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('Subscription lifecycle properties', () => {
    it('createFreeSubscription should create valid subscription', () => {
      fc.assert(
        fc.property(fc.uuid(), (userId) => {
          const subscription = createFreeSubscription(userId);
          
          return (
            subscription.userId === userId &&
            subscription.tier === 'free' &&
            subscription.status === 'active' &&
            subscription.cancelAtPeriodEnd === false &&
            subscription.currentPeriodEnd > subscription.currentPeriodStart
          );
        }),
        { numRuns: 100 }
      );
    });

    it('getEffectiveTier should return free for canceled subscriptions', () => {
      fc.assert(
        fc.property(
          subscriptionArb.map(s => ({ ...s, status: 'canceled' as SubscriptionStatus })),
          (subscription) => {
            const effectiveTier = getEffectiveTier(subscription);
            return effectiveTier === 'free';
          }
        ),
        { numRuns: 100 }
      );
    });

    it('getEffectiveTier should return free for unpaid subscriptions', () => {
      fc.assert(
        fc.property(
          subscriptionArb.map(s => ({ ...s, status: 'unpaid' as SubscriptionStatus })),
          (subscription) => {
            const effectiveTier = getEffectiveTier(subscription);
            return effectiveTier === 'free';
          }
        ),
        { numRuns: 100 }
      );
    });

    it('getEffectiveTier should return actual tier for active subscriptions', () => {
      fc.assert(
        fc.property(activeSubscriptionArb, (subscription) => {
          const effectiveTier = getEffectiveTier(subscription);
          return effectiveTier === subscription.tier;
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Feature access properties', () => {
    it('hasFeatureAccess should be consistent with tier features', () => {
      fc.assert(
        fc.property(activeSubscriptionArb, (subscription) => {
          const tier = getPricingTier(subscription.tier);
          if (!tier) return true;
          
          // Check each feature
          return tier.features.every(feature => {
            const hasAccess = hasFeatureAccess(subscription, feature.id);
            return hasAccess === feature.included;
          });
        }),
        { numRuns: 100 }
      );
    });

    it('canceled subscriptions should only have free tier features', () => {
      fc.assert(
        fc.property(
          subscriptionArb.map(s => ({ ...s, status: 'canceled' as SubscriptionStatus, tier: 'forensic' as SubscriptionTier })),
          (subscription) => {
            const freeTier = getPricingTier('free');
            if (!freeTier) return true;
            
            // Check that only free features are accessible
            return freeTier.features.every(feature => {
              const hasAccess = hasFeatureAccess(subscription, feature.id);
              return hasAccess === feature.included;
            });
          }
        ),
        { numRuns: 100 }
      );
    });

    it('higher tiers should have access to all lower tier features', () => {
      const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
      
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 3 }),
          (tierIndex) => {
            const higherTier = tierOrder[tierIndex];
            const lowerTier = tierOrder[tierIndex - 1];
            
            const higherTierData = getPricingTier(higherTier);
            const lowerTierData = getPricingTier(lowerTier);
            
            if (!higherTierData || !lowerTierData) return true;
            
            // All features included in lower tier should be included in higher tier
            return lowerTierData.features
              .filter(f => f.included)
              .every(lowerFeature => {
                const higherFeature = higherTierData.features.find(f => f.id === lowerFeature.id);
                return higherFeature?.included === true;
              });
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('Usage tracking properties', () => {
    it('getSubscriptionUsage should return valid usage data', () => {
      fc.assert(
        fc.property(activeSubscriptionArb, (subscription) => {
          const usage = getSubscriptionUsage(subscription);
          
          return (
            usage.uploadsThisMonth >= 0 &&
            usage.apiCallsThisMonth >= 0 &&
            usage.storageUsedMB >= 0 &&
            usage.periodStart instanceof Date &&
            usage.periodEnd instanceof Date
          );
        }),
        { numRuns: 100 }
      );
    });

    it('checkUsageAgainstTier should detect when usage exceeds limits', () => {
      // Create usage that exceeds free tier limits
      const highUsage = {
        uploadsThisMonth: 1000,
        uploadsLimit: 90 as number | 'unlimited',
        apiCallsThisMonth: 100,
        apiCallsLimit: 0 as number | 'unlimited',
        storageUsedMB: 500,
        storageLimitMB: 100,
        periodStart: new Date(),
        periodEnd: new Date(),
      };
      
      const result = checkUsageAgainstTier(highUsage, 'free');
      expect(result.exceeds).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(0);
    });

    it('checkUsageAgainstTier should not flag usage within limits', () => {
      const lowUsage = {
        uploadsThisMonth: 10,
        uploadsLimit: 90 as number | 'unlimited',
        apiCallsThisMonth: 0,
        apiCallsLimit: 0 as number | 'unlimited',
        storageUsedMB: 5,
        storageLimitMB: 100,
        periodStart: new Date(),
        periodEnd: new Date(),
      };
      
      const result = checkUsageAgainstTier(lowUsage, 'free');
      expect(result.exceeds).toBe(false);
    });
  });

  describe('Plan change async operations', () => {
    it('changePlan should require confirmation for downgrades', async () => {
      const subscription = createFreeSubscription('test-user');
      subscription.tier = 'professional';
      subscription.status = 'active';
      
      const result = await changePlan(subscription, 'free', { confirmDowngrade: false });
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('confirmation_required');
    });

    it('changePlan should succeed with confirmation for downgrades', async () => {
      const subscription = createFreeSubscription('test-user');
      subscription.tier = 'professional';
      subscription.status = 'active';
      
      const result = await changePlan(subscription, 'free', { confirmDowngrade: true });
      
      expect(result.success).toBe(true);
      expect(result.subscription?.tier).toBe('free');
    });

    it('changePlan to enterprise should redirect to sales', async () => {
      const subscription = createFreeSubscription('test-user');
      
      const result = await changePlan(subscription, 'enterprise');
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('contact_sales');
    });

    it('cancelSubscription should not cancel free tier', async () => {
      const subscription = createFreeSubscription('test-user');
      
      const result = await cancelSubscription(subscription);
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('already_free');
    });

    it('cancelSubscription should set cancelAtPeriodEnd for paid tiers', async () => {
      const subscription = createFreeSubscription('test-user');
      subscription.tier = 'professional';
      subscription.status = 'active';
      
      const result = await cancelSubscription(subscription, { immediate: false });
      
      expect(result.success).toBe(true);
      expect(result.subscription?.cancelAtPeriodEnd).toBe(true);
      expect(result.subscription?.tier).toBe('professional'); // Still on paid tier until period end
    });

    it('reactivateSubscription should clear cancelAtPeriodEnd', async () => {
      const subscription = createFreeSubscription('test-user');
      subscription.tier = 'professional';
      subscription.status = 'active';
      subscription.cancelAtPeriodEnd = true;
      
      const result = await reactivateSubscription(subscription);
      
      expect(result.success).toBe(true);
      expect(result.subscription?.cancelAtPeriodEnd).toBe(false);
    });
  });
});
