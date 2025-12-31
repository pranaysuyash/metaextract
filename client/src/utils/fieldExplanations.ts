/**
 * Metadata Field Explanations
 * 
 * Human-readable explanations for technical metadata terms
 * to help users understand what each field means.
 */

export interface FieldExplanation {
  /** Short title for the field */
  title: string;
  
  /** Brief description (1-2 sentences) */
  description: string;
  
  /** Detailed explanation with examples */
  details?: string[];
  
  /** Related fields */
  relatedFields?: string[];
  
  /** Common use cases */
  useCases?: string[];
}

/**
 * Comprehensive metadata term explanations
 */
export const FIELD_EXPLANATIONS: Record<string, FieldExplanation> = {
  // ============================================================================
  // Basic Camera/EXIF Terms
  // ============================================================================
  
  'EXIF': {
    title: 'Basic Camera Settings',
    description: 'Exchangeable Image File Format - standard metadata embedded by cameras and smartphones.',
    details: [
      'Contains technical shooting parameters',
      'Automatically added by camera at time of capture',
      'Includes ISO, aperture, shutter speed, focal length'
    ],
    useCases: [
      'Verify camera settings for photography analysis',
      'Confirm photo authenticity',
      'Learn from other photographers\' settings'
    ]
  },
  
  'ISO': {
    title: 'Light Sensitivity',
    description: 'Camera sensor sensitivity to light. Higher ISO = brighter photos in low light, but more noise.',
    details: [
      'ISO 100-200: Bright daylight',
      'ISO 400-800: Indoor/cloudy',
      'ISO 1600+: Low light/night'
    ]
  },
  
  'Aperture': {
    title: 'Lens Opening Size',
    description: 'Size of the lens opening (f-stop). Lower f-number = larger opening = blurrier background.',
    details: [
      'f/1.4-f/2.8: Wide open, shallow depth of field (blurry background)',
      'f/5.6-f/8: Balanced depth',
      'f/11-f/22: Everything in focus'
    ]
  },
  
  'ShutterSpeed': {
    title: 'Exposure Duration',
    description: 'How long the camera sensor is exposed to light. Faster speeds freeze motion.',
    details: [
      '1/1000s or faster: Freeze fast action (sports)',
      '1/60s - 1/250s: General photography',
      '1s or slower: Light trails, smooth water (requires tripod)'
    ]
  },
  
  'FocalLength': {
    title: 'Lens Zoom Level',
    description: 'Optical zoom setting. Lower = wider view, Higher = more zoomed in.',
    details: [
      '14-35mm: Wide angle (landscapes, architecture)',
      '50mm: Standard (similar to human eye)',
      '70-200mm: Telephoto (portraits, wildlife)',
      '300mm+: Super telephoto (sports, astronomy)'
    ]
  },
  
  // ============================================================================
  // Advanced Metadata
  // ============================================================================
  
  'MakerNote': {
    title: 'Camera Manufacturer Data',
    description: 'Proprietary metadata specific to camera brand (Canon, Nikon, Sony, etc.).',
    details: [
      'Contains brand-specific features and settings',
      'Autofocus points used in the shot',
      'Image processing settings',
      'Lens calibration data',
      'Camera serial number',
      'Shutter count (total photos taken with camera)'
    ],
    useCases: [
      'Forensic analysis: Link photos to specific camera',
      'Equipment verification',
      'Professional photography workflow optimization'
    ],
    relatedFields: ['SerialNumber', 'InternalSerialNumber', 'ShutterCount']
  },
  
  'IPTC': {
    title: 'Professional Photo Metadata',
    description: 'International Press Telecommunications Council standard for photo information.',
    details: [
      'Added by photographers/editors, not camera',
      'Caption and headline',
      'Keywords for searchability',
      'Copyright and licensing',
      'Credit and byline',
      'Location: city, state, country',
      'Creation date and time'
    ],
    useCases: [
      'Photo agencies and stock photography',
      'Journalism: verify photo source and attribution',
      'Copyright protection',
      'Media asset management'
    ],
    relatedFields: ['Caption', 'Keywords', 'Copyright', 'Byline', 'Credit']
  },
  
  'XMP': {
    title: 'Editing Software Metadata',
    description: 'Extensible Metadata Platform - tracks photo editing history from Adobe software.',
    details: [
      'Records all Lightroom/Photoshop adjustments',
      'Edit history with timestamps',
      'Software version used',
      'Rating and color labels',
      'Hierarchical keywords',
      'Camera Raw settings'
    ],
    useCases: [
      'Detect photo manipulation',
      'Verify editing software used',
      'Understand post-processing workflow',
      'Forensic timeline reconstruction'
    ],
    relatedFields: ['Software', 'ModifyDate', 'HistoryAction']
  },
  
  // ============================================================================
  // Location & Time
  // ============================================================================
  
  'GPS': {
    title: 'Location Coordinates',
    description: 'Geographic coordinates where photo was taken (if camera/phone has GPS enabled).',
    details: [
      'Latitude and longitude',
      'Altitude above sea level',
      'Direction camera was facing',
      'Timestamp from GPS satellites'
    ],
    useCases: [
      'Photo geotagging for travel memories',
      'Journalism: verify location of events',
      'Forensic investigation',
      'Privacy concern: remove before sharing online'
    ],
    relatedFields: ['GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'GPSImgDirection']
  },
  
  'DateTimeOriginal': {
    title: 'Photo Capture Time',
    description: 'Exact date and time when photo was taken (from camera clock).',
    details: [
      'Set by camera internal clock',
      'May be inaccurate if clock not set correctly',
      'Different from file modification date'
    ],
    useCases: [
      'Photo organization by capture date',
      'Timeline reconstruction',
      'Verify when event occurred'
    ]
  },
  
  // ============================================================================
  // File Integrity
  // ============================================================================
  
  'MD5': {
    title: 'File Fingerprint (MD5)',
    description: 'Unique cryptographic hash to verify file has not been altered.',
    details: [
      '128-bit hash value',
      'Even tiny change produces completely different hash',
      'Used for file integrity verification'
    ],
    useCases: [
      'Verify file has not been modified',
      'Detect duplicate files',
      'Chain of custody for legal evidence'
    ],
    relatedFields: ['SHA256', 'SHA1', 'CRC32']
  },
  
  'SHA256': {
    title: 'File Fingerprint (SHA-256)',
    description: 'Cryptographically secure hash for file integrity verification (stronger than MD5).',
    details: [
      '256-bit hash value',
      'Industry standard for security',
      'Virtually impossible to create fake file with same hash'
    ],
    useCases: [
      'Legal evidence preservation',
      'Verify file authenticity',
      'Blockchain/digital asset verification'
    ]
  },
  
  // ============================================================================
  // Image Properties
  // ============================================================================
  
  'ColorSpace': {
    title: 'Color Profile',
    description: 'Color range used in the image. sRGB (standard) vs Adobe RGB (wider range).',
    details: [
      'sRGB: Standard for web and most displays',
      'Adobe RGB: Professional printing, wider color gamut',
      'ProPhoto RGB: Maximum color range for editing'
    ]
  },
  
  'WhiteBalance': {
    title: 'Color Temperature',
    description: 'Color adjustment to make whites appear neutral under different lighting.',
    details: [
      'Daylight: ~5500K (neutral)',
      'Tungsten: ~3200K (warm/orange light)',
      'Fluorescent: ~4000K (cool light)',
      'Auto: Camera decides'
    ]
  },
  
  'BitDepth': {
    title: 'Color Depth',
    description: 'Number of bits per color channel. Higher = more colors and smoother gradients.',
    details: [
      '8-bit: 16.7 million colors (JPEG standard)',
      '12-bit: 68 billion colors (most RAW files)',
      '14-bit: 4.4 trillion colors (high-end cameras)',
      '16-bit: Maximum editing flexibility'
    ]
  },
  
  // ============================================================================
  // Medical/Scientific
  // ============================================================================
  
  'DICOM': {
    title: 'Medical Imaging Standard',
    description: 'Digital Imaging and Communications in Medicine - standard for medical scan files.',
    details: [
      'Contains patient information',
      'Study and series metadata',
      'Equipment and scan parameters',
      'Image properties (slice thickness, pixel spacing)',
      'Used by X-ray, CT, MRI, ultrasound equipment'
    ],
    useCases: [
      'Medical diagnosis and analysis',
      'Research and clinical trials',
      'Quality assurance',
      'Equipment verification'
    ]
  },
  
  'Modality': {
    title: 'Scan Type',
    description: 'Type of medical imaging used (X-ray, CT, MRI, Ultrasound, etc.).',
    details: [
      'CR: Computed Radiography (X-ray)',
      'CT: Computed Tomography',
      'MR: Magnetic Resonance Imaging',
      'US: Ultrasound',
      'PET: Positron Emission Tomography'
    ]
  },
  
  'FITS': {
    title: 'Astronomy Data Format',
    description: 'Flexible Image Transport System - standard for astronomical data.',
    details: [
      'Header keywords with observation parameters',
      'World Coordinate System (WCS)',
      'Telescope and instrument info',
      'Observation date/time and exposure'
    ]
  },
  
  // ============================================================================
  // Forensic Fields
  // ============================================================================
  
  'Thumbnail': {
    title: 'Embedded Preview Image',
    description: 'Small preview image embedded in file metadata.',
    details: [
      'Can be different from main image if edited',
      'Forensic analysis: compare thumbnail to main image',
      'May contain original image if photo was cropped'
    ],
    useCases: [
      'Detect if image was edited/cropped',
      'Recover original uncropped photo'
    ]
  },
  
  'Software': {
    title: 'Editing Software Used',
    description: 'Name and version of software used to create or edit the file.',
    details: [
      'Camera firmware version if unedited',
      'Adobe Photoshop, Lightroom if edited',
      'Can reveal if image was manipulated'
    ],
    useCases: [
      'Detect photo editing',
      'Verify software version',
      'Forensic investigation'
    ]
  },
  
  'HistoryAction': {
    title: 'Edit History',
    description: 'Log of editing operations performed on the image.',
    details: [
      'Timestamps of each edit',
      'Operations performed (crop, adjust, filter)',
      'Software and tools used',
      'Can be removed by "Save As"'
    ],
    useCases: [
      'Detect photo manipulation',
      'Timeline of editing',
      'Verify authenticity'
    ]
  }
};

/**
 * Get explanation for a metadata field
 */
export function getFieldExplanation(fieldName: string): FieldExplanation | null {
  // Direct match
  if (FIELD_EXPLANATIONS[fieldName]) {
    return FIELD_EXPLANATIONS[fieldName];
  }
  
  // Fuzzy match (case-insensitive, partial)
  const normalizedField = fieldName.toLowerCase();
  
  for (const [key, explanation] of Object.entries(FIELD_EXPLANATIONS)) {
    if (normalizedField.includes(key.toLowerCase()) || key.toLowerCase().includes(normalizedField)) {
      return explanation;
    }
  }
  
  return null;
}

/**
 * Check if field has an explanation available
 */
export function hasExplanation(fieldName: string): boolean {
  return getFieldExplanation(fieldName) !== null;
}

/**
 * Get category-level explanations
 */
export const CATEGORY_EXPLANATIONS: Record<string, FieldExplanation> = {
  'exif': FIELD_EXPLANATIONS['EXIF'],
  'makernote': FIELD_EXPLANATIONS['MakerNote'],
  'iptc': FIELD_EXPLANATIONS['IPTC'],
  'xmp': FIELD_EXPLANATIONS['XMP'],
  'gps': FIELD_EXPLANATIONS['GPS'],
  'dicom': FIELD_EXPLANATIONS['DICOM'],
  'fits': FIELD_EXPLANATIONS['FITS']
};
