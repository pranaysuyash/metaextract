/**
 * Metadata Category Definitions
 * 
 * Logical grouping of metadata fields to reduce overwhelm and improve
 * navigation for users exploring 7,000+ metadata fields.
 */

import { 
  Camera, 
  MapPin, 
  HardDrive, 
  Settings, 
  Palette, 
  FileText, 
  Edit3, 
  Shield, 
  Wrench,
  LucideIcon
} from 'lucide-react';

export interface CategoryDefinition {
  /** Internal category key */
  key: string;
  
  /** Display name shown to users */
  displayName: string;
  
  /** Icon component */
  icon: LucideIcon;
  
  /** Brief description of what's in this category */
  description: string;
  
  /** Field key patterns that belong to this category */
  fieldPatterns: string[];
  
  /** Whether this category should be expanded by default */
  expandedByDefault: boolean;
  
  /** Priority order (lower = shown higher in list) */
  priority: number;
}

/**
 * Logical category definitions for metadata organization
 */
export const METADATA_CATEGORIES: CategoryDefinition[] = [
  {
    key: 'capture',
    displayName: '📷 Capture Settings',
    icon: Camera,
    description: 'Camera settings when photo was taken',
    fieldPatterns: [
      'iso', 'aperture', 'fnumber', 'shutterspeed', 'exposuretime',
      'focallength', 'flash', 'meteringmode', 'exposuremode',
      'exposurecompensation', 'brightness', 'contrast', 'saturation',
      'sharpness', 'scenetype', 'lightsource'
    ],
    expandedByDefault: true,
    priority: 1
  },
  {
    key: 'location',
    displayName: '📍 Location & Time',
    icon: MapPin,
    description: 'When and where the photo was taken',
    fieldPatterns: [
      'gps', 'latitude', 'longitude', 'altitude', 'datetime',
      'date', 'time', 'timezone', 'location', 'city', 'country',
      'datetimeoriginal', 'createdate', 'modifydate'
    ],
    expandedByDefault: true,
    priority: 2
  },
  {
    key: 'file',
    displayName: '💾 File Information',
    icon: HardDrive,
    description: 'File properties and technical details',
    fieldPatterns: [
      'filesize', 'filename', 'filetype', 'mimetype', 'extension',
      'width', 'height', 'dimension', 'resolution', 'bitdepth',
      'compression', 'encoding', 'format'
    ],
    expandedByDefault: true,
    priority: 3
  },
  {
    key: 'camera',
    displayName: '🔧 Camera & Lens Details',
    icon: Settings,
    description: 'Equipment used to capture the image',
    fieldPatterns: [
      'make', 'model', 'serialnumber', 'lens', 'lensmodel',
      'lensmake', 'lensserial', 'firmware', 'software',
      'orientation', 'cameraserialnumber', 'internalserialnumber',
      'shuttercount', 'imagecount'
    ],
    expandedByDefault: false,
    priority: 4
  },
  {
    key: 'color',
    displayName: '🎨 Color & Processing',
    icon: Palette,
    description: 'Color profiles and in-camera processing',
    fieldPatterns: [
      'colorspace', 'whitebalance', 'colortemperature', 'tint',
      'icc', 'profile', 'gamma', 'colormatrix', 'calibration',
      'renderingintent', 'chromaticity'
    ],
    expandedByDefault: false,
    priority: 5
  },
  {
    key: 'professional',
    displayName: '📝 Professional Metadata',
    icon: FileText,
    description: 'IPTC, keywords, copyright, and captions',
    fieldPatterns: [
      'iptc', 'keyword', 'caption', 'description', 'title',
      'copyright', 'artist', 'creator', 'credit', 'byline',
      'headline', 'instructions', 'category', 'subject',
      'usageterms', 'rights'
    ],
    expandedByDefault: false,
    priority: 6
  },
  {
    key: 'editing',
    displayName: '✏️ Edit History',
    icon: Edit3,
    description: 'Software edits and modification history',
    fieldPatterns: [
      'xmp', 'history', 'photoshop', 'lightroom', 'edited',
      'software', 'application', 'creator', 'processingdate',
      'historyaction', 'historyparameters', 'rawfilename',
      'derivedfrom', 'documentid'
    ],
    expandedByDefault: false,
    priority: 7
  },
  {
    key: 'security',
    displayName: '🔐 Security & Integrity',
    icon: Shield,
    description: 'File hashes and verification',
    fieldPatterns: [
      'md5', 'sha', 'hash', 'checksum', 'signature',
      'certificate', 'encryption', 'verified'
    ],
    expandedByDefault: false,
    priority: 8
  },
  {
    key: 'advanced',
    displayName: '⚙️ Advanced Technical',
    icon: Wrench,
    description: 'MakerNotes and low-level technical data',
    fieldPatterns: [
      'makernote', 'exif', 'subifd', 'ifd', 'tag',
      'binary', 'hex', 'raw', 'proprietary', 'vendor',
      'canon', 'nikon', 'sony', 'fuji', 'olympus'
    ],
    expandedByDefault: false,
    priority: 9
  }
];

/**
 * Categorize a metadata field based on its key
 */
export function categorizeField(fieldKey: string): string {
  const normalizedKey = fieldKey.toLowerCase();
  
  // Find matching category
  for (const category of METADATA_CATEGORIES) {
    for (const pattern of category.fieldPatterns) {
      if (normalizedKey.includes(pattern)) {
        return category.key;
      }
    }
  }
  
  // Default to advanced if no match
  return 'advanced';
}

/**
 * Get category definition by key
 */
export function getCategoryDefinition(key: string): CategoryDefinition | undefined {
  return METADATA_CATEGORIES.find(cat => cat.key === key);
}

/**
 * Get default expanded categories
 */
export function getDefaultExpandedCategories(): string[] {
  return METADATA_CATEGORIES
    .filter(cat => cat.expandedByDefault)
    .map(cat => cat.key);
}

/**
 * Sort categories by priority
 */
export function sortCategories(categoryKeys: string[]): string[] {
  return categoryKeys.sort((a, b) => {
    const catA = getCategoryDefinition(a);
    const catB = getCategoryDefinition(b);
    if (!catA || !catB) return 0;
    return catA.priority - catB.priority;
  });
}

/**
 * Group metadata fields by category
 */
export function groupFieldsByCategory(
  fields: Record<string, any>
): Record<string, Record<string, any>> {
  const grouped: Record<string, Record<string, any>> = {};
  
  // Initialize all categories
  METADATA_CATEGORIES.forEach(cat => {
    grouped[cat.key] = {};
  });
  
  // Assign fields to categories
  Object.entries(fields).forEach(([key, value]) => {
    const category = categorizeField(key);
    grouped[category][key] = value;
  });
  
  // Remove empty categories
  Object.keys(grouped).forEach(key => {
    if (Object.keys(grouped[key]).length === 0) {
      delete grouped[key];
    }
  });
  
  return grouped;
}
