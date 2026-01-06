/**
 * Pricing Calculator Component
 * 
 * Interactive pricing calculator with tier comparisons, usage estimation,
 * and currency localization.
 * 
 * Requirements: 4.1, 4.2, 4.3, 4.6
 */

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Check,
  X,
  Zap,
  ChevronDown,
  Calculator,
  Globe,
  Info,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  PRICING_TIERS,
  SUPPORTED_CURRENCIES,
  type CurrencyCode,
  type SubscriptionTier,
  type PricingTier,
  type UsageEstimate,
  detectUserCurrency,
  formatPrice,
  calculateMonthlyPrice,
  calculateAnnualPrice,
  calculateAnnualSavings,
  recommendTier,
  getFeatureDifferences,
} from '@/lib/pricing';

interface PricingCalculatorProps {
  onSelectTier?: (tier: SubscriptionTier, billingCycle: 'monthly' | 'annual') => void;
  currentTier?: SubscriptionTier;
  showCalculator?: boolean;
  className?: string;
}

export function PricingCalculator({
  onSelectTier,
  currentTier,
  showCalculator = true,
  className = '',
}: PricingCalculatorProps) {
  const [currency, setCurrency] = useState<CurrencyCode>('USD');
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [showComparison, setShowComparison] = useState(false);
  const [highlightedTier, setHighlightedTier] = useState<SubscriptionTier | null>(null);
  
  // Usage estimation state
  const [usage, setUsage] = useState<UsageEstimate>({
    filesPerMonth: 50,
    averageFileSizeMB: 10,
    needsRawFormats: false,
    needsVideoAudio: false,
    needsForensicAnalysis: false,
    needsApiAccess: false,
    needsPdfReports: false,
  });

  // Detect user's currency on mount
  useEffect(() => {
    const detectedCurrency = detectUserCurrency();
    setCurrency(detectedCurrency);
  }, []);

  // Calculate recommended tier based on usage
  const recommendedTier = useMemo(() => recommendTier(usage), [usage]);

  const handleTierSelect = (tierId: SubscriptionTier) => {
    onSelectTier?.(tierId, billingCycle);
  };

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Currency and Billing Toggle */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-slate-300" />
            <Select value={currency} onValueChange={(v) => setCurrency(v as CurrencyCode)}>
              <SelectTrigger className="w-[140px] bg-white/5 border-white/10">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(SUPPORTED_CURRENCIES).map(([code, info]) => (
                  <SelectItem key={code} value={code}>
                    {info.symbol} {code}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-white/5 rounded-full p-1">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              billingCycle === 'monthly'
                ? 'bg-primary text-black'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('annual')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
              billingCycle === 'annual'
                ? 'bg-primary text-black'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            Annual
            <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400 text-xs">
              Save 20%
            </Badge>
          </button>
        </div>
      </div>

      {/* Usage Calculator */}
      {showCalculator && (
        <Card className="bg-white/5 border-white/10">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Calculator className="w-5 h-5 text-primary" />
              Find Your Perfect Plan
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Files per month slider */}
              <div className="space-y-3">
                <div className="flex justify-between">
                  <Label className="text-slate-200">Files per month</Label>
                  <span className="text-primary font-mono">{usage.filesPerMonth}</span>
                </div>
                <Slider
                  value={[usage.filesPerMonth]}
                  onValueChange={([v]) => setUsage(prev => ({ ...prev, filesPerMonth: v }))}
                  min={1}
                  max={500}
                  step={10}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-slate-500">
                  <span>1</span>
                  <span>500+</span>
                </div>
              </div>

              {/* Feature toggles */}
              <div className="space-y-3">
                <Label className="text-slate-200">Features needed</Label>
                <div className="space-y-2">
                  {[
                    { key: 'needsRawFormats', label: 'RAW image formats' },
                    { key: 'needsVideoAudio', label: 'Video & Audio files' },
                    { key: 'needsForensicAnalysis', label: 'Forensic analysis' },
                    { key: 'needsApiAccess', label: 'API access' },
                    { key: 'needsPdfReports', label: 'PDF reports' },
                  ].map(({ key, label }) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm text-slate-300">{label}</span>
                      <Switch
                        checked={usage[key as keyof UsageEstimate] as boolean}
                        onCheckedChange={(checked) =>
                          setUsage(prev => ({ ...prev, [key]: checked }))
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className="flex items-center justify-between p-4 bg-primary/10 border border-primary/20 rounded-lg">
              <div className="flex items-center gap-3">
                <Sparkles className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-white">
                    Recommended: <span className="text-primary">{PRICING_TIERS.find(t => t.id === recommendedTier)?.name}</span>
                  </p>
                  <p className="text-xs text-slate-300">Based on your usage estimate</p>
                </div>
              </div>
              <Button
                size="sm"
                onClick={() => handleTierSelect(recommendedTier)}
                className="bg-primary text-black hover:bg-primary/90"
              >
                Select Plan
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {PRICING_TIERS.map((tier) => (
          <PricingCard
            key={tier.id}
            tier={tier}
            currency={currency}
            billingCycle={billingCycle}
            isCurrentTier={currentTier === tier.id}
            isRecommended={recommendedTier === tier.id}
            isHighlighted={highlightedTier === tier.id}
            onSelect={() => handleTierSelect(tier.id)}
            onHover={() => setHighlightedTier(tier.id)}
            onLeave={() => setHighlightedTier(null)}
          />
        ))}
      </div>

      {/* Feature Comparison Toggle */}
      <div className="flex justify-center">
        <button
          onClick={() => setShowComparison(!showComparison)}
          className="flex items-center gap-2 text-sm text-slate-300 hover:text-white transition-colors"
        >
          <span>Compare all features</span>
          <ChevronDown
            className={`w-4 h-4 transition-transform ${showComparison ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      {/* Feature Comparison Table */}
      <AnimatePresence>
        {showComparison && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <FeatureComparisonTable currency={currency} billingCycle={billingCycle} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface PricingCardProps {
  tier: PricingTier;
  currency: CurrencyCode;
  billingCycle: 'monthly' | 'annual';
  isCurrentTier: boolean;
  isRecommended: boolean;
  isHighlighted: boolean;
  onSelect: () => void;
  onHover: () => void;
  onLeave: () => void;
}

function PricingCard({
  tier,
  currency,
  billingCycle,
  isCurrentTier,
  isRecommended,
  isHighlighted,
  onSelect,
  onHover,
  onLeave,
}: PricingCardProps) {
  const monthlyPrice = calculateMonthlyPrice(tier, billingCycle, currency);
  const annualSavings = calculateAnnualSavings(tier, currency);
  const currencyInfo = SUPPORTED_CURRENCIES[currency];

  return (
    <motion.div
      whileHover={{ y: -4 }}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      className={`relative flex flex-col h-full rounded-lg border transition-all ${
        tier.recommended
          ? 'bg-primary text-black border-primary'
          : isHighlighted
          ? 'bg-white/10 border-white/30'
          : 'bg-white/5 border-white/10 hover:border-white/20'
      }`}
    >
      {/* Recommended badge */}
      {tier.recommended && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge className="bg-black text-primary px-3">
            <Zap className="w-3 h-3 mr-1" />
            Most Popular
          </Badge>
        </div>
      )}

      {/* Current tier badge */}
      {isCurrentTier && (
        <div className="absolute -top-3 right-4">
          <Badge variant="outline" className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
            Current Plan
          </Badge>
        </div>
      )}

      <div className="p-6 flex-1 flex flex-col">
        {/* Header */}
        <div className="mb-4">
          <h3 className={`text-xl font-bold ${tier.recommended ? 'text-black' : 'text-white'}`}>
            {tier.name}
          </h3>
          <p className={`text-sm ${tier.recommended ? 'text-black/70' : 'text-slate-300'}`}>
            {tier.tagline}
          </p>
        </div>

        {/* Price */}
        <div className="mb-6">
          <div className="flex items-baseline gap-1">
            <span className={`text-4xl font-bold ${tier.recommended ? 'text-black' : 'text-white'}`}>
              {tier.basePrice === 0 ? 'Free' : formatPrice(monthlyPrice / currencyInfo.rate, currency, { showDecimals: false })}
            </span>
            {tier.basePrice > 0 && (
              <span className={`text-sm ${tier.recommended ? 'text-black/60' : 'text-slate-500'}`}>
                /mo
              </span>
            )}
          </div>
          {billingCycle === 'annual' && tier.basePrice > 0 && (
            <p className={`text-xs mt-1 ${tier.recommended ? 'text-black/70' : 'text-emerald-400'}`}>
              Save {formatPrice(annualSavings / currencyInfo.rate, currency)} per year
            </p>
          )}
        </div>

        {/* Features */}
        <ul className="space-y-2 mb-6 flex-1">
          {tier.features.slice(0, 6).map((feature) => (
            <li
              key={feature.id}
              className={`flex items-center gap-2 text-sm ${
                tier.recommended ? 'text-black/80' : 'text-slate-200'
              }`}
            >
              {feature.included ? (
                <Check className={`w-4 h-4 ${tier.recommended ? 'text-black' : 'text-emerald-500'}`} />
              ) : (
                <X className={`w-4 h-4 ${tier.recommended ? 'text-black/30' : 'text-slate-600'}`} />
              )}
              <span className={!feature.included ? 'opacity-50' : ''}>
                {feature.name}
                {feature.value && ` (${feature.value})`}
              </span>
            </li>
          ))}
        </ul>

        {/* CTA Button */}
        <Button
          onClick={onSelect}
          disabled={isCurrentTier}
          className={`w-full ${
            tier.recommended
              ? 'bg-black text-white hover:bg-black/80'
              : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
          }`}
        >
          {isCurrentTier ? 'Current Plan' : tier.isEnterprise ? 'Contact Sales' : 'Get Started'}
          {!isCurrentTier && <ArrowRight className="w-4 h-4 ml-2" />}
        </Button>
      </div>
    </motion.div>
  );
}

interface FeatureComparisonTableProps {
  currency: CurrencyCode;
  billingCycle: 'monthly' | 'annual';
}

function FeatureComparisonTable({ currency, billingCycle }: FeatureComparisonTableProps) {
  // Get all unique features
  const allFeatures = useMemo(() => {
    const featureMap = new Map<string, { id: string; name: string; description: string }>();
    PRICING_TIERS.forEach(tier => {
      tier.features.forEach(feature => {
        if (!featureMap.has(feature.id)) {
          featureMap.set(feature.id, {
            id: feature.id,
            name: feature.name,
            description: feature.description,
          });
        }
      });
    });
    return Array.from(featureMap.values());
  }, []);

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left p-4 text-slate-300 font-medium">Feature</th>
            {PRICING_TIERS.map(tier => (
              <th
                key={tier.id}
                className={`p-4 text-center font-medium ${
                  tier.recommended ? 'text-primary' : 'text-white'
                }`}
              >
                {tier.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {/* Pricing row */}
          <tr className="border-b border-white/5">
            <td className="p-4 text-slate-200">Monthly Price</td>
            {PRICING_TIERS.map(tier => (
              <td key={tier.id} className="p-4 text-center">
                <span className={tier.recommended ? 'text-primary font-bold' : 'text-white'}>
                  {tier.basePrice === 0
                    ? 'Free'
                    : formatPrice(calculateMonthlyPrice(tier, billingCycle, currency) / SUPPORTED_CURRENCIES[currency].rate, currency)}
                </span>
              </td>
            ))}
          </tr>

          {/* Feature rows */}
          {allFeatures.map(feature => (
            <tr key={feature.id} className="border-b border-white/5 hover:bg-white/5">
              <td className="p-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger className="flex items-center gap-2 text-slate-200">
                      {feature.name}
                      <Info className="w-3 h-3 text-slate-500" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{feature.description}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </td>
              {PRICING_TIERS.map(tier => {
                const tierFeature = tier.features.find(f => f.id === feature.id);
                const included = tierFeature?.included ?? false;
                const value = tierFeature?.value;

                return (
                  <td key={tier.id} className="p-4 text-center">
                    {value ? (
                      <span className={tier.recommended ? 'text-primary' : 'text-white'}>
                        {value}
                      </span>
                    ) : included ? (
                      <Check className={`w-5 h-5 mx-auto ${tier.recommended ? 'text-primary' : 'text-emerald-500'}`} />
                    ) : (
                      <X className="w-5 h-5 mx-auto text-slate-600" />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}

          {/* Limits rows */}
          <tr className="border-b border-white/5">
            <td className="p-4 text-slate-200">Monthly Uploads</td>
            {PRICING_TIERS.map(tier => (
              <td key={tier.id} className="p-4 text-center text-white">
                {tier.limits.monthlyUploads === 'unlimited' ? 'Unlimited' : tier.limits.monthlyUploads}
              </td>
            ))}
          </tr>
          <tr className="border-b border-white/5">
            <td className="p-4 text-slate-200">Max File Size</td>
            {PRICING_TIERS.map(tier => (
              <td key={tier.id} className="p-4 text-center text-white">
                {tier.limits.maxFileSize >= 1024
                  ? `${tier.limits.maxFileSize / 1024}GB`
                  : `${tier.limits.maxFileSize}MB`}
              </td>
            ))}
          </tr>
          <tr className="border-b border-white/5">
            <td className="p-4 text-slate-200">Support Level</td>
            {PRICING_TIERS.map(tier => (
              <td key={tier.id} className="p-4 text-center">
                <Badge
                  variant="outline"
                  className={`capitalize ${
                    tier.limits.supportLevel === 'dedicated'
                      ? 'border-emerald-500/30 text-emerald-400'
                      : tier.limits.supportLevel === 'priority'
                      ? 'border-primary/30 text-primary'
                      : 'border-white/20 text-slate-300'
                  }`}
                >
                  {tier.limits.supportLevel}
                </Badge>
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default PricingCalculator;
