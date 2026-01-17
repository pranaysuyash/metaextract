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
// Constants
// ============================================================================

const TIME_CONSTANTS = {
  MINUTE_MS: 60 * 1000,
  FIVE_MINUTES_MS: 5 * 60 * 1000,
  ONE_HOUR_MS: 60 * 60 * 1000,
  ONE_DAY_MS: 24 * 60 * 60 * 1000,
  CLEANUP_INTERVAL_MS: 5 * 60 * 1000, // 5 minutes
};

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

interface RateLimiterMiddleware {
  (req: Request, res: Response, next: NextFunction): void;
  windowMs: number;
}

interface CreateRateLimiterOptions {
  windowMs?: number;
  /**
   * Fixed limit per window. When provided, this limiter ignores tierConfig.
   * This is used for route-specific limits (e.g. Images MVP upload burst protection).
   */
  max?: number;
  /** Optional fixed daily limit. When omitted, no daily cap is enforced. */
  maxPerDay?: number;
  /** Skip function (compatible with common rate-limiter middleware APIs). */
  skip?: (req: Request) => boolean;
  skipFailedRequests?: boolean;
  keyGenerator?: (req: Request) => string;
  /** Optional name for key scoping/observability. */
  name?: string;
}

// ============================================================================
// In-Memory Rate Limit Store
// ============================================================================

const rateLimitStore = new Map<string, RateLimitEntry>();
let cleanupInterval: NodeJS.Timeout | null = null;

export function resetRateLimitStore(): void {
  rateLimitStore.clear();
}

/**
 * Start the cleanup interval for expired rate limit entries
 */
function startCleanupInterval(): void {
  if (cleanupInterval) return;

  cleanupInterval = setInterval(() => {
    const now = Date.now();
    const oneHourAgo = now - TIME_CONSTANTS.ONE_HOUR_MS;

    for (const [key, entry] of rateLimitStore.entries()) {
      // Only remove entries that have been inactive for over an hour
      if (entry.windowStart < oneHourAgo && entry.dayStart < oneHourAgo) {
        rateLimitStore.delete(key);
      }
    }
  }, TIME_CONSTANTS.CLEANUP_INTERVAL_MS);

  // Allow process to exit even with active interval
  if (typeof cleanupInterval.unref === 'function') {
    cleanupInterval.unref();
  }
}

/**
 * Stop the cleanup interval (for testing/graceful shutdown)
 */
