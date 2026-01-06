/**
 * Common cache configuration interfaces and defaults
 */

export interface CacheConfig {
  /** Whether caching is enabled */
  enabled: boolean;
  /** Redis connection URL */
  redisUrl: string;
  /** Default TTL in seconds */
  defaultTTL: number;
  /** Maximum cache size in MB */
  maxMemory: number;
  /** Cache eviction policy */
  evictionPolicy: string;
}

export const DEFAULT_CACHE_CONFIG: CacheConfig = {
  enabled: process.env.CACHE_ENABLED === 'true',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  defaultTTL: 3600, // 1 hour default
  maxMemory: 512, // 512MB default
  evictionPolicy: 'allkeys-lru',
};