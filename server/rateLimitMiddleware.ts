/**
 * Rate Limiting Middleware for Express Routes
 *
 * Provides Redis-backed distributed rate limiting with configurable
 * strategies, tier-based limits, and real-time monitoring integration.
 */

import { Request, Response, NextFunction } from 'express';
import { rateLimitManager, RateLimitStrategy } from './rateLimitRedis';
import type { AuthRequest } from './auth';

// ============================================================================
// Rate Limit Middleware Options
// ============================================================================

export interface RateLimitMiddlewareOptions {
  enabled?: boolean;
  strategy?: RateLimitStrategy;
  keyGenerator?: (req: Request) => string;
  skipRateLimit?: (req: Request) => boolean;
  tierBased?: boolean;
  ipBased?: boolean;
  endpoints?: {
    requestsPerMinute: number;
    requestsPerDay: number;
    burstLimit?: number;
  };
}

export interface RateLimitResponse extends Response {
  _rateLimited?: boolean;
  _rateLimitKey?: string;
}

// ============================================================================
// Default Key Generators
// ============================================================================

export const defaultKeyGenerator = (req: Request): string => {
  // For authenticated requests, use user ID
  if ((req as any).user?.id) {
    return `user:${(req as any).user.id}`;
  }

  // For anonymous requests, use IP address
  return `ip:${req.ip}`;
};

export const ipBasedKeyGenerator = (req: Request): string => {
  return `ip:${req.ip}`;
};

export const userBasedKeyGenerator = (req: Request): string => {
  const userId = (req as any).user?.id;
  if (!userId) {
    throw new Error('User not authenticated for user-based rate limiting');
  }
  return `user:${userId}`;
};

// ============================================================================
// Rate Limit Middleware Factory
// ============================================================================

export function rateLimitMiddleware(options: RateLimitMiddlewareOptions = {}) {
  const {
    enabled = true,
    keyGenerator = defaultKeyGenerator,
    skipRateLimit = () => false,
    tierBased = true,
    ipBased = false,
    endpoints,
  } = options;

  return async (req: Request, res: RateLimitResponse, next: NextFunction) => {
    // Skip rate limiting if disabled or should skip
    if (!enabled || skipRateLimit(req)) {
      return next();
    }

    try {
      const rateLimitKey = keyGenerator(req);
      res._rateLimitKey = rateLimitKey;

      let result;

      // Tier-based rate limiting for authenticated users
      if (tierBased && (req as any).user?.tier && !ipBased) {
        const userId = (req as any).user.id;
        const tier = (req as any).user.tier;

        result = await rateLimitManager.checkUserRateLimit(userId, tier);

        // Add tier-specific headers
        res.setHeader('X-RateLimit-Tier', tier);
      }
      // IP-based rate limiting for anonymous requests or when forced
      else {
        const ip = req.ip || req.socket?.remoteAddress || 'unknown';
        result = await rateLimitManager.checkIPRateLimit(ip);

        res.setHeader('X-RateLimit-Type', 'IP');
      }

      // Set rate limit headers
      res.setHeader('X-RateLimit-Limit', result.remaining.toString());
      res.setHeader('X-RateLimit-Remaining', result.remaining.toString());
      res.setHeader('X-RateLimit-Reset', new Date(Date.now() + 60000).toISOString());

      if (!result.allowed) {
        res._rateLimited = true;

        return res.status(429).json({
          error: 'Too Many Requests',
          message: 'Rate limit exceeded. Please try again later.',
          retryAfter: result.retryAfter,
          resetTime: new Date(Date.now() + (result.retryAfter || 60) * 1000).toISOString(),
        });
      }

      next();
    } catch (error) {
      console.error('Rate limit middleware error:', error);
      // Continue without rate limiting on error
      next();
    }
  };
}

// ============================================================================
// Specialized Rate Limit Middleware
// ============================================================================

/**
 * Rate limit middleware for metadata extraction endpoints
 */
export function rateLimitExtraction(options: Partial<RateLimitMiddlewareOptions> = {}) {
  return rateLimitMiddleware({
    ...options,
    keyGenerator: (req) => {
      // More aggressive rate limiting for extraction (expensive operation)
      if ((req as any).user?.id) {
        return `extraction:user:${(req as any).user.id}`;
      }
      return `extraction:ip:${req.ip}`;
    },
    tierBased: true,
  });
}

