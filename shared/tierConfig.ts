/**
 * MetaExtract Tier Configuration
 *
 * Pricing based on forensic value proposition:
 * - 7,000+ metadata fields (competitors: 50-200)
 * - Parsed MakerNotes (Canon, Sony, Nikon proprietary data)
 * - Advanced forensic analysis (steganography, manipulation detection)
 * - Court-admissible evidence preservation
 *
 * This is enterprise-grade forensic software, priced accordingly.
 */

export type TierName = 'free' | 'professional' | 'forensic' | 'enterprise';

export interface TierConfig {
  name: TierName;
  displayName: string;
  tagline: string;
  price: number;
  priceLabel: string;
  billingPeriod: 'month' | 'year' | 'one-time';
  allowedFileTypes: string[];
  maxFileSizeMB: number;
  monthlyFileLimit: number | null; // null = unlimited
  dailyFileLimit: number | null; // null = unlimited (for free tier rate limiting)
  apiRequestsPerMonth: number | null;
  features: {
    // Basic extraction
    basicExif: boolean;
    imageProperties: boolean;

    // File integrity
    fileHashes: boolean;
    filesystemMetadata: boolean;

    // Location & Time
    gpsData: boolean;
    calculatedFields: boolean;

    // Advanced metadata
    makerNotes: boolean;
    iptcXmp: boolean;
    extendedAttributes: boolean;
    serialNumbers: boolean;

    // File type support
    rawFormats: boolean;
    videoSupport: boolean;
    audioSupport: boolean;
    pdfSupport: boolean;

    // Forensic features
    forensicAnalysis: boolean;
    manipulationDetection: boolean;
    timelineReconstruction: boolean;

    // Processing features
    batchUpload: boolean;
    apiAccess: boolean;
    priorityProcessing: boolean;

    // Export
    jsonExport: boolean;
    csvExport: boolean;
    pdfReport: boolean;

    // Support
    emailSupport: boolean;
    prioritySupport: boolean;
    dedicatedSupport: boolean;
  };
  fieldCount: string;
  fieldCategories: string[];
  description: string;
}

