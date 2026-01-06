/**
 * Original UI Help Content
 * Explanations, definitions, and guidance for Original UI
 */

export interface HelpTopic {
  id: string;
  title: string;
  category: 'general' | 'gps' | 'exif' | 'filesystem' | 'forensic' | 'batch';
  content: string;
  relatedTerms?: string[];
  examples?: string[];
}

export const ORIGINAL_HELP_TOPICS: Record<string, HelpTopic> = {
  'metadata-overview': {
    id: 'metadata-overview',
    title: 'What is Metadata?',
    category: 'general',
    content:
      "Metadata is data about data. In the context of files, it's information embedded within the file itself that describes the file's properties, origins, and history.",
    relatedTerms: ['EXIF', 'GPS', 'hash', 'checksum'],
    examples: [
      'Camera model and settings',
      'GPS coordinates where photo was taken',
      'Date and time of creation',
      'File size and format',
    ],
  },

  'gps-data': {
    id: 'gps-data',
    title: 'GPS Location Data',
    category: 'gps',
    content:
      'GPS (Global Positioning System) coordinates are latitude and longitude values that indicate where a photo was taken. This data is captured by cameras with built-in GPS receivers.',
    relatedTerms: [
      'geotagging',
      'coordinates',
      'latitude',
      'longitude',
      'altitude',
      'maps',
    ],
    examples: [
      'Latitude: 37.7749° N',
      'Longitude: -122.4194° W',
      'Altitude: 12.5 meters',
      'Click to view in Google Maps',
    ],
  },

  'exif-data': {
    id: 'exif-data',
    title: 'EXIF Data',
    category: 'exif',
    content:
      'EXIF (Exchangeable Image File Format) is metadata embedded in image files by cameras and smartphones. It includes camera settings, capture time, and device information.',
    relatedTerms: [
      'aperture',
      'shutter speed',
      'ISO',
      'focal length',
      'exposure',
    ],
    examples: [
      'Aperture: f/2.8',
      'Shutter Speed: 1/250s',
      'ISO: 400',
      'Focal Length: 50mm',
      'Camera: Canon EOS R5',
    ],
  },

  'filesystem-metadata': {
    id: 'filesystem-metadata',
    title: 'File System Metadata',
    category: 'filesystem',
    content:
      'File system metadata is information stored by the operating system when files are created, modified, or accessed. This includes timestamps and file attributes.',
    relatedTerms: [
      'timestamp',
      'creation date',
      'modification date',
      'file attributes',
    ],
    examples: [
      'Created: 2024-01-06 10:30:00',
      'Modified: 2024-01-06 14:45:00',
      'File Size: 3.2 MB',
      'File Type: JPEG',
    ],
  },

  'hash-integrity': {
    id: 'hash-integrity',
    title: 'Cryptographic Hashes',
    category: 'forensic',
    content:
      "Cryptographic hashes like MD5, SHA-1, and SHA-256 are mathematical fingerprints of files. They allow you to verify that a file hasn't been modified or corrupted.",
    relatedTerms: [
      'MD5',
      'SHA-1',
      'SHA-256',
      'checksum',
      'digital signature',
      'integrity verification',
    ],
    examples: [
      'MD5: d41d8cd98f00b204e9800998ecf8427e',
      'SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      'Compare hashes to verify file integrity',
      'Detect if file has been tampered with',
    ],
  },

  'burned-metadata': {
    id: 'burned-metadata',
    title: 'Burned-in Text (OCR)',
    category: 'forensic',
    content:
      "Burned-in metadata refers to text that's literally part of the image pixels (like text overlays on screenshots). We use OCR (Optical Character Recognition) to extract this text.",
    relatedTerms: [
      'OCR',
      'screenshot text',
      'watermark',
      'image text extraction',
    ],
    examples: [
      'Timestamp burned into video frame',
      'Address on screenshot overlay',
      'Copyright notice in corner',
      'Caption at bottom of image',
    ],
  },

  'metadata-comparison': {
    id: 'metadata-comparison',
    title: 'Metadata Comparison',
    category: 'forensic',
    content:
      "Comparing embedded metadata with burned-in text helps detect tampering. If timestamps don't match or GPS data contradicts visible locations, the file may have been edited.",
    relatedTerms: [
      'tampering detection',
      'forensic analysis',
      'discrepancy',
      'verification',
    ],
    examples: [
      'Embedded GPS: San Francisco, Burned text: New York',
      'Embedded date: 2024-01-01, Burned date: 2023-12-25',
      'Camera data missing but photo shows watermark',
    ],
  },

  'batch-upload': {
    id: 'batch-upload',
    title: 'Batch Processing',
    category: 'batch',
    content:
      'Batch processing allows you to upload multiple files at once. Metadata is extracted in parallel, saving you time when working with many files.',
    relatedTerms: [
      'bulk upload',
      'parallel processing',
      'batch operations',
      'multi-file',
    ],
    examples: [
      'Upload 50 photos from a folder',
      'Process entire SD card contents',
      'Extract metadata from multiple file types at once',
      'Compare metadata across multiple files',
    ],
  },

  'export-formats': {
    id: 'export-formats',
    title: 'Export Formats',
    category: 'general',
    content:
      'Export your extracted metadata in various formats for different use cases: JSON for developers, CSV for spreadsheets, PDF for reports and documentation.',
    relatedTerms: ['JSON', 'CSV', 'PDF', 'export', 'data format'],
    examples: [
      'JSON: Use in web applications and APIs',
      'CSV: Open in Excel or Google Sheets',
      'PDF: Print or archive as report',
      'Include all metadata fields or selected ones',
    ],
  },
};

export function getHelpTopic(topicId: string): HelpTopic | undefined {
  return ORIGINAL_HELP_TOPICS[topicId];
}

export function getHelpTopicsByCategory(
  category: HelpTopic['category']
): HelpTopic[] {
  return Object.values(ORIGINAL_HELP_TOPICS).filter(
    topic => topic.category === category
  );
}

export function searchHelpTopics(query: string): HelpTopic[] {
  const lowerQuery = query.toLowerCase();
  return Object.values(ORIGINAL_HELP_TOPICS).filter(
    topic =>
      topic.title.toLowerCase().includes(lowerQuery) ||
      topic.content.toLowerCase().includes(lowerQuery) ||
      topic.relatedTerms?.some(term => term.toLowerCase().includes(lowerQuery))
  );
}
