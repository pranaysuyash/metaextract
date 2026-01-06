/**
 * Geocoding Result Caching Layer
 * Caches reverse geocoding results to reduce API calls and improve performance
 */

import { Redis } from 'ioredis';
import crypto from 'crypto';
import { CacheConfig, DEFAULT_CACHE_CONFIG } from './cache-config';

export interface GeocodingCacheConfig extends CacheConfig {
  /** TTL for reverse geocoding results in seconds */
  reverseGeocodeTTL: number;
  /** TTL for forward geocoding results in seconds */
  forwardGeocodeTTL: number;
  /** TTL for batch geocoding results in seconds */
  batchGeocodeTTL: number;
  /** Maximum number of locations to cache in batch results */
  maxBatchSize: number;
}

export const DEFAULT_GEOCODING_CACHE_CONFIG: GeocodingCacheConfig = {
  ...DEFAULT_CACHE_CONFIG,
  reverseGeocodeTTL: 86400,    // 24 hours for reverse geocoding (addresses don't change often)
  forwardGeocodeTTL: 604800,   // 7 days for forward geocoding (more stable)
  batchGeocodeTTL: 43200,      // 12 hours for batch results
  maxBatchSize: 100,           // Maximum 100 locations per batch
};

export interface GeocodingCacheEntry {
  key: string;
  value: any;
  timestamp: number;
  ttl: number;
  metadata: {
    queryType: 'reverse' | 'forward' | 'batch';
    queryParams: any;
    resultCount: number;
    cacheHit: boolean;
  };
}

export interface ReverseGeocodeResult {
  address: string;
  city: string;
  region: string;
  country: string;
  postalCode?: string;
  confidence: number;
  accuracy?: string;
  placeId?: string;
}

export interface ForwardGeocodeResult {
  latitude: number;
  longitude: number;
  accuracy?: string;
  placeId?: string;
}

export class GeocodingCache {
  private redis: Redis;
  private config: GeocodingCacheConfig;

  constructor(redis: Redis, config?: Partial<GeocodingCacheConfig>) {
    this.redis = redis;
    this.config = { ...DEFAULT_GEOCODING_CACHE_CONFIG, ...config };
  }

  /**
   * Generate a cache key for reverse geocoding
   */
  generateReverseGeocodeKey(latitude: number, longitude: number, options: any = {}): string {
    const locationHash = crypto
      .createHash('sha256')
      .update(`${latitude},${longitude}`)
      .digest('hex');
    
    const optionsHash = options.includeDetails 
      ? crypto.createHash('sha256').update(JSON.stringify(options)).digest('hex')
      : 'basic';
    
    return `reverse-geocode:${locationHash}:${optionsHash}`;
  }

  /**
   * Generate a cache key for forward geocoding
   */
  generateForwardGeocodeKey(address: string, options: any = {}): string {
    const addressHash = crypto
      .createHash('sha256')
      .update(address.toLowerCase().trim())
      .digest('hex');
    
    const optionsHash = options.exactMatch 
      ? crypto.createHash('sha256').update(JSON.stringify(options)).digest('hex')
      : 'fuzzy';
    
    return `forward-geocode:${addressHash}:${optionsHash}`;
  }

  /**
   * Generate a cache key for batch geocoding
   */
  generateBatchGeocodeKey(queries: Array<string | { lat: number; lng: number }>, options: any = {}): string {
    const queriesHash = crypto
      .createHash('sha256')
      .update(JSON.stringify(queries))
      .digest('hex');
    
    const optionsHash = crypto.createHash('sha256').update(JSON.stringify(options)).digest('hex');
    
    return `batch-geocode:${queriesHash}:${optionsHash}`;
  }

  /**
   * Cache reverse geocoding result
   */
  async setReverseGeocodeResult(
    latitude: number,
    longitude: number,
    result: ReverseGeocodeResult,
    options: any = {}
  ): Promise<boolean> {
    try {
      const key = this.generateReverseGeocodeKey(latitude, longitude, options);
      const entry: GeocodingCacheEntry = {
        key,
        value: result,
        timestamp: Date.now(),
        ttl: this.config.reverseGeocodeTTL,
        metadata: {
          queryType: 'reverse',
          queryParams: { latitude, longitude, ...options },
          resultCount: 1,
          cacheHit: false,
        }
      };

      await this.redis.setex(key, this.config.reverseGeocodeTTL, JSON.stringify(entry));
      console.log(`Cached reverse geocode result for ${latitude},${longitude}`);
      return true;
    } catch (error) {
      console.error('Error caching reverse geocode result:', error);
      return false;
    }
  }

  /**
   * Get cached reverse geocoding result
   */
  async getReverseGeocodeResult(
    latitude: number,
    longitude: number,
    options: any = {}
  ): Promise<ReverseGeocodeResult | null> {
    try {
      const key = this.generateReverseGeocodeKey(latitude, longitude, options);
      const cached = await this.redis.get(key);
      
      if (!cached) {
        return null;
      }

      const entry: GeocodingCacheEntry = JSON.parse(cached);
      console.log(`Cache hit for reverse geocode: ${latitude},${longitude}`);
      return entry.value as ReverseGeocodeResult;
    } catch (error) {
      console.error('Error getting cached reverse geocode result:', error);
      return null;
    }
  }

