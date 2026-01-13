export const IMAGES_MVP_MP_BUCKETS = [
  { label: 'standard', maxMp: 12, credits: 0 },
  { label: 'large', maxMp: 24, credits: 1 },
  { label: 'xl', maxMp: 48, credits: 3 },
  { label: 'xxl', maxMp: 96, credits: 7 },
] as const;

export const IMAGES_MVP_CREDIT_SCHEDULE = {
  base: 1,
  embedding: 3,
  ocr: 5,
  forensics: 4,
  mpBuckets: IMAGES_MVP_MP_BUCKETS,
} as const;

export type ImagesMvpQuoteOps = {
  embedding: boolean;
  ocr: boolean;
  forensics: boolean;
};

export function computeMp(
  width?: number | null,
  height?: number | null
): number | null {
  if (!width || !height || width <= 0 || height <= 0) return null;
  const mp = (width * height) / 1_000_000;
  return Number.isFinite(mp) ? Math.round(mp * 10) / 10 : null;
}

export function resolveMpBucket(mp: number | null): {
  label: string;
  credits: number;
  warning?: string;
} {
  const maxBucket = IMAGES_MVP_MP_BUCKETS[IMAGES_MVP_MP_BUCKETS.length - 1];
  if (mp === null) {
    return {
      label: 'unknown',
      credits: 0,
      warning: 'Dimensions unavailable; skipping megapixel bucket charge.',
    };
  }
  for (const bucket of IMAGES_MVP_MP_BUCKETS) {
    if (mp <= bucket.maxMp) {
      return {
        label: bucket.label,
        credits: bucket.credits,
      };
    }
  }
  return {
    label: maxBucket.label,
    credits: maxBucket.credits,
    warning: 'Very large image; charging max size bucket.',
  };
}

export function resolveSizeBucketFromBytes(bytes: number): {
  label: string;
  credits: number;
} {
  const mb = bytes / (1024 * 1024);
  if (!Number.isFinite(mb) || mb <= 0) return { label: 'unknown', credits: 0 };
  if (mb <= 10) return { label: 'standard', credits: 0 };
  if (mb <= 25) return { label: 'large', credits: 1 };
  if (mb <= 50) return { label: 'xl', credits: 3 };
  return { label: 'xxl', credits: 7 };
}

export function computeImagesMvpCreditsTotal(
  ops: ImagesMvpQuoteOps,
  mpCredits: number
): {
  creditsTotal: number;
  breakdown: {
    base: number;
    embedding: number;
    ocr: number;
    forensics: number;
    mp: number;
  };
} {
  const breakdown = {
    base: IMAGES_MVP_CREDIT_SCHEDULE.base,
    embedding: ops.embedding ? IMAGES_MVP_CREDIT_SCHEDULE.embedding : 0,
    ocr: ops.ocr ? IMAGES_MVP_CREDIT_SCHEDULE.ocr : 0,
    forensics: ops.forensics ? IMAGES_MVP_CREDIT_SCHEDULE.forensics : 0,
    mp: mpCredits,
  };

  const creditsTotal =
    breakdown.base +
    breakdown.embedding +
    breakdown.ocr +
    breakdown.forensics +
    breakdown.mp;

  return { creditsTotal, breakdown };
}
