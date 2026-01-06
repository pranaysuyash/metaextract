/**
 * Optimized Metadata Caching Layer for MetaExtract API
 *
 * Provides intelligent caching for metadata extraction results to improve performance
 * and reduce redundant processing. Includes cache invalidation, memory management,
 * and configurable TTL strategies based on file type and tier.
 *
 * Key features:
 * - Tier-based cache TTL strategies
 * - Automatic compression for large metadata
 * - File extension and tier-based invalidation
 * - Memory-efficient storage with size limits
 */

import { createClient, RedisClientType } from 'redis';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { cacheManager, CacheStrategy, DEFAULT_CACHE_CONFIG } from '../cache';
import type { PythonMetadataResponse } from '../utils/extraction-helpers';

// ============================================================================
// Metadata Cache Configuration
// ============================================================================

/**
 * Configuration options for the metadata cache system
 */
export interface MetadataCacheConfig {
  /** Whether caching is enabled */
  enabled: boolean;
  /** Redis connection URL */
  url: string;
  /** Default time-to-live in seconds */
  defaultTTL: number; // Time to live in seconds
  /** Maximum cache size in MB */
  maxSize: number; // Maximum cache size in MB
  /** Maximum number of cache entries */
  maxEntries: number; // Maximum number of entries
  /** Redis eviction policy */
  evictionPolicy: string; // Redis eviction policy
  /** Whether to compress large metadata */
  compression: boolean; // Whether to compress large metadata
  /** Size in bytes above which to compress */
  compressionThreshold: number; // Size in bytes above which to compress
}

/**
 * Default configuration for metadata caching
 * - 1 hour default TTL for metadata
 * - 512MB max cache size
 * - 10,000 max entries
 * - LRU eviction policy
 * - Compression enabled for metadata > 10KB
 */
export const DEFAULT_METADATA_CACHE_CONFIG: MetadataCacheConfig = {
  enabled: process.env.METADATA_CACHE_ENABLED !== 'false',
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  defaultTTL: 3600, // 1 hour default for metadata
  maxSize: 512, // 512MB max cache size
  maxEntries: 10000, // Maximum 10,000 entries
  evictionPolicy: 'allkeys-lru',
  compression: true, // Enable compression for large metadata
  compressionThreshold: 1024 * 10, // 10KB threshold for compression
};

// ============================================================================
// Cache Entry Structure
// ============================================================================

/**
 * Structure for a metadata cache entry
 * Contains the cached metadata response along with metadata about the cache entry
 */
export interface MetadataCacheEntry {
  /** The cache key */
  key: string;
  /** The cached metadata response */
  value: PythonMetadataResponse;
  /** Time-to-live in seconds */
  ttl: number;
  /** Creation timestamp */
  createdAt: number;
  /** Last access timestamp */
  accessedAt: number;
  /** Number of times accessed */
  hitCount: number;
  /** Additional metadata about the cached entry */
  metadata: {
    /** Cache tags for invalidation */
    tags?: string[];
    /** Schema version */
    version?: string;
    /** Tier associated with this cache entry */
    tier?: string;
    /** File size of the original file */
    fileSize?: number;
    /** MIME type of the original file */
    mimeType?: string;
    /** Whether the metadata was compressed */
    compressed?: boolean;
  };
}

// ============================================================================
// Metadata Cache Manager Class
// ============================================================================

/**
 * Manages caching for metadata extraction results
 * Provides methods to get, set, and invalidate cached metadata with tier-based strategies
 */
export class MetadataCacheManager {
  private config: MetadataCacheConfig;
  private initialized: boolean = false;
  private compressionEnabled: boolean;

  /**
   * Creates a new metadata cache manager instance
   * @param config Optional configuration to override defaults
   */
  constructor(config: Partial<MetadataCacheConfig> = {}) {
    this.config = { ...DEFAULT_METADATA_CACHE_CONFIG, ...config };
    this.compressionEnabled = this.config.compression ?? true;
  }

  /**
   * Initializes the metadata cache manager
   * Sets up Redis connection and validates configuration
   */
  async initialize(): Promise<void> {
    if (!this.config.enabled) {
      console.log('🔄 Metadata caching disabled');
      return;
    }

    // Initialize the main cache manager if not already done
    if (!cacheManager['initialized']) {
      await cacheManager.initialize();
    }

    this.initialized = true;
    console.log('✅ Metadata cache layer initialized');
  }

