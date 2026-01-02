/**
 * Rate Limiting Integration Examples
 *
 * Shows how to integrate the Redis-backed rate limiting layer into existing MetaExtract routes
 */

import { Router } from 'express';
import { rateLimitManager } from './rateLimitRedis';
import {
  rateLimitMiddleware,
  rateLimitExtraction,
  rateLimitAuth,
  rateLimitAPI,
  rateLimitPublic,
  rateLimitErrorHandler,
  shouldSkipRateLimit,
  combineSkipConditions,
  rateLimitMiddlewareCollection,
} from './rateLimitMiddleware';

// ============================================================================
// Example 1: Basic API Rate Limiting
// ============================================================================

export function setupAPIRateLimiting(router: Router): void {
  // Apply tier-based rate limiting to all API routes
  router.use('/api',
    rateLimitAPI(),
    async (req, res, next) => {
      // Your normal API logic here
      res.json({ message: 'API response' });
    }
  );
}

// ============================================================================
// Example 2: Metadata Extraction Rate Limiting
// ============================================================================

export function setupExtractionRateLimiting(router: Router): void {
  // POST /api/extract - Expensive operation, stricter rate limits
  router.post('/extract',
    rateLimitExtraction({
      enabled: true,
      skipRateLimit: combineSkipConditions(
        shouldSkipRateLimit.adminUser,
        shouldSkipRateLimit.healthCheck
      ),
    }),
    async (req, res) => {
      // Expensive metadata extraction logic
      const metadata = await performExtraction(req.body);

      res.json(metadata);
    }
  );
}

// ============================================================================
// Example 3: Authentication Rate Limiting
// ============================================================================

export function setupAuthRateLimiting(router: Router): void {
  // POST /api/auth/login - IP-based rate limiting
  router.post('/auth/login',
    rateLimitAuth({
      enabled: true,
      endpoints: {
        requestsPerMinute: 5,   // Very strict for login
        requestsPerDay: 50,
      },
    }),
    async (req, res) => {
      // Authentication logic
      const result = await authenticateUser(req.body);

      res.json(result);
    }
  );

  // POST /api/auth/register - IP-based rate limiting
  router.post('/auth/register',
    rateLimitAuth({
      enabled: true,
      endpoints: {
        requestsPerMinute: 3,   // Even stricter for registration
        requestsPerDay: 10,
      },
    }),
    async (req, res) => {
      // Registration logic
      const result = await registerUser(req.body);

      res.json(result);
    }
  );

  // POST /api/auth/forgot-password - Rate limit password reset
  router.post('/auth/forgot-password',
    rateLimitAuth({
      enabled: true,
      endpoints: {
        requestsPerMinute: 3,
        requestsPerDay: 10,
      },
    }),
    async (req, res) => {
      // Password reset logic
      const result = await initiatePasswordReset(req.body);

      res.json(result);
    }
  );
}

// ============================================================================
// Example 4: Public Endpoint Rate Limiting
// ============================================================================

export function setupPublicRateLimiting(router: Router): void {
  // GET /api/public/tiers - Public tier information
  router.get('/public/tiers',
    rateLimitPublic({
      enabled: true,
    }),
    async (req, res) => {
      // Fetch public tier information
      const tiers = await getPublicTiers();

      res.json(tiers);
    }
  );

  // GET /api/public/features - Public feature list
  router.get('/public/features',
    rateLimitPublic({
      enabled: true,
    }),
    async (req, res) => {
      // Fetch public features
      const features = await getPublicFeatures();

      res.json(features);
    }
  );
}

// ============================================================================
// Example 5: Custom Rate Limiting with Conditions
// ============================================================================

export function setupCustomRateLimiting(router: Router): void {
  // Custom rate limiting for search endpoints
  router.get('/search',
    rateLimitMiddleware({
      enabled: true,
      keyGenerator: (req) => {
        // Generate unique key based on user and search query
        const userId = (req as any).user?.id || 'anonymous';
        const query = req.query.q?.toString().substring(0, 20) || 'default';
        return `search:${userId}:${query}`;
      },
      endpoints: {
        requestsPerMinute: 20,
        requestsPerDay: 500,
      },
      skipRateLimit: (req) => {
        // Skip rate limiting for premium users
        return (req as any).user?.tier === 'premium';
      },
    }),
    async (req, res) => {
      // Search logic
      const results = await performSearch(req.query);

      res.json(results);
    }
  );
}

// ============================================================================
// Example 6: Admin Endpoints with No Rate Limiting
// ============================================================================

export function setupAdminEndpoints(router: Router): void {
  // Admin endpoints - skip rate limiting for admin users
  router.post('/admin/cache/clear',
    rateLimitMiddleware({
      enabled: true,
      skipRateLimit: shouldSkipRateLimit.adminUser,
    }),
    async (req, res) => {
      // Admin cache clearing logic
      const result = await clearAdminCache(req.body);

      res.json(result);
    }
  );

  // GET /api/admin/metrics - No rate limiting for admins
  router.get('/admin/metrics',
    rateLimitMiddleware({
      enabled: true,
      skipRateLimit: shouldSkipRateLimit.adminUser,
    }),
    async (req, res) => {
      // Admin metrics logic
      const metrics = await getAdminMetrics();

      res.json(metrics);
    }
  );
}

// ============================================================================
// Example 7: Rate Limit Monitoring Endpoints
// ============================================================================

