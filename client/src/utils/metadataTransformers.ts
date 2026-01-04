/**
 * Metadata Transformers
 *
 * Convert raw technical metadata into user-friendly insights and findings.
 * This module translates metadata into plain English answers to key questions:
 * - When was this captured?
 * - Where was it captured?
 * - What device captured it?
 * - Is it authentic?
 */

/**
 * Key findings extracted from metadata
 */
export interface KeyFindings {
  when: string | null;        // "January 3, 2025 at 3:45 PM"
  where: string | null;       // "San Francisco, California"
  device: string | null;      // "iPhone 15 Pro"
  edited: boolean;            // false
  authenticity: string;       // "Appears authentic"
  confidence: 'high' | 'medium' | 'low';
}

/**
 * Enhanced location information
 */
export interface EnhancedLocation {
  formatted: string;          // "San Francisco, CA, USA"
  coordinates: string;        // "37.7749° N, 122.4194° W"
  mapUrl: string;             // Google Maps URL
  confidence: 'high' | 'medium' | 'low';
  country?: string;
  region?: string;
  city?: string;
}

/**
 * Quick details for summary display
 */
export interface QuickDetails {
  resolution: string;         // "12.2 megapixels"
  fileSize: string;           // "3.2 MB"
  cameraSettings: string;     // "f/1.6, 1/120s, ISO 64"
  colorSpace: string;         // "sRGB"
  dimensions: string;         // "4032 x 3024"
}

/**
 * Extract key findings from raw metadata
 */
export function extractKeyFindings(metadata: any): KeyFindings {
  const findings: KeyFindings = {
    when: formatDateTimeOriginal(metadata),
    where: extractLocation(metadata),
    device: formatDeviceName(metadata),
    edited: detectEditing(metadata),
    authenticity: assessAuthenticity(metadata),
    confidence: calculateConfidence(metadata)
  };

  return findings;
}

/**
 * Format datetime original into readable format
 * e.g., "January 3, 2025 at 3:45 PM"
 */
function formatDateTimeOriginal(metadata: any): string | null {
  try {
    // Try EXIF DateTimeOriginal first (most accurate)
    const dateTimeOriginal = metadata?.exif?.DateTimeOriginal ||
                            metadata?.metadata?.exif?.DateTimeOriginal;
    if (dateTimeOriginal) {
      const date = parseExifDate(dateTimeOriginal);
      return formatDateWithTime(date);
    }

    // Fall back to file modification time
    const fileModified = metadata?.file?.modified || metadata?.metadata?.file?.modified;
    if (fileModified) {
      const date = new Date(fileModified);
      return formatDateWithTime(date);
    }

    return null;
  } catch (error) {
    console.warn('Error formatting datetime:', error);
    return null;
  }
}

/**
 * Parse EXIF date format: "2025:01:03 15:45:32"
 */
function parseExifDate(exifDateString: string): Date {
  if (!exifDateString) throw new Error('Invalid EXIF date');

  const parts = exifDateString.match(/(\d{4}):(\d{2}):(\d{2})\s(\d{2}):(\d{2}):(\d{2})/);
  if (!parts) throw new Error('Invalid EXIF date format');

  const [, year, month, day, hour, minute, second] = parts;
  return new Date(
    parseInt(year), 
    parseInt(month) - 1, 
    parseInt(day),
    parseInt(hour),
    parseInt(minute),
    parseInt(second)
  );
}

/**
 * Format date with time: "January 3, 2025 at 3:45 PM"
 */
function formatDateWithTime(date: Date): string {
  const dateOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  };
  
  const timeOptions: Intl.DateTimeFormatOptions = {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  };

  const dateStr = date.toLocaleDateString('en-US', dateOptions);
  const timeStr = date.toLocaleTimeString('en-US', timeOptions);
  
  return `${dateStr} at ${timeStr}`;
}

/**
 * Extract location from GPS metadata
 * Returns formatted address or "Unknown location"
 */
function extractLocation(metadata: any): string | null {
  try {
    const gps = metadata?.gps || metadata?.metadata?.gps;
    if (!gps || (!gps.latitude && !gps.Latitude)) {
      return null;
    }

    // For now, just show coordinates
    // This will be enhanced with reverse geocoding in Phase 1.2
    const lat = gps.latitude || gps.Latitude;
    const lng = gps.longitude || gps.Longitude;
    
    if (!lat || !lng) return null;

    // Format coordinates
    return formatCoordinates(lat, lng);
  } catch (error) {
    console.warn('Error extracting location:', error);
    return null;
  }
}

