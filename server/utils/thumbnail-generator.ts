/**
 * Thumbnail Generation Utility
 * 
 * Generates optimized thumbnails for CDN delivery.
 * Uses sharp for efficient image processing.
 * EXIF is stripped from thumbnails for privacy (not from extraction).
 */

import sharp from 'sharp';

export interface ThumbnailOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'jpeg' | 'png' | 'avif';
}

export interface ThumbnailResult {
  buffer: Buffer;
  width: number;
  height: number;
  format: string;
  sizeBytes: number;
}

const DEFAULT_OPTIONS: ThumbnailOptions = {
  width: 400,
  height: 400,
  quality: 80,
  format: 'webp',
};

/**
 * Generate a thumbnail from an image buffer.
 * EXIF metadata is stripped for privacy.
 * 
 * @param buffer - Original image buffer
 * @param options - Thumbnail options
 * @returns Thumbnail result with buffer and metadata
 */
export async function generateThumbnail(
  buffer: Buffer,
  options: ThumbnailOptions = {}
): Promise<ThumbnailResult> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  let pipeline = sharp(buffer)
    .rotate() // Auto-orient based on EXIF, then strip EXIF
    .resize(opts.width, opts.height, {
      fit: 'inside',
      withoutEnlargement: true,
    });

  // Apply format conversion
  switch (opts.format) {
    case 'webp':
      pipeline = pipeline.webp({ quality: opts.quality });
      break;
    case 'avif':
      pipeline = pipeline.avif({ quality: opts.quality });
      break;
    case 'png':
      pipeline = pipeline.png({ quality: opts.quality });
      break;
    case 'jpeg':
    default:
      pipeline = pipeline.jpeg({ quality: opts.quality });
      break;
  }

  const result = await pipeline.toBuffer({ resolveWithObject: true });

  return {
    buffer: result.data,
    width: result.info.width,
    height: result.info.height,
    format: result.info.format,
    sizeBytes: result.data.length,
  };
}

/**
 * Generate multiple thumbnail sizes for responsive delivery.
 * 
 * @param buffer - Original image buffer
 * @returns Object with small, medium, and large thumbnails
 */
export async function generateResponsiveThumbnails(buffer: Buffer): Promise<{
  small: ThumbnailResult;
  medium: ThumbnailResult;
  large: ThumbnailResult;
}> {
  const [small, medium, large] = await Promise.all([
    generateThumbnail(buffer, { width: 150, height: 150, format: 'webp' }),
    generateThumbnail(buffer, { width: 400, height: 400, format: 'webp' }),
    generateThumbnail(buffer, { width: 800, height: 800, format: 'webp' }),
  ]);

  return { small, medium, large };
}

/**
 * Check if a buffer is a valid image that sharp can process.
 * 
 * @param buffer - Buffer to validate
 * @returns True if valid image
 */
export async function isValidImage(buffer: Buffer): Promise<boolean> {
  try {
    await sharp(buffer).metadata();
    return true;
  } catch {
    return false;
  }
}

/**
 * Get image dimensions without full processing.
 * 
 * @param buffer - Image buffer
 * @returns Width and height
 */
export async function getImageDimensions(buffer: Buffer): Promise<{
  width: number;
  height: number;
} | null> {
  try {
    const metadata = await sharp(buffer).metadata();
    if (metadata.width && metadata.height) {
      return { width: metadata.width, height: metadata.height };
    }
    return null;
  } catch {
    return null;
  }
}
