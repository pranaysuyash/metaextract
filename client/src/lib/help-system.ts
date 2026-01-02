/**
 * Comprehensive Help and Documentation System
 * 
 * Provides contextual tooltips, help content, metadata field descriptions,
 * and searchable help documentation.
 * 
 * @module help-system
 * @validates Requirements 2.6, 3.3 - Contextual help and metadata documentation
 */

// ============================================================================
// Types
// ============================================================================

export interface HelpTopic {
  /** Unique identifier */
  id: string;
  /** Display title */
  title: string;
  /** Short description for tooltips */
  shortDescription: string;
  /** Full description for help panels */
  fullDescription: string;
  /** Related topics */
  relatedTopics?: string[];
  /** Keywords for search */
  keywords: string[];
  /** Category for grouping */
  category: HelpCategory;
  /** Link to external documentation */
  externalLink?: string;
}

export type HelpCategory = 
  | 'getting-started'
  | 'upload'
  | 'metadata'
  | 'analysis'
  | 'export'
  | 'account'
  | 'pricing'
  | 'security'
  | 'troubleshooting';

export interface MetadataFieldDoc {
  /** Field name/key */
  field: string;
  /** Human-readable label */
  label: string;
  /** Description of what this field contains */
  description: string;
  /** Example value */
  example?: string;
  /** Data type */
  type: 'string' | 'number' | 'date' | 'boolean' | 'array' | 'object';
  /** Category this field belongs to */
  category: MetadataCategory;
  /** Whether this is a common/important field */
  common?: boolean;
  /** Technical standard this field comes from */
  standard?: string;
}

export type MetadataCategory =
  | 'basic'
  | 'camera'
  | 'location'
  | 'datetime'
  | 'technical'
  | 'color'
  | 'copyright'
  | 'software'
  | 'forensic'
  | 'audio'
  | 'video'
  | 'document';

// ============================================================================
// Help Topics Database
// ============================================================================

