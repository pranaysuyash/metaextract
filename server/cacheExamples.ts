/**
 * Cache Integration Examples
 *
 * Shows how to integrate the Redis caching layer into existing MetaExtract routes
 */

import { Router, Request } from 'express';
import {
  cacheMiddleware,
  cacheMetadata,
  cacheTierConfig,
  invalidateMetadataCache,
  invalidateTierCache,
  cacheKeys,
  preventCaching,
  setCacheControl
} from './cacheMiddleware';
import { cacheManager } from './cache';

// ============================================================================
// Example 1: Basic Route Caching
// ============================================================================

export function setupCachedRoutes(router: Router): void {
  // GET /api/tiers - Cache tier configurations for 1 day
  router.get('/tiers',
    cacheTierConfig(),
    async (req, res) => {
      // Expensive database operation
      const tiers = await fetchAllTiersFromDatabase();

      res.json(tiers);
    }
  );

  // POST /api/tiers - Invalidate cache when tiers change
  router.post('/tiers',
    invalidateTierCache(),
    async (req, res) => {
      // Update tier configuration
      await updateTierConfiguration(req.body);

      res.json({
        success: true,
        message: 'Tier configuration updated'
      });
    }
  );
}

// ============================================================================
// Example 2: Metadata Caching with Custom Keys
// ============================================================================

export function setupMetadataCaching(router: Router): void {
  // GET /api/metadata/:fileId - Cache specific file metadata
  router.get('/metadata/:fileId',
    cacheMetadata({
      keyGenerator: (req: Request) => {
        const fileId = req.params.fileId;
        const tier = (req as any).user?.tier || 'anonymous';
        return cacheKeys.metadata(fileId, tier);
      },
      ttl: 3600, // 1 hour
      tags: ['metadata']
    }),
    async (req, res) => {
      const fileId = req.params.fileId;

      // Expensive metadata extraction or database query
      const metadata = await fetchMetadataForFile(fileId);

      res.json(metadata);
    }
  );

  // POST /api/metadata/:fileId - Invalidate cache on updates
  router.post('/metadata/:fileId',
    invalidateMetadataCache(),
    async (req, res) => {
      const fileId = req.params.fileId;

      // Update metadata
      await updateFileMetadata(fileId, req.body);

      res.json({
        success: true,
        message: 'Metadata updated'
      });
    }
  );
}

// ============================================================================
// Example 3: Conditional Caching
// ============================================================================

export function setupConditionalCaching(router: Router): void {
  // Cache analytics, but skip for real-time requests
  router.get('/analytics',
    cacheMiddleware({
      keyGenerator: (req: Request) => {
        const url = new URL(req.url as string, `http://${req.headers.host}`);
        const period = url.searchParams.get('period') || '24h';
        return cacheKeys.analytics('overview', period);
      },
      ttl: 600, // 10 minutes
      skipCache: (req: Request) => {
        // Don't cache if requesting real-time data
        const url = new URL(req.url as string, `http://${req.headers.host}`);
        return url.searchParams.has('realtime') || url.searchParams.has('live');
      },
      tags: ['analytics']
    }),
    async (req, res) => {
      // Generate analytics data
      const analytics = await generateAnalytics(req.query);

      res.json(analytics);
    }
  );
}

// ============================================================================
// Example 4: Search Results Caching
// ============================================================================

export function setupSearchCaching(router: Router): void {
  // GET /api/search - Cache search results
  router.get('/search',
    cacheMiddleware({
      keyGenerator: (req: Request) => {
        const url = new URL(req.url as string, `http://${req.headers.host}`);
        const query = url.searchParams.get('q') || '';
        const filters = url.searchParams.toString();
        return cacheKeys.search(query, filters);
      },
      ttl: 1800, // 30 minutes
      tags: ['search'],
      skipCache: (req: Request) => {
        // Don't cache if user requests fresh results
        return req.headers['cache-control'] === 'no-cache';
      }
    }),
    async (req, res) => {
      const query = req.query.q as string;
      const filters = req.query.filters || {};

      // Expensive search operation
      const results = await performSearch(query, filters);

      res.json(results);
    }
  );
}

// ============================================================================
// Example 5: User-Specific Caching
// ============================================================================

