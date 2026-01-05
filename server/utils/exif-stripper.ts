/**
 * EXIF Stripper Utility
 * 
 * Strips EXIF/metadata from images for privacy protection.
 * Uses sharp which removes metadata by default during processing.
 */

import sharp from 'sharp';

/**
 * Strip EXIF and other metadata from an image buffer.
 * Sharp automatically strips metadata when processing images.
 * 
 * @param buffer - Original image buffer
 * @returns Buffer with metadata stripped
 */
export async function stripExif(buffer: Buffer): Promise<Buffer> {
  try {
    // sharp's rotate() without args auto-orients based on EXIF, then strips EXIF
    // This is the simplest way to strip metadata while preserving orientation
    return await sharp(buffer)
      .rotate() // Auto-orient based on EXIF, then strip
      .toBuffer();
  } catch (error) {
    // If sharp fails (unsupported format), return original
    console.warn('EXIF stripping failed, returning original:', error);
    return buffer;
  }
}

/**
 * Check if an image has GPS/location metadata.
 * This is useful for warning users about location data.
 * 
 * @param buffer - Image buffer
 * @returns Object with hasLocation and coordinates if found
 */
export async function checkGpsMetadata(buffer: Buffer): Promise<{
  hasLocation: boolean;
  latitude?: number;
  longitude?: number;
}> {
  try {
    const metadata = await sharp(buffer).metadata();
    // sharp doesn't directly expose GPS, but we can detect if EXIF exists
    // For detailed GPS extraction, the Python extractor is used
    const hasExif = metadata.exif !== undefined;
    return { hasLocation: hasExif }; // Simplified check
  } catch {
    return { hasLocation: false };
  }
}

/**
 * Process image with optional metadata preservation.
 * 
 * @param buffer - Original image buffer  
 * @param preserveMetadata - If true, keep original metadata
 * @returns Processed buffer
 */
export async function processImageBuffer(
  buffer: Buffer,
  preserveMetadata: boolean = false
): Promise<Buffer> {
  if (preserveMetadata) {
    return buffer; // Return original with metadata intact
  }
  return stripExif(buffer);
}
