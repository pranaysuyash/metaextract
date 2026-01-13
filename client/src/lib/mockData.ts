/**
 * MetaExtract Frontend Data
 *
 * Pricing tiers based on forensic value proposition.
 */

// Generate extended fields for demo
const generateExtendedFields = () => {
  const fields: Record<string, any> = {};

  // Canon MakerNote simulation
  for (let i = 1; i <= 2500; i++) {
    const hex = i.toString(16).padStart(4, '0').toUpperCase();
    fields[`Canon MakerNote 0x${hex}`] = `0x${Math.floor(Math.random() * 65536)
      .toString(16)
      .toUpperCase()}`;
  }

  // IPTC Extension simulation
  for (let i = 1; i <= 1500; i++) {
    fields[`IPTC Extension Field ${i}`] =
      `Data Segment ${Math.random().toString(36).substring(7)}`;
  }

  // XMP Raw simulation
  for (let i = 1; i <= 3000; i++) {
    fields[`XMP-crs:RawData-${i}`] = Math.random() > 0.5 ? 'True' : 'False';
  }

  return fields;
};

export const MOCK_METADATA = {
  filename: 'EVIDENCE_IMG_20240515_A74.RAW',
  filesize: '84.2 MB',
  filetype: 'Sony ARW (RAW)',
  created: '2024-05-15T14:23:01.452Z',
  modified: '2024-05-15T14:23:01.452Z',
  hash: 'a1b2c3d4e5f67890abcdef1234567890',

  file_integrity: {
    md5: 'a1b2c3d4e5f67890abcdef1234567890',
    sha256: 'a1b2c3d4e5f67890abcdef1234567890a1b2c3d4e5f67890abcdef1234567890',
  },

  summary: {
    make: 'Sony',
    model: 'Alpha 7 IV',
    serial: '384729104',
    lens: 'FE 24-70mm F2.8 GM II',
    firmware: 'v2.01',
    shutter_count: '14,203',
    capture_time: '2024-05-15 14:23:01.452',
    location: '37.7749° N, 122.4194° W',
  },

  gps: {
    latitude_decimal: 37.7749,
    longitude_decimal: -122.4194,
    latitude_dms: '37° 46\' 29.64" N',
    longitude_dms: '122° 25\' 9.84" W',
    altitude_meters: 52.3,
    coordinates_formatted: '37.774900, -122.419400',
    google_maps_url: 'https://www.google.com/maps?q=37.7749,-122.4194',
  },

  filesystem: {
    size_bytes: 88320000,
    size_human: '84.2 MB',
    created: '2024-05-15T14:23:01.452Z',
    modified: '2024-05-15T14:23:01.452Z',
    accessed: '2024-12-29T10:00:00.000Z',
    permissions_octal: '0644',
    permissions_human: '-rw-r--r--',
    owner: 'user',
    owner_uid: 501,
    group: 'staff',
    group_gid: 20,
    inode: 12345678,
    hard_links: 1,
  },

  calculated: {
    aspect_ratio: '3:2',
    aspect_ratio_decimal: 1.5,
    megapixels: 33.0,
    orientation: 'landscape',
    file_age_days: 228,
    file_age_human: '7 months ago',
    is_modified: false,
    time_between_creation_modification: '0 seconds',
  },

  forensic: {
    Device_Manufacturer: 'Sony',
    Device_Model: 'ILCE-7M4',
    Creation_Timestamp: '2024-05-15T14:23:01.452Z',
    Last_Modified: '2024-05-15T14:23:01.452Z',
    Original_DateTime: '2024:05:15 14:23:01',
    Creation_Software: 'ILCE-7M4 v2.01',
    Device_Serial: '384729104',
    Lens_Serial: '99283711',
    Internal_Serial: 'SN001234567890',
    Firmware: 'v2.01',
    Owner_Name: 'John Doe',
    Artist: 'John Doe Photography',
    Copyright: '© 2024 John Doe',
    Image_Unique_ID: 'a1b2c3d4e5f67890',
  },

  exif: {
    Camera_Make: 'Sony',
    Camera_Model: 'ILCE-7M4',
    Lens_Model: 'FE 24-70mm F2.8 GM II',
    Lens_Make: 'Sony',
    Focal_Length: '35mm',
    Focal_Length_35mm: '35mm',
    F_Number: 'f/2.8',
    Exposure_Time: '1/250s',
    ISO: '100',
    White_Balance: 'Auto',
    Flash: 'Did not fire',
    Metering_Mode: 'Pattern',
    Exposure_Mode: 'Manual',
    Exposure_Program: 'Manual',
    Exposure_Compensation: '0 EV',
    Scene_Type: 'Standard',
    Contrast: 'Normal',
    Saturation: 'Normal',
    Sharpness: 'Normal',
    Digital_Zoom: '1.0',
    Focus_Mode: 'AF-C',
    Image_Stabilization: 'On',
  },

  makernote: {
    _locked: false,
    Sony_ImageWidth: '7008',
    Sony_ImageHeight: '4672',
    Sony_FocusMode: 'AF-C',
    Sony_AFPointSelected: 'Wide',
    Sony_AFPointsUsed: '128',
    Sony_InternalSerialNumber: 'SN001234567890',
    Sony_ShutterCount: '14203',
    Sony_LensType: 'FE 24-70mm F2.8 GM II',
    Sony_DynamicRangeOptimizer: 'Auto',
    Sony_Quality: 'RAW',
    Sony_ColorTemperature: '5500',
    Sony_Brightness: '128',
    Sony_Contrast: 'Normal',
    Sony_Saturation: 'Normal',
  },

  iptc: {
    _locked: false,
    IPTC_Keywords: 'landscape, california, sunset',
    IPTC_Caption: 'Sunset over San Francisco Bay',
    IPTC_Credit: 'John Doe Photography',
    IPTC_Source: 'Original',
    IPTC_Copyright: '© 2024 John Doe',
    IPTC_City: 'San Francisco',
    IPTC_Province: 'California',
    IPTC_Country: 'United States',
  },

  xmp: {
    _locked: false,
    XMP_Creator: 'John Doe',
    XMP_CreateDate: '2024-05-15T14:23:01',
    XMP_ModifyDate: '2024-05-15T14:23:01',
    XMP_Rating: '5',
    XMP_Label: 'Blue',
  },

  extended: generateExtendedFields(),

  locked_fields: [],
};

