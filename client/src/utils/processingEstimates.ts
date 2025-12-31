/**
 * Processing Time Estimation
 * 
 * Estimate metadata extraction time based on file type, size, and tier.
 */

export interface ProcessingEstimate {
  /** Estimated time in seconds */
  estimatedSeconds: number;
  
  /** Range (min-max) in seconds */
  range: [number, number];
  
  /** Human-readable estimate */
  displayText: string;
  
  /** Confidence level */
  confidence: 'low' | 'medium' | 'high';
  
  /** Factors affecting time */
  factors: string[];
}

/**
 * File type processing complexity
 */
const FILE_COMPLEXITY: Record<string, number> = {
  // Images - Fast
  'image/jpeg': 1.0,
  'image/png': 1.2,
  'image/gif': 0.8,
  'image/webp': 1.0,
  
  // RAW - Medium
  'image/x-canon-cr2': 2.0,
  'image/x-canon-cr3': 2.5,
  'image/x-nikon-nef': 2.0,
  'image/x-sony-arw': 2.0,
  'image/x-adobe-dng': 1.8,
  
  // Video - Slow
  'video/mp4': 5.0,
  'video/quicktime': 5.0,
  'video/x-msvideo': 6.0,
  'video/webm': 4.5,
  
  // Medical - Varies
  'application/dicom': 3.0,
  
  // Documents
  'application/pdf': 2.5,
  
  // Default
  'default': 2.0
};

/**
 * Estimate processing time for a file
 */
export function estimateProcessingTime(
  file: File,
  tier: 'free' | 'professional' | 'forensic' | 'enterprise' = 'free'
): ProcessingEstimate {
  const mimeType = file.type || 'default';
  const fileSizeMB = file.size / (1024 * 1024);
  
  // Base complexity from file type
  const complexity = FILE_COMPLEXITY[mimeType] || FILE_COMPLEXITY['default'];
  
  // Size factor (logarithmic scaling)
  const sizeFactor = Math.log10(Math.max(fileSizeMB, 0.1)) + 1;
  
  // Tier factor (higher tiers extract more fields = longer time)
  const tierMultiplier = {
    'free': 0.5,         // Basic extraction only
    'professional': 1.0, // Standard extraction
    'forensic': 1.5,     // Full extraction
    'enterprise': 1.5    // Full extraction
  }[tier];
  
  // Base time (seconds)
  const baseTime = 2.0;
  
  // Calculate estimate
  const estimatedSeconds = baseTime * complexity * sizeFactor * tierMultiplier;
  
  // Add variance (±30%)
  const variance = 0.3;
  const minTime = Math.max(1, estimatedSeconds * (1 - variance));
  const maxTime = estimatedSeconds * (1 + variance);
  
  // Determine factors
  const factors: string[] = [];
  
  if (fileSizeMB > 50) {
    factors.push('Large file size');
  }
  
  if (mimeType.startsWith('video/')) {
    factors.push('Video files require frame analysis');
  }
  
  if (mimeType.includes('raw') || mimeType.includes('cr2') || mimeType.includes('nef')) {
    factors.push('RAW format processing');
  }
  
  if (tier === 'forensic' || tier === 'enterprise') {
    factors.push('Comprehensive extraction (7,000+ fields)');
  }
  
  // Generate display text
  let displayText: string;
  let confidence: 'low' | 'medium' | 'high' = 'medium';
  
  if (estimatedSeconds < 3) {
    displayText = '~2-3 seconds';
    confidence = 'high';
  } else if (estimatedSeconds < 10) {
    displayText = `~${Math.round(minTime)}-${Math.round(maxTime)} seconds`;
    confidence = 'high';
  } else if (estimatedSeconds < 30) {
    displayText = `~${Math.round(estimatedSeconds / 5) * 5} seconds`;
    confidence = 'medium';
  } else if (estimatedSeconds < 60) {
    displayText = '~30-60 seconds';
    confidence = 'medium';
  } else {
    const minutes = Math.ceil(estimatedSeconds / 60);
    displayText = `~${minutes} minute${minutes > 1 ? 's' : ''}`;
    confidence = 'low';
  }
  
  return {
    estimatedSeconds: Math.round(estimatedSeconds),
    range: [Math.round(minTime), Math.round(maxTime)],
    displayText,
    confidence,
    factors
  };
}

/**
 * Get processing speed tier description
 */
export function getProcessingSpeedInfo(tier: string): string {
  const descriptions = {
    'free': 'Basic extraction - fastest processing',
    'professional': 'Standard extraction - moderate speed',
    'forensic': 'Comprehensive extraction - thorough analysis',
    'enterprise': 'Full forensic analysis - maximum detail'
  };
  
  return descriptions[tier as keyof typeof descriptions] || descriptions.professional;
}

/**
 * Format time duration for display
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return remainingSeconds > 0 
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return minutes > 0
      ? `${hours}h ${minutes}m`
      : `${hours}h`;
  }
}
