/**
 * Rate Limiting Middleware
 *
 * Implements tier-based rate limiting for API endpoints.
 * Uses in-memory storage with sliding window algorithm.
 */

import type { Request, Response, NextFunction } from 'express';
import { getRateLimits, normalizeTier } from '@shared/tierConfig';
import type { AuthRequest } from '../auth';

// ============================================================================
// Types
// ============================================================================

interface RateLimitEntry {
  count: number;
  windowStart: number;
  dailyCount: number;
  dayStart: number;
}

interface RateLimitConfig {
  requestsPerMinute: number;
  requestsPerDay: number;
  burstLimit: number;
}

// ============================================================================
// In-Memory Rate Limit Store
// ============================================================================

const rateLimitStore = new Map<string, RateLimitEntry>();

// Cleanup old entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  const oneHourAgo = now - 3600000;

  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.windowStart < oneHourAgo) {
      rateLimitStore.delete(key);
    }
  }
}, 300000);

// ============================================================================
// Helper Functions
// ============================================================================

function getClientKey(req: Request): string {
  // Use user ID if authenticated, otherwise use IP
  const authReq = req as AuthRequest;
  if (authReq.user?.id) {
    return `user:${authReq.user.id}`;
  }

  const ip =
    req.ip ||
    req.headers['x-forwarded-for']?.toString().split(',')[0] ||
    req.socket.remoteAddress ||
    'unknown';
  return `ip:${ip}`;
}

function getTierFromRequest(req: Request): string {
  const authReq = req as AuthRequest;

  // Check user's subscription tier
  if (authReq.user?.tier) {
    return authReq.user.tier;
  }

  // Check query parameter (for testing)
  if (req.query.tier) {
    return req.query.tier as string;
  }

  // Default to free tier
  return 'free';
}

// ============================================================================
// Rate Limit Middleware Factory
// ============================================================================

export function createRateLimiter(options?: {
  windowMs?: number;
  skipFailedRequests?: boolean;
  keyGenerator?: (req: Request) => string;
}) {
  const windowMs = options?.windowMs || 60000; // 1 minute
  const skipFailedRequests = options?.skipFailedRequests ?? false;
  const keyGenerator = options?.keyGenerator || getClientKey;

  return function rateLimitMiddleware(
    req: Request,
    res: Response,
    next: NextFunction
  ): void {
    const now = Date.now();
    const key = keyGenerator(req);
    const tier = normalizeTier(getTierFromRequest(req));
    const limits = getRateLimits(tier);

    // Get or create rate limit entry
    let entry = rateLimitStore.get(key);

    if (!entry) {
      entry = {
        count: 0,
        windowStart: now,
        dailyCount: 0,
        dayStart: now,
      };
      rateLimitStore.set(key, entry);
    }

    // Reset window if expired
    if (now - entry.windowStart > windowMs) {
      entry.count = 0;
      entry.windowStart = now;
    }

    // Reset daily count if new day
    const dayMs = 24 * 60 * 60 * 1000;
    if (now - entry.dayStart > dayMs) {
      entry.dailyCount = 0;
      entry.dayStart = now;
    }

    // Check per-minute limit
    if (entry.count >= limits.requestsPerMinute) {
      const retryAfter = Math.ceil((entry.windowStart + windowMs - now) / 1000);

      res.setHeader('Retry-After', retryAfter);
      res.setHeader('X-RateLimit-Limit', limits.requestsPerMinute);
      res.setHeader('X-RateLimit-Remaining', 0);
      res.setHeader(
        'X-RateLimit-Reset',
        Math.ceil((entry.windowStart + windowMs) / 1000)
      );

      res.status(429).json({
        error: 'Too many requests',
        message: `Rate limit exceeded. Maximum ${limits.requestsPerMinute} requests per minute for ${tier} tier.`,
        tier,
        retry_after_seconds: retryAfter,
        upgrade_message:
          tier === 'free'
            ? 'Upgrade to Professional for higher rate limits'
            : tier === 'professional'
            ? 'Upgrade to Forensic for higher rate limits'
            : undefined,
      });
      return;
    }

    // Check daily limit
    if (entry.dailyCount >= limits.requestsPerDay) {
      const nextDay = new Date(entry.dayStart + dayMs);

      res.setHeader('X-RateLimit-Daily-Limit', limits.requestsPerDay);
      res.setHeader('X-RateLimit-Daily-Remaining', 0);
      res.setHeader('X-RateLimit-Daily-Reset', nextDay.toISOString());

      res.status(429).json({
        error: 'Daily limit exceeded',
        message: `Daily limit of ${limits.requestsPerDay} requests exceeded for ${tier} tier.`,
        tier,
        reset_at: nextDay.toISOString(),
        upgrade_message:
          tier === 'free'
            ? 'Upgrade to Professional for unlimited daily extractions'
            : undefined,
      });
      return;
    }

    // Increment counters
    entry.count++;
    entry.dailyCount++;

    // Set rate limit headers
    res.setHeader('X-RateLimit-Limit', limits.requestsPerMinute);
    res.setHeader(
      'X-RateLimit-Remaining',
      Math.max(0, limits.requestsPerMinute - entry.count)
    );
    res.setHeader(
      'X-RateLimit-Reset',
      Math.ceil((entry.windowStart + windowMs) / 1000)
    );
    res.setHeader('X-RateLimit-Daily-Limit', limits.requestsPerDay);
    res.setHeader(
      'X-RateLimit-Daily-Remaining',
      Math.max(0, limits.requestsPerDay - entry.dailyCount)
    );

    // Handle response to decrement on failure if configured
    if (skipFailedRequests) {
      const originalEnd = res.end;
      res.end = function (...args: any[]) {
        if (res.statusCode >= 400) {
          entry!.count = Math.max(0, entry!.count - 1);
          entry!.dailyCount = Math.max(0, entry!.dailyCount - 1);
        }
        return (originalEnd as any).apply(res, args as any);
      };
    }

    next();
  };
}

