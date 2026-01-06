/**
 * Extraction Result Caching Layer
 * Caches metadata extraction results to reduce redundant processing
 */

import { Redis } from 'ioredis';
import crypto from 'crypto';
import { CacheConfig, DEFAULT_CACHE_CONFIG } from './cache-config';

export interface ExtractionCacheConfig extends CacheConfig {
  /** TTL for extraction results in seconds */
  extractionTTL: number;
  /** TTL for field-specific results in seconds */
  fieldTTL: number;
  /** TTL for tier-filtered results in seconds */
  tierTTL: number;
  /** Maximum size of cached extraction results in MB */
  maxResultSize: number;
}

export const DEFAULT_EXTRACTION_CACHE_CONFIG: ExtractionCacheConfig = {
  ...DEFAULT_CACHE_CONFIG,
  extractionTTL: 3600, // 1 hour for extraction results
  fieldTTL: 1800,      // 30 minutes for field-specific results
  tierTTL: 7200,       // 2 hours for tier-filtered results
  maxResultSize: 10,   // 10MB max result size
};

export interface ExtractionCacheEntry {
  key: string;
  value: any;
  timestamp: number;
  ttl: number;
  metadata: {
    fileType: string;
    tier: string;
    fieldsExtracted: number;
    processingTime: number;
    size: number;
  };
}

export class ExtractionCache {
  private redis: Redis;
  private config: ExtractionCacheConfig;

  constructor(redis: Redis, config?: Partial<ExtractionCacheConfig>) {
    this.redis = redis;
    this.config = { ...DEFAULT_EXTRACTION_CACHE_CONFIG, ...config };
  }

  /**
   * Generate a cache key for extraction results
   */
  generateExtractionKey(filePath: string, tier: string, options: any = {}): string {
    const fileHash = crypto.createHash('sha256').update(filePath).digest('hex');
    const optionsHash = crypto.createHash('sha256').update(JSON.stringify(options)).digest('hex');
    
    return `extraction:${fileHash}:${tier}:${optionsHash}`;
  }

  /**
   * Generate a cache key for field-specific results
   */
  generateFieldKey(filePath: string, tier: string, field: string): string {
    const fileHash = crypto.createHash('sha256').update(filePath).digest('hex');
    
    return `field:${fileHash}:${tier}:${field}`;
  }

  /**
   * Cache extraction results
   */
  async setExtractionResult(
    filePath: string, 
    tier: string, 
    result: any, 
    options: any = {}
  ): Promise<boolean> {
    try {
      const key = this.generateExtractionKey(filePath, tier, options);
      const size = JSON.stringify(result).length;
      
      // Don't cache if result is too large
      if (size > this.config.maxResultSize * 1024 * 1024) {
        console.log(`Extraction result too large to cache: ${size} bytes`);
        return false;
      }

      const entry: ExtractionCacheEntry = {
        key,
        value: result,
        timestamp: Date.now(),
        ttl: this.config.extractionTTL,
        metadata: {
          fileType: options.fileType || 'unknown',
          tier,
          fieldsExtracted: result.fieldsExtracted || 0,
          processingTime: result.processingTime || 0,
          size,
        }
      };

      await this.redis.setex(key, this.config.extractionTTL, JSON.stringify(entry));
      console.log(`Cached extraction result for ${filePath} (tier: ${tier})`);
      return true;
    } catch (error) {
      console.error('Error caching extraction result:', error);
      return false;
    }
  }

  /**
   * Get cached extraction results
   */
  async getExtractionResult(
    filePath: string, 
    tier: string, 
    options: any = {}
  ): Promise<any | null> {
    try {
      const key = this.generateExtractionKey(filePath, tier, options);
      const cached = await this.redis.get(key);
      
      if (!cached) {
        return null;
      }

      const entry: ExtractionCacheEntry = JSON.parse(cached);
      console.log(`Cache hit for extraction result: ${filePath} (tier: ${tier})`);
      return entry.value;
    } catch (error) {
      console.error('Error getting cached extraction result:', error);
      return null;
    }
  }