// ============================================================================
// OBSOLETE: REVISED PRICING - Based on forensic value proposition
// ============================================================================
//
// DEPRECATION NOTICE:
// This PRICING_TIERS object is OBSOLETE and no longer used for the Images MVP launch.
// The Images MVP uses a credit-based pricing model (packs), not tier subscriptions.
//
// This data is preserved for historical reference only.
// Do not use in new code.
//
// Original comment:
// REVISED PRICING - Based on forensic value proposition
//

/*
export const PRICING_TIERS = [
  {
    tier: "enterprise",
    name: "Free",
    price: "FREE",
    period: "",
    tagline: "Evaluate our extraction quality",
    description: "3 files/day, basic web formats only",
    features: [
      "Standard images (JPEG, PNG, GIF, WebP)", 
      "10MB file limit", 
      "Basic EXIF + GPS + Hashes",
      "200-300 fields",
      "3 extractions per day",
      "JSON export"
    ],
    cta: "Start Free",
    recommended: false,
    isPaid: false,
    fieldCount: "200-300"
  },
  {
    tier: "professional",
    name: "Professional",
    price: "$19",
    period: "/mo",
    tagline: "For investigators & photographers",
    description: "All image formats including RAW",
    features: [
      "All image formats + RAW", 
      "100MB file limit",
      "Full EXIF + MakerNotes",
      "IPTC + XMP metadata",
      "2,000+ fields extracted",
      "500 files/month",
      "Forensic analysis",
      "JSON + CSV export",
      "Email support"
    ],
    cta: "Get Professional",
    recommended: false,
    isPaid: true,
    fieldCount: "2,000+"
  },
  {
    tier: "forensic",
    name: "Forensic",
    price: "$49",
    period: "/mo",
    tagline: "Complete forensic toolkit",
    description: "All file types, advanced analysis",
    features: [
      "All file types (Video, Audio, PDF)",
      "500MB file limit",
      "7,000+ fields extracted",
      "Manipulation detection",
      "Timeline reconstruction",
      "Batch processing",
      "API access (5,000 calls/mo)",
      "Priority processing",
      "PDF reports",
      "Priority support"
    ],
    cta: "Go Forensic",
    recommended: true,
    isPaid: true,
    fieldCount: "7,000+"
  },
  {
    tier: "enterprise",
    name: "Enterprise",
    price: "$149",
    period: "/mo",
    tagline: "For agencies & legal teams",
    description: "Unlimited everything + dedicated support",
    features: [
      "Everything in Forensic",
      "2GB file limit",
      "Unlimited API calls",
      "Unlimited files",
      "Custom integrations",
      "Compliance reporting",
      "Dedicated support",
      "SLA guarantee"
    ],
    cta: "Contact Sales",
    recommended: false,
    isPaid: true,
    fieldCount: "7,000+",
    isEnterprise: true
  }
];
*/