export const TIER_CONFIGS: Record<TierName, TierConfig> = {
  // =========================================================================
  // FREE - Evaluation Tier
  // =========================================================================
  free: {
    name: 'free',
    displayName: 'Free',
    tagline: 'Evaluate our extraction quality',
    price: 0,
    priceLabel: 'Free',
    billingPeriod: 'month',
    allowedFileTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    maxFileSizeMB: 10,
    monthlyFileLimit: null,
    dailyFileLimit: 3, // 3 files per day for evaluation
    apiRequestsPerMonth: null,
    features: {
      basicExif: true,
      imageProperties: true,
      fileHashes: true,
      filesystemMetadata: false,
      gpsData: true,
      calculatedFields: true,
      makerNotes: false,
      iptcXmp: false,
      extendedAttributes: false,
      serialNumbers: false,
      rawFormats: false,
      videoSupport: false,
      audioSupport: false,
      pdfSupport: false,
      forensicAnalysis: false,
      manipulationDetection: false,
      timelineReconstruction: false,
      batchUpload: false,
      apiAccess: false,
      priorityProcessing: false,
      jsonExport: true,
      csvExport: false,
      pdfReport: false,
      emailSupport: false,
      prioritySupport: false,
      dedicatedSupport: false,
    },
    fieldCount: '200-300',
    fieldCategories: [
      'summary',
      'basic_exif',
      'image',
      'gps',
      'hashes',
      'calculated',
    ],
    description:
      'Basic EXIF + GPS + file hashes. Perfect for evaluation before upgrading.',
  },

  // =========================================================================
  // PROFESSIONAL - Investigator Tier ($19/month)
  // =========================================================================
  professional: {
    name: 'professional',
    displayName: 'Professional',
    tagline: 'For investigators & photographers',
    price: 19,
    priceLabel: '$19/month',
    billingPeriod: 'month',
    allowedFileTypes: [
      // Standard images
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/tiff',
      'image/bmp',
      'image/heic',
      'image/heif',
      'image/svg+xml',
      // RAW formats
      'image/x-canon-cr2',
      'image/x-canon-cr3',
      'image/x-nikon-nef',
      'image/x-nikon-nrw',
      'image/x-sony-arw',
      'image/x-sony-sr2',
      'image/x-adobe-dng',
      'image/x-olympus-orf',
      'image/x-panasonic-rw2',
      'image/x-panasonic-raw',
      'image/x-fuji-raf',
      'image/x-pentax-pef',
      'image/x-leica-rwl',
      'image/x-hasselblad-3fr',
      'image/x-phaseone-iiq',
      // Documents
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation', // .pptx
      'text/plain',
      'text/html',
      'application/json',
      'application/xml',
      'text/csv',
    ],
    maxFileSizeMB: 500, // Increased for convenience
    monthlyFileLimit: 500,
    dailyFileLimit: null,
    apiRequestsPerMonth: null,
    features: {
      basicExif: true,
      imageProperties: true,
      fileHashes: true,
      filesystemMetadata: true,
      gpsData: true,
      calculatedFields: true,
      makerNotes: true,
      iptcXmp: true,
      extendedAttributes: true,
      serialNumbers: true,
      rawFormats: true,
      videoSupport: false,
      audioSupport: false,
      pdfSupport: true,
      forensicAnalysis: true,
      manipulationDetection: false,
      timelineReconstruction: false,
      batchUpload: false,
      apiAccess: false,
      priorityProcessing: false,
      jsonExport: true,
      csvExport: true,
      pdfReport: false,
      emailSupport: true,
      prioritySupport: false,
      dedicatedSupport: false,
    },
    fieldCount: '2,000+',
    fieldCategories: [
      'summary',
      'exif',
      'image',
      'gps',
      'filesystem',
      'hashes',
      'calculated',
      'forensic',
      'makernote',
      'iptc',
      'xmp',
      'extended_attributes',
    ],
    description:
      'Full EXIF + MakerNotes + IPTC/XMP. All image formats including RAW.',
  },

  // =========================================================================
  // FORENSIC - Expert Tier ($49/month)
  // =========================================================================
  forensic: {
    name: 'forensic',
    displayName: 'Forensic',
    tagline: 'Complete forensic analysis toolkit',
    price: 49,
    priceLabel: '$49/month',
    billingPeriod: 'month',
    allowedFileTypes: [
      // All Professional types + Video/Audio + Scientific/Medical
      'image/*',
      'video/*',
      'audio/*',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'text/*',
      'application/json',
      'application/xml',
      'application/zip',
      'application/x-tar',
      'application/x-rar-compressed',
      'application/x-7z-compressed',
      // Medical / Scientific
      'application/dicom',
      'application/fits',
      'application/x-hdf',
      'application/x-netcdf',
      'application/x-shapefile',
      // Emerging Tech
      'application/x-ai-model',
      'application/x-blockchain',
      'application/x-ar-vr',
      'application/x-iot',
      'application/x-quantum',
      'application/x-neural',
      'application/x-robotics',
      'application/x-biotech',
    ],
    maxFileSizeMB: 2000, 
    monthlyFileLimit: null, // Unlimited
    dailyFileLimit: null,
    apiRequestsPerMonth: 5000,
    features: {
      basicExif: true,
      imageProperties: true,
      fileHashes: true,
      filesystemMetadata: true,
      gpsData: true,
      calculatedFields: true,
      makerNotes: true,
      iptcXmp: true,
      extendedAttributes: true,
      serialNumbers: true,
      rawFormats: true,
      videoSupport: true,
      audioSupport: true,
      pdfSupport: true,
      forensicAnalysis: true,
      manipulationDetection: true,
      timelineReconstruction: true,
      batchUpload: true,
      apiAccess: true,
      priorityProcessing: true,
      jsonExport: true,
      csvExport: true,
      pdfReport: true,
      emailSupport: true,
      prioritySupport: true,
      dedicatedSupport: false,
    },
    fieldCount: '7,000+',
    fieldCategories: ['*'],
    description:
      'Complete 7,000+ field extraction. Video, audio, batch processing. API access.',
  },

  // =========================================================================
  // ENTERPRISE - Agency Tier ($149/month)
  // =========================================================================
  enterprise: {
    name: 'enterprise',
    displayName: 'Enterprise',
    tagline: 'For agencies & legal teams',
    price: 149,
    priceLabel: '$149/month',
    billingPeriod: 'month',
    allowedFileTypes: ['*/*'], // All file types
    maxFileSizeMB: 5000, // 5GB
    monthlyFileLimit: null, // Unlimited
    dailyFileLimit: null,
    apiRequestsPerMonth: null, // Unlimited
    features: {
      basicExif: true,
      imageProperties: true,
      fileHashes: true,
      filesystemMetadata: true,
      gpsData: true,
      calculatedFields: true,
      makerNotes: true,
      iptcXmp: true,
      extendedAttributes: true,
      serialNumbers: true,
      rawFormats: true,
      videoSupport: true,
      audioSupport: true,
      pdfSupport: true,
      forensicAnalysis: true,
      manipulationDetection: true,
      timelineReconstruction: true,
      batchUpload: true,
      apiAccess: true,
      priorityProcessing: true,
      jsonExport: true,
      csvExport: true,
      pdfReport: true,
      emailSupport: true,
      prioritySupport: true,
      dedicatedSupport: true,
    },
    fieldCount: '7,000+',
    fieldCategories: ['*'],
    description:
      'Everything in Forensic + unlimited API, 5GB files, dedicated support, compliance reporting.',
  },
};

