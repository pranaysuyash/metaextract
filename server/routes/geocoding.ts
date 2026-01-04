/**
 * Geocoding Routes
 *
 * Reverse geocoding endpoints for converting GPS coordinates to addresses.
 * Includes caching for performance optimization.
 */

import type { Express, Request, Response } from 'express';
import {
  reverseGeocode,
  validateCoordinates,
  generateGoogleMapsUrl,
  generateMapPreviewUrl,
  formatCoordinatesForDisplay,
  getCoordinateConfidence
} from '../utils/geolocation';

/**
 * Simple in-memory cache for geocoding results
 * In production, use Redis or database
 */
const geocodingCache = new Map<string, any>();

/**
 * Cache key for coordinates
 */
function getCacheKey(lat: number, lon: number): string {
  // Round to 4 decimal places for caching (≈11m precision)
  const roundedLat = Math.round(lat * 10000) / 10000;
  const roundedLon = Math.round(lon * 10000) / 10000;
  return `${roundedLat},${roundedLon}`;
}

/**
 * Register geocoding routes
 */
export function registerGeocodingRoutes(app: Express): void {
  /**
   * POST /api/geocode/reverse
   * Reverse geocode GPS coordinates to address
   */
  app.post('/api/geocode/reverse', async (req: Request, res: Response) => {
    try {
      const { latitude, longitude } = req.body;

      // Validate input
      if (latitude === undefined || longitude === undefined) {
        return res.status(400).json({
          error: 'Missing required fields: latitude, longitude'
        });
      }

      const lat = parseFloat(latitude);
      const lon = parseFloat(longitude);

      // Validate coordinates
      if (!validateCoordinates(lat, lon)) {
        return res.status(400).json({
          error: 'Invalid coordinates. Latitude must be -90 to 90, longitude must be -180 to 180'
        });
      }

      // Check cache
      const cacheKey = getCacheKey(lat, lon);
      if (geocodingCache.has(cacheKey)) {
        const cached = geocodingCache.get(cacheKey);
        return res.json({
          ...cached,
          cached: true
        });
      }

      // Reverse geocode
      const result = await reverseGeocode(lat, lon);

      if (!result.success) {
        return res.status(400).json({
          error: result.error || 'Geocoding failed'
        });
      }

      // Add maps URLs
      const response = {
        ...result,
        coordinates: formatCoordinatesForDisplay(lat, lon),
        mapsUrl: generateGoogleMapsUrl(lat, lon),
        osmUrl: `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}&zoom=15`,
        cached: false
      };

      // Cache result
      geocodingCache.set(cacheKey, response);

      // Limit cache size (keep last 1000 entries)
      if (geocodingCache.size > 1000) {
        const firstKey = geocodingCache.keys().next().value;
        if (firstKey !== undefined) {
          geocodingCache.delete(firstKey);
        }
      }

      res.json(response);
    } catch (error) {
      console.error('Geocoding error:', error);
      res.status(500).json({
        error: 'Internal server error'
      });
    }
  });

  /**
   * GET /api/geocode/reverse
   * Reverse geocode via query parameters
   */
  app.get('/api/geocode/reverse', async (req: Request, res: Response) => {
    try {
      const { latitude, longitude } = req.query;

      // Validate input
      if (!latitude || !longitude) {
        return res.status(400).json({
          error: 'Missing required parameters: latitude, longitude'
        });
      }

      const lat = parseFloat(latitude as string);
      const lon = parseFloat(longitude as string);

      // Validate coordinates
      if (!validateCoordinates(lat, lon)) {
        return res.status(400).json({
          error: 'Invalid coordinates'
        });
      }

      // Check cache
      const cacheKey = getCacheKey(lat, lon);
      if (geocodingCache.has(cacheKey)) {
        const cached = geocodingCache.get(cacheKey);
        return res.json({
          ...cached,
          cached: true
        });
      }

      // Reverse geocode
      const result = await reverseGeocode(lat, lon);

      if (!result.success) {
        return res.status(400).json({
          error: result.error || 'Geocoding failed'
        });
      }

      const response = {
        ...result,
        coordinates: formatCoordinatesForDisplay(lat, lon),
        mapsUrl: generateGoogleMapsUrl(lat, lon),
        osmUrl: `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}&zoom=15`,
        cached: false
      };

      // Cache result
      geocodingCache.set(cacheKey, response);

      res.json(response);
    } catch (error) {
      console.error('Geocoding error:', error);
      res.status(500).json({
        error: 'Internal server error'
      });
    }
  });

  /**
   * POST /api/geocode/batch
   * Batch reverse geocoding for multiple coordinates
   */
  app.post('/api/geocode/batch', async (req: Request, res: Response) => {
    try {
      const { coordinates } = req.body;

      if (!Array.isArray(coordinates)) {
        return res.status(400).json({
          error: 'coordinates must be an array'
        });
      }

      if (coordinates.length === 0) {
        return res.status(400).json({
          error: 'coordinates array cannot be empty'
        });
      }

      if (coordinates.length > 100) {
        return res.status(400).json({
          error: 'Maximum 100 coordinates per batch'
        });
      }

      // Process all coordinates
      const results = await Promise.all(
        coordinates.map(async (coord) => {
          const { latitude, longitude } = coord;

          if (latitude === undefined || longitude === undefined) {
            return {
              success: false,
              error: 'Missing latitude or longitude'
            };
          }

          const lat = parseFloat(latitude);
          const lon = parseFloat(longitude);

          if (!validateCoordinates(lat, lon)) {
            return {
              success: false,
              error: 'Invalid coordinates'
            };
          }

          // Check cache
          const cacheKey = getCacheKey(lat, lon);
          if (geocodingCache.has(cacheKey)) {
            return {
              ...geocodingCache.get(cacheKey),
              cached: true
            };
          }

          // Reverse geocode
          const result = await reverseGeocode(lat, lon);

          if (result.success) {
            const response = {
              ...result,
              coordinates: formatCoordinatesForDisplay(lat, lon),
              mapsUrl: generateGoogleMapsUrl(lat, lon),
              cached: false
            };

            // Cache result
            geocodingCache.set(cacheKey, response);
            return response;
          }

          return result;
        })
      );

      res.json({
        success: true,
        count: results.length,
        results
      });
    } catch (error) {
      console.error('Batch geocoding error:', error);
      res.status(500).json({
        error: 'Internal server error'
      });
    }
  });

  /**
   * GET /api/geocode/cache/clear
   * Clear geocoding cache (admin only)
   */
  app.get('/api/geocode/cache/clear', (req: Request, res: Response) => {
    // In production, add proper authorization
    geocodingCache.clear();
    res.json({
      success: true,
      message: 'Geocoding cache cleared'
    });
  });

  /**
   * GET /api/geocode/cache/stats
   * Get cache statistics
   */
  app.get('/api/geocode/cache/stats', (req: Request, res: Response) => {
    res.json({
      cacheSize: geocodingCache.size,
      maxSize: 1000
    });
  });
}
