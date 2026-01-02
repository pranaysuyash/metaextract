/**
 * Cache Middleware for Express Routes
 *
 * Provides intelligent caching for API responses with configurable
 * strategies, automatic invalidation, and monitoring integration.
 */

import { Request, Response, NextFunction } from 'express';
import { cacheManager, CacheStrategy, CacheMetricsSnapshot } from './cache';

// ============================================================================
// Cache Middleware Options
// ============================================================================

export interface CacheMiddlewareOptions {
  enabled?: boolean;
  keyGenerator?: (req: Request) => string;
  ttl?: number;
  strategy?: CacheStrategy;
  tags?: string[];
  skipCache?: (req: Request) => boolean;
  varyOn?: string[];
}

export interface CachedResponse extends Response {
  _cached?: boolean;
  _cacheKey?: string;
}

// ============================================================================
// Default Key Generators
// ============================================================================

export const defaultKeyGenerator = (req: Request): string => {
  const parts = [
    'api',
    req.method,
    req.path,
    // Include query parameters for GET requests
    req.method === 'GET' ? new URLSearchParams(req.url as string).toString() : '',
    // Include user tier for authenticated requests
    (req as any).user?.tier || 'anonymous',
  ].filter(Boolean).join(':');

  return parts;
};

export const metadataKeyGenerator = (req: Request): string => {
  const url = new URL(req.url as string, `http://${req.headers.host}`);
  const fileId = url.searchParams.get('file_id');

  if (fileId) {
    return `metadata:file:${fileId}`;
  }

  return `metadata:${req.method}:${req.path}:${url.searchParams.toString()}`;
};

// ============================================================================
// Cache Middleware Factory
// ============================================================================

export function cacheMiddleware(options: CacheMiddlewareOptions = {}) {
  const {
    enabled = true,
    keyGenerator = defaultKeyGenerator,
    ttl = 300, // 5 minutes default
    strategy = CacheStrategy.SHORT_TERM,
    tags = [],
    skipCache = () => false,
  } = options;

  return async (req: Request, res: CachedResponse, next: NextFunction) => {
    // Skip caching if disabled or should skip
    if (!enabled || skipCache(req)) {
      return next();
    }

    const cacheKey = keyGenerator(req);
    res._cacheKey = cacheKey;

    try {
      // Try to get from cache
      const cached = await cacheManager.get<any>(cacheKey);
      if (cached !== null) {
        res._cached = true;

        // Set cache headers
        res.setHeader('X-Cache', 'HIT');
        res.setHeader('X-Cache-Key', cacheKey);
        if (cached.etag) {
          res.setHeader('ETag', cached.etag);
        }

        return res.json(cached.data);
      }

      // Cache miss - intercept response
      res.setHeader('X-Cache', 'MISS');
      res.setHeader('X-Cache-Key', cacheKey);

      // Store original json method
      const originalJson = res.json.bind(res);
      res.json = (data: any) => {
        // Cache the response
        cacheManager.set(cacheKey, { data, etag: res.getHeader('ETag') }, { ttl, tags })
          .catch((err) => console.error('Cache set error:', err));

        return originalJson(data);
      };

      next();
    } catch (error) {
      console.error('Cache middleware error:', error);
      // Continue without caching on error
      next();
    }
  };
}

// ============================================================================
// Specialized Cache Middleware
// ============================================================================

/**
 * Cache middleware for metadata endpoints
 */
export function cacheMetadata(options: Partial<CacheMiddlewareOptions> = {}) {
  return cacheMiddleware({
    ...options,
    keyGenerator: metadataKeyGenerator,
    ttl: 3600, // 1 hour for metadata
    tags: ['metadata'],
    strategy: CacheStrategy.MEDIUM_TERM,
  });
}

/**
 * Cache middleware for tier configuration
 */
export function cacheTierConfig(options: Partial<CacheMiddlewareOptions> = {}) {
  return cacheMiddleware({
    ...options,
    ttl: 86400, // 1 day for tier configs (rarely change)
    tags: ['tier', 'config'],
    strategy: CacheStrategy.LONG_TERM,
    skipCache: (req) => {
      // Don't cache if user is authenticated and tier might vary
      return !!(req as any).user;
    },
  });
}

/**
 * Cache middleware for analytics data
 */