export function stopCleanupInterval(): void {
  if (cleanupInterval) {
    clearInterval(cleanupInterval);
    cleanupInterval = null;
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Extract client IP address from request
 * Handles proxied requests via x-forwarded-for header
 */
function getClientIp(req: Request): string {
  return (
    req.ip ||
    req.headers['x-forwarded-for']?.toString().split(',')[0] ||
    req.socket.remoteAddress ||
    'unknown'
  );
}

function getClientKey(req: Request): string {
  // Use user ID if authenticated, otherwise use IP
  const authReq = req as AuthRequest;
  if (authReq.user?.id) {
    return `user:${authReq.user.id}`;
  }

  const ip = getClientIp(req);
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
  max?: number;
  maxPerDay?: number;
  skip?: (req: Request) => boolean;
  skipFailedRequests?: boolean;
  keyGenerator?: (req: Request) => string;
  name?: string;
}): RateLimiterMiddleware {
  const windowMs = options?.windowMs || TIME_CONSTANTS.MINUTE_MS;
  const skipFailedRequests = options?.skipFailedRequests ?? false;
  const keyGenerator = options?.keyGenerator || getClientKey;
  const skip = options?.skip;
  const fixedMax = typeof options?.max === 'number' ? options.max : undefined;
  const fixedMaxPerDay =
    typeof options?.maxPerDay === 'number' ? options.maxPerDay : undefined;

  const limiterId =
    options?.name ||
    (fixedMax !== undefined
      ? `fixed:${windowMs}:${fixedMax}:${fixedMaxPerDay ?? 'nodaily'}`
      : `tier:${windowMs}`);

  // Start cleanup interval on first middleware creation
  startCleanupInterval();

  function rateLimitMiddleware(
    req: Request,
    res: Response,
    next: NextFunction
  ): void {
    if (skip && skip(req)) {
      next();
      return;
    }

    const now = Date.now();
    const rawKey = keyGenerator(req);
    const key = `${limiterId}:${rawKey}`;

    const tier = fixedMax === undefined ? normalizeTier(getTierFromRequest(req)) : null;
    const tierLimits = tier ? getRateLimits(tier) : null;

    const windowLimit = fixedMax ?? tierLimits?.requestsPerMinute ?? 0;
    const dailyLimit = fixedMax !== undefined ? fixedMaxPerDay : tierLimits?.requestsPerDay;

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
    if (now - entry.dayStart > TIME_CONSTANTS.ONE_DAY_MS) {
      entry.dailyCount = 0;
      entry.dayStart = now;
    }

    // ✅ ATOMIC: Pre-increment counters to prevent race conditions
    // This ensures concurrent requests atomically consume quota
    // If multiple requests arrive simultaneously:
    // - Request A: count=0 → 1 (allowed)
    // - Request B: count=1 → 2 (allowed)
    // - Request C: count=2 → 3 (allowed if limit >= 3)
    // Without this, all 3 could see count=0 and all pass the check
    const newCount = ++entry.count;
    const newDailyCount = ++entry.dailyCount;

    // Check per-minute limit (after increment)
    if (windowLimit > 0 && newCount > windowLimit) {
      const retryAfter = Math.ceil((entry.windowStart + windowMs - now) / 1000);

      res.setHeader('Retry-After', retryAfter);
      res.setHeader('X-RateLimit-Limit', windowLimit);
      res.setHeader('X-RateLimit-Remaining', 0);
      res.setHeader(
        'X-RateLimit-Reset',
        Math.ceil((entry.windowStart + windowMs) / 1000)
      );

      res.status(429).json({
        error: 'Too many requests',
        message:
          fixedMax !== undefined
            ? `Rate limit exceeded. Maximum ${windowLimit} requests per window.`
            : `Rate limit exceeded. Maximum ${windowLimit} requests per minute for ${tier} tier.`,
        tier: tier ?? undefined,
        retry_after_seconds: retryAfter,
        upgrade_message:
          fixedMax !== undefined
            ? undefined
            : tier === 'free'
              ? 'Upgrade to Professional for higher rate limits'
              : tier === 'professional'
                ? 'Upgrade to Forensic for higher rate limits'
                : undefined,
      });

      // Decrement since we're rejecting this request
      entry.count--;
      entry.dailyCount--;
      return;
    }

    // Check daily limit (after increment)
    if (typeof dailyLimit === 'number' && newDailyCount > dailyLimit) {
      const nextDay = new Date(entry.dayStart + TIME_CONSTANTS.ONE_DAY_MS);

      res.setHeader('X-RateLimit-Daily-Limit', dailyLimit);
      res.setHeader('X-RateLimit-Daily-Remaining', 0);
      res.setHeader('X-RateLimit-Daily-Reset', nextDay.toISOString());

      res.status(429).json({
        error: 'Daily limit exceeded',
        message:
          fixedMax !== undefined
            ? `Daily limit of ${dailyLimit} requests exceeded.`
            : `Daily limit of ${dailyLimit} requests exceeded for ${tier} tier.`,
        tier: tier ?? undefined,
        reset_at: nextDay.toISOString(),
        upgrade_message:
          fixedMax !== undefined
            ? undefined
            : tier === 'free'
              ? 'Upgrade to Professional for unlimited daily extractions'
              : undefined,
      });

      // Decrement since we're rejecting this request
      entry.count--;
      entry.dailyCount--;
      return;
    }

    // Set rate limit headers
    res.setHeader('X-RateLimit-Limit', windowLimit);
    res.setHeader(
      'X-RateLimit-Remaining',
      Math.max(0, windowLimit - newCount)
    );
    res.setHeader(
      'X-RateLimit-Reset',
      Math.ceil((entry.windowStart + windowMs) / 1000)
    );
    if (typeof dailyLimit === 'number') {
      res.setHeader('X-RateLimit-Daily-Limit', dailyLimit);
      res.setHeader(
        'X-RateLimit-Daily-Remaining',
        Math.max(0, dailyLimit - newDailyCount)
      );
    }

    // Handle response to decrement on failure if configured
    if (skipFailedRequests) {
      const originalEnd = res.end;
      res.end = function (...args: any[]) {
        if (res.statusCode >= 400 && entry) {
          entry.count = Math.max(0, entry.count - 1);
          entry.dailyCount = Math.max(0, entry.dailyCount - 1);
        }
        return (originalEnd as any).apply(res, args as any);
      };
    }

    next();
  }

  // Attach windowMs property for status endpoint compatibility
  (rateLimitMiddleware as RateLimiterMiddleware).windowMs = windowMs;

  return rateLimitMiddleware as RateLimiterMiddleware;
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
  windowMs: TIME_CONSTANTS.FIVE_MINUTES_MS,
  keyGenerator: req => {
    const ip = getClientIp(req);
    return `auth:${ip}`;
  },
});

// ============================================================================
// Rate Limit Status Endpoint Handler
// ============================================================================

/**
 * Get current rate limit status for a request
 * Uses the standard 1-minute window for status reporting
 */
export function getRateLimitStatus(req: Request, res: Response): void {
  const rawKey = getClientKey(req);
  const tier = normalizeTier(getTierFromRequest(req));
  const limits = getRateLimits(tier);
  const limiterId = `tier:${TIME_CONSTANTS.MINUTE_MS}`;
  const entry = rateLimitStore.get(`${limiterId}:${rawKey}`);

  const now = Date.now();
  // Use standard window for status reporting
  const windowMs = TIME_CONSTANTS.MINUTE_MS;

  res.json({
    tier,
    limits: {
      requests_per_minute: limits.requestsPerMinute,
      requests_per_day: limits.requestsPerDay,
    },
    current: {
      minute_count: entry?.count || 0,
      minute_remaining: Math.max(
        0,
        limits.requestsPerMinute - (entry?.count || 0)
      ),
      minute_reset: entry
        ? new Date(entry.windowStart + windowMs).toISOString()
        : null,
      daily_count: entry?.dailyCount || 0,
      daily_remaining: Math.max(
        0,
        limits.requestsPerDay - (entry?.dailyCount || 0)
      ),
      daily_reset: entry
        ? new Date(entry.dayStart + TIME_CONSTANTS.ONE_DAY_MS).toISOString()
        : null,
    },
  });
}