// ============================================================================
// OBSOLETE: CREDIT PACKS - Pay-per-use option
// ============================================================================
//
// DEPRECATION NOTICE:
// This CREDIT_PACKS object is OBSOLETE for the Images MVP.
// The MVP uses IMAGES_MVP_CREDIT_PACKS from server/payments.ts instead.
//
// This data is preserved for historical reference only.
// Do not use in new code.
//
// Original comment:
// CREDIT PACKS - Pay-per-use option
//

/*
export const CREDIT_PACKS = [
  {
    id: "single",
    name: "Single",
    credits: 1,
    price: "$2",
    per_credit: "$2.00 per file",
    description: "1 full forensic analysis"
  },
  {
    id: "investigation",
    name: "Investigation",
    credits: 10,
    price: "$15",
    per_credit: "$1.50 per file",
    description: "Perfect for small cases",
    popular: true
  },
  {
    id: "case",
    name: "Case Pack",
    credits: 50,
    price: "$50",
    per_credit: "$1.00 per file",
    description: "Best value for cases"
  },
  {
    id: "agency",
    name: "Agency",
    credits: 200,
    price: "$150",
    per_credit: "$0.75 per file",
    description: "Bulk discount"
  }
];
*/

// ============================================================================
// CREDIT COST EXPLANATION
// ============================================================================

export const CREDIT_EXPLANATION = [
  { action: 'Standard Image (JPG/PNG/GIF/WebP)', cost: '1 Credit' },
  { action: 'RAW Image (CR2/NEF/ARW/DNG/HEIC)', cost: '2 Credits' },
  { action: 'Video File (MP4/MOV/AVI/MKV)', cost: '5 Credits' },
  { action: 'Audio File (MP3/FLAC/WAV/OGG)', cost: '2 Credits' },
  { action: 'PDF Document', cost: '2 Credits' },
  { action: 'SVG File', cost: '1 Credit' },
];

// ============================================================================
// OBSOLETE: FEATURE COMPARISON TABLE DATA
// ============================================================================
//
// DEPRECATION NOTICE:
// This FEATURE_COMPARISON object is OBSOLETE for the Images MVP.
// It was used for the old tier-based pricing UI.
//
// This data is preserved for historical reference only.
// Do not use in new code.
//

