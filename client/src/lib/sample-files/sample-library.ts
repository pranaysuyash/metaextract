/**
 * Sample File Library - Curated metadata samples for onboarding
 */

export interface SampleFile {
  id: string;
  name: string;
  description: string;
  category: 'privacy' | 'photography' | 'authenticity' | 'forensics';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  metadata: {
    filename: string;
    filesize: string;
    filetype: string;
    mime_type: string;
    gps?: Record<string, unknown>;
    exif?: Record<string, unknown>;
    filesystem?: Record<string, unknown>;
    hashes?: Record<string, unknown>;
    [key: string]: unknown;
  };
  highlights: string[];
  learningPoints: string[];
}

/**
 * Curated sample files demonstrating different capabilities
 */

export const SAMPLE_FILES: SampleFile[] = [
  {
    id: 'sample-gps-location',
    name: 'GPS Location Demo',
    description:
      'Example with embedded GPS coordinates showing precise location data',
    category: 'privacy',
    difficulty: 'beginner',
    metadata: {
      filename: 'vacation-photo.jpg',
      filesize: '3.2 MB',
      filetype: 'JPEG',
      mime_type: 'image/jpeg',
      gps: {
        latitude: 37.7749,
        longitude: -122.4194,
        altitude: 12.5,
        direction: 'NW',
        accuracy: 5.0,
        timestamp: '2024-06-15T14:30:00Z',
        google_maps_url: 'https://maps.google.com/?q=37.7749,-122.4194',
      },
      exif: {
        make: 'Apple',
        model: 'iPhone 15 Pro',
        software: 'iOS 17.4',
        datetime_original: '2024-06-15T14:30:00',
        orientation: 1,
        x_resolution: 4032,
        y_resolution: 3024,
      },
    },
    highlights: [
      'GPS coordinates: 37.7749°N, 122.4194°W',
      'Altitude: 12.5 meters',
      'Timestamp: June 15, 2024',
      'Camera: iPhone 15 Pro',
    ],
    learningPoints: [
      'GPS metadata reveals exact photo location',
      'Altitude data can indicate photo perspective',
      'Camera model is always embedded in EXIF',
    ],
  },
  {
    id: 'sample-camera-settings',
    name: 'Photography Settings',
    description: 'Professional photo with detailed camera settings',
    category: 'photography',
    difficulty: 'beginner',
    metadata: {
      filename: 'portrait-raw.jpg',
      filesize: '8.7 MB',
      filetype: 'JPEG',
      mime_type: 'image/jpeg',
      exif: {
        make: 'Canon',
        model: 'EOS R5',
        lens_model: 'EF 85mm f/1.2L USM',
        aperture: 'f/1.2',
        shutter_speed: '1/250',
        iso: 400,
        focal_length: '85.0 mm',
        datetime_original: '2024-06-15T10:15:30',
        exposure_mode: 'Manual',
        white_balance: 'Auto',
        color_space: 'sRGB',
      },
    },
    highlights: [
      'Aperture: f/1.2 (very wide, shallow depth of field)',
      'Shutter: 1/250s (fast, freezes motion)',
      'ISO: 400 (moderate, good light)',
      'Lens: 85mm prime (portrait lens)',
    ],
    learningPoints: [
      'Aperture affects depth of field (background blur)',
      'Shutter speed controls motion blur',
      'ISO affects image noise/grain',
      'Focal length determines perspective',
    ],
  },
  {
    id: 'sample-metadata-stripped',
    name: 'Metadata Stripped',
    description: 'Example showing what happens when metadata is removed',
    category: 'privacy',
    difficulty: 'intermediate',
    metadata: {
      filename: 'cleaned-photo.jpg',
      filesize: '2.1 MB',
      filetype: 'JPEG',
      mime_type: 'image/jpeg',
      exif: {
        make: null,
        model: null,
        datetime_original: null,
        orientation: 1,
      },
      filesystem: {
        created: '2024-06-15T15:00:00',
        modified: '2024-06-15T15:00:00',
      },
    },
    highlights: [
      'No camera manufacturer',
      'No capture timestamp',
      'No GPS data',
      'Filesystem timestamp only',
    ],
    learningPoints: [
      'Metadata can be intentionally removed for privacy',
      'Stripped files lose forensic value',
      'Filesystem timestamps remain even after stripping',
    ],
  },
  {
    id: 'sample-tampering-suspected',
    name: 'Tampering Suspicion',
    description: 'Photo with inconsistencies suggesting editing',
    category: 'authenticity',
    difficulty: 'advanced',
    metadata: {
      filename: 'questionable-photo.jpg',
      filesize: '4.5 MB',
      filetype: 'JPEG',
      mime_type: 'image/jpeg',
      exif: {
        make: 'Adobe Photoshop',
        model: 'Photoshop CS6',
        software: 'Adobe Photoshop 24.0',
        datetime_original: '2024-06-15T12:00:00',
        datetime_modified: '2024-06-15T14:30:00',
        orientation: 1,
      },
      burned_metadata: {
        has_burned_metadata: true,
        extracted_text: 'Original taken at 2024-06-10',
        confidence: 'high',
        parsed_data: {
          timestamp: '2024-06-10',
        },
      },
      metadata_comparison: {
        has_both: true,
        discrepancies: [
          {
            field: 'timestamp',
            matches: false,
            embedded: '2024-06-15T12:00:00',
            burned: '2024-06-10',
            warning: 'Timestamps do not match',
          },
        ],
        summary: {
          overall_status: 'suspicious',
          timestamp_comparison: 'discrepancy detected',
          gps_comparison: 'not applicable',
        },
      },
    },
    highlights: [
      'EXIF shows Adobe Photoshop',
      'Burned-in text shows different date',
      'Timestamp mismatch detected',
      'Software indicates editing',
    ],
    learningPoints: [
      'EXIF data reveals editing software used',
      'Burned-in metadata can contradict embedded data',
      'Timestamp inconsistencies suggest tampering',
      'Professional tools preserve some metadata',
    ],
  },
  {
    id: 'sample-forensic-complex',
    name: 'Forensic Analysis',
    description: 'Complex metadata with multiple data sources',
    category: 'forensics',
    difficulty: 'advanced',
    metadata: {
      filename: 'forensic-evidence.jpg',
      filesize: '6.2 MB',
      filetype: 'JPEG',
      mime_type: 'image/jpeg',
      gps: {
        latitude: 40.7128,
        longitude: -74.006,
        accuracy: 3.0,
        timestamp: '2024-06-15T16:45:00Z',
      },
      exif: {
        make: 'Nikon',
        model: 'D850',
        lens_model: 'AF-S NIKKOR 24-70mm f/2.8E ED',
        aperture: 'f/8.0',
        shutter_speed: '1/125',
        iso: 800,
        datetime_original: '2024-06-15T16:45:00',
        datetime_digitized: '2024-06-15T16:45:05',
      },
      hashes: {
        md5: 'd41d8cd98f00b204e9800998ecf8427e',
        sha256:
          'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      },
      file_integrity: {
        md5: 'd41d8cd98f00b204e9800998ecf8427e',
        sha256:
          'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        crc32: '00000000',
      },
      burned_metadata: {
        has_burned_metadata: true,
        extracted_text:
          'Evidence #4729 - Crime Scene Investigation\nDate: June 15, 2024',
        confidence: 'high',
        parsed_data: {
          timestamp: '2024-06-15',
          case_number: '4729',
          context: 'Crime Scene Investigation',
        },
      },
    },
    highlights: [
      'GPS: New York City area',
      'Camera: Nikon D850 (pro DSLR)',
      'Hashes for verification',
      'Burned-in text with case number',
    ],
    learningPoints: [
      'Multiple data sources enable cross-verification',
      'Cryptographic hashes verify file integrity',
      'Burned-in metadata survives editing',
      'Professional cameras embed rich EXIF data',
    ],
  },
];

/**
 * Get sample files by category
 */
export function getSamplesByCategory(
  category: SampleFile['category']
): SampleFile[] {
  return SAMPLE_FILES.filter(sample => sample.category === category);
}

/**
 * Get sample files by difficulty
 */
export function getSamplesByDifficulty(
  difficulty: SampleFile['difficulty']
): SampleFile[] {
  return SAMPLE_FILES.filter(sample => sample.difficulty === difficulty);
}

/**
 * Get sample by ID
 */
export function getSampleById(id: string): SampleFile | undefined {
  return SAMPLE_FILES.find(sample => sample.id === id);
}

/**
 * Get recommended samples for user level
 */
export function getRecommendedSamples(
  userLevel: 'beginner' | 'intermediate' | 'advanced'
): SampleFile[] {
  const difficulties: SampleFile['difficulty'][] =
    userLevel === 'beginner'
      ? ['beginner']
      : userLevel === 'intermediate'
        ? ['beginner', 'intermediate']
        : ['beginner', 'intermediate', 'advanced'];

  return SAMPLE_FILES.filter(sample =>
    difficulties.includes(sample.difficulty)
  ).slice(0, 3);
}