/**
 * Rate limit middleware for authentication endpoints
 */
export function rateLimitAuth(options: Partial<RateLimitMiddlewareOptions> = {}) {
  return rateLimitMiddleware({
    ...options,
    keyGenerator: ipBasedKeyGenerator, // Always IP-based for auth
    tierBased: false,
    ipBased: true,
    endpoints: {
      requestsPerMinute: 10,  // Stricter for auth endpoints
      requestsPerDay: 100,
    },
  });
}

/**
 * Rate limit middleware for API endpoints
 */
export function rateLimitAPI(options: Partial<RateLimitMiddlewareOptions> = {}) {
  return rateLimitMiddleware({
    ...options,
    tierBased: true,
    skipRateLimit: (req) => {
      // Skip rate limiting for health checks
      return req.path === '/health' || req.path === '/api/health';
    },
  });
}

/**
 * Rate limit middleware for public endpoints
 */
export function rateLimitPublic(options: Partial<RateLimitMiddlewareOptions> = {}) {
  return rateLimitMiddleware({
    ...options,
    keyGenerator: ipBasedKeyGenerator,
    tierBased: false,
    ipBased: true,
    endpoints: {
      requestsPerMinute: 30,
      requestsPerDay: 500,
    },
  });
}

// ============================================================================
// Rate Limit Monitoring Middleware
// ============================================================================

/**
 * Add rate limit metrics to response headers
 */
export function rateLimitMetrics(req: Request, res: Response, next: NextFunction) {
  res.setHeader('X-RateLimit-Enabled', 'true');
  next();
}

/**
 * Rate limit monitoring endpoint
 */
export async function getRateLimitMetrics(req: Request, res: Response): Promise<void> {
  try {
    const metrics = await rateLimitManager.getMetrics();
    res.json(metrics);
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve rate limit metrics',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

/**
 * Rate limit reset endpoint (admin only)
 */
export async function resetRateLimit(req: Request, res: Response): Promise<void> {
  try {
    const { identifier } = req.params;

    if (!identifier) {
      res.status(400).json({
        error: 'Identifier is required'
      });
      return;
    }

    const success = await rateLimitManager.resetRateLimit(identifier);

    res.json({
      success,
      message: success
        ? `Rate limit reset for ${identifier}`
        : `Failed to reset rate limit for ${identifier}`
    });
  } catch (error) {
    res.status(500).json({
      error: 'Rate limit reset failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// ============================================================================
// Rate Limit Control Helpers
// ============================================================================

/**
 * Check if request should skip rate limiting
 */
export const shouldSkipRateLimit = {
  // Skip for WebSocket upgrades
  webSocket: (req: Request) =>
    req.headers.upgrade?.toLowerCase() === 'websocket',

  // Skip for admin users
  adminUser: (req: Request) =>
    (req as any).user?.role === 'admin',

  // Skip for health checks
  healthCheck: (req: Request) =>
    req.path === '/health' || req.path === '/api/health',

  // Skip for specific user roles
  roles: (roles: string[]) => (req: Request) =>
    (req as any).user?.role && roles.includes((req as any).user.role),
};

/**
 * Combine multiple skip conditions
 */
export function combineSkipConditions(...conditions: Array<(req: Request) => boolean>) {
  return (req: Request) => conditions.some(condition => condition(req));
}

// ============================================================================
// Rate Limit Error Handling
// ============================================================================

/**
 * Custom rate limit error handler
 */
export function rateLimitErrorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  if (err.message.includes('Rate limit')) {
    return res.status(429).json({
      error: 'Too Many Requests',
      message: err.message,
      retryAfter: 60,
    });
  }

  next(err);
}

// ============================================================================
// Export rate limit middleware collections
// ============================================================================

export const rateLimitMiddlewareCollection = {
  // General purpose
  api: rateLimitAPI,

  // Specific endpoint types
  extraction: rateLimitExtraction,
  auth: rateLimitAuth,
  public: rateLimitPublic,

  // Monitoring
  metrics: rateLimitMetrics,

  // Error handling
  errorHandler: rateLimitErrorHandler,
};