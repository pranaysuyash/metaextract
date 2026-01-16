/**
 * Routes Index
 *
 * Central registration for all API routes.
 * Modular organization for better maintainability.
 *
 * SECURITY NOTICE: Legacy extraction route disabled due to memory exhaustion vulnerability
 * See: https://github.com/your-org/metaextract/security/advisories/001
 *
 * NOTE: The Images MVP uses credit-based pricing instead of tier subscriptions.
 */

import type { Express } from 'express';
import type { Server } from 'http';
import { registerImagesMvpRoutes } from './images-mvp';
// import { registerExtractionRoutes } from './extraction';
// import { registerForensicRoutes } from './forensic';
// import { registerMetadataRoutes } from './metadata';
// import { registerLLMFindingsRoutes } from './llm-findings';
import { registerTierRoutes } from './tiers';
import { registerAdminRoutes } from './admin';
import { registerMonitoringRoutes } from './monitoring';
import { registerPaymentRoutes } from '../payments';
import { registerGeocodingRoutes } from './geocoding';
import { registerOnboardingRoutes } from './onboarding';
import { registerLegalComplianceRoutes } from './legal-compliance';
import { registerBatchRoutes } from './batch';
import { rateLimitManager } from '../rateLimitRedis';
import { rateLimitAPI } from '../rateLimitMiddleware';
import { applyUploadRateLimiting } from '../middleware/upload-rate-limit';
import advancedProtectionRouter from './advanced-protection';
import enhancedProtectionRouter from './enhanced-protection';
import adminSecurityRouter from './admin-security';

/**
 * Register all API routes on the Express app.
 *
 * Route modules:
 * - extraction: File upload and metadata extraction
 * - forensic: Advanced forensic analysis, comparison, timeline
 * - metadata: Search, storage, favorites, similar files
 * - tiers: Tier configurations, field info, samples
 * - admin: Analytics, performance, health checks
 * - payments: Subscription and payment handling
 */
export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  const isImagesMvpOnly = process.env.IMAGES_MVP_ONLY === 'true';

  if (isImagesMvpOnly) {
    registerImagesMvpRoutes(app);

    // Advanced protection routes (Phase 1 & 2 integration)
    app.use('/api/protection', advancedProtectionRouter);
    app.use('/api/enhanced-protection', enhancedProtectionRouter);
    app.use('/api/admin', adminSecurityRouter);

    app.get('/api/health', (_req, res) => {
      res.json({
        status: 'ok',
        service: 'MetaExtract Images MVP API',
        timestamp: new Date().toISOString(),
      });
    });

    return httpServer;
  }

  // Initialize rate limiter
  await rateLimitManager.initialize();

  // Apply global API rate limiting to all /api routes
  app.use('/api', rateLimitAPI());

  // Apply upload-specific rate limiting to images MVP extract endpoint
  applyUploadRateLimiting(app);

  // Register route modules
  registerImagesMvpRoutes(app);
  // SECURITY: Legacy extraction route disabled for Images MVP launch
  // registerExtractionRoutes(app); // 🚨 CRITICAL: 2GB memory storage vulnerability

  // SECURITY: Forensic routes disabled for MVP launch (memory risk from 2GB limit)
  // registerForensicRoutes(app);

  // SECURITY: Legacy routes disabled - not needed for Images MVP
  // registerMetadataRoutes(app);
  // registerLLMFindingsRoutes(app);
  registerTierRoutes(app);
  registerMonitoringRoutes(app);
  registerBatchRoutes(app);

  // These routes are still needed for the overall platform
  registerAdminRoutes(app);
  registerPaymentRoutes(app);
  registerGeocodingRoutes(app);
  registerOnboardingRoutes(app);
  registerLegalComplianceRoutes(app);

  // Advanced protection routes (Phase 1 & 2 integration)
  app.use('/api/protection', advancedProtectionRouter);
  app.use('/api/enhanced-protection', enhancedProtectionRouter);
  app.use('/api/admin', adminSecurityRouter);

  return httpServer;
}

// Re-export for backwards compatibility
export { registerExtractionRoutes } from './extraction';
export { registerForensicRoutes } from './forensic';
export { registerMetadataRoutes } from './metadata';
// Tiers routes DELETED
export { registerAdminRoutes } from './admin';
