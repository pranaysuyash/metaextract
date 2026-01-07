/**
 * Redis-Backed Distributed Rate Limiting
 *
 * Replaces in-memory rate limiting with Redis-based solution for:
 * - Distributed rate limiting across multiple server instances
 * - Persistent rate limit state across restarts
 * - Sliding window algorithm with Redis sorted sets
 * - Tier-based and IP-based rate limiting
 * - Real-time monitoring and metrics
 */

import { createClient, RedisClientType } from 'redis';
import type { Request, Response, NextFunction } from 'express';
import type { AuthRequest } from './auth';
import { getRateLimits, normalizeTier } from '@shared/tierConfig';

// ============================================================================
// Configuration
// ============================================================================

export interface RateLimitConfig {
  enabled: boolean;
  redisUrl: string;
  defaultLimits: {
    requestsPerMinute: number;
    requestsPerDay: number;
    burstLimit: number;
  };
}

export const DEFAULT_RATE_LIMIT_CONFIG: RateLimitConfig = {
  enabled: process.env.RATE_LIMIT_ENABLED !== 'false',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  defaultLimits: {
    requestsPerMinute: 60,
    requestsPerDay: 1000,
    burstLimit: 10,
  },
};

// ============================================================================
// Rate Limit Strategies
// ============================================================================

export enum RateLimitStrategy {
  SLIDING_WINDOW = 'sliding_window',  // Precise, Redis-backed
  TOKEN_BUCKET = 'token_bucket',      // Smooth rate limiting
  FIXED_WINDOW = 'fixed_window',      // Simple, can have edge effects
}

// ============================================================================
// Rate Limit Manager
// ============================================================================

export class RateLimitManager {
  private client: RedisClientType | null = null;
  private config: RateLimitConfig;
  private metrics: RateLimitMetrics;
  private initialized: boolean = false;
  
  // In-memory fallback for when Redis is unavailable
  private inMemoryFallback = new Map<string, { count: number; windowStart: number }>();
  private fallbackWindowMs = 60000; // 1 minute window
  private fallbackCleanupInterval: NodeJS.Timeout | null = null;

  constructor(config: Partial<RateLimitConfig> = {}) {
    this.config = { ...DEFAULT_RATE_LIMIT_CONFIG, ...config };
    this.metrics = new RateLimitMetrics();
    this.startFallbackCleanup();
  }
  