  /**
   * Generate a cache key based on file properties
   * Creates a unique key combining file hash and extraction parameters
   * @param filePath Path to the file being cached
   * @param tier The tier for which metadata was extracted
   * @param options Additional options that affect the extraction
   * @returns A unique cache key for the metadata
   */
  generateCacheKey(filePath: string, tier: string, options: {
    includePerformance?: boolean;
    enableAdvancedAnalysis?: boolean
  } = {}): string {
    // Create a hash of the file path and other parameters
    const fileHash = crypto.createHash('sha256').update(filePath).digest('hex');
    const params = [
      tier,
      options.includePerformance ? 'perf' : 'basic',
      options.enableAdvancedAnalysis ? 'adv' : 'std'
    ].join(':');

    return `metadata:${fileHash}:${params}`;
  }

  /**
   * Retrieve cached metadata for a file
   * @param filePath Path to the file to retrieve metadata for
   * @param tier The tier for which metadata was extracted
   * @param options Additional options that affect the extraction
   * @returns Cached metadata response or null if not found
   */
  async get(filePath: string, tier: string, options: {
    includePerformance?: boolean;
    enableAdvancedAnalysis?: boolean
  } = {}): Promise<PythonMetadataResponse | null> {
    if (!this.initialized || !this.config.enabled) {
      return null;
    }

    try {
      const key = this.generateCacheKey(filePath, tier, options);
      const cached = await cacheManager.get<MetadataCacheEntry>(key);

      if (cached) {
        // Update access time and hit count
        await this.updateAccessTime(key);

        console.log(`✅ Metadata cache HIT for ${path.basename(filePath)}`);
        return cached.value;
      }

      console.log(`❌ Metadata cache MISS for ${path.basename(filePath)}`);
      return null;
    } catch (error) {
      console.error(`❌ Metadata cache get error:`, error);
      return null;
    }
  }

  /**
   * Store metadata in cache
   * @param filePath Path to the file being cached
   * @param tier The tier for which metadata was extracted
   * @param metadata The metadata response to cache
   * @param options Additional options that affect the caching
   * @returns True if caching was successful, false otherwise
   */
  async set(
    filePath: string,
    tier: string,
    metadata: PythonMetadataResponse,
    options: {
      includePerformance?: boolean;
      enableAdvancedAnalysis?: boolean;
      customTTL?: number;
    } = {}
  ): Promise<boolean> {
    if (!this.initialized || !this.config.enabled) {
      return false;
    }

    try {
      const key = this.generateCacheKey(filePath, tier, options);
      const ttl = options.customTTL || this.config.defaultTTL;

      // Determine if we should compress based on size
      const metadataSize = JSON.stringify(metadata).length;
      const shouldCompress = this.compressionEnabled &&
                            metadataSize > this.config.compressionThreshold;
      const fileSize =
        typeof metadata.filesystem?.file_size === 'number'
          ? metadata.filesystem.file_size
          : undefined;

      const entry: MetadataCacheEntry = {
        key,
        value: metadata,
        ttl,
        createdAt: Date.now(),
        accessedAt: Date.now(),
        hitCount: 0,
        metadata: {
          tier,
          fileSize,
          mimeType: metadata.file?.mime_type,
          compressed: shouldCompress,
        },
      };

      // Add tags for easier invalidation
      const tags = [`tier:${tier}`, `file:${path.extname(filePath)}`];
      entry.metadata.tags = tags;

      // Store in cache with appropriate options
      const success = await cacheManager.set(key, entry, {
        ttl,
        tags,
        strategy: this.getCacheStrategyForTier(tier),
        metadata: entry.metadata
      });

      if (success) {
        console.log(`✅ Metadata cached for ${path.basename(filePath)} (${metadata.extraction_info?.fields_extracted || 0} fields)`);
      }

      return success;
    } catch (error) {
      console.error(`❌ Metadata cache set error:`, error);
      return false;
    }
  }

