/**
 * Images MVP Help Content
 * Purpose-specific help for privacy, photography, and authenticity modes
 */

export type ImagesPurpose = 'privacy' | 'photography' | 'authenticity';

export interface ImagesHelpTopic {
  id: string;
  purpose: ImagesPurpose;
  title: string;
  shortDescription: string;
  detailedContent: string;
  tips?: string[];
}

export const IMAGES_HELP_TOPICS: Record<string, ImagesHelpTopic> = {
  'gps-privacy': {
    id: 'gps-privacy',
    purpose: 'privacy',
    title: 'GPS Location Privacy',
    shortDescription: 'Remove location data before sharing',
    detailedContent:
      "GPS coordinates in photos reveal exactly where they were taken. This can be a privacy concern if you're sharing photos publicly. Check the Privacy tab to see GPS data, and consider removing it before sharing.",
    tips: [
      'Use camera apps that strip GPS by default',
      'Check metadata before posting on social media',
      'Be aware of home/work locations',
      'Consider EXIF removal tools for batch processing',
    ],
  },

  'timestamps-privacy': {
    id: 'timestamps-privacy',
    purpose: 'privacy',
    title: 'Timestamp Privacy',
    shortDescription: 'Control when your photos appear to be taken',
    detailedContent:
      'Timestamps show when photos were taken, which can reveal your habits and location patterns. Some cameras have incorrect timestamps, which you can correct in editing software.',
    tips: [
      'Verify camera time is correct',
      'Consider privacy implications of exact times',
      'Some cameras allow timestamp modification',
    ],
  },

  'burned-text-privacy': {
    id: 'burned-text-privacy',
    purpose: 'privacy',
    title: 'Burned-in Text',
    shortDescription: 'Text visible in image pixels',
    detailedContent:
      'Burned-in text refers to text overlays on images (like timestamps on screenshots, captions, watermarks). This text cannot be removed by standard metadata cleaning tools. You need to edit the actual image to remove it.',
    tips: [
      'Screenshot timestamps cannot be removed with metadata tools',
      'Watermarks require image editing',
      'OCR can detect but not remove burned text',
    ],
  },

  'exposure-triangle': {
    id: 'exposure-triangle',
    purpose: 'photography',
    title: 'Exposure Triangle',
    shortDescription: 'Aperture, Shutter, ISO relationship',
    detailedContent:
      'The exposure triangle is the foundation of photography. Aperture controls light and depth of field, shutter speed controls motion blur, and ISO affects noise. Understanding how these three work together helps you achieve proper exposure.',
    tips: [
      'Wide aperture (low f-number) = more light, shallow depth of field',
      'Fast shutter = freezes motion, less light',
      'Low ISO = less noise but requires more light',
      'Adjust all three to balance exposure',
    ],
  },

  'focal-length': {
    id: 'focal-length',
    purpose: 'photography',
    title: 'Focal Length & Perspective',
    shortDescription: 'How focal length affects your photos',
    detailedContent:
      'Focal length determines how much of the scene you capture. Wide-angle lenses (24mm or less) capture more of the scene. Telephoto lenses (85mm+) compress distance and bring subjects closer.',
    tips: [
      '24mm or less = wide-angle for landscapes',
      '35-50mm = normal view, similar to human eye',
      '85mm+ = portrait/telephoto for subjects',
      'Crop factor applies to some cameras',
    ],
  },

  'white-balance': {
    id: 'white-balance',
    purpose: 'photography',
    title: 'White Balance & Color',
    shortDescription: 'Understanding color temperature in photos',
    detailedContent:
      'White balance affects how colors appear in your photos. Auto white balance usually works well, but custom white balance can correct artificial lighting or achieve artistic effects.',
    tips: [
      'Daylight = warm tones, good for outdoor sun',
      'Tungsten = cool tones, for indoor incandescent',
      'Fluorescent = neutral/green tint, for office lighting',
      'Custom WB for artistic control',
    ],
  },

  'iso-performance': {
    id: 'iso-performance',
    purpose: 'photography',
    title: 'ISO & Image Quality',
    shortDescription: 'Balancing noise and light sensitivity',
    detailedContent:
      "ISO determines your camera's sensitivity to light. Lower ISO (100-400) gives cleaner images with less noise. Higher ISO (800-3200) allows shooting in low light but introduces noise.",
    tips: [
      'Use lowest ISO possible for given light',
      'Modern cameras handle high ISO better than older ones',
      'Noise is most visible in dark areas',
    ],
  },

  'tampering-signs': {
    id: 'tampering-signs',
    purpose: 'authenticity',
    title: 'Signs of Tampering',
    shortDescription: 'Detect if a photo has been edited',
    detailedContent:
      'Look for inconsistencies that suggest editing: timestamp mismatches between embedded and burned metadata, GPS data contradicting visible locations, missing expected metadata, or unusual software mentions in EXIF.',
    tips: [
      "Timestamps that don't match the scene",
      'GPS in metadata but not visible in photo',
      'Missing EXIF from original camera',
      'Software like Adobe Photoshop mentioned',
    ],
  },

  'metadata-comparison': {
    id: 'metadata-comparison',
    purpose: 'authenticity',
    title: 'Metadata Comparison',
    shortDescription: 'Compare embedded vs burned-in data',
    detailedContent:
      'Metadata comparison checks if embedded data (from camera) matches burned-in text (visible in pixels). Mismatches can indicate tampering or time zone errors. Authentic photos usually show matching or reasonable timestamps.',
    tips: [
      'Matching timestamps = likely authentic',
      'Missing embedded GPS but visible location = suspicious',
      'Inconsistent dates = investigate further',
    ],
  },

  'format-support': {
    id: 'format-support',
    purpose: 'photography',
    title: 'Image Format Support',
    shortDescription: 'What metadata each format contains',
    detailedContent:
      'Different image formats support different metadata. JPEG has rich EXIF data. PNG has minimal metadata. HEIC (iPhone) has comprehensive data including depth information. WebP support varies by source.',
    tips: [
      'JPEG = most compatible, rich metadata',
      'PNG = lossless, minimal metadata',
      'HEIC = iPhone format, depth data included',
      'WebP = modern format, metadata support varies',
    ],
  },
};

export function getImagesHelpTopic(
  topicId: string
): ImagesHelpTopic | undefined {
  return IMAGES_HELP_TOPICS[topicId];
}

export function getHelpTopicsByPurpose(
  purpose: ImagesHelpTopic['purpose']
): ImagesHelpTopic[] {
  return Object.values(IMAGES_HELP_TOPICS).filter(
    topic => topic.purpose === purpose
  );
}

export function searchImagesHelpTopics(query: string): ImagesHelpTopic[] {
  const lowerQuery = query.toLowerCase();
  return Object.values(IMAGES_HELP_TOPICS).filter(
    topic =>
      topic.title.toLowerCase().includes(lowerQuery) ||
      topic.shortDescription.toLowerCase().includes(lowerQuery) ||
      topic.detailedContent.toLowerCase().includes(lowerQuery)
  );
}