  /**
   * Start periodic cleanup of in-memory fallback entries
   */
  private startFallbackCleanup(): void {
    if (this.fallbackCleanupInterval) return;
    
    this.fallbackCleanupInterval = setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.inMemoryFallback.entries()) {
        if (now - entry.windowStart > this.fallbackWindowMs * 2) {
          this.inMemoryFallback.delete(key);
        }
      }
    }, this.fallbackWindowMs);
    
    if (typeof this.fallbackCleanupInterval.unref === 'function') {
      this.fallbackCleanupInterval.unref();
    }
  }
  
  /**
   * In-memory rate limit check when Redis is unavailable
   * Uses conservative limits to prevent abuse during Redis outages
   */
  private checkInMemoryFallback(
    identifier: string, 
    limits: { requestsPerMinute: number; requestsPerDay: number }
  ): { allowed: boolean; remaining: number } {
    const now = Date.now();
    const entry = this.inMemoryFallback.get(identifier);
    
    // Conservative limit during Redis outage (50% of normal)
    const fallbackLimit = Math.max(1, Math.floor(limits.requestsPerMinute / 2));
    
    if (!entry || now - entry.windowStart > this.fallbackWindowMs) {
      this.inMemoryFallback.set(identifier, { count: 1, windowStart: now });
      return { allowed: true, remaining: fallbackLimit - 1 };
    }
    
    if (entry.count >= fallbackLimit) {
      return { allowed: false, remaining: 0 };
    }
    
    entry.count++;
    return { allowed: true, remaining: fallbackLimit - entry.count };
  }

  async initialize(): Promise<void> {
    if (!this.config.enabled) {
      console.log('🔄 Rate limiting disabled');
      return;
    }

    try {
      this.client = createClient({
        url: this.config.redisUrl,
        socket: {
          reconnectStrategy: (retries: number) => {
            if (retries > 10) {
              console.error('❌ Redis reconnection failed for rate limiting');
              return new Error('Reconnection failed');
            }
            return Math.min(retries * 100, 3000);
          },
        },
      });

      this.client.on('error', (err: Error) => {
        console.error('❌ Rate limiter Redis error:', err);
        this.metrics.incrementError();
      });

      this.client.on('connect', () => {
        console.log('✅ Rate limiter Redis connected');
        this.initialized = true;
      });

      await this.client.connect();
      console.log('✅ Redis-backed rate limiting initialized');
    } catch (error) {
      console.error('❌ Failed to initialize rate limiting:', error);
      this.client = null;
      this.initialized = false;
    }
  }

  // ============================================================================
  // Sliding Window Rate Limiting
  // ============================================================================

  async checkRateLimit(
    identifier: string,
    limits: {
      requestsPerMinute: number;
      requestsPerDay: number;
      burstLimit?: number;
    }
  ): Promise<{
    allowed: boolean;
    remaining: number;
    resetTime: number;
    retryAfter?: number;
  }> {
    if (!this.client || !this.initialized) {
      // If rate limiting is disabled, always allow
      return {
        allowed: true,
        remaining: limits.requestsPerMinute,
        resetTime: Date.now() + 60000,
      };
    }

    try {
      const now = Date.now();
      const oneMinuteAgo = now - 60000;
      const oneDayAgo = now - 86400000;

      // Check minute-level limit using sliding window
      const minuteKey = `ratelimit:minute:${identifier}`;
      await this.client.zRemRangeByScore(minuteKey, oneMinuteAgo, now);
      const minuteCount = await this.client.zCount(minuteKey, oneMinuteAgo, now);

      // Check day-level limit
      const dayKey = `ratelimit:day:${identifier}`;
      await this.client.zRemRangeByScore(dayKey, oneDayAgo, now);
      const dayCount = await this.client.zCount(dayKey, oneDayAgo, now);

      const minuteRequests = Number(minuteCount || 0);
      const dayRequests = Number(dayCount || 0);

      // Check if limits are exceeded
      const minuteExceeded = minuteRequests >= limits.requestsPerMinute;
      const dayExceeded = dayRequests >= limits.requestsPerDay;

      if (minuteExceeded || dayExceeded) {
        this.metrics.incrementBlock();
        const retryAfter = minuteExceeded ? 60 : 86400;

        return {
          allowed: false,
          remaining: 0,
          resetTime: now + (retryAfter * 1000),
          retryAfter,
        };
      }

      // Add current request to sliding windows
      await this.client.zAdd(minuteKey, { score: now, value: now.toString() });
      await this.client.expire(minuteKey, 120); // 2 minutes cleanup

      await this.client.zAdd(dayKey, { score: now, value: now.toString() });
      await this.client.expire(dayKey, 172800); // 2 days cleanup

      this.metrics.incrementAllow();

      const remaining = Math.min(
        limits.requestsPerMinute - minuteRequests - 1,
        limits.requestsPerDay - dayRequests - 1
      );

      return {
        allowed: true,
        remaining: Math.max(0, remaining),
        resetTime: now + 60000,
      };
    } catch (error) {
      console.error('❌ Rate limit check error:', error);
      this.metrics.incrementError();

      // SECURITY FIX: Use in-memory fallback instead of fail-open
      // This prevents attackers from bypassing rate limits by causing Redis errors
      console.warn('⚠️  Using in-memory rate limit fallback due to Redis error');
      const fallbackResult = this.checkInMemoryFallback(identifier, limits);
      
      if (!fallbackResult.allowed) {
        return {
          allowed: false,
          remaining: 0,
          resetTime: Date.now() + 60000,
          retryAfter: 60,
        };
      }
      
      return {
        allowed: true,
        remaining: fallbackResult.remaining,
        resetTime: Date.now() + 60000,
      };
    }
  }

  // ============================================================================
  // IP-Based Rate Limiting
  // ============================================================================

  async checkIPRateLimit(ip: string): Promise<{
    allowed: boolean;
    remaining: number;
    retryAfter?: number;
  }> {
    const limits = {
      requestsPerMinute: 30,  // Stricter for anonymous
      requestsPerDay: 500,
    };

    const result = await this.checkRateLimit(`ip:${ip}`, limits);

    return {
      allowed: result.allowed,
      remaining: result.remaining,
      retryAfter: result.retryAfter,
    };
  }

  // ============================================================================
  // User-Based Rate Limiting
  // ============================================================================

  async checkUserRateLimit(userId: string, tier: string): Promise<{
    allowed: boolean;
    remaining: number;
    retryAfter?: number;
  }> {
    const tierLimits = getRateLimits(tier);

    const limits = {
      requestsPerMinute: tierLimits.requestsPerMinute,
      requestsPerDay: tierLimits.requestsPerDay,
    };

    const result = await this.checkRateLimit(`user:${userId}`, limits);

    return {
      allowed: result.allowed,
      remaining: result.remaining,
      retryAfter: result.retryAfter,
    };
  }

  // ============================================================================
  // Admin Functions
  // ============================================================================

  async resetRateLimit(identifier: string): Promise<boolean> {
    if (!this.client) return false;

    try {
      await this.client.del(`ratelimit:minute:${identifier}`);
      await this.client.del(`ratelimit:day:${identifier}`);

      console.log(`✅ Rate limit reset for ${identifier}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to reset rate limit for ${identifier}:`, error);
      return false;
    }
  }

  async getMetrics(): Promise<RateLimitMetricsSnapshot> {
    const snapshot = this.metrics.getSnapshot();

    if (this.client) {
      try {
        // Get Redis info for rate limit keys
        const minuteKeys = await this.client.keys('ratelimit:minute:*');
        const dayKeys = await this.client.keys('ratelimit:day:*');

        snapshot.activeIdentifiers = {
          minute: minuteKeys.length,
          day: dayKeys.length,
        };
      } catch (error) {
        console.error('❌ Error getting rate limit metrics:', error);
      }
    }

    return snapshot;
  }

  // ============================================================================
  // Shutdown
  // ============================================================================

  async shutdown(): Promise<void> {
    if (this.client) {
      await this.client.quit();
      this.initialized = false;
      console.log('✅ Rate limiter Redis disconnected');
    }
  }
}

