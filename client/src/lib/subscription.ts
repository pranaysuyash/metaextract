/**
 * Subscription Management System
 * 
 * Handles plan upgrades, downgrades, free tier access, and billing updates.
 * 
 * Requirements: 4.4, 4.5
 */

import {
  type SubscriptionTier,
  type PricingTier,
  getPricingTier,
  getFeatureDifferences,
  calculateMonthlyPrice,
  calculateAnnualPrice,
  type CurrencyCode,
} from './pricing';

// Subscription status
export type SubscriptionStatus = 
  | 'active'
  | 'trialing'
  | 'past_due'
  | 'canceled'
  | 'unpaid'
  | 'incomplete';

// Billing cycle
export type BillingCycle = 'monthly' | 'annual';

// Plan change type
export type PlanChangeType = 'upgrade' | 'downgrade' | 'same';

/**
 * User subscription data
 */
export interface UserSubscription {
  id: string;
  userId: string;
  tier: SubscriptionTier;
  status: SubscriptionStatus;
  billingCycle: BillingCycle;
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  cancelAtPeriodEnd: boolean;
  trialEnd?: Date;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Plan change preview
 */
export interface PlanChangePreview {
  fromTier: SubscriptionTier;
  toTier: SubscriptionTier;
  changeType: PlanChangeType;
  proratedAmount: number;
  newMonthlyPrice: number;
  newAnnualPrice: number;
  effectiveDate: Date;
  featuresGained: string[];
  featuresLost: string[];
  warnings: string[];
  requiresConfirmation: boolean;
}

/**
 * Plan change result
 */
export interface PlanChangeResult {
  success: boolean;
  subscription?: UserSubscription;
  error?: string;
  message: string;
}

/**
 * Usage data for a subscription
 */
export interface SubscriptionUsage {
  uploadsThisMonth: number;
  uploadsLimit: number | 'unlimited';
  apiCallsThisMonth: number;
  apiCallsLimit: number | 'unlimited';
  storageUsedMB: number;
  storageLimitMB: number;
  periodStart: Date;
  periodEnd: Date;
}

/**
 * Determine the type of plan change
 */
export function getPlanChangeType(
  fromTier: SubscriptionTier,
  toTier: SubscriptionTier
): PlanChangeType {
  const tierOrder: SubscriptionTier[] = ['free', 'professional', 'forensic', 'enterprise'];
  const fromIndex = tierOrder.indexOf(fromTier);
  const toIndex = tierOrder.indexOf(toTier);
  
  if (fromIndex < toIndex) return 'upgrade';
  if (fromIndex > toIndex) return 'downgrade';
  return 'same';
}

/**
 * Check if a plan change is allowed
 */
export function canChangePlan(
  currentSubscription: UserSubscription,
  targetTier: SubscriptionTier
): { allowed: boolean; reason?: string } {
  // Can't change to the same tier
  if (currentSubscription.tier === targetTier) {
    return { allowed: false, reason: 'You are already on this plan' };
  }
  
  // Can't change if subscription is in certain states
  if (currentSubscription.status === 'unpaid') {
    return { allowed: false, reason: 'Please resolve your payment issue before changing plans' };
  }
  
  if (currentSubscription.status === 'incomplete') {
    return { allowed: false, reason: 'Please complete your current subscription setup first' };
  }
  
  // Can always downgrade to free
  if (targetTier === 'free') {
    return { allowed: true };
  }
  
  // Enterprise requires contact with sales
  if (targetTier === 'enterprise') {
    return { allowed: true }; // Will redirect to sales contact
  }
  
  return { allowed: true };
}

/**
 * Calculate prorated amount for plan change
 */
export function calculateProratedAmount(
  currentSubscription: UserSubscription,
  targetTier: SubscriptionTier,
  currency: CurrencyCode = 'USD'
): number {
  const currentTier = getPricingTier(currentSubscription.tier);
  const newTier = getPricingTier(targetTier);
  
  if (!currentTier || !newTier) return 0;
  
  // Free tier has no proration
  if (currentSubscription.tier === 'free' || targetTier === 'free') {
    return 0;
  }
  
  const now = new Date();
  const periodEnd = new Date(currentSubscription.currentPeriodEnd);
  const periodStart = new Date(currentSubscription.currentPeriodStart);
  
  // Calculate days remaining in current period
  const totalDays = Math.ceil((periodEnd.getTime() - periodStart.getTime()) / (1000 * 60 * 60 * 24));
  const daysRemaining = Math.max(0, Math.ceil((periodEnd.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));
  
  if (totalDays === 0) return 0;
  
  const currentMonthlyPrice = calculateMonthlyPrice(currentTier, currentSubscription.billingCycle, currency);
  const newMonthlyPrice = calculateMonthlyPrice(newTier, currentSubscription.billingCycle, currency);
  
  // Calculate daily rates
  const currentDailyRate = currentMonthlyPrice / 30;
  const newDailyRate = newMonthlyPrice / 30;
  
  // Prorated amount = (new rate - current rate) * days remaining
  const proratedAmount = (newDailyRate - currentDailyRate) * daysRemaining;
  
  // For downgrades, this will be negative (credit)
  // For upgrades, this will be positive (charge)
  return Math.round(proratedAmount * 100) / 100;
}

/**
 * Preview a plan change before executing
 */
export function previewPlanChange(
  currentSubscription: UserSubscription,
  targetTier: SubscriptionTier,
  currency: CurrencyCode = 'USD'
): PlanChangePreview {
  const changeType = getPlanChangeType(currentSubscription.tier, targetTier);
  const { gained, lost } = getFeatureDifferences(currentSubscription.tier, targetTier);
  const newTier = getPricingTier(targetTier);
  
  const warnings: string[] = [];
  
  // Add warnings for downgrades
  if (changeType === 'downgrade') {
    if (lost.length > 0) {
      warnings.push(`You will lose access to ${lost.length} feature(s)`);
    }
    warnings.push('Your current usage may exceed the new plan limits');
  }
  
  // Add warning for enterprise
  if (targetTier === 'enterprise') {
    warnings.push('Enterprise plans require a sales consultation');
  }
  
  const proratedAmount = calculateProratedAmount(currentSubscription, targetTier, currency);
  
  return {
    fromTier: currentSubscription.tier,
    toTier: targetTier,
    changeType,
    proratedAmount,
    newMonthlyPrice: newTier ? calculateMonthlyPrice(newTier, currentSubscription.billingCycle, currency) : 0,
    newAnnualPrice: newTier ? calculateAnnualPrice(newTier, currency) : 0,
    effectiveDate: changeType === 'downgrade' 
      ? new Date(currentSubscription.currentPeriodEnd) 
      : new Date(),
    featuresGained: gained.map(f => f.name),
    featuresLost: lost.map(f => f.name),
    warnings,
    requiresConfirmation: changeType === 'downgrade' || lost.length > 0,
  };
}

/**
 * Execute a plan change (mock implementation)
 * In production, this would call the backend API
 */
export async function changePlan(
  currentSubscription: UserSubscription,
  targetTier: SubscriptionTier,
  options: {
    billingCycle?: BillingCycle;
    confirmDowngrade?: boolean;
  } = {}
): Promise<PlanChangeResult> {
  // Check if change is allowed
  const { allowed, reason } = canChangePlan(currentSubscription, targetTier);
  if (!allowed) {
    return {
      success: false,
      error: reason,
      message: reason || 'Plan change not allowed',
    };
  }
  
  const changeType = getPlanChangeType(currentSubscription.tier, targetTier);
  
  // Require confirmation for downgrades
  if (changeType === 'downgrade' && !options.confirmDowngrade) {
    return {
      success: false,
      error: 'confirmation_required',
      message: 'Please confirm the downgrade to proceed',
    };
  }
  
  // Enterprise requires sales contact
  if (targetTier === 'enterprise') {
    return {
      success: false,
      error: 'contact_sales',
      message: 'Please contact our sales team for Enterprise plans',
    };
  }
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Create updated subscription
  const now = new Date();
  const periodEnd = new Date(now);
  periodEnd.setMonth(periodEnd.getMonth() + 1);
  
  const updatedSubscription: UserSubscription = {
    ...currentSubscription,
    tier: targetTier,
    billingCycle: options.billingCycle || currentSubscription.billingCycle,
    status: targetTier === 'free' ? 'active' : currentSubscription.status,
    currentPeriodStart: changeType === 'upgrade' ? now : currentSubscription.currentPeriodStart,
    currentPeriodEnd: changeType === 'upgrade' ? periodEnd : currentSubscription.currentPeriodEnd,
    updatedAt: now,
  };
  
  return {
    success: true,
    subscription: updatedSubscription,
    message: changeType === 'upgrade' 
      ? `Successfully upgraded to ${targetTier}!`
      : changeType === 'downgrade'
      ? `Your plan will change to ${targetTier} at the end of your billing period`
      : 'Plan updated successfully',
  };
}

/**
 * Cancel a subscription
 */
export async function cancelSubscription(
  subscription: UserSubscription,
  options: {
    immediate?: boolean;
    reason?: string;
  } = {}
): Promise<PlanChangeResult> {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  if (subscription.tier === 'free') {
    return {
      success: false,
      error: 'already_free',
      message: 'You are already on the free plan',
    };
  }
  
  const updatedSubscription: UserSubscription = {
    ...subscription,
    cancelAtPeriodEnd: !options.immediate,
    status: options.immediate ? 'canceled' : subscription.status,
    tier: options.immediate ? 'free' : subscription.tier,
    updatedAt: new Date(),
  };
  
  return {
    success: true,
    subscription: updatedSubscription,
    message: options.immediate
      ? 'Your subscription has been canceled'
      : 'Your subscription will be canceled at the end of the billing period',
  };
}

/**
 * Reactivate a canceled subscription
 */
export async function reactivateSubscription(
  subscription: UserSubscription
): Promise<PlanChangeResult> {
  if (!subscription.cancelAtPeriodEnd && subscription.status !== 'canceled') {
    return {
      success: false,
      error: 'not_canceled',
      message: 'Your subscription is not scheduled for cancellation',
    };
  }
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const updatedSubscription: UserSubscription = {
    ...subscription,
    cancelAtPeriodEnd: false,
    status: 'active',
    updatedAt: new Date(),
  };
  
  return {
    success: true,
    subscription: updatedSubscription,
    message: 'Your subscription has been reactivated',
  };
}

/**
 * Get usage for a subscription
 */
export function getSubscriptionUsage(subscription: UserSubscription): SubscriptionUsage {
  const tier = getPricingTier(subscription.tier);
  
  // Mock usage data - in production this would come from the backend
  return {
    uploadsThisMonth: Math.floor(Math.random() * 50),
    uploadsLimit: tier?.limits.monthlyUploads || 0,
    apiCallsThisMonth: Math.floor(Math.random() * 100),
    apiCallsLimit: tier?.limits.apiCalls || 0,
    storageUsedMB: Math.floor(Math.random() * 500),
    storageLimitMB: tier?.limits.maxFileSize ? tier.limits.maxFileSize * 10 : 100,
    periodStart: subscription.currentPeriodStart,
    periodEnd: subscription.currentPeriodEnd,
  };
}

/**
 * Check if usage exceeds limits for a target tier
 */
export function checkUsageAgainstTier(
  usage: SubscriptionUsage,
  targetTier: SubscriptionTier
): { exceeds: boolean; warnings: string[] } {
  const tier = getPricingTier(targetTier);
  if (!tier) return { exceeds: false, warnings: [] };
  
  const warnings: string[] = [];
  let exceeds = false;
  
  // Check uploads
  if (tier.limits.monthlyUploads !== 'unlimited' && 
      usage.uploadsThisMonth > tier.limits.monthlyUploads) {
    exceeds = true;
    warnings.push(`Your current uploads (${usage.uploadsThisMonth}) exceed the ${tier.name} limit (${tier.limits.monthlyUploads})`);
  }
  
  // Check API calls
  if (tier.limits.apiCalls !== 'unlimited' && 
      typeof usage.apiCallsLimit === 'number' &&
      usage.apiCallsThisMonth > tier.limits.apiCalls) {
    exceeds = true;
    warnings.push(`Your API usage (${usage.apiCallsThisMonth}) exceeds the ${tier.name} limit (${tier.limits.apiCalls})`);
  }
  
  return { exceeds, warnings };
}

/**
 * Create a default free subscription for new users
 */
export function createFreeSubscription(userId: string): UserSubscription {
  const now = new Date();
  const periodEnd = new Date(now);
  periodEnd.setMonth(periodEnd.getMonth() + 1);
  
  return {
    id: `sub_${Date.now()}`,
    userId,
    tier: 'free',
    status: 'active',
    billingCycle: 'monthly',
    currentPeriodStart: now,
    currentPeriodEnd: periodEnd,
    cancelAtPeriodEnd: false,
    createdAt: now,
    updatedAt: now,
  };
}

/**
 * Check if a feature is available for a subscription
 */
export function hasFeatureAccess(
  subscription: UserSubscription,
  featureId: string
): boolean {
  const tier = getPricingTier(subscription.tier);
  if (!tier) return false;
  
  // Check subscription status
  if (subscription.status === 'canceled' || subscription.status === 'unpaid') {
    // Fall back to free tier features
    const freeTier = getPricingTier('free');
    const freeFeature = freeTier?.features.find(f => f.id === featureId);
    return freeFeature?.included ?? false;
  }
  
  const feature = tier.features.find(f => f.id === featureId);
  return feature?.included ?? false;
}

/**
 * Get the effective tier for a subscription (considering status)
 */
export function getEffectiveTier(subscription: UserSubscription): SubscriptionTier {
  // If subscription is in a bad state, treat as free
  if (subscription.status === 'canceled' || subscription.status === 'unpaid') {
    return 'free';
  }
  
  return subscription.tier;
}