  /**
   * Cache a specific field result
   */
  async setFieldResult(
    filePath: string,
    tier: string,
    field: string,
    result: any
  ): Promise<boolean> {
    try {
      const key = this.generateFieldKey(filePath, tier, field);
      const entry: ExtractionCacheEntry = {
        key,
        value: result,
        timestamp: Date.now(),
        ttl: this.config.fieldTTL,
        metadata: {
          fileType: 'unknown', // Would need to be passed in
          tier,
          fieldsExtracted: 1,
          processingTime: 0,
          size: JSON.stringify(result).length,
        }
      };

      await this.redis.setex(key, this.config.fieldTTL, JSON.stringify(entry));
      console.log(`Cached field result for ${filePath} (field: ${field})`);
      return true;
    } catch (error) {
      console.error('Error caching field result:', error);
      return false;
    }
  }

  /**
   * Get cached field result
   */
  async getFieldResult(
    filePath: string,
    tier: string,
    field: string
  ): Promise<any | null> {
    try {
      const key = this.generateFieldKey(filePath, tier, field);
      const cached = await this.redis.get(key);
      
      if (!cached) {
        return null;
      }

      const entry: ExtractionCacheEntry = JSON.parse(cached);
      console.log(`Cache hit for field result: ${filePath} (field: ${field})`);
      return entry.value;
    } catch (error) {
      console.error('Error getting cached field result:', error);
      return null;
    }
  }

  /**
   * Cache tier-specific filtered results
   */
  async setTierFilteredResult(
    filePath: string,
    originalTier: string,
    targetTier: string,
    result: any
  ): Promise<boolean> {
    try {
      const key = `tier-filter:${filePath}:${originalTier}:${targetTier}`;
      const entry: ExtractionCacheEntry = {
        key,
        value: result,
        timestamp: Date.now(),
        ttl: this.config.tierTTL,
        metadata: {
          fileType: 'unknown',
          tier: targetTier,
          fieldsExtracted: result.fieldsExtracted || 0,
          processingTime: 0,
          size: JSON.stringify(result).length,
        }
      };

      await this.redis.setex(key, this.config.tierTTL, JSON.stringify(entry));
      console.log(`Cached tier-filtered result for ${filePath} (${originalTier} -> ${targetTier})`);
      return true;
    } catch (error) {
      console.error('Error caching tier-filtered result:', error);
      return false;
    }
  }

  /**
   * Get cached tier-specific filtered results
   */
  async getTierFilteredResult(
    filePath: string,
    originalTier: string,
    targetTier: string
  ): Promise<any | null> {
    try {
      const key = `tier-filter:${filePath}:${originalTier}:${targetTier}`;
      const cached = await this.redis.get(key);
      
      if (!cached) {
        return null;
      }

      const entry: ExtractionCacheEntry = JSON.parse(cached);
      console.log(`Cache hit for tier-filtered result: ${filePath} (${originalTier} -> ${targetTier})`);
      return entry.value;
    } catch (error) {
      console.error('Error getting cached tier-filtered result:', error);
      return null;
    }
  }

  /**
   * Invalidate extraction cache for a specific file
   */
  async invalidateExtractionCache(filePath: string): Promise<number> {
    try {
      const fileHash = crypto.createHash('sha256').update(filePath).digest('hex');
      const pattern = `extraction:${fileHash}:*`;
      
      // Get all keys matching the pattern
      const keys = await this.redis.keys(pattern);
      
      if (keys.length === 0) {
        return 0;
      }

      // Delete all matching keys
      const result = await this.redis.del(...keys);
      console.log(`Invalidated ${result} extraction cache entries for ${filePath}`);
      return result;
    } catch (error) {
      console.error('Error invalidating extraction cache:', error);
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
        extractionCacheEnabled: this.config.enabled,
        extractionTTL: this.config.extractionTTL,
        fieldTTL: this.config.fieldTTL,
        tierTTL: this.config.tierTTL,
        maxResultSize: this.config.maxResultSize,
        redisInfo: info,
      };
    } catch (error) {
      console.error('Error getting cache stats:', error);
      return null;
    }
  }
}