export function setupUserCaching(router: Router): void {
  // GET /api/user/preferences - Cache user preferences
  router.get('/user/preferences',
    cacheMiddleware({
      keyGenerator: (req: Request) => {
        const userId = (req as any).user?.id;
        if (!userId) {
          throw new Error('User not authenticated');
        }
        return cacheKeys.userSession(userId);
      },
      ttl: 7200, // 2 hours
      tags: ['user'],
      skipCache: (req: Request) => {
        // Don't cache if user explicitly refreshes
        return req.headers['cache-control'] === 'no-cache';
      }
    }),
    async (req, res) => {
      const userId = (req as any).user.id;

      // Fetch user preferences
      const preferences = await getUserPreferences(userId);

      res.json(preferences);
    }
  );
}

// ============================================================================
// Example 6: Health Check Caching
// ============================================================================

export function setupHealthCheckCaching(router: Router): void {
  // GET /api/health - Cache health status (changes infrequently)
  router.get('/health',
    cacheMiddleware({
      keyGenerator: () => cacheKeys.health('system'),
      ttl: 60, // 1 minute
      tags: ['health']
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

export function setupNoCacheZones(router: Router): void {
  // POST /api/auth/login - Never cache authentication responses
  router.post('/auth/login',
    async (req, res) => {
      // Handle authentication
      const authResult = await authenticateUser(req.body);

      // Explicitly prevent caching
      preventCaching(res);

      res.json(authResult);
    }
  );

  // POST /api/payment - Never cache payment operations
  router.post('/payment',
    async (req, res) => {
      // Handle payment
      const paymentResult = await processPayment(req.body);

      // Prevent caching with short max-age
      setCacheControl(res, 0, { noStore: true });

      res.json(paymentResult);
    }
  );
}

// ============================================================================
// Example 8: Cache Invalidation Triggers
// ============================================================================

export function setupCacheInvalidation(router: Router): void {
  // POST /api/admin/cache/clear - Manual cache clearing
  router.post('/admin/cache/clear',
    async (req, res) => {
      const { tags, pattern } = req.body;

      if (tags && Array.isArray(tags)) {
        // Invalidate by tags
        let totalInvalidated = 0;
        for (const tag of tags) {
          const count = await cacheManager.invalidateByTag(tag);
          totalInvalidated += count;
        }

        res.json({
          success: true,
          invalidated: totalInvalidated,
          method: 'tags'
        });
      } else if (pattern) {
        // Invalidate by pattern
        const count = await cacheManager.invalidatePattern(pattern);

        res.json({
          success: true,
          invalidated: count,
          method: 'pattern'
        });
      } else {
        // Clear all cache
        const success = await cacheManager.clear();

        res.json({
          success,
          message: success ? 'All cache cleared' : 'Failed to clear cache'
        });
      }
    }
  );

  // POST /api/admin/cache/warmup - Pre-warm cache with important data
  router.post('/admin/cache/warmup',
    async (req, res) => {
      const keys = req.body.keys || [];

      // Common keys to warm up
      const defaultKeys = [
        { key: 'tier:config:free', value: await getTierConfig('free'), ttl: 86400 },
        { key: 'tier:config:premium', value: await getTierConfig('premium'), ttl: 86400 },
        { key: 'health:system', value: await getSystemHealth(), ttl: 60 },
      ];

      const keysToWarm = keys.length > 0 ? keys : defaultKeys;
      const warmed = await cacheManager.warmup(keysToWarm);

      res.json({
        success: true,
        warmed,
        total: keysToWarm.length
      });
    }
  );
}

// ============================================================================
// Helper Functions (to be implemented)
// ============================================================================

async function fetchAllTiersFromDatabase() {
  // Implementation would fetch tiers from database
  return {};
}

async function updateTierConfiguration(config: any) {
  // Implementation would update tier configuration
}

async function fetchMetadataForFile(fileId: string) {
  // Implementation would fetch metadata
  return {};
}

async function updateFileMetadata(fileId: string, metadata: any) {
  // Implementation would update metadata
}

async function generateAnalytics(query: any) {
  // Implementation would generate analytics
  return {};
}

async function performSearch(query: string, filters: any) {
  // Implementation would perform search
  return {};
}

async function getUserPreferences(userId: string) {
  // Implementation would fetch user preferences
  return {};
}

async function authenticateUser(credentials: any) {
  // Implementation would authenticate user
  return {};
}

async function processPayment(paymentData: any) {
  // Implementation would process payment
  return {};
}

async function checkSystemHealth() {
  // Implementation would check system health
  return {};
}

async function getTierConfig(tier: string) {
  // Implementation would get tier config
  return {};
}

async function getSystemHealth() {
  // Implementation would get system health
  return {};
}