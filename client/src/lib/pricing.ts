/**
 * Pricing System
 *
 * Dynamic pricing calculator with feature comparisons, usage-based calculations,
 * and currency localization.
 *
 * Requirements: 4.1, 4.2, 4.3, 4.6
 */

// Supported currencies with exchange rates (relative to USD)
export const SUPPORTED_CURRENCIES = {
  USD: { symbol: '$', rate: 1, name: 'US Dollar', locale: 'en-US' },
  EUR: { symbol: '€', rate: 0.92, name: 'Euro', locale: 'de-DE' },
  GBP: { symbol: '£', rate: 0.79, name: 'British Pound', locale: 'en-GB' },
  CAD: { symbol: 'CA$', rate: 1.36, name: 'Canadian Dollar', locale: 'en-CA' },
  AUD: { symbol: 'A$', rate: 1.53, name: 'Australian Dollar', locale: 'en-AU' },
  JPY: {
    symbol: '¥',
    rate: 149.5,
    name: 'Japanese Yen',
    locale: 'ja-JP',
    decimals: 0,
  },
  INR: { symbol: '₹', rate: 83.12, name: 'Indian Rupee', locale: 'en-IN' },
  BRL: { symbol: 'R$', rate: 4.97, name: 'Brazilian Real', locale: 'pt-BR' },
  MXN: { symbol: 'MX$', rate: 17.15, name: 'Mexican Peso', locale: 'es-MX' },
  CHF: { symbol: 'CHF', rate: 0.88, name: 'Swiss Franc', locale: 'de-CH' },
} as const;

export type CurrencyCode = keyof typeof SUPPORTED_CURRENCIES;

export interface CurrencyInfo {
  symbol: string;
  rate: number;
  name: string;
  locale: string;
  decimals?: number;
}

// Subscription tiers
export type SubscriptionTier =
  | 'free'
  | 'professional'
  | 'forensic'
  | 'enterprise';

export interface PricingTier {
  id: SubscriptionTier;
  name: string;
  basePrice: number; // USD per month
  annualDiscount: number; // percentage discount for annual billing
  description: string;
  tagline: string;
  features: PricingFeature[];
  limits: TierLimits;
  recommended?: boolean;
  isEnterprise?: boolean;
}

export interface PricingFeature {
  id: string;
  name: string;
  description: string;
  included: boolean;
  value?: string | number; // For features with specific values (e.g., "5,000 API calls")
}

export interface TierLimits {
  monthlyUploads: number | 'unlimited';
  maxFileSize: number; // in MB
  apiCalls: number | 'unlimited';
  batchSize: number;
  retentionDays: number;
  supportLevel: 'community' | 'email' | 'priority' | 'dedicated';
}

// Feature categories for comparison
export const FEATURE_CATEGORIES = [
  'file-support',
  'metadata-extraction',
  'forensic-analysis',
  'processing',
  'export-support',
] as const;

export type FeatureCategory = (typeof FEATURE_CATEGORIES)[number];

// ============================================================================
// OBSOLETE: PRICING TIERS
// ============================================================================
//
// DEPRECATION NOTICE:
// This PRICING_TIERS object is OBSOLETE for the Images MVP launch.
// The MVP uses a credit-based pricing model (IMAGES_MVP_CREDIT_PACKS).
//
// This data is preserved for historical reference only.
// Do not use in new code.
//

/**
 * @deprecated OBSOLETE - tier pricing is not used for Images MVP (credits are used instead).
 * This is kept exported because legacy UI components still import it.
 */
