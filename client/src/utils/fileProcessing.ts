/**
 * Utility functions for file processing and validation
 * Extracted from SimpleUploadZone component for reusability
 */

/**
 * Extract file extension from filename
 * Returns null if no valid extension found
 */
export const getFileExtension = (name: string): string | null => {
  if (!name || typeof name !== 'string') return null;
  
  const index = name.lastIndexOf('.');
  if (index <= 0) return null; // No extension or starts with dot (hidden file)
  
  return name.slice(index).toLowerCase();
};

/**
 * Probe image dimensions from a file
 * Returns width and height or null if unable to determine
 */
export const probeImageDimensions = async (
  file: File
): Promise<{ width: number; height: number } | null> => {
  try {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      return null;
    }

    const objectUrl = URL.createObjectURL(file);
    
    const result = await new Promise<{ width: number; height: number } | null>(resolve => {
      const img = new Image();
      
      img.onload = () => {
        resolve({ width: img.width, height: img.height });
        URL.revokeObjectURL(objectUrl);
      };
      
      img.onerror = () => {
        resolve(null);
        URL.revokeObjectURL(objectUrl);
      };
      
      img.src = objectUrl;
    });
    
    return result;
  } catch {
    return null;
  }
};

/**
 * Validate file type for image upload
 * Returns true if file type is supported
 */
export const isValidImageType = (file: File): boolean => {
  const validTypes = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/heic',
    'image/heif',
    'image/tiff',
    'image/bmp'
  ];
  
  return validTypes.includes(file.type.toLowerCase());
};

/**
 * Calculate file size in human-readable format
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Check if file size exceeds limit
 */
export const isFileTooLarge = (file: File, maxBytes: number): boolean => {
  return file.size > maxBytes;
};

/**
 * Calculate megapixels from dimensions
 */
export const calculateMegapixels = (width: number, height: number): number => {
  return (width * height) / 1000000;
};

/**
 * Validate image dimensions against maximum allowed megapixels
 */
export const exceedsMegapixelLimit = (
  width: number, 
  height: number, 
  maxMegapixels: number
): boolean => {
  const megapixels = calculateMegapixels(width, height);
  return megapixels > maxMegapixels;
};