/**
 * Subscription Manager Component
 *
 * Handles plan upgrades, downgrades, and subscription management UI.
 *
 * Requirements: 4.4, 4.5
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowUp,
  ArrowDown,
  AlertTriangle,
  Check,
  X,
  Loader2,
  Calendar,
  Shield,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  type UserSubscription,
  type PlanChangePreview,
  type SubscriptionUsage,
  previewPlanChange,
  changePlan,
  cancelSubscription,
  reactivateSubscription,
  getSubscriptionUsage,
} from '@/lib/subscription';
import {
  type SubscriptionTier,
  type CurrencyCode,
  PRICING_TIERS,
  getPricingTier,
  formatPrice,
  detectUserCurrency,
} from '@/lib/pricing';

interface SubscriptionManagerProps {
  subscription: UserSubscription;
  onSubscriptionChange?: (subscription: UserSubscription) => void;
  className?: string;
}

export function SubscriptionManager({
  subscription,
  onSubscriptionChange,
  className = '',
}: SubscriptionManagerProps) {
  const [currency, setCurrency] = useState<CurrencyCode>('USD');
  const [usage, setUsage] = useState<SubscriptionUsage | null>(null);
  const [selectedTier, setSelectedTier] = useState<SubscriptionTier | null>(
    null
  );
  const [preview, setPreview] = useState<PlanChangePreview | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const currentTier = getPricingTier(subscription.tier);

  useEffect(() => {
    setCurrency(detectUserCurrency());
    setUsage(getSubscriptionUsage(subscription));
  }, [subscription]);

  const handleTierSelect = (tierId: SubscriptionTier) => {
    if (tierId === subscription.tier) return;

    setSelectedTier(tierId);
    const changePreview = previewPlanChange(subscription, tierId, currency);
    setPreview(changePreview);

    if (changePreview.requiresConfirmation) {
      setShowConfirmDialog(true);
    } else {
      handlePlanChange(tierId);
    }
  };

  const handlePlanChange = async (
    tierId: SubscriptionTier,
    confirmDowngrade = false
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await changePlan(subscription, tierId, {
        confirmDowngrade,
      });

      if (result.success && result.subscription) {
        setSuccess(result.message);
        onSubscriptionChange?.(result.subscription);
        setShowConfirmDialog(false);
      } else if (result.error === 'contact_sales') {
        // Redirect to sales contact
        window.open(
          'mailto:sales@metaextract.com?subject=Enterprise%20Plan%20Inquiry',
          '_blank'
        );
      } else {
        setError(result.error || result.message);
      }
    } catch {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
      setSelectedTier(null);
      setPreview(null);
    }
  };

  const handleCancel = async (immediate = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await cancelSubscription(subscription, { immediate });

      if (result.success && result.subscription) {
        setSuccess(result.message);
        onSubscriptionChange?.(result.subscription);
        setShowCancelDialog(false);
      } else {
        setError(result.error || result.message);
      }
    } catch {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReactivate = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await reactivateSubscription(subscription);

      if (result.success && result.subscription) {
        setSuccess(result.message);
        onSubscriptionChange?.(result.subscription);
      } else {
        setError(result.error || result.message);
      }
    } catch {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Current Plan Card */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Current Plan
              </CardTitle>
              <CardDescription>
                Manage your subscription and billing
              </CardDescription>
            </div>
            <Badge
              variant={
                subscription.status === 'active' ? 'default' : 'destructive'
              }
              className={
                subscription.status === 'active'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : ''
              }
            >
              {subscription.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Plan Info */}
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
            <div>
              <h3 className="text-2xl font-bold text-white">
                {currentTier?.name}
              </h3>
              <p className="text-sm text-slate-300">{currentTier?.tagline}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary">
                {currentTier?.basePrice === 0
                  ? 'Free'
                  : formatPrice(currentTier?.basePrice || 0, currency)}
              </p>
              <p className="text-sm text-slate-300">
                {subscription.billingCycle === 'annual'
                  ? 'per month (billed annually)'
                  : 'per month'}
              </p>
            </div>
          </div>

          {/* Billing Period */}
          <div className="flex items-center gap-4 text-sm text-slate-300">
            <Calendar className="w-4 h-4" />
            <span>
              Current period:{' '}
              {new Date(subscription.currentPeriodStart).toLocaleDateString()} -{' '}
              {new Date(subscription.currentPeriodEnd).toLocaleDateString()}
            </span>
          </div>

          {/* Cancellation Warning */}
          {subscription.cancelAtPeriodEnd && (
            <Alert className="border-amber-500/20 bg-amber-500/10">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <AlertTitle className="text-amber-400">
                Subscription Ending
              </AlertTitle>
              <AlertDescription className="text-amber-300">
                Your subscription will be canceled on{' '}
                {new Date(subscription.currentPeriodEnd).toLocaleDateString()}.
                <Button
                  variant="link"
                  className="text-amber-400 p-0 h-auto ml-2"
                  onClick={handleReactivate}
                  disabled={isLoading}
                >
                  Reactivate
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {/* Usage Stats */}
          {usage && (
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-slate-200">
                Usage This Period
              </h4>

              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300">Uploads</span>
                    <span className="text-white">
                      {usage.uploadsThisMonth} /{' '}
                      {usage.uploadsLimit === 'unlimited'
                        ? '∞'
                        : usage.uploadsLimit}
                    </span>
                  </div>
                  <Progress
                    value={
                      usage.uploadsLimit === 'unlimited'
                        ? 0
                        : (usage.uploadsThisMonth /
                            (usage.uploadsLimit as number)) *
                          100
                    }
                    className="h-2"
                  />
                </div>

                {usage.apiCallsLimit !== 0 && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-300">API Calls</span>
                      <span className="text-white">
                        {usage.apiCallsThisMonth} /{' '}
                        {usage.apiCallsLimit === 'unlimited'
                          ? '∞'
                          : usage.apiCallsLimit}
                      </span>
                    </div>
                    <Progress
                      value={
                        usage.apiCallsLimit === 'unlimited'
                          ? 0
                          : (usage.apiCallsThisMonth /
                              (usage.apiCallsLimit as number)) *
                            100
                      }
                      className="h-2"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            {subscription.tier !== 'free' &&
              !subscription.cancelAtPeriodEnd && (
                <Button
                  variant="outline"
                  className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                  onClick={() => setShowCancelDialog(true)}
                >
                  Cancel Subscription
                </Button>
              )}
          </div>
        </CardContent>
      </Card>

      {/* Success/Error Messages */}
      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Alert className="border-emerald-500/20 bg-emerald-500/10">
              <Check className="h-4 w-4 text-emerald-400" />
              <AlertDescription className="text-emerald-300">
                {success}
              </AlertDescription>
            </Alert>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Alert className="border-red-500/20 bg-red-500/10">
              <X className="h-4 w-4 text-red-400" />
              <AlertDescription className="text-red-300">
                {error}
              </AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Available Plans */}
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle>Change Plan</CardTitle>
          <CardDescription>
            Upgrade or downgrade your subscription
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {PRICING_TIERS.map(tier => {
              const isCurrentTier = tier.id === subscription.tier;
              const changeType =
                tier.id === subscription.tier
                  ? 'same'
                  : PRICING_TIERS.findIndex(t => t.id === tier.id) >
                      PRICING_TIERS.findIndex(t => t.id === subscription.tier)
                    ? 'upgrade'
                    : 'downgrade';

              return (
                <div
                  key={tier.id}
                  className={`p-4 rounded-lg border transition-all cursor-pointer ${
                    isCurrentTier
                      ? 'border-primary bg-primary/10'
                      : 'border-white/10 hover:border-white/30 bg-white/5'
                  }`}
                  role="button"
                  tabIndex={0}
                  onClick={() => !isCurrentTier && handleTierSelect(tier.id)}
                  onKeyDown={(e: React.KeyboardEvent) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      !isCurrentTier && handleTierSelect(tier.id);
                    }
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-white">{tier.name}</h4>
                    {isCurrentTier && (
                      <Badge className="bg-primary/20 text-primary text-xs">
                        Current
                      </Badge>
                    )}
                    {!isCurrentTier && changeType === 'upgrade' && (
                      <ArrowUp className="w-4 h-4 text-emerald-400" />
                    )}
                    {!isCurrentTier && changeType === 'downgrade' && (
                      <ArrowDown className="w-4 h-4 text-amber-400" />
                    )}
                  </div>
                  <p className="text-xl font-bold text-white mb-1">
                    {tier.basePrice === 0
                      ? 'Free'
                      : formatPrice(tier.basePrice, currency)}
                    {tier.basePrice > 0 && (
                      <span className="text-sm font-normal text-slate-300">
                        /mo
                      </span>
                    )}
                  </p>
                  <p className="text-xs text-slate-300">{tier.description}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Plan Change Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent className="bg-[#1a1a2e] border-white/10 text-white">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {preview?.changeType === 'upgrade' ? (
                <ArrowUp className="w-5 h-5 text-emerald-400" />
              ) : (
                <ArrowDown className="w-5 h-5 text-amber-400" />
              )}
              Confirm Plan Change
            </DialogTitle>
            <DialogDescription className="text-slate-300">
              {preview?.changeType === 'upgrade'
                ? 'You are upgrading your plan'
                : 'You are downgrading your plan'}
            </DialogDescription>
          </DialogHeader>

          {preview && (
            <div className="space-y-4">
              {/* Plan Change Summary */}
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-sm text-slate-300">From</p>
                  <p className="font-medium">
                    {getPricingTier(preview.fromTier)?.name}
                  </p>
                </div>
                <ArrowDown className="w-5 h-5 text-slate-500 rotate-[-90deg]" />
                <div>
                  <p className="text-sm text-slate-300">To</p>
                  <p className="font-medium text-primary">
                    {getPricingTier(preview.toTier)?.name}
                  </p>
                </div>
              </div>

              {/* Price Change */}
              <div className="p-4 bg-white/5 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-slate-300">New Monthly Price</span>
                  <span className="font-medium">
                    {formatPrice(preview.newMonthlyPrice, currency)}
                  </span>
                </div>
                {preview.proratedAmount !== 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">
                      Prorated{' '}
                      {preview.proratedAmount > 0 ? 'Charge' : 'Credit'}
                    </span>
                    <span
                      className={
                        preview.proratedAmount > 0
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }
                    >
                      {formatPrice(Math.abs(preview.proratedAmount), currency)}
                    </span>
                  </div>
                )}
              </div>

              {/* Features Changes */}
              {preview.featuresGained.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-emerald-400 mb-2">
                    Features You'll Gain
                  </p>
                  <ul className="space-y-1">
                    {preview.featuresGained.map((feature, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 text-sm text-slate-200"
                      >
                        <Check className="w-4 h-4 text-emerald-400" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {preview.featuresLost.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-amber-400 mb-2">
                    Features You'll Lose
                  </p>
                  <ul className="space-y-1">
                    {preview.featuresLost.map((feature, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 text-sm text-slate-200"
                      >
                        <X className="w-4 h-4 text-amber-400" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Warnings */}
              {preview.warnings.length > 0 && (
                <Alert className="border-amber-500/20 bg-amber-500/10">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  <AlertDescription className="text-amber-300">
                    <ul className="list-disc list-inside">
                      {preview.warnings.map((warning, i) => (
                        <li key={i}>{warning}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}

              {/* Effective Date */}
              <p className="text-sm text-slate-300">
                Effective: {preview.effectiveDate.toLocaleDateString()}
              </p>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowConfirmDialog(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={() =>
                selectedTier && handlePlanChange(selectedTier, true)
              }
              disabled={isLoading}
              className={
                preview?.changeType === 'upgrade'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-amber-600 hover:bg-amber-700'
              }
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : null}
              Confirm{' '}
              {preview?.changeType === 'upgrade' ? 'Upgrade' : 'Downgrade'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Subscription Dialog */}
      <Dialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <DialogContent className="bg-[#1a1a2e] border-white/10 text-white">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-400">
              <AlertTriangle className="w-5 h-5" />
              Cancel Subscription
            </DialogTitle>
            <DialogDescription className="text-slate-300">
              Are you sure you want to cancel your subscription?
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Alert className="border-amber-500/20 bg-amber-500/10">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <AlertDescription className="text-amber-300">
                You will lose access to premium features at the end of your
                billing period.
              </AlertDescription>
            </Alert>

            <p className="text-sm text-slate-300">
              Your subscription will remain active until{' '}
              {new Date(subscription.currentPeriodEnd).toLocaleDateString()}.
              You can reactivate anytime before then.
            </p>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowCancelDialog(false)}
              disabled={isLoading}
            >
              Keep Subscription
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleCancel(false)}
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : null}
              Cancel at Period End
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default SubscriptionManager;