export const helpTopics: Record<string, HelpTopic> = {
  // Getting Started
  'getting-started': {
    id: 'getting-started',
    title: 'Getting Started',
    shortDescription: 'Learn the basics of metadata extraction',
    fullDescription: 'MetaExtract helps you extract and analyze metadata from images, documents, and media files. Simply upload a file to see all the hidden information it contains, including camera settings, location data, timestamps, and more.',
    relatedTopics: ['upload-file', 'supported-formats', 'metadata-basics'],
    keywords: ['start', 'begin', 'intro', 'introduction', 'basics', 'how to'],
    category: 'getting-started',
  },
  'upload-file': {
    id: 'upload-file',
    title: 'Uploading Files',
    shortDescription: 'How to upload files for analysis',
    fullDescription: 'Drag and drop files onto the upload zone, or click to browse. You can upload multiple files at once. Supported formats include JPEG, PNG, TIFF, PDF, MP4, and many more.',
    relatedTopics: ['supported-formats', 'file-limits'],
    keywords: ['upload', 'drag', 'drop', 'file', 'browse', 'select'],
    category: 'upload',
  },
  'supported-formats': {
    id: 'supported-formats',
    title: 'Supported File Formats',
    shortDescription: 'List of supported file types',
    fullDescription: 'We support over 100 file formats including: Images (JPEG, PNG, TIFF, RAW, HEIC), Documents (PDF, DOCX, XLSX), Audio (MP3, WAV, FLAC), Video (MP4, MOV, AVI), and many specialized formats.',
    relatedTopics: ['upload-file', 'file-limits'],
    keywords: ['format', 'type', 'extension', 'jpeg', 'png', 'pdf', 'mp4', 'supported'],
    category: 'upload',
    externalLink: '/docs/supported-formats',
  },
  'file-limits': {
    id: 'file-limits',
    title: 'File Size Limits',
    shortDescription: 'Maximum file sizes by plan',
    fullDescription: 'Free tier: 10MB per file. Pro tier: 100MB per file. Enterprise: 1GB per file. Batch uploads are limited to 10 files at a time on Free, 50 on Pro, and unlimited on Enterprise.',
    relatedTopics: ['pricing', 'upload-file'],
    keywords: ['size', 'limit', 'maximum', 'mb', 'gb', 'large'],
    category: 'upload',
  },

  // Metadata Topics
  'metadata-basics': {
    id: 'metadata-basics',
    title: 'Understanding Metadata',
    shortDescription: 'What is metadata and why it matters',
    fullDescription: 'Metadata is data about data. For images, this includes when and where a photo was taken, camera settings, and editing history. Understanding metadata helps with organization, verification, and forensic analysis.',
    relatedTopics: ['exif-data', 'iptc-data', 'xmp-data'],
    keywords: ['metadata', 'what is', 'understand', 'basics', 'definition'],
    category: 'metadata',
  },
  'exif-data': {
    id: 'exif-data',
    title: 'EXIF Data',
    shortDescription: 'Camera and technical image data',
    fullDescription: 'EXIF (Exchangeable Image File Format) contains technical information recorded by cameras: aperture, shutter speed, ISO, focal length, GPS coordinates, date/time, and camera model.',
    relatedTopics: ['metadata-basics', 'iptc-data'],
    keywords: ['exif', 'camera', 'technical', 'settings', 'photo'],
    category: 'metadata',
    externalLink: '/docs/exif',
  },
  'iptc-data': {
    id: 'iptc-data',
    title: 'IPTC Data',
    shortDescription: 'Editorial and copyright information',
    fullDescription: 'IPTC (International Press Telecommunications Council) metadata includes editorial information: captions, keywords, copyright, creator credits, and usage rights.',
    relatedTopics: ['metadata-basics', 'exif-data'],
    keywords: ['iptc', 'editorial', 'caption', 'keywords', 'press'],
    category: 'metadata',
  },
  'xmp-data': {
    id: 'xmp-data',
    title: 'XMP Data',
    shortDescription: 'Adobe extensible metadata',
    fullDescription: 'XMP (Extensible Metadata Platform) is Adobe\'s standard for embedding metadata. It can store editing history, ratings, labels, and custom metadata fields.',
    relatedTopics: ['metadata-basics', 'iptc-data'],
    keywords: ['xmp', 'adobe', 'extensible', 'editing', 'history'],
    category: 'metadata',
  },

  // Analysis Topics
  'forensic-analysis': {
    id: 'forensic-analysis',
    title: 'Forensic Analysis',
    shortDescription: 'Detect image manipulation and authenticity',
    fullDescription: 'Our forensic tools analyze images for signs of manipulation: ELA (Error Level Analysis), clone detection, metadata inconsistencies, and compression artifacts.',
    relatedTopics: ['ela-analysis', 'metadata-basics'],
    keywords: ['forensic', 'manipulation', 'fake', 'authentic', 'detect', 'analysis'],
    category: 'analysis',
  },
  'ela-analysis': {
    id: 'ela-analysis',
    title: 'Error Level Analysis (ELA)',
    shortDescription: 'Detect edited regions in images',
    fullDescription: 'ELA highlights areas that have been resaved at different quality levels, which can indicate editing. Edited regions often show different error levels than the original image.',
    relatedTopics: ['forensic-analysis'],
    keywords: ['ela', 'error level', 'editing', 'detection', 'quality'],
    category: 'analysis',
  },

  // Export Topics
  'export-results': {
    id: 'export-results',
    title: 'Exporting Results',
    shortDescription: 'Download your analysis results',
    fullDescription: 'Export your metadata analysis in multiple formats: JSON for developers, CSV for spreadsheets, PDF for reports, or XML for archival purposes.',
    relatedTopics: ['json-export'],
    keywords: ['export', 'download', 'save', 'json', 'csv', 'pdf'],
    category: 'export',
  },
  'json-export': {
    id: 'json-export',
    title: 'JSON Export',
    shortDescription: 'Machine-readable metadata export',
    fullDescription: 'JSON export provides the complete metadata in a structured format ideal for developers, APIs, and automated processing.',
    relatedTopics: ['export-results'],
    keywords: ['json', 'export', 'developer', 'api', 'structured'],
    category: 'export',
  },

  // Account Topics
  'account-settings': {
    id: 'account-settings',
    title: 'Account Settings',
    shortDescription: 'Manage your account preferences',
    fullDescription: 'Update your profile, change password, manage API keys, view usage statistics, and configure notification preferences.',
    relatedTopics: ['api-keys'],
    keywords: ['account', 'settings', 'profile', 'preferences', 'password'],
    category: 'account',
  },
  'api-keys': {
    id: 'api-keys',
    title: 'API Keys',
    shortDescription: 'Manage your API access keys',
    fullDescription: 'Generate and manage API keys for programmatic access to MetaExtract. Each key can have specific permissions and rate limits.',
    relatedTopics: ['account-settings'],
    keywords: ['api', 'key', 'token', 'access', 'programmatic'],
    category: 'account',
    externalLink: '/docs/api',
  },

  // Pricing Topics
  'pricing': {
    id: 'pricing',
    title: 'Pricing Plans',
    shortDescription: 'Compare our pricing tiers',
    fullDescription: 'Choose from Free, Pro, or Enterprise plans. Each tier offers different file limits, features, and support levels. Upgrade anytime to unlock more capabilities.',
    relatedTopics: ['file-limits'],
    keywords: ['pricing', 'plan', 'tier', 'cost', 'free', 'pro', 'enterprise'],
    category: 'pricing',
    externalLink: '/#pricing',
  },

  // Security Topics
  'data-privacy': {
    id: 'data-privacy',
    title: 'Data Privacy',
    shortDescription: 'How we protect your data',
    fullDescription: 'Your files are processed securely and deleted immediately after analysis. We never store your files or share your data. All transfers are encrypted with TLS 1.3.',
    keywords: ['privacy', 'data', 'security', 'delete', 'encrypt', 'gdpr'],
    category: 'security',
  },

  // Troubleshooting
  'upload-failed': {
    id: 'upload-failed',
    title: 'Upload Failed',
    shortDescription: 'Troubleshoot upload issues',
    fullDescription: 'If your upload fails, check: file size limits, supported formats, internet connection, and browser compatibility. Try refreshing the page or using a different browser.',
    relatedTopics: ['file-limits', 'supported-formats'],
    keywords: ['upload', 'failed', 'error', 'problem', 'troubleshoot'],
    category: 'troubleshooting',
  },
};