// ============================================================================
// Pre-configured Rate Limiters
// ============================================================================

/**
 * Standard API rate limiter
 * Uses tier-based limits from tierConfig
 */
export const apiRateLimiter = createRateLimiter();

/**
 * Extraction endpoint rate limiter
 * Stricter limits for resource-intensive operations
 */
export const extractionRateLimiter = createRateLimiter({
  skipFailedRequests: true,
});

/**
 * Authentication rate limiter
 * Prevents brute force attacks
 */
export const authRateLimiter = createRateLimiter({
  windowMs: 300000, // 5 minutes
  keyGenerator: (req) => {
    const ip =
      req.ip ||
      req.headers['x-forwarded-for']?.toString().split(',')[0] ||
      'unknown';
    return `auth:${ip}`;
  },
});

// ============================================================================
// Rate Limit Status Endpoint Handler
// ============================================================================

export function getRateLimitStatus(req: Request, res: Response): void {
  const key = getClientKey(req);
  const tier = normalizeTier(getTierFromRequest(req));
  const limits = getRateLimits(tier);
  const entry = rateLimitStore.get(key);

  const now = Date.now();
  const windowMs = 60000;
  const dayMs = 24 * 60 * 60 * 1000;

  res.json({
    tier,
    limits: {
      requests_per_minute: limits.requestsPerMinute,
      requests_per_day: limits.requestsPerDay,
    },
    current: {
      minute_count: entry?.count || 0,
      minute_remaining: limits.requestsPerMinute - (entry?.count || 0),
      minute_reset: entry
        ? new Date(entry.windowStart + windowMs).toISOString()
        : null,
      daily_count: entry?.dailyCount || 0,
      daily_remaining: limits.requestsPerDay - (entry?.dailyCount || 0),
      daily_reset: entry
        ? new Date(entry.dayStart + dayMs).toISOString()
        : null,
    },
  });
}