export const PRICING_TIERS: PricingTier[] = [
  {
    id: 'free',
    name: 'Free',
    basePrice: 0,
    annualDiscount: 0,
    description: '3 files/day, basic web formats only',
    tagline: 'Evaluate our extraction quality',
    recommended: false,
    limits: {
      monthlyUploads: 90, // ~3/day
      maxFileSize: 10,
      apiCalls: 0,
      batchSize: 1,
      retentionDays: 1,
      supportLevel: 'community',
    },
    features: [
      { id: 'standard-images', name: 'Standard Images', description: 'JPEG, PNG, GIF, WebP', included: true },
      { id: 'raw-formats', name: 'RAW Formats', description: 'CR2, NEF, ARW, DNG', included: false },
      { id: 'video-audio', name: 'Video & Audio', description: 'MP4, MOV, MP3, FLAC', included: false },
      { id: 'basic-exif', name: 'Basic EXIF', description: 'Core metadata fields', included: true },
      { id: 'gps-data', name: 'GPS/Location', description: 'Geolocation extraction', included: true },
      { id: 'file-hashes', name: 'File Hashes', description: 'MD5, SHA256', included: true },
      { id: 'makernotes', name: 'MakerNotes', description: 'Camera-specific data', included: false },
      { id: 'forensic-analysis', name: 'Forensic Analysis', description: 'Manipulation detection', included: false },
      { id: 'json-export', name: 'JSON Export', description: 'Export to JSON', included: true },
      { id: 'csv-export', name: 'CSV Export', description: 'Export to CSV', included: false },
      { id: 'pdf-reports', name: 'PDF Reports', description: 'Professional reports', included: false },
      { id: 'api-access', name: 'API Access', description: 'Programmatic access', included: false },
    ],
  },
  {
    id: 'professional',
    name: 'Professional',
    basePrice: 19,
    annualDiscount: 20,
    description: 'All image formats including RAW',
    tagline: 'For investigators & photographers',
    recommended: false,
    limits: {
      monthlyUploads: 500,
      maxFileSize: 100,
      apiCalls: 0,
      batchSize: 10,
      retentionDays: 30,
      supportLevel: 'email',
    },
    features: [
      { id: 'standard-images', name: 'Standard Images', description: 'JPEG, PNG, GIF, WebP', included: true },
      { id: 'raw-formats', name: 'RAW Formats', description: 'CR2, NEF, ARW, DNG', included: true },
      { id: 'video-audio', name: 'Video & Audio', description: 'MP4, MOV, MP3, FLAC', included: false },
      { id: 'basic-exif', name: 'Basic EXIF', description: 'Core metadata fields', included: true },
      { id: 'gps-data', name: 'GPS/Location', description: 'Geolocation extraction', included: true },
      { id: 'file-hashes', name: 'File Hashes', description: 'MD5, SHA256', included: true },
      { id: 'makernotes', name: 'MakerNotes', description: 'Camera-specific data', included: true },
      { id: 'forensic-analysis', name: 'Forensic Analysis', description: 'Manipulation detection', included: true },
      { id: 'json-export', name: 'JSON Export', description: 'Export to JSON', included: true },
      { id: 'csv-export', name: 'CSV Export', description: 'Export to CSV', included: true },
      { id: 'pdf-reports', name: 'PDF Reports', description: 'Professional reports', included: false },
      { id: 'api-access', name: 'API Access', description: 'Programmatic access', included: false },
    ],
  },
  {
    id: 'forensic',
    name: 'Forensic',
    basePrice: 49,
    annualDiscount: 20,
    description: 'Complete forensic toolkit',
    tagline: 'Complete forensic toolkit',
    recommended: true,
    limits: {
      monthlyUploads: 5000,
      maxFileSize: 500,
      apiCalls: 5000,
      batchSize: 100,
      retentionDays: 90,
      supportLevel: 'priority',
    },
    features: [
      { id: 'standard-images', name: 'Standard Images', description: 'JPEG, PNG, GIF, WebP', included: true },
      { id: 'raw-formats', name: 'RAW Formats', description: 'CR2, NEF, ARW, DNG', included: true },
      { id: 'video-audio', name: 'Video & Audio', description: 'MP4, MOV, MP3, FLAC', included: true },
      { id: 'basic-exif', name: 'Basic EXIF', description: 'Core metadata fields', included: true },
      { id: 'gps-data', name: 'GPS/Location', description: 'Geolocation extraction', included: true },
      { id: 'file-hashes', name: 'File Hashes', description: 'MD5, SHA256', included: true },
      { id: 'makernotes', name: 'MakerNotes', description: 'Camera-specific data', included: true },
      { id: 'forensic-analysis', name: 'Forensic Analysis', description: 'Manipulation detection', included: true },
      { id: 'json-export', name: 'JSON Export', description: 'Export to JSON', included: true },
      { id: 'csv-export', name: 'CSV Export', description: 'Export to CSV', included: true },
      { id: 'pdf-reports', name: 'PDF Reports', description: 'Professional reports', included: true },
      { id: 'api-access', name: 'API Access', description: 'Programmatic access', included: true },
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    basePrice: 149,
    annualDiscount: 0,
    description: 'Unlimited everything + dedicated support',
    tagline: 'For agencies & legal teams',
    recommended: false,
    limits: {
      monthlyUploads: -1, // unlimited
      maxFileSize: 2000,
      apiCalls: -1, // unlimited
      batchSize: -1, // unlimited
      retentionDays: 365,
      supportLevel: 'dedicated',
    },
    features: [
      { id: 'standard-images', name: 'Standard Images', description: 'JPEG, PNG, GIF, WebP', included: true },
      { id: 'raw-formats', name: 'RAW Formats', description: 'CR2, NEF, ARW, DNG', included: true },
      { id: 'video-audio', name: 'Video & Audio', description: 'MP4, MOV, MP3, FLAC', included: true },
      { id: 'basic-exif', name: 'Basic EXIF', description: 'Core metadata fields', included: true },
      { id: 'gps-data', name: 'GPS/Location', description: 'Geolocation extraction', included: true },
      { id: 'file-hashes', name: 'File Hashes', description: 'MD5, SHA256', included: true },
      { id: 'makernotes', name: 'MakerNotes', description: 'Camera-specific data', included: true },
      { id: 'forensic-analysis', name: 'Forensic Analysis', description: 'Manipulation detection', included: true },
      { id: 'json-export', name: 'JSON Export', description: 'Export to JSON', included: true },
      { id: 'csv-export', name: 'CSV Export', description: 'Export to CSV', included: true },
      { id: 'pdf-reports', name: 'PDF Reports', description: 'Professional reports', included: true },
      { id: 'api-access', name: 'API Access', description: 'Programmatic access', included: true },
    ],
  },
];

// ============================================================================
// OBSOLETE: CREDIT PACKS
// ============================================================================
//
// DEPRECATION NOTICE:
// This CREDIT_PACKS object is OBSOLETE for the Images MVP.
// The MVP uses IMAGES_MVP_CREDIT_PACKS from server/payments.ts instead.
//
// This data is preserved for historical reference only.
// Do not use in new code.
//

// Credit pack definitions for pay-as-you-go
export interface CreditPack {
  id: string;
  name: string;
  credits: number;
  basePrice: number; // USD
  perCreditPrice: number;
  description: string;
  popular?: boolean;
}

/**
 * @deprecated OBSOLETE - Images MVP uses `IMAGES_MVP_CREDIT_PACKS` server-side.
 * This is kept exported because legacy UI components still import it.
 */
export const CREDIT_PACKS: CreditPack[] = [
  {
    id: 'single',
    name: 'Single',
    credits: 1,
    basePrice: 2,
    perCreditPrice: 2.0,
    description: '1 full forensic analysis',
  },
  {
    id: 'investigation',
    name: 'Investigation',
    credits: 10,
    basePrice: 15,
    perCreditPrice: 1.5,
    description: 'Perfect for small cases',
    popular: true,
  },
  {
    id: 'case',
    name: 'Case Pack',
    credits: 50,
    basePrice: 50,
    perCreditPrice: 1.0,
    description: 'Best value for cases',
  },
  {
    id: 'agency',
    name: 'Agency',
    credits: 200,
    basePrice: 150,
    perCreditPrice: 0.75,
    description: 'Bulk discount',
  },
];

// Credit costs by file type
export const CREDIT_COSTS: Record<string, number> = {
  'image/jpeg': 1,
  'image/png': 1,
  'image/gif': 1,
  'image/webp': 1,
  'image/heic': 2,
  'image/heif': 2,
  'image/x-canon-cr2': 2,
  'image/x-nikon-nef': 2,
  'image/x-sony-arw': 2,
  'image/x-adobe-dng': 2,
  'video/mp4': 5,
  'video/quicktime': 5,
  'video/x-msvideo': 5,
  'video/x-matroska': 5,
  'audio/mpeg': 2,
  'audio/flac': 2,
  'audio/wav': 2,
  'audio/ogg': 2,
  'application/pdf': 2,
  'image/svg+xml': 1,
};

/**
 * Get the default credit cost for unknown file types
 */
export function getDefaultCreditCost(): number {
  return 2;
}

/**
 * Get credit cost for a specific file type
 */
export function getCreditCost(mimeType: string): number {
  return CREDIT_COSTS[mimeType] ?? getDefaultCreditCost();
}

/**
 * Calculate total credits needed for a list of files
 */
export function calculateTotalCredits(
  files: Array<{ type: string; size?: number }>
): number {
  return files.reduce((total, file) => total + getCreditCost(file.type), 0);
}

// Country to currency mapping (simplified)
const COUNTRY_CURRENCY_MAP: Record<string, CurrencyCode> = {
  US: 'USD',
  CA: 'CAD',
  GB: 'GBP',
  AU: 'AUD',
  JP: 'JPY',
  DE: 'EUR',
  FR: 'EUR',
  IT: 'EUR',
  ES: 'EUR',
  NL: 'EUR',
  BE: 'EUR',
  AT: 'EUR',
  PT: 'EUR',
  IE: 'EUR',
  FI: 'EUR',
  IN: 'INR',
  BR: 'BRL',
  MX: 'MXN',
  CH: 'CHF',
};

/**
 * Detect user's preferred currency based on locale/location
 */
export function detectUserCurrency(): CurrencyCode {
  // Try to get from browser locale
  const locale = navigator.language || 'en-US';
  const countryCode = locale.split('-')[1]?.toUpperCase();

  if (countryCode && COUNTRY_CURRENCY_MAP[countryCode]) {
    return COUNTRY_CURRENCY_MAP[countryCode];
  }

  // Try timezone-based detection
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (timezone.includes('Europe')) return 'EUR';
  if (timezone.includes('Asia/Tokyo')) return 'JPY';
  if (timezone.includes('Asia/Kolkata')) return 'INR';
  if (timezone.includes('America/Sao_Paulo')) return 'BRL';
  if (timezone.includes('America/Mexico')) return 'MXN';
  if (timezone.includes('Australia')) return 'AUD';
  if (timezone.includes('Europe/London')) return 'GBP';
  if (timezone.includes('Europe/Zurich')) return 'CHF';

  return 'USD';
}

/**
 * Convert price from USD to target currency
 */
export function convertPrice(priceUSD: number, currency: CurrencyCode): number {
  const currencyInfo = SUPPORTED_CURRENCIES[currency];
  return priceUSD * currencyInfo.rate;
}

/**
 * Format price with currency symbol and locale
 */
export function formatPrice(
  priceUSD: number,
  currency: CurrencyCode,
  options: { showDecimals?: boolean; compact?: boolean } = {}
): string {
  const currencyInfo = SUPPORTED_CURRENCIES[currency] as CurrencyInfo;
  const convertedPrice = convertPrice(priceUSD, currency);
  const decimals =
    currencyInfo.decimals ?? (options.showDecimals !== false ? 2 : 0);

  if (options.compact && convertedPrice >= 1000) {
    const formatter = new Intl.NumberFormat(currencyInfo.locale, {
      style: 'currency',
      currency,
      notation: 'compact',
      maximumFractionDigits: 1,
    });
    return formatter.format(convertedPrice);
  }

  const formatter = new Intl.NumberFormat(currencyInfo.locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return formatter.format(convertedPrice);
}

/**
 * Get pricing tier by ID
 *
 * @deprecated OBSOLETE - This function uses obsolete tier-based pricing.
 * The Images MVP uses credit-based pricing instead.
 * Use IMAGES_MVP_CREDIT_PACKS from server/payments.ts instead.
 */
export function getPricingTier(
  _tierId: SubscriptionTier
): PricingTier | undefined {
  console.warn(
    '[DEPRECATED] getPricingTier called - tier-based pricing is obsolete'
  );
  return undefined;
}

/**
 * Get recommended tier
 *
 * @deprecated OBSOLETE - This function uses obsolete tier-based pricing.
 * The Images MVP uses credit-based pricing instead.
 */
export function getRecommendedTier(): PricingTier | undefined {
  console.warn(
    '[DEPRECATED] getRecommendedTier called - tier-based pricing is obsolete'
  );
  return undefined;
}

/**
 * Calculate monthly price for a tier
 */
export function calculateMonthlyPrice(
  tier: PricingTier,
  billingCycle: 'monthly' | 'annual',
  currency: CurrencyCode = 'USD'
): number {
  let price = tier.basePrice;

  if (billingCycle === 'annual') {
    price = price * (1 - tier.annualDiscount / 100);
  }

  return convertPrice(price, currency);
}

/**
 * Calculate annual price for a tier
 */
export function calculateAnnualPrice(
  tier: PricingTier,
  currency: CurrencyCode = 'USD'
): number {
  const monthlyPrice = calculateMonthlyPrice(tier, 'annual', currency);
  return monthlyPrice * 12;
}

/**
 * Calculate savings from annual billing
 */
export function calculateAnnualSavings(
  tier: PricingTier,
  currency: CurrencyCode = 'USD'
): number {
  const monthlyTotal = convertPrice(tier.basePrice * 12, currency);
  const annualTotal = calculateAnnualPrice(tier, currency);
  return monthlyTotal - annualTotal;
}

export interface UsageEstimate {
  filesPerMonth: number;
  averageFileSizeMB: number;
  needsRawFormats: boolean;
  needsVideoAudio: boolean;
  needsForensicAnalysis: boolean;
  needsApiAccess: boolean;
  needsPdfReports: boolean;
}

/**
 * Recommend a tier based on usage estimate
 */
export function recommendTier(usage: UsageEstimate): SubscriptionTier {
  // Enterprise for high volume or API needs
  if (
    usage.filesPerMonth > 2000 ||
    (usage.needsApiAccess && usage.filesPerMonth > 500)
  ) {
    return 'enterprise';
  }

  // Forensic for video/audio or heavy forensic needs
  if (
    usage.needsVideoAudio ||
    usage.needsPdfReports ||
    (usage.needsForensicAnalysis && usage.filesPerMonth > 100)
  ) {
    return 'forensic';
  }

  // Professional for RAW formats or moderate usage
  if (usage.needsRawFormats || usage.filesPerMonth > 90) {
    return 'professional';
  }

  // Free for basic usage
  return 'free';
}

/**
 * Calculate estimated monthly cost based on usage
 */
export function calculateEstimatedCost(
  usage: UsageEstimate,
  currency: CurrencyCode = 'USD'
): {
  tier: SubscriptionTier;
  monthlyPrice: number;
  annualPrice: number;
  savings: number;
} {
  const recommendedTierId = recommendTier(usage);
  const tier = getPricingTier(recommendedTierId)!;

  return {
    tier: recommendedTierId,
    monthlyPrice: calculateMonthlyPrice(tier, 'monthly', currency),
    annualPrice: calculateAnnualPrice(tier, currency),
    savings: calculateAnnualSavings(tier, currency),
  };
}

/**
 * Check if a feature is available in a tier
 */
export function isFeatureAvailable(
  tierId: SubscriptionTier,
  featureId: string
): boolean {
  const tier = getPricingTier(tierId);
  if (!tier) return false;

  const feature = tier.features.find(f => f.id === featureId);
  return feature?.included ?? false;
}

/**
 * Get all features that differ between two tiers
 */
export function getFeatureDifferences(
  fromTier: SubscriptionTier,
  toTier: SubscriptionTier
): { gained: PricingFeature[]; lost: PricingFeature[] } {
  const from = getPricingTier(fromTier);
  const to = getPricingTier(toTier);

  if (!from || !to) {
    return { gained: [], lost: [] };
  }

  const gained: PricingFeature[] = [];
  const lost: PricingFeature[] = [];

  to.features.forEach(toFeature => {
    const fromFeature = from.features.find(f => f.id === toFeature.id);
    if (toFeature.included && (!fromFeature || !fromFeature.included)) {
      gained.push(toFeature);
    }
  });

  from.features.forEach(fromFeature => {
    const toFeature = to.features.find(f => f.id === fromFeature.id);
    if (fromFeature.included && (!toFeature || !toFeature.included)) {
      lost.push(fromFeature);
    }
  });

  return { gained, lost };
}

/**
 * Compare all tiers for a specific feature
 *
 * @deprecated OBSOLETE - This function uses obsolete tier-based pricing.
 * The Images MVP uses credit-based pricing instead.
 */
export function compareFeatureAcrossTiers(
  _featureId: string
): Record<SubscriptionTier, boolean | string | number> {
  console.warn(
    '[DEPRECATED] compareFeatureAcrossTiers called - tier-based pricing is obsolete'
  );
  const result: Record<SubscriptionTier, boolean | string | number> =
    {} as Record<SubscriptionTier, boolean | string | number>;
  return result;
}

/**
 * Get credit pack by ID
 *
 * @deprecated OBSOLETE - This function uses obsolete credit packs.
 * The Images MVP uses IMAGES_MVP_CREDIT_PACKS from server/payments.ts instead.
 */
export function getCreditPack(_packId: string): CreditPack | undefined {
  console.warn(
    '[DEPRECATED] getCreditPack called - use IMAGES_MVP_CREDIT_PACKS instead'
  );
  return undefined;
}

/**
 * Calculate credit pack price in target currency
 */
export function getCreditPackPrice(
  packId: string,
  currency: CurrencyCode = 'USD'
): number {
  const pack = getCreditPack(packId);
  if (!pack) return 0;
  return convertPrice(pack.basePrice, currency);
}
