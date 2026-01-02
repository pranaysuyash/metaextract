/**
 * Redis Caching Layer for MetaExtract API
 *
 * Provides intelligent caching for API responses to improve performance
 * and reduce database load. Includes cache invalidation, monitoring,
 * and configurable TTL strategies.
 */

import { createClient, RedisClientType } from 'redis';

// ============================================================================
// Cache Configuration
// ============================================================================

export interface CacheConfig {
  enabled: boolean;
  url: string;
  defaultTTL: number; // Time to live in seconds
  maxMemory: string; // Redis max memory configuration
  evictionPolicy: string; // Redis eviction policy
}

export const DEFAULT_CACHE_CONFIG: CacheConfig = {
  enabled: process.env.REDIS_CACHE_ENABLED !== 'false',
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  defaultTTL: 300, // 5 minutes default
  maxMemory: '256mb',
  evictionPolicy: 'allkeys-lru',
};

// ============================================================================
// Cache Entry Structure
// ============================================================================

export interface CacheEntry<T> {
  key: string;
  value: T;
  ttl: number;
  createdAt: number;
  accessedAt: number;
  hitCount: number;
  metadata: {
    tags?: string[];
    version?: string;
    tier?: string;
  };
}

// ============================================================================
// Cache Strategies
// ============================================================================

export enum CacheStrategy {
  SHORT_TERM = 'short',      // 5 minutes - frequently changing data
  MEDIUM_TERM = 'medium',    // 1 hour - semi-static data
  LONG_TERM = 'long',        // 1 day - rarely changing data
  DYNAMIC = 'dynamic',       // Based on data characteristics
}

export const CACHE_TTL = {
  [CacheStrategy.SHORT_TERM]: 300,      // 5 minutes
  [CacheStrategy.MEDIUM_TERM]: 3600,    // 1 hour
  [CacheStrategy.LONG_TERM]: 86400,     // 1 day
  [CacheStrategy.DYNAMIC]: 0,           // Calculated at runtime
};

// ============================================================================
// Cache Manager Class
// ============================================================================