// ============================================================================
// Legacy tier mapping (for backwards compatibility)
// ============================================================================

export const LEGACY_TIER_MAP: Record<string, TierName> = {
  free: 'free',
  starter: 'professional', // Old starter → new professional
  premium: 'forensic', // Old premium → new forensic
  super: 'enterprise', // Old super → new enterprise
  pro: 'forensic', // Alias
};

export function normalizeTier(tier: string): TierName {
  const normalized = tier.toLowerCase();
  return (
    LEGACY_TIER_MAP[normalized] ||
    (TIER_CONFIGS[normalized as TierName]
      ? (normalized as TierName)
      : 'enterprise')
  );
}

export type PythonTierName = 'free' | 'starter' | 'premium' | 'super';

const PYTHON_TIER_MAP: Record<TierName, PythonTierName> = {
  free: 'free',
  professional: 'starter',
  forensic: 'premium',
  enterprise: 'super',
};

export function toPythonTier(tier: string): PythonTierName {
  const normalizedTier = normalizeTier(tier);
  return PYTHON_TIER_MAP[normalizedTier] || 'super';
}

// ============================================================================
// Helper Functions
// ============================================================================

export function getTierConfig(tier: string): TierConfig {
  const normalizedTier = normalizeTier(tier);
  return TIER_CONFIGS[normalizedTier] || TIER_CONFIGS.free;
}

export function isFileTypeAllowed(tier: string, mimeType: string): boolean {
  const config = getTierConfig(tier);

  // Enterprise allows all
  if (config.allowedFileTypes.includes('*/*')) return true;

  // Check exact match
  if (config.allowedFileTypes.includes(mimeType)) return true;

  // Check wildcard match (e.g., "image/*")
  const typePrefix = mimeType.split('/')[0];
  if (config.allowedFileTypes.includes(`${typePrefix}/*`)) return true;

  // Check if any allowed type matches the subtype
  const subtype = mimeType.split('/')[1];
  return config.allowedFileTypes.some((allowed) => {
    const allowedSubtype = allowed.split('/')[1];
    return allowedSubtype === subtype;
  });
}

export function isFileSizeAllowed(tier: string, sizeBytes: number): boolean {
  const config = getTierConfig(tier);
  const sizeMB = sizeBytes / (1024 * 1024);
  return sizeMB <= config.maxFileSizeMB;
}

export function getRequiredTierForFileType(mimeType: string): TierName {
  // Video requires forensic
  if (mimeType.startsWith('video/')) {
    return 'forensic';
  }

  // Audio and PDF require forensic
  if (mimeType.startsWith('audio/') || mimeType === 'application/pdf') {
    return 'forensic';
  }

  // RAW images require professional
  const rawIndicators = [
    'raw',
    'cr2',
    'cr3',
    'nef',
    'arw',
    'dng',
    'orf',
    'rw2',
    'raf',
    'pef',
    'rwl',
    '3fr',
    'iiq',
  ];
  if (rawIndicators.some((ind) => mimeType.toLowerCase().includes(ind))) {
    return 'professional';
  }

  // HEIC/HEIF requires professional
  if (mimeType.includes('heic') || mimeType.includes('heif')) {
    return 'professional';
  }

  // SVG requires forensic
  if (mimeType === 'image/svg+xml') {
    return 'forensic';
  }

  // Standard images are free
  return 'free';
}

export function canAccessFeature(
  tier: string,
  feature: keyof TierConfig['features']
): boolean {
  const config = getTierConfig(tier);
  return config.features[feature] === true;
}

// ============================================================================
// Field Category Labels
// ============================================================================

export const TIER_FIELD_LABELS: Record<string, string> = {
  summary: 'File Summary',
  basic_exif: 'Basic EXIF',
  exif: 'Full EXIF Data',
  image: 'Image Properties',
  gps: 'GPS/Location Data',
  filesystem: 'Filesystem Metadata',
  hashes: 'File Integrity (Hashes)',
  calculated: 'Calculated Fields',
  forensic: 'Forensic Evidence',
  makernote: 'Camera MakerNotes',
  iptc: 'IPTC Metadata',
  xmp: 'XMP Metadata',
  video: 'Video Properties',
  audio: 'Audio Properties',
  pdf: 'PDF Document Info',
  svg: 'SVG Metadata',
  extended_attributes: 'Extended Attributes',
};

