export type ImagesMvpQuoteOps = {
  embedding: boolean;
  ocr: boolean;
  forensics: boolean;
};

export type ImagesMvpQuoteFile = {
  id: string;
  name: string;
  mime: string | null;
  sizeBytes: number;
  width?: number | null;
  height?: number | null;
};

export type ImagesMvpQuoteResponse = {
  limits: {
    maxBytes: number;
    allowedMimes: string[];
    maxFiles: number;
  };
  creditSchedule: {
    base: number;
    embedding: number;
    ocr: number;
    forensics: number;
    mpBuckets: { label: string; maxMp: number; credits: number }[];
    standardCreditsPerImage: number;
  };
  quote: {
    perFile: Array<{
      id: string;
      accepted: boolean;
      reason?: string;
      detected_type?: string | null;
      creditsTotal?: number;
      mp?: number | null;
      mpBucket?: string | null;
      breakdown?: {
        base: number;
        embedding: number;
        ocr: number;
        forensics: number;
        mp: number;
      };
      warnings?: string[];
    }>;
    totalCredits: number;
    standardEquivalents: number | null;
  };
  quoteId: string;
  expiresAt: string;
  warnings: string[];
};

export async function fetchImagesMvpQuote(
  files: ImagesMvpQuoteFile[],
  ops: ImagesMvpQuoteOps
): Promise<ImagesMvpQuoteResponse> {
  const response = await fetch('/api/images_mvp/quote', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ files, ops }),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'Failed to get quote');
  }

  return response.json();
}

export function createDefaultQuoteOps(): ImagesMvpQuoteOps {
  return {
    embedding: true,
    ocr: false,
    forensics: false,
  };
}
