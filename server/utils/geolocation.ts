/**
 * Geolocation Utilities
 *
 * Handle GPS coordinate operations:
 * - Reverse geocoding (coordinates → addresses)
 * - Coordinate validation
 * - Distance calculations
 * - Coordinate formatting
 */

/**
 * Reverse geocoding result
 */
export interface ReverseGeocodingResult {
  success: boolean;
  address?: string;
  city?: string;
  region?: string;
  country?: string;
  confidence?: 'high' | 'medium' | 'low';
  error?: string;
}

/**
 * Map preview metadata
 */
export interface MapPreviewMetadata {
  url: string;
  width: number;
  height: number;
  zoom: number;
  latitude: number;
  longitude: number;
  attribution: string;
}

/**
 * Validate GPS coordinates
 * Returns true if coordinates are within valid ranges
 */
export function validateCoordinates(latitude: number, longitude: number): boolean {
  // Latitude: -90 to 90
  if (latitude < -90 || latitude > 90) {
    return false;
  }

  // Longitude: -180 to 180
  if (longitude < -180 || longitude > 180) {
    return false;
  }

  return true;
}

/**
 * Calculate distance between two coordinates (Haversine formula)
 * Returns distance in kilometers
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Convert degrees to radians
 */
function toRad(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Mock reverse geocoding implementation
 * In production, this would call a service like Google Maps API or Nominatim
 */
export async function reverseGeocode(
  latitude: number,
  longitude: number
): Promise<ReverseGeocodingResult> {
  try {
    // Validate coordinates
    if (!validateCoordinates(latitude, longitude)) {
      return {
        success: false,
        error: 'Invalid coordinates'
      };
    }

    // For now, return a mock implementation
    // This will be replaced with actual API call in production
    const result = getMockGeocodingResult(latitude, longitude);

    return result;
  } catch (error) {
    console.error('Geocoding error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Geocoding failed'
    };
  }
}

/**
 * Get mock geocoding result for testing/development
 * Maps known coordinates to cities
 */
function getMockGeocodingResult(
  latitude: number,
  longitude: number
): ReverseGeocodingResult {
  // Known city coordinates (for testing)
  const knownPlaces = [
    {
      lat: 37.7749,
      lng: -122.4194,
      address: 'San Francisco, California, USA',
      city: 'San Francisco',
      region: 'California',
      country: 'United States'
    },
    {
      lat: 51.5074,
      lng: -0.1278,
      address: 'London, England, United Kingdom',
      city: 'London',
      region: 'England',
      country: 'United Kingdom'
    },
    {
      lat: 48.8566,
      lng: 2.3522,
      address: 'Paris, Île-de-France, France',
      city: 'Paris',
      region: 'Île-de-France',
      country: 'France'
    },
    {
      lat: 35.6762,
      lng: 139.6503,
      address: 'Tokyo, Japan',
      city: 'Tokyo',
      region: 'Tokyo',
      country: 'Japan'
    },
    {
      lat: -33.8688,
      lng: 151.2093,
      address: 'Sydney, New South Wales, Australia',
      city: 'Sydney',
      region: 'New South Wales',
      country: 'Australia'
    }
  ];

  // Find nearest known place within 100km
  let nearest = null;
  let minDistance = Infinity;

  for (const place of knownPlaces) {
    const distance = calculateDistance(latitude, longitude, place.lat, place.lng);
    if (distance < minDistance) {
      minDistance = distance;
      nearest = place;
    }
  }

  if (nearest && minDistance < 100) {
    return {
      success: true,
      address: nearest.address,
      city: nearest.city,
      region: nearest.region,
      country: nearest.country,
      confidence: minDistance < 10 ? 'high' : 'medium'
    };
  }

  // Return generic result for unknown locations
  return {
    success: true,
    address: `${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° W`,
    confidence: 'low'
  };
}

/**
 * Generate Google Maps URL for coordinates
 */
export function generateGoogleMapsUrl(
  latitude: number,
  longitude: number,
  zoom: number = 15
): string {
  return `https://www.google.com/maps?q=${latitude},${longitude}&z=${zoom}`;
}

/**
 * Generate OpenStreetMap URL for coordinates
 */
export function generateOpenStreetMapUrl(
  latitude: number,
  longitude: number,
  zoom: number = 15
): string {
  return `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}&zoom=${zoom}`;
}

/**
 * Generate static map preview URL (using a map service)
 * For production, use Google Static Maps, Mapbox, or similar
 */
export function generateMapPreviewUrl(
  latitude: number,
  longitude: number,
  width: number = 400,
  height: number = 300,
  zoom: number = 15
): MapPreviewMetadata {
  // Using OpenStreetMap's Nominatim for static maps
  // In production, would use a proper map service API
  const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${latitude},${longitude}&zoom=${zoom}&size=${width}x${height}&maptype=roadmap&key=${process.env.GOOGLE_MAPS_API_KEY || 'demo'}`;

  return {
    url: mapUrl,
    width,
    height,
    zoom,
    latitude,
    longitude,
    attribution: 'Map data © 2025 Google Maps'
  };
}

/**
 * Format coordinates in standard format
 * Returns: "37.7749° N, 122.4194° W"
 */
export function formatCoordinatesForDisplay(
  latitude: number,
  longitude: number
): string {
  const latDir = latitude >= 0 ? 'N' : 'S';
  const lonDir = longitude >= 0 ? 'E' : 'W';

  return `${Math.abs(latitude).toFixed(4)}° ${latDir}, ${Math.abs(longitude).toFixed(4)}° ${lonDir}`;
}

/**
 * Parse coordinate string
 * Accepts formats like "37.7749, -122.4194" or "37.7749° N, 122.4194° W"
 */
export function parseCoordinateString(coordStr: string): { latitude: number; longitude: number } | null {
  try {
    // Try standard decimal format first
    const decimalMatch = coordStr.match(/(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)/);
    if (decimalMatch) {
      const lat = parseFloat(decimalMatch[1]);
      const lon = parseFloat(decimalMatch[2]);
      if (validateCoordinates(lat, lon)) {
        return { latitude: lat, longitude: lon };
      }
    }

    // Try DMS (Degrees Minutes Seconds) format
    const dmsRegex = /(\d+)°\s*(\d+)'\s*([\d.]+)"\s*([NSEW])\s*,?\s*(\d+)°\s*(\d+)'\s*([\d.]+)"\s*([NSEW])/i;
    const dmsMatch = coordStr.match(dmsRegex);
    if (dmsMatch) {
      let lat = parseInt(dmsMatch[1]) + parseInt(dmsMatch[2]) / 60 + parseFloat(dmsMatch[3]) / 3600;
      let lon = parseInt(dmsMatch[5]) + parseInt(dmsMatch[6]) / 60 + parseFloat(dmsMatch[7]) / 3600;

      if (dmsMatch[4].toUpperCase() === 'S') lat = -lat;
      if (dmsMatch[8].toUpperCase() === 'W') lon = -lon;

      if (validateCoordinates(lat, lon)) {
        return { latitude: lat, longitude: lon };
      }
    }

    return null;
  } catch (error) {
    console.error('Error parsing coordinates:', error);
    return null;
  }
}

/**
 * Get confidence level based on coordinate proximity to known location
 */
export function getCoordinateConfidence(
  latitude: number,
  longitude: number
): 'high' | 'medium' | 'low' {
  // If coordinates are suspicious (all zeros, invalid), return low
  if ((latitude === 0 && longitude === 0) || !validateCoordinates(latitude, longitude)) {
    return 'low';
  }

  // If coordinates are very precise (many decimal places), higher confidence
  const latStr = latitude.toString();
  const lonStr = longitude.toString();
  const decimalPlaces = Math.max(
    latStr.split('.')[1]?.length || 0,
    lonStr.split('.')[1]?.length || 0
  );

  if (decimalPlaces >= 6) return 'high';    // 0.000001° precision
  if (decimalPlaces >= 4) return 'medium';  // 0.0001° precision
  return 'low';                               // Less than 0.0001° precision
}