// ============================================================================
// Credit Costs (for pay-per-use)
// ============================================================================

export const CREDIT_COSTS: Record<string, number> = {
  // Standard images
  'image/jpeg': 1,
  'image/png': 1,
  'image/gif': 1,
  'image/webp': 1,
  'image/bmp': 1,
  'image/tiff': 1,

  // RAW images (more processing)
  'image/heic': 2,
  'image/heif': 2,
  'image/x-canon-cr2': 2,
  'image/x-canon-cr3': 2,
  'image/x-nikon-nef': 2,
  'image/x-sony-arw': 2,
  'image/x-adobe-dng': 2,
  'image/x-olympus-orf': 2,
  'image/x-panasonic-rw2': 2,
  'image/x-fuji-raf': 2,

  // Video (heavy processing)
  'video/mp4': 5,
  'video/quicktime': 5,
  'video/x-msvideo': 5,
  'video/webm': 5,
  'video/x-matroska': 5,

  // Audio
  'audio/mpeg': 2,
  'audio/wav': 2,
  'audio/flac': 2,
  'audio/ogg': 2,

  // Documents
  'application/pdf': 2,
  'image/svg+xml': 1,

  // Default
  default: 2,
};

export function getCreditCost(mimeType: string): number {
  return CREDIT_COSTS[mimeType] || CREDIT_COSTS['default'];
}

// ============================================================================
// Credit Pack Definitions
// ============================================================================

export interface CreditPack {
  id: string;
  name: string;
  credits: number;
  price: number;
  priceDisplay: string;
  pricePerCredit: string;
  description: string;
  popular?: boolean;
}

export const CREDIT_PACKS: CreditPack[] = [
  {
    id: 'single',
    name: 'Single Analysis',
    credits: 1,
    price: 200, // $2.00 in cents
    priceDisplay: '$2',
    pricePerCredit: '$2.00/file',
    description: '1 full forensic analysis',
  },
  {
    id: 'investigation',
    name: 'Investigation Pack',
    credits: 10,
    price: 1500, // $15.00
    priceDisplay: '$15',
    pricePerCredit: '$1.50/file',
    description: '10 file analyses - perfect for small cases',
    popular: true,
  },
  {
    id: 'case',
    name: 'Case Pack',
    credits: 50,
    price: 5000, // $50.00
    priceDisplay: '$50',
    pricePerCredit: '$1.00/file',
    description: '50 file analyses - best value',
  },
  {
    id: 'agency',
    name: 'Agency Pack',
    credits: 200,
    price: 15000, // $150.00
    priceDisplay: '$150',
    pricePerCredit: '$0.75/file',
    description: '200 file analyses - bulk discount',
  },
];

// ============================================================================
// Rate Limiting Configuration
// ============================================================================

export interface RateLimitConfig {
  maxRequestsPerMinute: number;
  maxRequestsPerHour: number;
  maxRequestsPerDay: number;
}

export const RATE_LIMITS: Record<TierName, RateLimitConfig> = {
  free: {
    maxRequestsPerMinute: 3,
    maxRequestsPerHour: 10,
    maxRequestsPerDay: 3, // Matches dailyFileLimit
  },
  professional: {
    maxRequestsPerMinute: 10,
    maxRequestsPerHour: 100,
    maxRequestsPerDay: 500, // Matches monthlyFileLimit / 30
  },
  forensic: {
    maxRequestsPerMinute: 30,
    maxRequestsPerHour: 500,
    maxRequestsPerDay: 5000,
  },
  enterprise: {
    maxRequestsPerMinute: 100,
    maxRequestsPerHour: 2000,
    maxRequestsPerDay: 50000,
  },
};

// Field count by tier for UI display
export const TIER_FIELD_COUNTS: Record<TierName, number> = {
  free: 200,
  professional: 1000,
  forensic: 15000,
  enterprise: 45000, // configurable goal; update as targets evolve
};

// Alias for backwards compatibility
export const fieldsPerFile = TIER_FIELD_COUNTS;

export function getRateLimits(tier: string): {
  requestsPerMinute: number;
  requestsPerDay: number;
} {
  const normalizedTier = normalizeTier(tier);
  const limits = RATE_LIMITS[normalizedTier] || RATE_LIMITS.free;
  return {
    requestsPerMinute: limits.maxRequestsPerMinute,
    requestsPerDay: limits.maxRequestsPerDay,
  };
}
