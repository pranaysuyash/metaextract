/**
 * Educational Examples & Use Cases
 * 
 * Real-world examples showing what metadata reveals and how it's used.
 */

export interface Example {
  /** Example title */
  title: string;
  
  /** Category */
  category: 'forensic' | 'privacy' | 'professional' | 'creative' | 'medical';
  
  /** Short description */
  description: string;
  
  /** What metadata revealed */
  revealed: string[];
  
  /** Fields involved */
  fields: string[];
  
  /** Impact/outcome */
  impact: string;
  
  /** Learn more URL (optional) */
  learnMoreUrl?: string;
}

/**
 * Real-world examples of metadata in action
 */
export const METADATA_EXAMPLES: Example[] = [
  // Forensic Examples
  {
    title: 'Viral Protest Photo Verification',
    category: 'forensic',
    description: 'Journalists verified the authenticity and location of a viral protest image',
    revealed: [
      'GPS coordinates matched claimed protest location',
      'Timestamp aligned with reported event time',
      'No editing software detected in history',
      'Camera serial number linked to photojournalist\'s registered equipment'
    ],
    fields: ['GPSLatitude', 'GPSLongitude', 'DateTimeOriginal', 'Software', 'SerialNumber'],
    impact: 'Photo verified as authentic, used as evidence in news coverage'
  },
  {
    title: 'Photoshop Manipulation Detected',
    category: 'forensic',
    description: 'Image forensics revealed undisclosed editing of a news photograph',
    revealed: [
      'XMP history showed 15+ editing operations',
      'Adobe Photoshop detected in software field',
      'Modification timestamps spanning 3 hours',
      'Thumbnail differed from main image (cropping detected)'
    ],
    fields: ['XMP', 'Software', 'ModifyDate', 'ThumbnailImage', 'HistoryAction'],
    impact: 'News outlet retracted image and issued correction'
  },
  
  // Privacy Examples
  {
    title: 'Vacation Photo Leaked Home Address',
    category: 'privacy',
    description: 'GPS data in shared vacation photo revealed user\'s home location',
    revealed: [
      'GPS coordinates embedded in "beach selfie"',
      'Coordinates traced to residential address',
      'Timestamp showed user was away on vacation',
      'Device model revealed expensive iPhone'
    ],
    fields: ['GPSLatitude', 'GPSLongitude', 'DateTimeOriginal', 'Make', 'Model'],
    impact: 'Home burglarized while family on vacation; photo GPS linked them to location'
  },
  {
    title: 'Anonymous Whistleblower Identified',
    category: 'privacy',
    description: 'Metadata in leaked documents revealed anonymous source\'s identity',
    revealed: [
      'Author name embedded in PDF properties',
      'Printer serial number in yellow tracking dots',
      'Modification timestamps matched office hours',
      'Software version unique to company department'
    ],
    fields: ['Author', 'Creator', 'ModifyDate', 'Producer', 'SerialNumber'],
    impact: 'Whistleblower identified and terminated despite precautions'
  },
  
  // Professional Photography
  {
    title: 'Copyright Infringement Proof',
    category: 'professional',
    description: 'Photographer proved copyright ownership through embedded metadata',
    revealed: [
      'Copyright notice in IPTC fields',
      'Photographer byline and contact info',
      'Original creation date predating infringer\'s claim',
      'Unique camera serial number matching photographer\'s equipment'
    ],
    fields: ['Copyright', 'Artist', 'Byline', 'DateTimeOriginal', 'SerialNumber'],
    impact: '$50,000 settlement in copyright infringement case'
  },
  {
    title: 'Wedding Photo Settings Analysis',
    category: 'creative',
    description: 'Aspiring photographer learned techniques by analyzing award-winning shots',
    revealed: [
      'ISO 3200 for low-light reception',
      'f/1.8 aperture for bokeh background',
      '1/125s shutter speed to freeze first dance',
      'Canon 85mm f/1.8 lens used',
      'No flash, only natural/ambient light'
    ],
 fields: ['ISO', 'FNumber', 'ShutterSpeed', 'LensModel', 'Flash'],
    impact: 'Photographer replicated lighting setup for own portfolio'
  },
  
  // Medical Examples
  {
    title: 'Medical Scan Quality Assurance',
    category: 'medical',
    description: 'Hospital detected malfunctioning CT scanner through DICOM metadata',
    revealed: [
      'Inconsistent slice thickness in scan series',
      'Scanner calibration date exceeded policy',
      'Radiation dose higher than protocol',
      'Equipment serial number flagged in recall database'
    ],
    fields: ['SliceThickness', 'CalibrationDate', 'ExposureDose', 'SerialNumber', 'Modality'],
    impact: 'Scanner taken offline, patients rescanned, potential diagnoses corrected'
  },
  {
    title: 'Research Imaging Verification',
    category: 'medical',
    description: 'Research team verified clinical trial image authenticity',
    revealed: [
      'Study UID matched trial protocol',
      'Patient ID consistent with enrolled subjects',
      'Acquisition timestamps aligned with visit schedule',
      'Imaging parameters met study requirements'
    ],
    fields: ['StudyUID', 'PatientID', 'AcquisitionDate', 'StudyDescription'],
    impact: 'Data validated for FDA submission in clinical trial'
  },
  
  // Creative/Photographic
  {
    title: 'Stolen Camera Recovery',
    category: 'creative',
    description: 'Photographer recovered stolen camera through serial number tracking',
    revealed: [
      'Camera serial number embedded in all photos',
      'Thief posted photos online from stolen camera',
      'Serial matched police theft report',
      'GPS data showed thief\'s location pattern'
    ],
    fields: ['SerialNumber', 'Make', 'Model', 'GPSLatitude', 'GPSLongitude'],
    impact: 'Camera recovered, thief arrested based on metadata evidence'
  }
];

/**
 * Get examples by category
 */
export function getExamplesByCategory(category: Example['category']): Example[] {
  return METADATA_EXAMPLES.filter(ex => ex.category === category);
}

/**
 * Get examples involving specific field
 */
export function getExamplesByField(fieldName: string): Example[] {
  const normalized = fieldName.toLowerCase();
  return METADATA_EXAMPLES.filter(ex => 
    ex.fields.some(f => f.toLowerCase().includes(normalized))
  );
}

/**
 * Get random example
 */
export function getRandomExample(): Example {
  return METADATA_EXAMPLES[Math.floor(Math.random() * METADATA_EXAMPLES.length)];
}

/**
 * Format example for display
 */
export function formatExample(example: Example): string {
  return `
**${example.title}**
${example.description}

What metadata revealed:
${example.revealed.map(r => `• ${r}`).join('\n')}

Impact: ${example.impact}
  `.trim();
}
