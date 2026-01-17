export const IMAGES_MVP_QUOTE_SCHEMA_VERSION = 'images_mvp_quote_v1' as const;

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
  schemaVersion: typeof IMAGES_MVP_QUOTE_SCHEMA_VERSION;
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

/**
 * Validates that the quote response has the expected schema version.
 * Throws an error if the version is unknown or missing.
 */
export function assertQuoteSchemaVersion(
  x: any
): asserts x is ImagesMvpQuoteResponse {
  if (!x || x.schemaVersion !== IMAGES_MVP_QUOTE_SCHEMA_VERSION) {
    throw new Error(
      `Unsupported quote schemaVersion: ${x?.schemaVersion || 'missing'}. ` +
        `Expected: ${IMAGES_MVP_QUOTE_SCHEMA_VERSION}`
    );
  }
}

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

  const data = await response.json();

  // Validate schema version before returning
  assertQuoteSchemaVersion(data);

  return data;
}

export function createDefaultQuoteOps(): ImagesMvpQuoteOps {
  return {
    embedding: true,
    ocr: false,
    forensics: false,
  };
}
