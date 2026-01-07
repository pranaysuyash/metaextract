/**
 * Cost Calculator for Compute-Based Rate Limiting
 * 
 * Assigns "cost units" to files based on processing requirements.
 * This allows fair rate limiting based on actual compute cost, not just request count.
 * 
 * Usage:
 * - Free tier: Gets limited cost budget per day
 * - Expensive files (HEIC, RAW) consume more budget
 * - Cheap files (JPG, PNG) consume less
 */

export interface FileCost {
  /** Credit cost for this file type (1 = base unit) */
  creditCost: number;
  /** Compute intensity level */
  computeLevel: 'low' | 'medium' | 'high' | 'blocked';
  /** Whether this file type is allowed on free tier */
  freeAllowed: boolean;
  /** Maximum resolution for free tier (0 = not allowed) */
  freeMaxResolution: number;
  /** Description for UI */
  description: string;
}

/**
 * Base cost matrix by MIME type
 * Higher credit cost = more expensive to process
 */
export const FILE_COST_MATRIX: Record<string, FileCost> = {
  // Free tier: cheap, common formats
  'image/jpeg': { 
    creditCost: 1, 
    computeLevel: 'low', 
    freeAllowed: true, 
    freeMaxResolution: 1600,
    description: 'Standard JPEG' 
  },
  'image/png': { 
    creditCost: 1, 
    computeLevel: 'low', 
    freeAllowed: true, 
    freeMaxResolution: 1600,
    description: 'PNG image' 
  },
  'image/webp': { 
    creditCost: 1, 
    computeLevel: 'low', 
    freeAllowed: true, 
    freeMaxResolution: 1600,
    description: 'WebP image' 
  },
  'image/gif': { 
    creditCost: 1, 
    computeLevel: 'low', 
    freeAllowed: true, 
    freeMaxResolution: 1600,
    description: 'GIF image' 
  },
  
  // Paid tier: medium cost formats
  'image/heic': { 
    creditCost: 2, 
    computeLevel: 'medium', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'Apple HEIC (requires conversion)' 
  },
  'image/heif': { 
    creditCost: 2, 
    computeLevel: 'medium', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'HEIF image' 
  },
  'image/tiff': { 
    creditCost: 2, 
    computeLevel: 'medium', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'TIFF image' 
  },
  
  // Paid tier: high cost formats (RAW)
  'image/x-canon-cr2': { 
    creditCost: 3, 
    computeLevel: 'high', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'Canon RAW' 
  },
  'image/x-nikon-nef': { 
    creditCost: 3, 
    computeLevel: 'high', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'Nikon RAW' 
  },
  'image/x-sony-arw': { 
    creditCost: 3, 
    computeLevel: 'high', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'Sony RAW' 
  },
  'image/x-adobe-dng': { 
    creditCost: 3, 
    computeLevel: 'high', 
    freeAllowed: false, 
    freeMaxResolution: 0,
    description: 'Adobe DNG' 
  },
};

/**
 * Default cost for unknown file types
 */
const DEFAULT_COST: FileCost = {
  creditCost: 2,
  computeLevel: 'medium',
  freeAllowed: false,
  freeMaxResolution: 0,
  description: 'Unknown format',
};

/**
 * Size multipliers for large files
 * Increases cost for files that take longer to process
 */
function getSizeMultiplier(sizeBytes: number): number {
  const sizeMB = sizeBytes / (1024 * 1024);
  
  if (sizeMB > 50) return 4;  // Very large
  if (sizeMB > 25) return 3;  // Large
  if (sizeMB > 10) return 2;  // Medium-large
  return 1;                    // Normal
}

/**
 * Calculate the processing cost for a file
 */
export function calculateFileCost(
  mimeType: string, 
  sizeBytes: number, 
  accessLevel: 'anonymous' | 'verified' | 'paid'
): FileCost & { totalCost: number; blocked: boolean; reason?: string } {
  const baseCost = FILE_COST_MATRIX[mimeType] || DEFAULT_COST;
  const sizeMultiplier = getSizeMultiplier(sizeBytes);
  const totalCost = baseCost.creditCost * sizeMultiplier;
  
  // Check if blocked for this access level
  if (accessLevel === 'anonymous' && !baseCost.freeAllowed) {
    return {
      ...baseCost,
      totalCost: 0,
      blocked: true,
      reason: `${baseCost.description} requires a paid account`,
    };
  }
  
  return {
    ...baseCost,
    totalCost,
    blocked: false,
  };
}

/**
 * Check if a file type is allowed for free tier
 */
export function isFileTypeAllowedForFree(mimeType: string): boolean {
  const cost = FILE_COST_MATRIX[mimeType];
  return cost?.freeAllowed ?? false;
}

/**
 * Get recommended downscale resolution for free tier
 */
export function getFreeMaxResolution(mimeType: string): number {
  const cost = FILE_COST_MATRIX[mimeType];
  return cost?.freeMaxResolution ?? 0;
}

/**
 * Identity tiers for progressive friction
 */
export type IdentityTier = 'anonymous' | 'challenge_verified' | 'email_verified' | 'oauth_verified' | 'paid';

/**
 * Daily credit budgets by identity tier
 */
export const TIER_BUDGETS: Record<IdentityTier, number> = {
  anonymous: 2,               // 2 cheap files/day
  challenge_verified: 5,       // +3 after captcha
  email_verified: 15,          // +10 after email OTP
  oauth_verified: 20,          // +5 for OAuth
  paid: 999999,                // Unlimited (plan limits apply)
};

/**
 * Get daily credit budget for identity tier
 */
export function getDailyBudget(tier: IdentityTier): number {
  return TIER_BUDGETS[tier] ?? TIER_BUDGETS.anonymous;
}
