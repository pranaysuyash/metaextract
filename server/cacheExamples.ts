/**
 * Cache Integration Examples
 *
 * Shows how to integrate the Redis caching layer into existing MetaExtract routes.
 * Each example demonstrates different caching patterns and strategies.
 *
 * ## Caching Strategy Guide
 *
 * - **Tier Config (24h)**: Rarely changes, high cost to compute
 * - **Metadata (1h)**: User may request same file, moderate cost
 * - **Analytics (10m)**: Users want near-real-time, high cost to compute
 * - **Search (30m)**: Popular queries benefit from caching, high cost
 * - **User Prefs (2h)**: Relatively static, frequent access pattern
 * - **Health (1m)**: Lightweight but called frequently
 */

import { Router, Request, Response } from 'express';
import {
  cacheMiddleware,
  cacheMetadata,
  cacheTierConfig,
  invalidateMetadataCache,
  invalidateTierCache,
  cacheKeys,
  preventCaching,
  setCacheControl,
} from './cacheMiddleware';
import { cacheManager } from './cache';
import type { AuthRequest } from './auth';

// ============================================================================
// Constants
// ============================================================================

const TTL = {
  TIER_CONFIG: 24 * 60 * 60, // 24 hours - rarely changes
  METADATA: 60 * 60, // 1 hour - good balance of freshness and reuse
  ANALYTICS: 10 * 60, // 10 minutes - near real-time with caching benefit
  SEARCH: 30 * 60, // 30 minutes - popular queries benefit from cache
  USER_PREFERENCES: 2 * 60 * 60, // 2 hours - relatively static user data
  HEALTH_CHECK: 60, // 1 minute - lightweight, frequent checks
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Safely extract user ID from request with proper typing
 * @throws Error if user is not authenticated
 */
function extractUserId(req: Request): string {
  const user = (req as AuthRequest).user;
  if (!user?.id) {
    throw new Error('User not authenticated');
  }
  return user.id;
}

/**
 * Safely extract user tier from request with fallback
 */
function getUserTier(req: Request): string {
  return (req as AuthRequest).user?.tier || 'anonymous';
}

/**
 * Parse URL and extract query parameters safely
 */
function parseQueryUrl(req: Request): URL {
  return new URL(req.url, `http://${req.headers.host}`);
}

/**
 * Check if request explicitly bypasses cache via headers
 */
function shouldBypassCache(req: Request): boolean {
  return req.headers['cache-control'] === 'no-cache';
}

/**
 * Check if URL has real-time or live parameters
 */
function isRealTimeRequest(url: URL): boolean {
  return url.searchParams.has('realtime') || url.searchParams.has('live');
}

// ============================================================================
// Example 1: Basic Route Caching
// ============================================================================

export function setupCachedRoutes(router: Router): void {
  // GET /api/tiers - Cache tier configurations for 1 day
  router.get('/tiers', cacheTierConfig(), async (req, res) => {
    // Expensive database operation
    const tiers = await fetchAllTiersFromDatabase();

    res.json(tiers);
  });

  // POST /api/tiers - Invalidate cache when tiers change
  router.post('/tiers', invalidateTierCache(), async (req, res) => {
    // Update tier configuration
    await updateTierConfiguration(req.body);

    res.json({
      success: true,
      message: 'Tier configuration updated',
    });
  });
}

// ============================================================================
// Example 2: Metadata Caching with Custom Keys
// ============================================================================

/**
 * Setup metadata caching with tier-aware cache keys
 * Ensures users with different tiers don't share cached metadata
 * (e.g., forensic tier may see more fields than free tier)
 */
export function setupMetadataCaching(router: Router): void {
  // GET /api/metadata/:fileId - Cache specific file metadata
  router.get(
    '/metadata/:fileId',
    cacheMetadata({
      keyGenerator: (req: Request) => {
        const fileId = req.params.fileId;
        const tier = getUserTier(req);
        return cacheKeys.metadata(fileId, tier);
      },
      ttl: TTL.METADATA,
      tags: ['metadata'],
    }),
    async (req, res) => {
      const fileId = req.params.fileId;
      // Expensive metadata extraction or database query
      const metadata = await fetchMetadataForFile(fileId);
      res.json(metadata);
    }
  );

  // POST /api/metadata/:fileId - Invalidate cache on updates
  router.post(
    '/metadata/:fileId',
    invalidateMetadataCache(),
    async (req, res) => {
      const fileId = req.params.fileId;
      // Update metadata
      await updateFileMetadata(fileId, req.body);
      res.json({
        success: true,
        message: 'Metadata updated',
      });
    }
  );
}

// ============================================================================
// Example 3: Conditional Caching
// ============================================================================

/**
 * Setup conditional caching for analytics
 * Bypasses cache for real-time/live requests to show fresh data
 * Regular requests use 10-minute cache for cost savings
 */
export function setupConditionalCaching(router: Router): void {
  router.get(
    '/analytics',
    cacheMiddleware({
      keyGenerator: (req: Request) => {
        const url = parseQueryUrl(req);
        const period = url.searchParams.get('period') || '24h';
        return cacheKeys.analytics('overview', period);
      },
      ttl: TTL.ANALYTICS,
      skipCache: (req: Request) => {
        // Don't cache if requesting real-time data
        const url = parseQueryUrl(req);
        return isRealTimeRequest(url);
      },
      tags: ['analytics'],
    }),
    async (req, res) => {
      const analytics = await generateAnalytics(req.query);
      res.json(analytics);
    }
  );
}

// ============================================================================
// Example 4: Search Results Caching
// ============================================================================

/**
 * Setup search result caching with query-based keys
 * Popular searches are cached for 30 minutes
 * Users can bypass cache with cache-control: no-cache header for fresh results
 */
export function setupSearchCaching(router: Router): void {
  router.get(
    '/search',
    cacheMiddleware({
      keyGenerator: (req: Request) => {
        const url = parseQueryUrl(req);
        const query = url.searchParams.get('q') || '';
        const filters = url.searchParams.toString();
        return cacheKeys.search(query, filters);
      },
      ttl: TTL.SEARCH,
      tags: ['search'],
      skipCache: shouldBypassCache,
    }),
    async (req, res) => {
      const query = req.query.q as string;
      const filters = req.query.filters || {};
      const results = await performSearch(query, filters);
      res.json(results);
    }
  );
}

// ============================================================================
// Example 5: User-Specific Caching
// ============================================================================

/**
 * Setup user preferences caching
 * Requires authentication. Caches per-user preferences for 2 hours.
 * Users can force refresh with cache-control: no-cache header
 */
export function setupUserCaching(router: Router): void {
  router.get(
    '/user/preferences',
    cacheMiddleware({
      keyGenerator: (req: Request) => {
        const userId = extractUserId(req);
        return cacheKeys.userSession(userId);
      },
      ttl: TTL.USER_PREFERENCES,
      tags: ['user'],
      skipCache: shouldBypassCache,
    }),
    async (req, res) => {
      try {
        const userId = extractUserId(req);
        const preferences = await getUserPreferences(userId);
        res.json(preferences);
      } catch (error: unknown) {
        const errMessage =
          error instanceof Error ? error.message : String(error);
        res.status(401).json({ error: errMessage });
      }
    }
  );
}

// ============================================================================
// Example 6: Health Check Caching
// ============================================================================

/**
 * Setup health check caching with short TTL
 * Minimizes impact of frequent health checks while keeping data reasonably fresh
 */
export function setupHealthCheckCaching(router: Router): void {
  router.get(
    '/health',
    cacheMiddleware({
      keyGenerator: () => cacheKeys.health('system'),
      ttl: TTL.HEALTH_CHECK,
      tags: ['health'],
    }),
    async (req, res) => {
      const health = await checkSystemHealth();
      res.json(health);
    }
  );
}

// ============================================================================
// Example 7: No-Cache Zones for Sensitive Data
// ============================================================================

/**
 * Setup routes that must never be cached
 * Critical for security and correctness: authentication and payments
 */
export function setupNoCacheZones(router: Router): void {
  /**
   * POST /api/auth/login - Never cache authentication responses
   * Each login must be fresh to prevent token reuse attacks
   */
  router.post('/auth/login', async (req, res) => {
    const authResult = await authenticateUser(req.body);
    preventCaching(res);
    res.json(authResult);
  });

  /**
   * POST /api/payment - Never cache payment operations
   * Payment state changes every request, must never be cached
   */
  router.post('/payment', async (req, res) => {
    const paymentResult = await processPayment(req.body);
    setCacheControl(res, 0, { noStore: true });
    res.json(paymentResult);
  });
}

// ============================================================================
// Example 8: Cache Invalidation Triggers
// ============================================================================

/**
 * Setup cache management endpoints (admin only)
 * Allows fine-grained control over cache invalidation and warming
 */
export function setupCacheInvalidation(router: Router): void {
  /**
   * POST /api/admin/cache/clear - Manual cache clearing
   * Supports three invalidation strategies: tags, pattern, or full clear
   */
  router.post('/admin/cache/clear', async (req, res) => {
    const { tags, pattern } = req.body;

    try {
      let invalidated: number;
      let method: string;

      if (tags && Array.isArray(tags)) {
        // Invalidate by tags (e.g., ['metadata', 'search'])
        let totalInvalidated = 0;
        for (const tag of tags) {
          const count = await cacheManager.invalidateByTag(tag);
          totalInvalidated += count;
        }
        invalidated = totalInvalidated;
        method = 'tags';
      } else if (pattern) {
        // Invalidate by pattern (e.g., 'metadata:*')
        invalidated = await cacheManager.invalidatePattern(pattern);
        method = 'pattern';
      } else {
        // Clear entire cache
        await cacheManager.clear();
        invalidated = -1; // -1 indicates full clear
        method = 'full';
      }

      res.json({
        success: true,
        invalidated,
        method,
      });
    } catch (error: unknown) {
      const errMessage = error instanceof Error ? error.message : String(error);
      res.status(500).json({
        success: false,
        error: errMessage,
      });
    }
  });

  /**
   * POST /api/admin/cache/warmup - Pre-warm cache with important data
   * Reduces initial latency for frequently accessed data
   */
  router.post('/admin/cache/warmup', async (req, res) => {
    const keys = req.body.keys || [];

    try {
      const defaultKeys = [
        {
          key: cacheKeys.tierConfig('free'),
          value: await getTierConfig('free'),
          ttl: TTL.TIER_CONFIG,
        },
        {
          key: cacheKeys.tierConfig('premium'),
          value: await getTierConfig('premium'),
          ttl: TTL.TIER_CONFIG,
        },
        {
          key: cacheKeys.health('system'),
          value: await getSystemHealth(),
          ttl: TTL.HEALTH_CHECK,
        },
      ];

      const keysToWarm = keys.length > 0 ? keys : defaultKeys;
      const warmed = await cacheManager.warmup(keysToWarm);

      res.json({
        success: true,
        warmed,
        total: keysToWarm.length,
      });
    } catch (error: unknown) {
      const errMessage = error instanceof Error ? error.message : String(error);
      res.status(500).json({
        success: false,
        error: errMessage,
      });
    }
  });
}

// ============================================================================
// Implementation Notes
// ============================================================================

/**
 * The helper functions below should be implemented in actual route handlers.
 * They're placeholders for demonstration purposes.
 *
 * Implement these functions with your actual business logic:
 * - fetchAllTiersFromDatabase() - Query tier data from database
 * - updateTierConfiguration() - Update tier config in database
 * - fetchMetadataForFile() - Extract/retrieve file metadata
 * - updateFileMetadata() - Persist metadata changes
 * - generateAnalytics() - Compute analytics from logs/data
 * - performSearch() - Query search index/database
 * - getUserPreferences() - Fetch user settings
 * - authenticateUser() - Validate credentials via auth provider
 * - processPayment() - Process payment through payment gateway
 * - checkSystemHealth() - Query service health status
 * - getTierConfig() - Fetch tier configuration
 * - getSystemHealth() - Aggregate system metrics
 */

// These function signatures are shown for reference only.
// Implement them with your actual business logic.

// declare function fetchAllTiersFromDatabase(): Promise<any>;
// declare function updateTierConfiguration(config: any): Promise<void>;
// declare function fetchMetadataForFile(fileId: string): Promise<any>;
// declare function updateFileMetadata(fileId: string, metadata: any): Promise<void>;
// declare function generateAnalytics(query: any): Promise<any>;
// ============================================================================
// Stub Implementations (for demonstration purposes)
// ============================================================================

async function fetchAllTiersFromDatabase(): Promise<any[]> {
  // Stub: In real implementation, this would query the database
  return [
    { id: 'free', name: 'Free', limits: { files: 10, size: '100MB' } },
    { id: 'premium', name: 'Premium', limits: { files: 100, size: '1GB' } },
  ];
}

async function updateTierConfiguration(config: any): Promise<void> {
  // Stub: In real implementation, this would update the database
  console.log('Updating tier configuration:', config);
}

async function fetchMetadataForFile(fileId: string): Promise<any> {
  // Stub: In real implementation, this would query the database
  return { id: fileId, metadata: { size: '1MB', type: 'image/jpeg' } };
}

async function updateFileMetadata(
  fileId: string,
  metadata: any
): Promise<void> {
  // Stub: In real implementation, this would update the database
  console.log('Updating metadata for file:', fileId, metadata);
}

async function generateAnalytics(query: any): Promise<any> {
  // Stub: In real implementation, this would perform complex analytics
  return { totalFiles: 1000, totalSize: '10GB', popularTypes: ['jpeg', 'png'] };
}

async function performSearch(query: string, filters: any): Promise<any[]> {
  // Stub: In real implementation, this would perform search
  return [{ id: 'file1', name: 'example.jpg', matches: ['query'] }];
}

async function getUserPreferences(userId: string): Promise<any> {
  // Stub: In real implementation, this would query user preferences
  return { theme: 'dark', notifications: true };
}

async function checkSystemHealth(): Promise<any> {
  // Stub: In real implementation, this would check system components
  return {
    status: 'healthy',
    uptime: '99.9%',
    services: ['db', 'cache', 'api'],
  };
}

async function authenticateUser(credentials: any): Promise<any> {
  // Stub: In real implementation, this would authenticate user
  return { id: 'user123', email: 'user@example.com' };
}

async function processPayment(paymentData: any): Promise<any> {
  // Stub: In real implementation, this would process payment
  return { transactionId: 'txn_123', status: 'success' };
}

async function getTierConfig(tier: string): Promise<any> {
  // Stub: In real implementation, this would get tier configuration
  return { name: tier, limits: { files: 50, size: '500MB' } };
}

async function getSystemHealth(): Promise<any> {
  // Stub: In real implementation, this would check system health
  return { status: 'healthy', services: ['api', 'db', 'cache'] };
}