/**
 * Format coordinates: "37.7749° N, 122.4194° W"
 */
export function formatCoordinates(latitude: number, longitude: number): string {
  const formatLat = (lat: number) => {
    const dir = lat >= 0 ? 'N' : 'S';
    return `${Math.abs(lat).toFixed(4)}° ${dir}`;
  };

  const formatLng = (lng: number) => {
    const dir = lng >= 0 ? 'E' : 'W';
    return `${Math.abs(lng).toFixed(4)}° ${dir}`;
  };

  return `${formatLat(latitude)}, ${formatLng(longitude)}`;
}

/**
 * Format device name from EXIF data
 * e.g., "iPhone 15 Pro" instead of "Apple iPhone15,5"
 */
function formatDeviceName(metadata: any): string | null {
  try {
    const exif = metadata?.exif || metadata?.metadata?.exif;
    if (!exif) return null;

    const make = exif.Make || exif.make;
    const model = exif.Model || exif.model;

    if (!make && !model) return null;

    // Clean up device names
    const cleanMake = make ? cleanDeviceName(make) : '';
    const cleanModel = model ? cleanDeviceName(model) : '';

    if (cleanMake && cleanModel) {
      return `${cleanMake} ${cleanModel}`.trim();
    }
    return cleanMake || cleanModel || null;
  } catch (error) {
    console.warn('Error formatting device name:', error);
    return null;
  }
}

/**
 * Clean device names for display
 * "Apple" → "Apple" (unchanged for Apple devices)
 * "NIKON CORPORATION" → "Nikon"
 * "Canon" → "Canon"
 */