// ============================================================================
// Metadata Field Documentation
// ============================================================================

export const metadataFieldDocs: Record<string, MetadataFieldDoc> = {
  // Basic Fields
  'fileName': {
    field: 'fileName',
    label: 'File Name',
    description: 'The name of the file as stored on disk',
    example: 'IMG_2024.jpg',
    type: 'string',
    category: 'basic',
    common: true,
  },
  'fileSize': {
    field: 'fileSize',
    label: 'File Size',
    description: 'The size of the file in bytes',
    example: '2457600',
    type: 'number',
    category: 'basic',
    common: true,
  },
  'mimeType': {
    field: 'mimeType',
    label: 'MIME Type',
    description: 'The media type identifier for the file format',
    example: 'image/jpeg',
    type: 'string',
    category: 'basic',
    common: true,
  },
  'imageWidth': {
    field: 'imageWidth',
    label: 'Image Width',
    description: 'Width of the image in pixels',
    example: '4032',
    type: 'number',
    category: 'basic',
    common: true,
  },
  'imageHeight': {
    field: 'imageHeight',
    label: 'Image Height',
    description: 'Height of the image in pixels',
    example: '3024',
    type: 'number',
    category: 'basic',
    common: true,
  },

  // Camera Fields
  'make': {
    field: 'make',
    label: 'Camera Make',
    description: 'The manufacturer of the camera or device',
    example: 'Apple',
    type: 'string',
    category: 'camera',
    common: true,
    standard: 'EXIF',
  },
  'model': {
    field: 'model',
    label: 'Camera Model',
    description: 'The specific model of the camera or device',
    example: 'iPhone 15 Pro',
    type: 'string',
    category: 'camera',
    common: true,
    standard: 'EXIF',
  },
  'exposureTime': {
    field: 'exposureTime',
    label: 'Exposure Time',
    description: 'Shutter speed in seconds (how long the sensor was exposed)',
    example: '1/125',
    type: 'string',
    category: 'camera',
    common: true,
    standard: 'EXIF',
  },
  'fNumber': {
    field: 'fNumber',
    label: 'F-Number (Aperture)',
    description: 'The aperture setting (f-stop) controlling depth of field',
    example: 'f/2.8',
    type: 'string',
    category: 'camera',
    common: true,
    standard: 'EXIF',
  },
  'iso': {
    field: 'iso',
    label: 'ISO Speed',
    description: 'Light sensitivity setting of the camera sensor',
    example: '400',
    type: 'number',
    category: 'camera',
    common: true,
    standard: 'EXIF',
  },
  'focalLength': {
    field: 'focalLength',
    label: 'Focal Length',
    description: 'The focal length of the lens in millimeters',
    example: '50mm',
    type: 'string',
    category: 'camera',
    standard: 'EXIF',
  },
  'flash': {
    field: 'flash',
    label: 'Flash',
    description: 'Whether flash was used and its mode',
    example: 'Flash did not fire',
    type: 'string',
    category: 'camera',
    standard: 'EXIF',
  },

  // Location Fields
  'gpsLatitude': {
    field: 'gpsLatitude',
    label: 'GPS Latitude',
    description: 'The north-south position where the photo was taken',
    example: '37.7749',
    type: 'number',
    category: 'location',
    common: true,
    standard: 'EXIF',
  },
  'gpsLongitude': {
    field: 'gpsLongitude',
    label: 'GPS Longitude',
    description: 'The east-west position where the photo was taken',
    example: '-122.4194',
    type: 'number',
    category: 'location',
    common: true,
    standard: 'EXIF',
  },
  'gpsAltitude': {
    field: 'gpsAltitude',
    label: 'GPS Altitude',
    description: 'Height above sea level in meters',
    example: '15.5',
    type: 'number',
    category: 'location',
    standard: 'EXIF',
  },

  // DateTime Fields
  'dateTimeOriginal': {
    field: 'dateTimeOriginal',
    label: 'Date Taken',
    description: 'When the photo was originally captured',
    example: '2024-03-15 14:30:00',
    type: 'date',
    category: 'datetime',
    common: true,
    standard: 'EXIF',
  },
  'dateTimeDigitized': {
    field: 'dateTimeDigitized',
    label: 'Date Digitized',
    description: 'When the image was digitized (scanned or converted)',
    example: '2024-03-15 14:30:00',
    type: 'date',
    category: 'datetime',
    standard: 'EXIF',
  },
  'modifyDate': {
    field: 'modifyDate',
    label: 'Date Modified',
    description: 'When the file was last modified',
    example: '2024-03-16 10:00:00',
    type: 'date',
    category: 'datetime',
    common: true,
  },

  // Technical Fields
  'colorSpace': {
    field: 'colorSpace',
    label: 'Color Space',
    description: 'The color model used (sRGB, Adobe RGB, etc.)',
    example: 'sRGB',
    type: 'string',
    category: 'color',
    standard: 'EXIF',
  },
  'bitDepth': {
    field: 'bitDepth',
    label: 'Bit Depth',
    description: 'Number of bits per color channel',
    example: '8',
    type: 'number',
    category: 'technical',
  },
  'compression': {
    field: 'compression',
    label: 'Compression',
    description: 'The compression method used',
    example: 'JPEG',
    type: 'string',
    category: 'technical',
  },

  // Copyright Fields
  'copyright': {
    field: 'copyright',
    label: 'Copyright',
    description: 'Copyright notice for the image',
    example: '© 2024 Photographer Name',
    type: 'string',
    category: 'copyright',
    common: true,
    standard: 'IPTC',
  },
  'artist': {
    field: 'artist',
    label: 'Artist/Creator',
    description: 'Name of the photographer or creator',
    example: 'John Doe',
    type: 'string',
    category: 'copyright',
    standard: 'EXIF',
  },

  // Software Fields
  'software': {
    field: 'software',
    label: 'Software',
    description: 'Software used to create or edit the file',
    example: 'Adobe Photoshop 25.0',
    type: 'string',
    category: 'software',
    standard: 'EXIF',
  },
  'editHistory': {
    field: 'editHistory',
    label: 'Edit History',
    description: 'Record of editing operations performed on the file',
    type: 'array',
    category: 'software',
    standard: 'XMP',
  },
};

