/**
 * CDN Helper Utility
 * 
 * Centralizes URL generation for assets.
 * Allows switching between local serving and CDN (CloudFront/S3/R2).
 */

const CDN_BASE_URL = process.env.CDN_BASE_URL || ''; // Empty = relative/local

export interface CdnAsset {
  key: string;      // Storage key/path
  bucket?: string;  // Optional bucket name
  variant?: 'original' | 'thumbnail' | 'preview';
}

/**
 * Generate a public URL for an asset.
 * 
 * @param asset - Asset details
 * @returns Full public URL
 */
export function getCdnUrl(asset: CdnAsset): string {
  const { key, variant } = asset;
  
  // If no CDN configured, serve via local API proxy
  if (!CDN_BASE_URL) {
    if (variant === 'thumbnail') {
      // Assuming key is resultId for local thumbnail endpoint
      return `/api/images_mvp/thumbnail/${key}`;
    }
    // Generic local file serve (not implemented in MVP yet, usually S3 signed url)
    return `/api/files/${key}`;
  }

  // Production CDN URL construction
  // e.g. https://cdn.metaextract.com/thumbnails/key.webp
  const path = variant ? `${variant}s/${key}` : key;
  return new URL(path, CDN_BASE_URL).toString();
}

/**
 * Generate a signed URL for private assets (Time-limited).
 * Placeholder for S3/CloudFront signed URLs.
 */
export async function getSignedUrl(key: string, expiresInSeconds = 3600): Promise<string> {
  // Mock implementation
  return getCdnUrl({ key });
}