function cleanDeviceName(name: string): string {
  if (!name) return '';

  // Replace common patterns
  let cleaned = name
    .replace(/CORPORATION/gi, '')
    .replace(/ELECTRONICS?/gi, '')
    .replace(/INC\.?/gi, '')
    .trim();

  // Special handling for common models like "iPhone 15 Pro"
  // Keep "iPhone" as-is, only clean other words
  if (cleaned.toLowerCase().includes('iphone')) {
    const parts = cleaned.split(' ');
    return parts.map((word, idx) => {
      if (word.toLowerCase() === 'iphone') return 'iPhone';
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    }).join(' ');
  }

  // Standard cleaning for other brands
  return cleaned
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Detect if image has been edited
 * Looks for editing software markers, metadata modifications, etc.
 */
function detectEditing(metadata: any): boolean {
  try {
    const exif = metadata?.exif || metadata?.metadata?.exif;
    if (!exif) return false;

    // Software tags indicating editing
    const editingSoftware = [
      'Photoshop',
      'GIMP',
      'Lightroom',
      'Snapseed',
      'Pixlr',
      'Affinity',
      'Procreate'
    ];

    const software = exif.Software || exif.software || '';
    const hasEditingSoftware = editingSoftware.some(s => 
      software.toLowerCase().includes(s.toLowerCase())
    );

    // Check for processing software
    const processingMarkers = [
      exif.ProcessingSoftware,
      exif.processing软件
    ].filter(Boolean);

    return hasEditingSoftware || processingMarkers.length > 0;
  } catch (error) {
    console.warn('Error detecting editing:', error);
    return false;
  }
}

/**
 * Assess file authenticity based on multiple factors
 * Returns a human-readable assessment
 */
function assessAuthenticity(metadata: any): string {
  try {
    const score = calculateAuthenticityScore(metadata);

    if (score >= 85) {
      return 'Appears authentic';
    } else if (score >= 60) {
      return 'Mostly authentic with minor modifications';
    } else if (score >= 40) {
      return 'Shows signs of modification';
    } else {
      return 'Significant modifications detected';
    }
  } catch (error) {
    console.warn('Error assessing authenticity:', error);
    return 'Unable to assess';
  }
}

/**
 * Calculate authenticity score (0-100)
 * Based on multiple integrity checks
 */
function calculateAuthenticityScore(metadata: any): number {
  let score = 100;
  let checksPerformed = 0;

  try {
    // Check for editing software (major penalty)
    if (detectEditing(metadata)) {
      score -= 30;
    }
    checksPerformed++;

    // Check EXIF integrity
    const exif = metadata?.exif || metadata?.metadata?.exif;
    if (!exif || Object.keys(exif).length === 0) {
      score -= 10; // No EXIF is suspicious
    }
    checksPerformed++;

    // Check GPS consistency
    const gps = metadata?.gps || metadata?.metadata?.gps;
    if (gps) {
      const lat = gps.latitude || gps.Latitude;
      const lng = gps.longitude || gps.Longitude;
      
      // Impossible coordinates indicate tampering
      if (lat && (lat > 90 || lat < -90)) {
        score -= 25;
      }
      if (lng && (lng > 180 || lng < -180)) {
        score -= 25;
      }
    }
    checksPerformed++;

    // Check timestamp consistency
    const creationDate = formatDateTimeOriginal(metadata);
    if (creationDate) {
      const date = parseExifDate(creationDate);
      const now = new Date();
      
      // Future dates indicate tampering
      if (date > now) {
        score -= 20;
      }
      
      // Very old dates (before digital cameras) are suspicious
      if (date.getFullYear() < 2000) {
        score -= 15;
      }
    }
    checksPerformed++;

    // Ensure score doesn't go below 0
    return Math.max(0, Math.min(100, score));
  } catch (error) {
    console.warn('Error calculating authenticity score:', error);
    return 50; // Neutral score if calculation fails
  }
}

/**
 * Calculate confidence level (high/medium/low)
 * Based on amount and quality of metadata available
 */
function calculateConfidence(metadata: any): 'high' | 'medium' | 'low' {
  try {
    let confidence = 0;
    let maxScore = 0;

    // Check for EXIF data
    const exif = metadata?.exif || metadata?.metadata?.exif;
    if (exif && Object.keys(exif).length > 10) {
      confidence += 30;
    }
    maxScore += 30;

    // Check for GPS data
    const gps = metadata?.gps || metadata?.metadata?.gps;
    if (gps && (gps.latitude || gps.Latitude)) {
      confidence += 20;
    }
    maxScore += 20;

    // Check for ISO and other technical data
    if (exif?.ISO || exif?.iso) {
      confidence += 15;
    }
    maxScore += 15;

    // Check for datetime
    if (metadata?.file?.created || exif?.DateTimeOriginal) {
      confidence += 20;
    }
    maxScore += 20;

    // Check for lens/camera data
    if (exif?.LensModel || exif?.lensModel) {
      confidence += 15;
    }
    maxScore += 15;

    const percentile = (confidence / maxScore) * 100;

    if (percentile >= 70) return 'high';
    if (percentile >= 40) return 'medium';
    return 'low';
  } catch (error) {
    console.warn('Error calculating confidence:', error);
    return 'low';
  }
}

/**
 * Extract quick details for summary card
 */
export function extractQuickDetails(metadata: any): QuickDetails {
  const exif = metadata?.exif || metadata?.metadata?.exif;
  const file = metadata?.file || metadata?.metadata?.file;

  return {
    resolution: formatResolution(exif?.PixelXDimension, exif?.PixelYDimension),
    fileSize: formatFileSize(file?.size || metadata?.size),
    cameraSettings: formatCameraSettings(exif),
    colorSpace: exif?.ColorSpace || exif?.colorSpace || 'Unknown',
    dimensions: formatDimensions(exif?.PixelXDimension, exif?.PixelYDimension)
  };
}

/**
 * Format resolution: "12.2 megapixels"
 */
function formatResolution(width?: number, height?: number): string {
  if (!width || !height) return 'Unknown';
  
  const megapixels = (width * height) / 1_000_000;
  return `${megapixels.toFixed(1)} megapixels`;
}

/**
 * Format file size: "3.2 MB"
 */
export function formatFileSize(bytes?: number): string {
  if (bytes === undefined || bytes === null) return 'Unknown';
  
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

/**
 * Format camera settings: "f/1.6, 1/120s, ISO 64"
 */
function formatCameraSettings(exif?: any): string {
  if (!exif) return 'Unknown';

  const parts = [];

  // Aperture
  if (exif.FNumber || exif.fNumber) {
    const fNum = exif.FNumber || exif.fNumber;
    parts.push(`f/${typeof fNum === 'string' ? fNum : fNum.toFixed(1)}`);
  }

  // Shutter speed
  if (exif.ExposureTime || exif.exposureTime) {
    const exposure = exif.ExposureTime || exif.exposureTime;
    if (exposure < 1) {
      parts.push(`1/${Math.round(1 / exposure)}s`);
    } else {
      parts.push(`${exposure}s`);
    }
  }

  // ISO
  if (exif.ISOSpeedRatings || exif.iso) {
    parts.push(`ISO ${exif.ISOSpeedRatings || exif.iso}`);
  }

  return parts.length > 0 ? parts.join(', ') : 'Unknown';
}

/**
 * Format dimensions: "4032 x 3024"
 */
function formatDimensions(width?: number, height?: number): string {
  if (!width || !height) return 'Unknown';
  return `${width} x ${height}`;
}