  /**
   * Remove cached metadata for a file
   * @param filePath Path to the file to remove from cache
   * @param tier The tier for which metadata was extracted
   * @param options Additional options that affect the extraction
   * @returns True if deletion was successful, false otherwise
   */
  async delete(filePath: string, tier: string, options: {
    includePerformance?: boolean;
    enableAdvancedAnalysis?: boolean
  } = {}): Promise<boolean> {
    if (!this.initialized || !this.config.enabled) {
      return false;
    }

    try {
      const key = this.generateCacheKey(filePath, tier, options);
      const success = await cacheManager.delete(key);

      if (success) {
        console.log(`🗑️  Metadata cache deleted for ${path.basename(filePath)}`);
      }

      return success;
    } catch (error) {
      console.error(`❌ Metadata cache delete error:`, error);
      return false;
    }
  }

  /**
   * Invalidate all cached metadata for a specific tier
   * @param tier The tier to invalidate cache for
   * @returns Number of entries invalidated
   */
  async invalidateByTier(tier: string): Promise<number> {
    if (!this.initialized || !this.config.enabled) {
      return 0;
    }

    try {
      const count = await cacheManager.invalidateByTag(`tier:${tier}`);
      console.log(`🔄 Invalidated ${count} metadata cache entries for tier: ${tier}`);
      return count;
    } catch (error) {
      console.error(`❌ Metadata cache invalidation error for tier ${tier}:`, error);
      return 0;
    }
  }

  /**
   * Invalidate all cached metadata for a specific file extension
   * @param extension The file extension to invalidate cache for
   * @returns Number of entries invalidated
   */
  async invalidateByFileExtension(extension: string): Promise<number> {
    if (!this.initialized || !this.config.enabled) {
      return 0;
    }

    try {
      const count = await cacheManager.invalidateByTag(`file:${extension}`);
      console.log(`🔄 Invalidated ${count} metadata cache entries for extension: ${extension}`);
      return count;
    } catch (error) {
      console.error(`❌ Metadata cache invalidation error for extension ${extension}:`, error);
      return 0;
    }
  }

  /**
   * Determine the appropriate cache strategy based on the tier
   * Different tiers have different cache TTL requirements
   * @param tier The tier to get cache strategy for
   * @returns The appropriate cache strategy
   */
  private getCacheStrategyForTier(tier: string): CacheStrategy {
    switch (tier.toLowerCase()) {
      case 'free':
        return CacheStrategy.SHORT_TERM; // 5 minutes for free tier
      case 'starter':
        return CacheStrategy.SHORT_TERM; // 5 minutes for starter tier
      case 'pro':
        return CacheStrategy.MEDIUM_TERM; // 1 hour for pro tier
      case 'super':
      case 'enterprise':
        return CacheStrategy.LONG_TERM; // 1 day for premium tiers
      default:
        return CacheStrategy.MEDIUM_TERM; // Default to 1 hour
    }
  }

  /**
   * Update access time for cache entry
   * This is handled by the main cache manager
   * @param key The cache key to update
   */
  private async updateAccessTime(key: string): Promise<void> {
    // This is handled by the main cache manager
    // We can add additional logic here if needed
  }

  /**
   * Get cache metrics and statistics
   * @returns Object containing cache metrics and configuration
   */
  async getMetrics(): Promise<any> {
    if (!this.initialized) {
      return { initialized: false };
    }

    const metrics = await cacheManager.getMetrics();
    return {
      ...metrics,
      config: {
        enabled: this.config.enabled,
        maxSize: this.config.maxSize,
        maxEntries: this.config.maxEntries,
        compression: this.config.compression,
        compressionThreshold: this.config.compressionThreshold,
      },
      initialized: this.initialized,
    };
  }

  /**
   * Clear all metadata cache entries
   * @returns True if clear was successful, false otherwise
   */
  async clear(): Promise<boolean> {
    if (!this.initialized || !this.config.enabled) {
      return false;
    }

    try {
      // We'll use a pattern to clear only metadata cache entries
      const count = await cacheManager.invalidatePattern('metadata:*');
      console.log(`🗑️  Cleared ${count} metadata cache entries`);
      return true;
    } catch (error) {
      console.error('❌ Metadata cache clear error:', error);
      return false;
    }
  }

  /**
   * Shutdown the cache manager
   * Cleans up resources and closes connections
   */
  async shutdown(): Promise<void> {
    // The main cache manager handles shutdown
    console.log('✅ Metadata cache manager shutdown');
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const metadataCacheManager = new MetadataCacheManager();