  /**
   * Cache forward geocoding result
   */
  async setForwardGeocodeResult(
    address: string,
    result: ForwardGeocodeResult | ForwardGeocodeResult[],
    options: any = {}
  ): Promise<boolean> {
    try {
      const key = this.generateForwardGeocodeKey(address, options);
      const results = Array.isArray(result) ? result : [result];
      
      const entry: GeocodingCacheEntry = {
        key,
        value: results,
        timestamp: Date.now(),
        ttl: this.config.forwardGeocodeTTL,
        metadata: {
          queryType: 'forward',
          queryParams: { address, ...options },
          resultCount: results.length,
          cacheHit: false,
        }
      };

      await this.redis.setex(key, this.config.forwardGeocodeTTL, JSON.stringify(entry));
      console.log(`Cached forward geocode result for "${address}" (${results.length} result(s))`);
      return true;
    } catch (error) {
      console.error('Error caching forward geocode result:', error);
      return false;
    }
  }

  /**
   * Get cached forward geocoding result
   */
  async getForwardGeocodeResult(
    address: string,
    options: any = {}
  ): Promise<ForwardGeocodeResult | ForwardGeocodeResult[] | null> {
    try {
      const key = this.generateForwardGeocodeKey(address, options);
      const cached = await this.redis.get(key);
      
      if (!cached) {
        return null;
      }

      const entry: GeocodingCacheEntry = JSON.parse(cached);
      console.log(`Cache hit for forward geocode: "${address}"`);
      return entry.value as ForwardGeocodeResult | ForwardGeocodeResult[];
    } catch (error) {
      console.error('Error getting cached forward geocode result:', error);
      return null;
    }
  }

  /**
   * Cache batch geocoding result
   */
  async setBatchGeocodeResult(
    queries: Array<string | { lat: number; lng: number }>,
    results: any[],
    options: any = {}
  ): Promise<boolean> {
    try {
      // Check if batch is too large
      if (queries.length > this.config.maxBatchSize) {
        console.log(`Batch geocode too large to cache: ${queries.length} queries`);
        return false;
      }

      const key = this.generateBatchGeocodeKey(queries, options);
      const entry: GeocodingCacheEntry = {
        key,
        value: results,
        timestamp: Date.now(),
        ttl: this.config.batchGeocodeTTL,
        metadata: {
          queryType: 'batch',
          queryParams: { queries, ...options },
          resultCount: results.length,
          cacheHit: false,
        }
      };

      await this.redis.setex(key, this.config.batchGeocodeTTL, JSON.stringify(entry));
      console.log(`Cached batch geocode result for ${queries.length} queries`);
      return true;
    } catch (error) {
      console.error('Error caching batch geocode result:', error);
      return false;
    }
  }

  /**
   * Get cached batch geocoding result
   */
  async getBatchGeocodeResult(
    queries: Array<string | { lat: number; lng: number }>,
    options: any = {}
  ): Promise<any[] | null> {
    try {
      const key = this.generateBatchGeocodeKey(queries, options);
      const cached = await this.redis.get(key);
      
      if (!cached) {
        return null;
      }

      const entry: GeocodingCacheEntry = JSON.parse(cached);
      console.log(`Cache hit for batch geocode: ${queries.length} queries`);
      return entry.value as any[];
    } catch (error) {
      console.error('Error getting cached batch geocode result:', error);
      return null;
    }
  }

  /**
   * Invalidate reverse geocoding cache for specific coordinates
   */
  async invalidateReverseGeocodeCache(latitude: number, longitude: number): Promise<number> {
    try {
      const locationHash = crypto
        .createHash('sha256')
        .update(`${latitude},${longitude}`)
        .digest('hex');
      
      const pattern = `reverse-geocode:${locationHash}:*`;
      const keys = await this.redis.keys(pattern);
      
      if (keys.length === 0) {
        return 0;
      }

      const result = await this.redis.del(...keys);
      console.log(`Invalidated ${result} reverse geocode cache entries for ${latitude},${longitude}`);
      return result;
    } catch (error) {
      console.error('Error invalidating reverse geocode cache:', error);
      return 0;
    }
  }

  /**
   * Invalidate forward geocoding cache for specific address
   */
  async invalidateForwardGeocodeCache(address: string): Promise<number> {
    try {
      const addressHash = crypto
        .createHash('sha256')
        .update(address.toLowerCase().trim())
        .digest('hex');
      
      const pattern = `forward-geocode:${addressHash}:*`;
      const keys = await this.redis.keys(pattern);
      
      if (keys.length === 0) {
        return 0;
      }

      const result = await this.redis.del(...keys);
      console.log(`Invalidated ${result} forward geocode cache entries for "${address}"`);
      return result;
    } catch (error) {
      console.error('Error invalidating forward geocode cache:', error);
      return 0;
    }
  }

  /**
   * Get cache statistics
   */
  async getStats(): Promise<any> {
    try {
      const info = await this.redis.info('keyspace');
      return {
        reverseGeocodeTTL: this.config.reverseGeocodeTTL,
        forwardGeocodeTTL: this.config.forwardGeocodeTTL,
        batchGeocodeTTL: this.config.batchGeocodeTTL,
        maxBatchSize: this.config.maxBatchSize,
        redisInfo: info,
      };
    } catch (error) {
      console.error('Error getting geocoding cache stats:', error);
      return null;
    }
  }
}