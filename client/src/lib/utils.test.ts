/**
 * Unit tests for utility functions
 */

import {
  cn,
  formatFileSize,
  getFileIcon,
  getFileExtension,
  isFileTypeSupported,
  getAuthenticityColor,
  formatDate,
} from '@/lib/utils';

describe('Utility Functions', () => {
  describe('cn (classnames)', () => {
    it('should merge classnames correctly', () => {
      const result = cn('base-class', 'extra-class');
      expect(result).toContain('base-class');
      expect(result).toContain('extra-class');
    });

    it('should handle conditional classes', () => {
      const result = cn(
        'base-class',
        true && 'conditional-true',
        false && 'conditional-false'
      );
      expect(result).toContain('base-class');
      expect(result).toContain('conditional-true');
      expect(result).not.toContain('conditional-false');
    });

    it('should merge tailwind classes intelligently', () => {
      const result = cn('p-2 p-4', 'm-2 m-4');
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
    });

    it('should handle array inputs', () => {
      const result = cn(['class1', 'class2'], ['class3', 'class4']);
      expect(result).toContain('class1');
      expect(result).toContain('class4');
    });

    it('should handle object inputs', () => {
      const result = cn({
        'active-class': true,
        'inactive-class': false,
      });
      expect(result).toContain('active-class');
      expect(result).not.toContain('inactive-class');
    });
  });

  describe('formatFileSize', () => {
    it('should format 0 bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
    });

    it('should format bytes correctly', () => {
      expect(formatFileSize(500)).toBe('500 Bytes');
    });

    it('should format kilobytes correctly', () => {
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(2048)).toBe('2 KB');
    });

    it('should format megabytes correctly', () => {
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
      expect(formatFileSize(5 * 1024 * 1024)).toBe('5 MB');
    });

    it('should format gigabytes correctly', () => {
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('should handle fractional values', () => {
      // Note: toFixed(2) doesn't show trailing zero, so 1.5 KB not 1.50 KB
      expect(formatFileSize(1536)).toBe('1.5 KB');
    });
  });

  describe('getFileIcon', () => {
    it('should return FileImage for image types', () => {
      expect(getFileIcon('image/jpeg')).toBe('FileImage');
      expect(getFileIcon('image/png')).toBe('FileImage');
      expect(getFileIcon('image/tiff')).toBe('FileImage');
    });

    it('should return FileText for PDF', () => {
      expect(getFileIcon('application/pdf')).toBe('FileText');
    });

    it('should return Database for application/dicom (not image/dicom which matches image first)', () => {
      expect(getFileIcon('application/dicom')).toBe('Database');
      // image/dicom is matched by 'image' first, so it returns FileImage
      expect(getFileIcon('image/dicom')).toBe('FileImage');
    });

    it('should return Music for audio types', () => {
      expect(getFileIcon('audio/mp3')).toBe('Music');
      expect(getFileIcon('audio/wav')).toBe('Music');
    });

    it('should return Video for video types', () => {
      expect(getFileIcon('video/mp4')).toBe('Video');
      expect(getFileIcon('video/avi')).toBe('Video');
      expect(getFileIcon('video/quicktime')).toBe('Video');
    });

    it('should return File for unknown types', () => {
      expect(getFileIcon('application/zip')).toBe('File');
      expect(getFileIcon('text/plain')).toBe('File');
    });
  });

  describe('getFileExtension', () => {
    it('should extract file extension from filename', () => {
      expect(getFileExtension('document.pdf')).toBe('pdf');
      expect(getFileExtension('image.jpg')).toBe('jpg');
      expect(getFileExtension('archive.tar.gz')).toBe('gz');
    });

    it('should return lowercase extension', () => {
      expect(getFileExtension('file.PDF')).toBe('pdf');
      expect(getFileExtension('file.JpEg')).toBe('jpeg');
    });

    it('should return empty string for files without extension', () => {
      expect(getFileExtension('filename')).toBe('');
      expect(getFileExtension('.hidden')).toBe('hidden');
    });

    it('should handle edge cases', () => {
      expect(getFileExtension('')).toBe('');
      expect(getFileExtension('file.')).toBe('');
    });
  });

  describe('isFileTypeSupported', () => {
    it('should support common image types', () => {
      expect(isFileTypeSupported('image/jpeg')).toBe(true);
      expect(isFileTypeSupported('image/png')).toBe(true);
      expect(isFileTypeSupported('image/tiff')).toBe(true);
      expect(isFileTypeSupported('image/gif')).toBe(true);
      expect(isFileTypeSupported('image/bmp')).toBe(true);
      expect(isFileTypeSupported('image/webp')).toBe(true);
    });

    it('should support PDF', () => {
      expect(isFileTypeSupported('application/pdf')).toBe(true);
    });

    it('should support DICOM', () => {
      expect(isFileTypeSupported('application/dicom')).toBe(true);
      expect(isFileTypeSupported('image/dicom')).toBe(true);
    });

    it('should support audio types', () => {
      expect(isFileTypeSupported('audio/mp3')).toBe(true);
      expect(isFileTypeSupported('audio/wav')).toBe(true);
      expect(isFileTypeSupported('audio/flac')).toBe(true);
    });

    it('should support video types', () => {
      expect(isFileTypeSupported('video/mp4')).toBe(true);
      expect(isFileTypeSupported('video/avi')).toBe(true);
      expect(isFileTypeSupported('video/mov')).toBe(true);
    });

    it('should reject unsupported types', () => {
      expect(isFileTypeSupported('application/zip')).toBe(false);
      expect(isFileTypeSupported('text/plain')).toBe(false);
      expect(isFileTypeSupported('application/json')).toBe(false);
    });

    it('should be case insensitive', () => {
      expect(isFileTypeSupported('IMAGE/JPEG')).toBe(true);
      expect(isFileTypeSupported('Image/Png')).toBe(true);
    });
  });

  describe('getAuthenticityColor', () => {
    it('should return emerald-400 for high scores (80+)', () => {
      expect(getAuthenticityColor(80)).toBe('text-emerald-400');
      expect(getAuthenticityColor(90)).toBe('text-emerald-400');
      expect(getAuthenticityColor(100)).toBe('text-emerald-400');
    });

    it('should return yellow-400 for medium scores (60-79)', () => {
      expect(getAuthenticityColor(60)).toBe('text-yellow-400');
      expect(getAuthenticityColor(70)).toBe('text-yellow-400');
      expect(getAuthenticityColor(79)).toBe('text-yellow-400');
    });

    it('should return red-400 for low scores (<60)', () => {
      expect(getAuthenticityColor(59)).toBe('text-red-400');
      expect(getAuthenticityColor(50)).toBe('text-red-400');
      expect(getAuthenticityColor(0)).toBe('text-red-400');
    });
  });

  describe('formatDate', () => {
    it('should format valid date strings', () => {
      const result = formatDate('2024-01-15T10:30:00Z');
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });

    it('should handle invalid date strings', () => {
      const result = formatDate('invalid-date');
      expect(result).toBe('Invalid Date');
    });

    it('should format different date formats', () => {
      expect(formatDate('2024-12-25')).toBeTruthy();
      expect(formatDate('2024-01-01T00:00:00.000Z')).toBeTruthy();
    });
  });
});
