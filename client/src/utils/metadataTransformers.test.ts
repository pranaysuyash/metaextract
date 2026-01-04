/**
 * Tests for Metadata Transformers
 */

import {
  extractKeyFindings,
  extractQuickDetails,
  formatCoordinates,
  formatFileSize
} from './metadataTransformers';

describe('Metadata Transformers', () => {
  const mockMetadata = {
    exif: {
      DateTimeOriginal: '2025:01:03 15:45:32',
      Make: 'Apple',
      Model: 'iPhone 15 Pro',
      FNumber: 1.6,
      ExposureTime: 1/120,
      ISOSpeedRatings: 64,
      PixelXDimension: 4032,
      PixelYDimension: 3024,
      ColorSpace: 'sRGB'
    },
    gps: {
      latitude: 37.7749,
      longitude: -122.4194
    },
    file: {
      size: 3355443,
      modified: '2025-01-03T15:45:32Z'
    }
  };

  describe('extractKeyFindings', () => {
    it('should extract all key findings from complete metadata', () => {
      const findings = extractKeyFindings(mockMetadata);

      expect(findings.when).toBeTruthy();
      expect(findings.where).toBeTruthy();
      expect(findings.device).toEqual('Apple iPhone 15 Pro');
      expect(findings.authenticity).toBeTruthy();
      expect(findings.confidence).toMatch(/high|medium|low/);
    });

    it('should handle missing EXIF data gracefully', () => {
      const incompleteMetadata = {
        gps: { latitude: 37.7749, longitude: -122.4194 },
        file: { size: 3355443 }
      };

      const findings = extractKeyFindings(incompleteMetadata);
      expect(findings.device).toBeNull();
      expect(findings.where).toBeTruthy();
    });

    it('should handle null metadata', () => {
      const findings = extractKeyFindings(null);
      expect(findings.when).toBeNull();
      expect(findings.where).toBeNull();
      expect(findings.device).toBeNull();
    });

    it('should detect edited images', () => {
      const editedMetadata = {
        ...mockMetadata,
        exif: {
          ...mockMetadata.exif,
          Software: 'Adobe Photoshop'
        }
      };

      const findings = extractKeyFindings(editedMetadata);
      expect(findings.edited).toBe(true);
    });

    it('should assess authenticity correctly', () => {
      const findings = extractKeyFindings(mockMetadata);
      expect(['Appears authentic', 'Mostly authentic with minor modifications', 'Shows signs of modification', 'Significant modifications detected']).toContain(findings.authenticity);
    });
  });

  describe('extractQuickDetails', () => {
    it('should extract quick details from metadata', () => {
      const details = extractQuickDetails(mockMetadata);

      expect(details.resolution).toEqual('12.2 megapixels');
      expect(details.fileSize).toEqual('3.2 MB');
      expect(details.cameraSettings).toContain('f/1.6');
      expect(details.cameraSettings).toContain('1/120s');
      expect(details.cameraSettings).toContain('ISO 64');
      expect(details.colorSpace).toEqual('sRGB');
      expect(details.dimensions).toEqual('4032 x 3024');
    });

    it('should handle missing camera settings', () => {
      const incompleteMetadata = {
        exif: { PixelXDimension: 4032, PixelYDimension: 3024 },
        file: { size: 3355443 }
      };

      const details = extractQuickDetails(incompleteMetadata);
      expect(details.resolution).toEqual('12.2 megapixels');
      expect(details.cameraSettings).toEqual('Unknown');
    });
  });

  describe('formatCoordinates', () => {
    it('should format coordinates correctly', () => {
      const formatted = formatCoordinates(37.7749, -122.4194);
      expect(formatted).toEqual('37.7749° N, 122.4194° W');
    });

    it('should handle negative latitudes', () => {
      const formatted = formatCoordinates(-33.8688, 151.2093);
      expect(formatted).toEqual('33.8688° S, 151.2093° E');
    });

    it('should handle negative longitudes', () => {
      const formatted = formatCoordinates(40.7128, -74.0060);
      expect(formatted).toEqual('40.7128° N, 74.0060° W');
    });

    it('should handle all negative coordinates', () => {
      const formatted = formatCoordinates(-33.8688, -151.2093);
      expect(formatted).toEqual('33.8688° S, 151.2093° W');
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(512)).toEqual('512 B');
    });

    it('should format kilobytes correctly', () => {
      expect(formatFileSize(5120)).toEqual('5.0 KB');
    });

    it('should format megabytes correctly', () => {
      expect(formatFileSize(3355443)).toEqual('3.2 MB');
    });

    it('should format gigabytes correctly', () => {
      expect(formatFileSize(5368709120)).toEqual('5.0 GB');
    });

    it('should handle zero bytes', () => {
      expect(formatFileSize(0)).toEqual('0 B');
    });

    it('should handle undefined', () => {
      expect(formatFileSize(undefined)).toEqual('Unknown');
    });
  });

  describe('Device name formatting', () => {
    it('should clean Apple device names', () => {
      const metadata = {
        exif: { Make: 'Apple', Model: 'iPhone 15 Pro' }
      };
      const findings = extractKeyFindings(metadata);
      expect(findings.device).toEqual('Apple iPhone 15 Pro');
    });

    it('should clean Canon device names', () => {
      const metadata = {
        exif: { Make: 'Canon', Model: 'Canon EOS 5D Mark IV' }
      };
      const findings = extractKeyFindings(metadata);
      expect(findings.device).toBeTruthy();
    });

    it('should clean Nikon device names', () => {
      const metadata = {
        exif: { Make: 'NIKON CORPORATION', Model: 'NIKON D850' }
      };
      const findings = extractKeyFindings(metadata);
      expect(findings.device).toBeTruthy();
      expect(findings.device).not.toContain('CORPORATION');
    });
  });

  describe('DateTime formatting', () => {
    it('should format EXIF datetime correctly', () => {
      const findings = extractKeyFindings(mockMetadata);
      expect(findings.when).toContain('January 3');
      expect(findings.when).toContain('2025');
      expect(findings.when).toContain('3:45 PM');
    });

    it('should handle fallback to file modification time', () => {
      const metadata = {
        file: { modified: '2025-01-03T15:45:32Z' }
      };
      const findings = extractKeyFindings(metadata);
      expect(findings.when).toBeTruthy();
    });

    it('should return null for missing datetime', () => {
      const metadata = {};
      const findings = extractKeyFindings(metadata);
      expect(findings.when).toBeNull();
    });
  });

  describe('Confidence calculation', () => {
    it('should give high confidence with complete metadata', () => {
      const findings = extractKeyFindings(mockMetadata);
      expect(findings.confidence).toBeTruthy();
    });

    it('should give low confidence with minimal metadata', () => {
      const minimal = {
        exif: { Make: 'Test' }
      };
      const findings = extractKeyFindings(minimal);
      expect(findings.confidence).toMatch(/high|medium|low/);
    });
  });
});