export function setupRateLimitMonitoring(router: Router): void {
  // GET /api/admin/rate-limit/metrics - Get rate limit metrics
  router.get('/admin/rate-limit/metrics',
    async (req, res) => {
      try {
        const metrics = await rateLimitManager.getMetrics();

        res.json({
          success: true,
          data: metrics,
        });
      } catch (error) {
        res.status(500).json({
          error: 'Failed to retrieve rate limit metrics',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );

  // POST /api/admin/rate-limit/reset/:identifier - Reset rate limit for specific user/IP
  router.post('/admin/rate-limit/reset/:identifier',
    async (req, res) => {
      try {
        const { identifier } = req.params;

        const success = await rateLimitManager.resetRateLimit(identifier);

        res.json({
          success,
          message: success
            ? `Rate limit reset for ${identifier}`
            : `Failed to reset rate limit for ${identifier}`,
        });
      } catch (error) {
        res.status(500).json({
          error: 'Rate limit reset failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );
}

// ============================================================================
// Example 8: Progressive Rate Limiting
// ============================================================================

export function setupProgressiveRateLimiting(router: Router): void {
  // Upload endpoint with progressive rate limiting based on file size
  router.post('/upload',
    rateLimitMiddleware({
      enabled: true,
      keyGenerator: (req) => {
        const userId = (req as any).user?.id || 'anonymous';
        const fileSize = parseInt(req.headers['content-length'] || '0');
        const sizeCategory = fileSize > 10 * 1024 * 1024 ? 'large' : 'small'; // 10MB threshold
        return `upload:${userId}:${sizeCategory}`;
      },
      endpoints: {
        requestsPerMinute: 10,
        requestsPerDay: 100,
      },
    }),
    async (req, res) => {
      // File upload logic
      const result = await handleFileUpload(req);

      res.json(result);
    }
  );
}

// ============================================================================
// Example 9: WebSocket Upgrade Handling
// ============================================================================

export function setupWebSocketRateLimiting(router: Router): void {
  // WebSocket upgrade endpoint - skip rate limiting
  router.get('/ws',
    rateLimitMiddleware({
      enabled: true,
      skipRateLimit: shouldSkipRateLimit.webSocket,
    }),
    async (req, res) => {
      // WebSocket upgrade logic
      res.status(101).send('Switching Protocols');
    }
  );
}

// ============================================================================
// Example 10: Health Check Endpoint (No Rate Limiting)
// ============================================================================

export function setupHealthCheck(router: Router): void {
  // GET /health - No rate limiting
  router.get('/health',
    rateLimitMiddleware({
      enabled: true,
      skipRateLimit: shouldSkipRateLimit.healthCheck,
    }),
    async (req, res) => {
      const health = await checkSystemHealth();

      res.json(health);
    }
  );
}

// ============================================================================
// Example 11: Global Rate Limiting Setup
// ============================================================================

export function setupGlobalRateLimiting(app: any): void {
  // Apply rate limiting to all routes
  app.use(rateLimitAPI({
    enabled: true,
    skipRateLimit: combineSkipConditions(
      shouldSkipRateLimit.webSocket,
      shouldSkipRateLimit.healthCheck,
      (req) => (req as any).user?.role === 'admin' // Skip for admins
    ),
  }));

  // Add rate limit error handler
  app.use(rateLimitErrorHandler);
}

// ============================================================================
// Example 12: Route-Specific Rate Limit Overrides
// ============================================================================

export function setupRouteSpecificOverrides(router: Router): void {
  // Default rate limiting for API routes
  router.use('/api',
    rateLimitAPI({
      enabled: true,
    })
  );

  // Override with stricter rate limiting for expensive operations
  router.post('/api/batch-process',
    rateLimitExtraction({
      enabled: true,
      endpoints: {
        requestsPerMinute: 2,  // Very strict for batch processing
        requestsPerDay: 20,
      },
    }),
    async (req, res) => {
      // Batch processing logic
      const result = await processBatch(req.body);

      res.json(result);
    }
  );

  // Override with no rate limiting for admin endpoints
  router.use('/api/admin',
    rateLimitMiddleware({
      enabled: true,
      skipRateLimit: shouldSkipRateLimit.adminUser,
    })
  );
}

// ============================================================================
// Helper Functions (to be implemented)
// ============================================================================

async function performExtraction(data: any) {
  // Implementation would perform metadata extraction
  return {};
}

async function authenticateUser(credentials: any) {
  // Implementation would authenticate user
  return {};
}

async function registerUser(userData: any) {
  // Implementation would register user
  return {};
}

async function initiatePasswordReset(emailData: any) {
  // Implementation would initiate password reset
  return {};
}

async function getPublicTiers() {
  // Implementation would fetch public tiers
  return [];
}

async function getPublicFeatures() {
  // Implementation would fetch public features
  return [];
}

async function performSearch(query: any) {
  // Implementation would perform search
  return {};
}

async function clearAdminCache(data: any) {
  // Implementation would clear admin cache
  return {};
}

async function getAdminMetrics() {
  // Implementation would get admin metrics
  return {};
}

async function handleFileUpload(req: any) {
  // Implementation would handle file upload
  return {};
}

async function checkSystemHealth() {
  // Implementation would check system health
  return {};
}

async function processBatch(data: any) {
  // Implementation would process batch
  return {};
}