export function cacheAnalytics(options: Partial<CacheMiddlewareOptions> = {}) {
  return cacheMiddleware({
    ...options,
    ttl: 600, // 10 minutes for analytics
    tags: ['analytics'],
    strategy: CacheStrategy.SHORT_TERM,
    skipCache: (req) => {
      // Don't cache if requesting real-time data
      const url = new URL(req.url as string, `http://${req.headers.host}`);
      return url.searchParams.has('realtime') || url.searchParams.has('live');
    },
  });
}

// ============================================================================
// Cache Invalidation Middleware
// ============================================================================

/**
 * Invalidate cache after mutations
 */
export function invalidateCache(tags: string[]) {
  return async (req: Request, res: Response, next: NextFunction) => {
    // Store original json method
    const originalJson = res.json.bind(res);

    res.json = (data: any) => {
      // Invalidate caches by tags after successful response
      if (res.statusCode >= 200 && res.statusCode < 300) {
        tags.forEach(tag => {
          cacheManager.invalidateByTag(tag)
            .catch((err) => console.error(`Cache invalidation error for tag ${tag}:`, err));
        });
      }

      return originalJson(data);
    };

    next();
  };
}

/**
 * Invalidate cache for specific metadata
 */
export function invalidateMetadataCache() {
  return invalidateCache(['metadata']);
}

/**
 * Invalidate cache for tier configurations
 */
export function invalidateTierCache() {
  return invalidateCache(['tier', 'config']);
}

// ============================================================================
// Cache Monitoring Middleware
// ============================================================================

/**
 * Add cache metrics to response headers
 */
export function cacheMetrics(req: Request, res: Response, next: NextFunction) {
  // Send metrics as response headers
  res.setHeader('X-Cache-Enabled', 'true');

  next();
}

/**
 * Cache monitoring endpoint
 */
export async function getCacheMetrics(req: Request, res: Response): Promise<void> {
  try {
    const metrics = await cacheManager.getMetrics();
    res.json(metrics);
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve cache metrics',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

/**
 * Cache warming endpoint
 */
export async function warmCache(req: Request, res: Response): Promise<void> {
  try {
    const { keys } = req.body;
    if (!Array.isArray(keys)) {
      res.status(400).json({
        error: 'Invalid request: keys must be an array'
      });
      return;
    }

    const warmed = await cacheManager.warmup(keys);
    res.json({
      success: true,
      warmed,
      total: keys.length
    });
  } catch (error) {
    res.status(500).json({
      error: 'Cache warming failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

/**
 * Cache clearing endpoint
 */
export async function clearCache(req: Request, res: Response): Promise<void> {
  try {
    const success = await cacheManager.clear();
    res.json({
      success,
      message: success ? 'Cache cleared successfully' : 'Failed to clear cache'
    });
  } catch (error) {
    res.status(500).json({
      error: 'Cache clearing failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// ============================================================================
// Cache Control Helpers
// ============================================================================

/**
 * Generate cache control headers
 */
export function setCacheControl(
  res: Response,
  maxAge: number,
  options: {
    mustRevalidate?: boolean;
    noCache?: boolean;
    noStore?: boolean;
    private?: boolean;
  } = {}
): void {
  const parts: string[] = [];

  if (options.noStore) {
    parts.push('no-store');
  } else {
    if (options.noCache) {
      parts.push('no-cache');
    }
    if (maxAge > 0) {
      parts.push(`max-age=${maxAge}`);
    }
    if (options.mustRevalidate) {
      parts.push('must-revalidate');
    }
    if (options.private) {
      parts.push('private');
    }
  }

  res.setHeader('Cache-Control', parts.join(', '));
}

/**
 * Prevent caching for sensitive responses
 */
export function preventCaching(res: Response): void {
  setCacheControl(res, 0, {
    noStore: true,
    noCache: true,
    mustRevalidate: true,
  });
}

// ============================================================================
// Cache Key Generators for Common Patterns
// ============================================================================

export const cacheKeys = {
  // Metadata caching
  metadata: (fileId: string, tier?: string) =>
    `metadata:file:${fileId}:${tier || 'default'}`,

  // Tier configuration caching
  tierConfig: (tier: string) =>
    `tier:config:${tier}`,

  // User session caching
  userSession: (userId: string) =>
    `session:user:${userId}`,

  // Analytics caching
  analytics: (type: string, period: string) =>
    `analytics:${type}:${period}`,

  // Search results caching
  search: (query: string, filters: string) =>
    `search:${query}:${filters}`,

  // Health check caching
  health: (service: string) =>
    `health:${service}`,
};