// ============================================================================
// Rate Limit Metrics
// ============================================================================

export class RateLimitMetrics {
  private allowed: number = 0;
  private blocked: number = 0;
  private errors: number = 0;
  private resets: number = 0;

  incrementAllow(): void {
    this.allowed++;
  }

  incrementBlock(): void {
    this.blocked++;
  }

  incrementError(): void {
    this.errors++;
  }

  incrementReset(): void {
    this.resets++;
  }

  reset(): void {
    this.allowed = 0;
    this.blocked = 0;
    this.errors = 0;
    this.resets = 0;
  }

  getSnapshot(): RateLimitMetricsSnapshot {
    const total = this.allowed + this.blocked;
    const blockRate = total > 0 ? (this.blocked / total) * 100 : 0;

    return {
      allowed: this.allowed,
      blocked: this.blocked,
      errors: this.errors,
      resets: this.resets,
      total,
      blockRate: blockRate.toFixed(2) + '%',
      allowRate: (100 - blockRate).toFixed(2) + '%',
    };
  }
}

export interface RateLimitMetricsSnapshot {
  allowed: number;
  blocked: number;
  errors: number;
  resets: number;
  total: number;
  blockRate: string;
  allowRate: string;
  activeIdentifiers?: {
    minute: number;
    day: number;
  };
}

// ============================================================================
// Export Singleton
// ============================================================================

export const rateLimitManager = new RateLimitManager();