/**
 * Tests for Geolocation Utilities
 */

import {
  validateCoordinates,
  calculateDistance,
  reverseGeocode,
  formatCoordinatesForDisplay,
  parseCoordinateString,
  getCoordinateConfidence,
  generateGoogleMapsUrl,
  generateOpenStreetMapUrl
} from './geolocation';

describe('Geolocation Utilities', () => {
  describe('validateCoordinates', () => {
    it('should validate correct coordinates', () => {
      expect(validateCoordinates(37.7749, -122.4194)).toBe(true);
      expect(validateCoordinates(0, 0)).toBe(true);
      expect(validateCoordinates(90, 180)).toBe(true);
      expect(validateCoordinates(-90, -180)).toBe(true);
    });

    it('should reject invalid latitude', () => {
      expect(validateCoordinates(91, 0)).toBe(false);
      expect(validateCoordinates(-91, 0)).toBe(false);
    });

    it('should reject invalid longitude', () => {
      expect(validateCoordinates(0, 181)).toBe(false);
      expect(validateCoordinates(0, -181)).toBe(false);
    });

    it('should accept boundary values', () => {
      expect(validateCoordinates(90, 180)).toBe(true);
      expect(validateCoordinates(-90, -180)).toBe(true);
    });
  });

  describe('calculateDistance', () => {
    it('should calculate distance between two points', () => {
      // San Francisco to Los Angeles (approximately 559 km)
      const distance = calculateDistance(37.7749, -122.4194, 34.0522, -118.2437);
      expect(distance).toBeGreaterThan(500);
      expect(distance).toBeLessThan(650);
    });

    it('should return 0 for same coordinates', () => {
      const distance = calculateDistance(37.7749, -122.4194, 37.7749, -122.4194);
      expect(distance).toBeLessThan(1);
    });

    it('should calculate distance across equator', () => {
      // North pole to south pole (approximately 20000 km)
      const distance = calculateDistance(90, 0, -90, 0);
      expect(distance).toBeGreaterThan(19000);
      expect(distance).toBeLessThan(21000);
    });
  });

  describe('formatCoordinatesForDisplay', () => {
    it('should format positive coordinates', () => {
      const formatted = formatCoordinatesForDisplay(37.7749, -122.4194);
      expect(formatted).toContain('37.7749');
      expect(formatted).toContain('122.4194');
      expect(formatted).toContain('N');
      expect(formatted).toContain('W');
    });

    it('should format negative latitude as South', () => {
      const formatted = formatCoordinatesForDisplay(-33.8688, 151.2093);
      expect(formatted).toContain('33.8688');
      expect(formatted).toContain('S');
    });

    it('should format negative longitude as West', () => {
      const formatted = formatCoordinatesForDisplay(40.7128, -74.0060);
      expect(formatted).toContain('74.0060');
      expect(formatted).toContain('W');
    });
  });

  describe('parseCoordinateString', () => {
    it('should parse decimal format', () => {
      const result = parseCoordinateString('37.7749, -122.4194');
      expect(result).not.toBeNull();
      expect(result?.latitude).toBeCloseTo(37.7749);
      expect(result?.longitude).toBeCloseTo(-122.4194);
    });

    it('should parse format without spaces', () => {
      const result = parseCoordinateString('37.7749,-122.4194');
      expect(result).not.toBeNull();
      expect(result?.latitude).toBeCloseTo(37.7749);
      expect(result?.longitude).toBeCloseTo(-122.4194);
    });

    it('should reject invalid format', () => {
      const result = parseCoordinateString('invalid coordinates');
      expect(result).toBeNull();
    });

    it('should reject out-of-bounds coordinates', () => {
      const result = parseCoordinateString('95, 200');
      expect(result).toBeNull();
    });

    it('should handle negative coordinates', () => {
      const result = parseCoordinateString('-33.8688, 151.2093');
      expect(result).not.toBeNull();
      expect(result?.latitude).toBeCloseTo(-33.8688);
      expect(result?.longitude).toBeCloseTo(151.2093);
    });
  });

  describe('getCoordinateConfidence', () => {
    it('should return high confidence for precise coordinates', () => {
      // 6+ decimal places is high precision
      const confidence = getCoordinateConfidence(37.774912, -122.419485);
      expect(confidence).toBe('high');
    });

    it('should return medium confidence for moderate precision', () => {
      // 4-5 decimal places is moderate
      const confidence = getCoordinateConfidence(37.7749, -122.4194);
      expect(confidence).toBe('medium');
    });

    it('should return low confidence for low precision', () => {
      // 1-3 decimal places is low
      const confidence = getCoordinateConfidence(37.77, -122.42);
      expect(confidence).toBe('low');
    });

    it('should return low confidence for 0,0 coordinates', () => {
      const confidence = getCoordinateConfidence(0, 0);
      expect(confidence).toBe('low');
    });

    it('should return low confidence for invalid coordinates', () => {
      const confidence = getCoordinateConfidence(95, 200);
      expect(confidence).toBe('low');
    });
  });

  describe('reverseGeocode', () => {
    it('should geocode known location (San Francisco)', async () => {
      const result = await reverseGeocode(37.7749, -122.4194);
      expect(result.success).toBe(true);
      expect(result.address).toBeDefined();
      expect(result.city).toBeDefined();
      expect(result.country).toBeDefined();
    });

    it('should geocode another known location (London)', async () => {
      const result = await reverseGeocode(51.5074, -0.1278);
      expect(result.success).toBe(true);
      expect(result.address).toBeDefined();
    });

    it('should return valid confidence level', async () => {
      const result = await reverseGeocode(37.7749, -122.4194);
      if (result.success) {
        expect(['high', 'medium', 'low']).toContain(result.confidence);
      }
    });

    it('should reject invalid coordinates', async () => {
      const result = await reverseGeocode(95, 200);
      expect(result.success).toBe(false);
    });

    it('should handle geocoding errors gracefully', async () => {
      // This should return a result (not throw)
      const result = await reverseGeocode(95, 200);
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  describe('URL generation', () => {
    it('should generate valid Google Maps URL', () => {
      const url = generateGoogleMapsUrl(37.7749, -122.4194);
      expect(url).toContain('google.com/maps');
      expect(url).toContain('37.7749');
      expect(url).toContain('-122.4194');
      expect(url).toContain('z=15');
    });

    it('should generate valid OpenStreetMap URL', () => {
      const url = generateOpenStreetMapUrl(37.7749, -122.4194);
      expect(url).toContain('openstreetmap.org');
      expect(url).toContain('37.7749');
      expect(url).toContain('-122.4194');
      expect(url).toContain('zoom=15');
    });

    it('should accept custom zoom level', () => {
      const url = generateGoogleMapsUrl(37.7749, -122.4194, 10);
      expect(url).toContain('z=10');
    });
  });

  describe('Edge cases', () => {
    it('should handle zero coordinates (not necessarily invalid)', () => {
      expect(validateCoordinates(0, 0)).toBe(true);
    });

    it('should handle coordinates at poles', () => {
      expect(validateCoordinates(90, 0)).toBe(true);
      expect(validateCoordinates(-90, 0)).toBe(true);
    });

    it('should handle coordinates at date line', () => {
      expect(validateCoordinates(0, 180)).toBe(true);
      expect(validateCoordinates(0, -180)).toBe(true);
    });

    it('should handle very small differences', () => {
      const distance = calculateDistance(
        37.7749,
        -122.4194,
        37.77490001,
        -122.41940001
      );
      expect(distance).toBeLessThan(0.01); // Should be less than 10 meters
    });
  });
});