/*
export const FEATURE_COMPARISON = {
  categories: [
    {
      name: 'File Support',
      features: [
        {
          name: 'Standard Images (JPEG, PNG, GIF, WebP)',
          free: true,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'RAW Formats (CR2, NEF, ARW, DNG)',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'HEIC/HEIF',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Video (MP4, MOV, AVI, MKV)',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Audio (MP3, FLAC, WAV)',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'PDF Documents',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'SVG Files',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
      ],
    },
    {
      name: 'Metadata Extraction',
      features: [
        {
          name: 'Basic EXIF',
          free: true,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'GPS/Location Data',
          free: true,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'File Integrity Hashes',
          free: true,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Full EXIF (all tags)',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Camera MakerNotes',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'IPTC Metadata',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'XMP Metadata',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Extended Attributes',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Serial Numbers',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
      ],
    },
    {
      name: 'Forensic Analysis',
      features: [
        {
          name: 'Basic Forensics',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Manipulation Detection',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Timeline Reconstruction',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Steganography Detection',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
      ],
    },
    {
      name: 'Processing',
      features: [
        {
          name: 'Single File Upload',
          free: true,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Batch Upload',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'API Access',
          free: false,
          professional: false,
          forensic: '5K/mo',
          enterprise: 'Unlimited',
        },
        {
          name: 'Priority Processing',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
      ],
    },
    {
      name: 'Export & Support',
      features: [
        {
          name: 'JSON Export',
          free: true,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'CSV Export',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'PDF Reports',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Email Support',
          free: false,
          professional: true,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Priority Support',
          free: false,
          professional: false,
          forensic: true,
          enterprise: true,
        },
        {
          name: 'Dedicated Support',
          free: false,
          professional: false,
          forensic: false,
          enterprise: true,
        },
      ],
    },
  ],
};
*/

// ============================================================================
// VALUE PROPOSITIONS
// ============================================================================

export const VALUE_PROPS = [
  {
    icon: 'Database',
    title: '7,000+ Fields',
    description:
      'Extract more metadata than any competitor. We parse proprietary MakerNotes, IPTC, XMP, and codec-specific data.',
  },
  {
    icon: 'Shield',
    title: 'Court-Ready',
    description:
      'File integrity hashes, chain of custody timestamps, and forensic analysis suitable for legal proceedings.',
  },
  {
    icon: 'Zap',
    title: 'Fast Processing',
    description:
      'Sub-second extraction for most files. Batch process hundreds of files with our enterprise-grade infrastructure.',
  },
  {
    icon: 'Lock',
    title: 'Privacy-First',
    description:
      'Files processed in memory, deleted immediately after analysis. No data retention, no third-party sharing.',
  },
];

// ============================================================================
// FAQ DATA
// ============================================================================

export const FAQ_ITEMS = [
  {
    question: 'How is this different from other EXIF viewers?',
    answer:
      "Most EXIF viewers extract 50-200 fields. MetaExtract extracts 7,000+ fields including parsed camera MakerNotes (Canon, Sony, Nikon proprietary data), full IPTC/XMP metadata, video codec parameters, and forensic indicators. We're built for investigators, not casual users.",
  },
  {
    question: 'Is my data safe?',
    answer:
      'Yes. Files are processed in temporary memory and permanently deleted immediately after extraction. We never store your files, and our servers are SOC 2 compliant. For enterprise customers, we offer on-premise deployment.',
  },
  {
    question: "What's the difference between subscriptions and credits?",
    answer:
      'Subscriptions are monthly plans for regular users. Credits are pay-per-use for occasional needs. Credits never expire and include full forensic analysis on any file type. Both options give you access to our complete 7,000+ field extraction.',
  },
  {
    question: 'Can I use this for legal/forensic investigations?',
    answer:
      'Yes. Our Forensic and Enterprise tiers include features specifically designed for investigations: file integrity hashes (MD5, SHA256), manipulation detection, timeline reconstruction, and detailed chain-of-custody metadata. Many law enforcement agencies and legal teams use MetaExtract.',
  },
  {
    question: 'Do you offer API access?',
    answer:
      'Yes. The Forensic tier includes 5,000 API calls per month. Enterprise tier includes unlimited API access. Our REST API supports all extraction features and returns structured JSON.',
  },
  {
    question: 'What file types do you support?',
    answer:
      'Free tier supports standard web images. Professional tier adds RAW formats from all major camera manufacturers. Forensic and Enterprise tiers support everything: video (MP4, MOV, AVI, MKV), audio (MP3, FLAC, WAV), PDF, SVG, and more.',
  },
];
