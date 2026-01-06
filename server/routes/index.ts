/**
 * Routes Index
 *
 * Central registration for all API routes.
 * Modular organization for better maintainability.
 */

import type { Express } from 'express';
import type { Server } from 'http';
import { registerImagesMvpRoutes } from './images-mvp';
import { registerExtractionRoutes } from './extraction';
import { registerForensicRoutes } from './forensic';
import { registerMetadataRoutes } from './metadata';
import { registerLLMFindingsRoutes } from './llm-findings';
import { registerTierRoutes } from './tiers';
import { registerAdminRoutes } from './admin';
import { registerPaymentRoutes } from '../payments';
import { registerGeocodingRoutes } from './geocoding';
import { registerOnboardingRoutes } from './onboarding';
// import { registerLegalComplianceRoutes } from './legal-compliance'; // Disabled
import { rateLimitManager } from '../rateLimitRedis';
import { rateLimitAPI } from '../rateLimitMiddleware';

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
  // Initialize rate limiter
  await rateLimitManager.initialize();

  // Apply global API rate limiting to all /api routes
  app.use('/api', rateLimitAPI());

  // Register route modules
  registerImagesMvpRoutes(app);
  registerExtractionRoutes(app);
  registerForensicRoutes(app);
  registerMetadataRoutes(app);
  registerLLMFindingsRoutes(app);
  registerTierRoutes(app);
  registerAdminRoutes(app);
  registerPaymentRoutes(app);
  registerGeocodingRoutes(app);
  registerOnboardingRoutes(app);
  // registerLegalComplianceRoutes(app); // Disabled

  return httpServer;
}

// Re-export for backwards compatibility
export { registerExtractionRoutes } from './extraction';
export { registerForensicRoutes } from './forensic';
export { registerMetadataRoutes } from './metadata';
export { registerTierRoutes } from './tiers';
export { registerAdminRoutes } from './admin';