// ============================================================================
// Search and Lookup Functions
// ============================================================================

/**
 * Search help topics by query
 */
export function searchHelpTopics(query: string): HelpTopic[] {
  if (!query || query.trim().length === 0) {
    return Object.values(helpTopics);
  }
  
  const normalizedQuery = query.toLowerCase().trim();
  const words = normalizedQuery.split(/\s+/);
  
  return Object.values(helpTopics)
    .map(topic => {
      // Calculate relevance score
      let score = 0;
      const searchableText = [
        topic.title,
        topic.shortDescription,
        topic.fullDescription,
        ...topic.keywords,
      ].join(' ').toLowerCase();
      
      words.forEach(word => {
        if (topic.title.toLowerCase().includes(word)) score += 10;
        if (topic.keywords.some(k => k.toLowerCase().includes(word))) score += 5;
        if (topic.shortDescription.toLowerCase().includes(word)) score += 3;
        if (topic.fullDescription.toLowerCase().includes(word)) score += 1;
      });
      
      return { topic, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .map(({ topic }) => topic);
}

/**
 * Get help topic by ID
 */
export function getHelpTopic(id: string): HelpTopic | undefined {
  return helpTopics[id];
}

/**
 * Get help topics by category
 */
export function getHelpTopicsByCategory(category: HelpCategory): HelpTopic[] {
  return Object.values(helpTopics).filter(topic => topic.category === category);
}

/**
 * Get related help topics
 */
export function getRelatedTopics(topicId: string): HelpTopic[] {
  const topic = helpTopics[topicId];
  if (!topic || !topic.relatedTopics) return [];
  
  return topic.relatedTopics
    .map(id => helpTopics[id])
    .filter((t): t is HelpTopic => t !== undefined);
}

/**
 * Get metadata field documentation
 */
export function getMetadataFieldDoc(field: string): MetadataFieldDoc | undefined {
  return metadataFieldDocs[field];
}

/**
 * Get metadata fields by category
 */
export function getMetadataFieldsByCategory(category: MetadataCategory): MetadataFieldDoc[] {
  return Object.values(metadataFieldDocs).filter(doc => doc.category === category);
}

/**
 * Get common/important metadata fields
 */
export function getCommonMetadataFields(): MetadataFieldDoc[] {
  return Object.values(metadataFieldDocs).filter(doc => doc.common);
}

/**
 * Search metadata field documentation
 */
export function searchMetadataFields(query: string): MetadataFieldDoc[] {
  if (!query || query.trim().length === 0) {
    return Object.values(metadataFieldDocs);
  }
  
  const normalizedQuery = query.toLowerCase().trim();
  
  return Object.values(metadataFieldDocs).filter(doc => {
    const searchableText = [
      doc.field,
      doc.label,
      doc.description,
      doc.standard || '',
    ].join(' ').toLowerCase();
    
    return searchableText.includes(normalizedQuery);
  });
}

// ============================================================================
// Contextual Help Utilities
// ============================================================================

/** Context identifiers for contextual help */
export type HelpContext = 
  | 'upload-zone'
  | 'results-view'
  | 'metadata-panel'
  | 'forensic-panel'
  | 'export-dialog'
  | 'pricing-page'
  | 'settings-page'
  | 'dashboard';

/** Map contexts to relevant help topics */
const contextHelpMap: Record<HelpContext, string[]> = {
  'upload-zone': ['upload-file', 'supported-formats', 'file-limits'],
  'results-view': ['metadata-basics', 'export-results'],
  'metadata-panel': ['exif-data', 'iptc-data', 'xmp-data'],
  'forensic-panel': ['forensic-analysis', 'ela-analysis'],
  'export-dialog': ['export-results', 'json-export'],
  'pricing-page': ['pricing', 'file-limits'],
  'settings-page': ['account-settings', 'api-keys', 'data-privacy'],
  'dashboard': ['getting-started', 'upload-file'],
};

/**
 * Get contextual help topics for a specific UI context
 */
export function getContextualHelp(context: HelpContext): HelpTopic[] {
  const topicIds = contextHelpMap[context] || [];
  return topicIds
    .map(id => helpTopics[id])
    .filter((t): t is HelpTopic => t !== undefined);
}

/**
 * Get tooltip content for a metadata field
 */
export function getFieldTooltip(field: string): string | undefined {
  const doc = metadataFieldDocs[field];
  if (!doc) return undefined;
  
  let tooltip = doc.description;
  if (doc.example) {
    tooltip += ` Example: ${doc.example}`;
  }
  return tooltip;
}

// ============================================================================
// Category Labels
// ============================================================================

export const helpCategoryLabels: Record<HelpCategory, string> = {
  'getting-started': 'Getting Started',
  'upload': 'Uploading Files',
  'metadata': 'Understanding Metadata',
  'analysis': 'Analysis Tools',
  'export': 'Exporting Results',
  'account': 'Account & Settings',
  'pricing': 'Pricing & Plans',
  'security': 'Security & Privacy',
  'troubleshooting': 'Troubleshooting',
};

export const metadataCategoryLabels: Record<MetadataCategory, string> = {
  'basic': 'Basic Information',
  'camera': 'Camera Settings',
  'location': 'Location Data',
  'datetime': 'Date & Time',
  'technical': 'Technical Details',
  'color': 'Color Information',
  'copyright': 'Copyright & Credits',
  'software': 'Software & Editing',
  'forensic': 'Forensic Data',
  'audio': 'Audio Metadata',
  'video': 'Video Metadata',
  'document': 'Document Metadata',
};

// ============================================================================
// Export All
// ============================================================================

export const helpSystem = {
  helpTopics,
  metadataFieldDocs,
  searchHelpTopics,
  getHelpTopic,
  getHelpTopicsByCategory,
  getRelatedTopics,
  getMetadataFieldDoc,
  getMetadataFieldsByCategory,
  getCommonMetadataFields,
  searchMetadataFields,
  getContextualHelp,
  getFieldTooltip,
  helpCategoryLabels,
  metadataCategoryLabels,
} as const;

export default helpSystem;