export class CacheManager {
  private client: RedisClientType | null = null;
  private config: CacheConfig;
  private metrics: CacheMetrics;
  private initialized: boolean = false;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...DEFAULT_CACHE_CONFIG, ...config };
    this.metrics = new CacheMetrics();
  }

  async initialize(): Promise<void> {
    if (!this.config.enabled) {
      console.log('🔄 Redis caching disabled');
      return;
    }

    try {
      this.client = createClient({
        url: this.config.url,
        socket: {
          reconnectStrategy: (retries: number) => {
            if (retries > 10) {
              console.error('❌ Redis reconnection failed after 10 attempts');
              return new Error('Reconnection failed');
            }
            return Math.min(retries * 100, 3000);
          },
        },
      });

      this.client.on('error', (err: Error) => {
        console.error('❌ Redis client error:', err);
        this.metrics.incrementError();
      });

      this.client.on('connect', () => {
        console.log('✅ Redis cache connected');
        this.initialized = true;
      });

      this.client.on('reconnecting', () => {
        console.log('🔄 Redis cache reconnecting...');
      });

      await this.client.connect();
      await this.configureRedis();

      console.log('✅ Redis cache layer initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Redis cache:', error);
      this.client = null;
      this.initialized = false;
    }
  }

  private async configureRedis(): Promise<void> {
    if (!this.client) return;

    try {
      // Configure memory limits and eviction policy
      await this.client.configSet('maxmemory', this.config.maxMemory);
      await this.client.configSet('maxmemory-policy', this.config.evictionPolicy);

      console.log('✅ Redis configured:', {
        maxMemory: this.config.maxMemory,
        evictionPolicy: this.config.evictionPolicy,
      });
    } catch (error) {
      console.error('❌ Failed to configure Redis:', error);
    }
  }

  // ============================================================================
  // Cache Operations
  // ============================================================================

  async get<T>(key: string): Promise<T | null> {
    if (!this.client || !this.initialized) {
      this.metrics.incrementMiss('cache_disabled');
      return null;
    }

    try {
      const data = await this.client.get(key);
      if (data) {
        this.metrics.incrementHit();
        await this.updateAccessTime(key);
        return JSON.parse(data) as T;
      }

      this.metrics.incrementMiss();
      return null;
    } catch (error) {
      console.error(`❌ Cache get error for key ${key}:`, error);
      this.metrics.incrementError();
      return null;
    }
  }

  async set<T>(
    key: string,
    value: T,
    options: {
      ttl?: number;
      tags?: string[];
      strategy?: CacheStrategy;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<boolean> {
    if (!this.client || !this.initialized) {
      return false;
    }

    try {
      const ttl = options.ttl || this.config.defaultTTL;
      const entry: CacheEntry<T> = {
        key,
        value,
        ttl,
        createdAt: Date.now(),
        accessedAt: Date.now(),
        hitCount: 0,
        metadata: options.metadata || {},
      };

      // Add tags if provided
      if (options.tags && options.tags.length > 0) {
        entry.metadata.tags = options.tags;
        await this.addToTags(key, options.tags);
      }

      await this.client.setEx(key, ttl, JSON.stringify(value));
      this.metrics.incrementSet();

      return true;
    } catch (error) {
      console.error(`❌ Cache set error for key ${key}:`, error);
      this.metrics.incrementError();
      return false;
    }
  }

  async delete(key: string): Promise<boolean> {
    if (!this.client || !this.initialized) {
      return false;
    }

    try {
      await this.client.del(key);
      this.metrics.incrementDelete();
      return true;
    } catch (error) {
      console.error(`❌ Cache delete error for key ${key}:`, error);
      this.metrics.incrementError();
      return false;
    }
  }

  async invalidateByTag(tag: string): Promise<number> {
    if (!this.client || !this.initialized) {
      return 0;
    }

    try {
      const keys = await this.getKeysByTag(tag);
      if (keys.length > 0) {
        await this.client.del(keys);
        this.metrics.incrementInvalidation(keys.length);
        return keys.length;
      }
      return 0;
    } catch (error) {
      console.error(`❌ Cache invalidation error for tag ${tag}:`, error);
      this.metrics.incrementError();
      return 0;
    }
  }

  async invalidatePattern(pattern: string): Promise<number> {
    if (!this.client || !this.initialized) {
      return 0;
    }

    try {
      const keys = await this.client.keys(pattern);
      if (keys.length > 0) {
        await this.client.del(keys);
        this.metrics.incrementInvalidation(keys.length);
        return keys.length;
      }
      return 0;
    } catch (error) {
      console.error(`❌ Cache pattern invalidation error:`, error);
      this.metrics.incrementError();
      return 0;
    }
  }

  // ============================================================================
  // Cache Management
  // ============================================================================

  async clear(): Promise<boolean> {
    if (!this.client || !this.initialized) {
      return false;
    }

    try {
      await this.client.flushDb();
      this.metrics.reset();
      console.log('✅ Cache cleared');
      return true;
    } catch (error) {
      console.error('❌ Cache clear error:', error);
      return false;
    }
  }

  async getMetrics(): Promise<CacheMetricsSnapshot> {
    const info = this.client ? await this.client.info('stats') : '';
    return {
      ...this.metrics.getSnapshot(),
      redisInfo: this.parseRedisInfo(info),
      initialized: this.initialized,
    };
  }

  async warmup(keys: Array<{ key: string; value: any; ttl?: number }>): Promise<number> {
    if (!this.client || !this.initialized) {
      return 0;
    }

    let warmed = 0;
    for (const { key, value, ttl } of keys) {
      const success = await this.set(key, value, { ttl });
      if (success) warmed++;
    }

    console.log(`✅ Cache warmed with ${warmed}/${keys.length} entries`);
    return warmed;
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  private async updateAccessTime(key: string): Promise<void> {
    if (!this.client) return;
    try {
      // Update access time in metadata (stored separately)
      await this.client.hSet(`access:${key}`, 'lastAccess', Date.now().toString());
    } catch (error) {
      // Silently fail to avoid impacting cache performance
    }
  }

  private async addToTags(key: string, tags: string[]): Promise<void> {
    if (!this.client) return;
    try {
      for (const tag of tags) {
        await this.client.sAdd(`tag:${tag}`, key);
      }
    } catch (error) {
      console.error(`❌ Error adding tags for key ${key}:`, error);
    }
  }

  private async getKeysByTag(tag: string): Promise<string[]> {
    if (!this.client) return [];
    try {
      const members = await this.client.sMembers(`tag:${tag}`);
      return members as string[];
    } catch (error) {
      console.error(`❌ Error getting keys by tag ${tag}:`, error);
      return [];
    }
  }

  private parseRedisInfo(info: string): Record<string, any> {
    const parsed: Record<string, any> = {};
    const lines = info.split('\r\n');

    for (const line of lines) {
      if (line.includes(':')) {
        const [key, value] = line.split(':');
        parsed[key] = value;
      }
    }

    return parsed;
  }

  // ============================================================================
  // Shutdown
  // ============================================================================

  async shutdown(): Promise<void> {
    if (this.client) {
      await this.client.quit();
      this.initialized = false;
      console.log('✅ Redis cache disconnected');
    }
  }
}

// ============================================================================
// Cache Metrics
// ============================================================================

export class CacheMetrics {
  private hits: number = 0;
  private misses: number = 0;
  private sets: number = 0;
  private deletes: number = 0;
  private errors: number = 0;
  private invalidations: number = 0;

  incrementHit(): void {
    this.hits++;
  }

  incrementMiss(reason: string = 'unknown'): void {
    this.misses++;
  }

  incrementSet(): void {
    this.sets++;
  }

  incrementDelete(): void {
    this.deletes++;
  }

  incrementError(): void {
    this.errors++;
  }

  incrementInvalidation(count: number = 1): void {
    this.invalidations += count;
  }

  reset(): void {
    this.hits = 0;
    this.misses = 0;
    this.sets = 0;
    this.deletes = 0;
    this.errors = 0;
    this.invalidations = 0;
  }

  getSnapshot(): CacheMetricsSnapshot {
    const total = this.hits + this.misses;
    const hitRate = total > 0 ? (this.hits / total) * 100 : 0;

    return {
      hits: this.hits,
      misses: this.misses,
      sets: this.sets,
      deletes: this.deletes,
      errors: this.errors,
      invalidations: this.invalidations,
      hitRate: hitRate.toFixed(2) + '%',
      totalOperations: total,
    };
  }
}

export interface CacheMetricsSnapshot {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  errors: number;
  invalidations: number;
  hitRate: string;
  totalOperations: number;
  redisInfo?: Record<string, any>;
  initialized?: boolean;
}

// ============================================================================
// Cache Decorators
// ============================================================================

export function cacheResponse<T>(
  keyGenerator: (...args: any[]) => string,
  options: {
    ttl?: number;
    tags?: string[];
    strategy?: CacheStrategy;
  } = {}
) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]): Promise<T> {
      const cacheManager = (this as any).cacheManager as CacheManager;
      if (!cacheManager) {
        return originalMethod.apply(this, args);
      }

      const key = keyGenerator(...args);

      // Try to get from cache
      const cached = await cacheManager.get<T>(key);
      if (cached !== null) {
        return cached;
      }

      // Execute original method
      const result = await originalMethod.apply(this, args);

      // Cache the result
      await cacheManager.set(key, result, options);

      return result;
    };

    return descriptor;
  };
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const cacheManager = new CacheManager();