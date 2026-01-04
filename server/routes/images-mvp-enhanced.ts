/**
 * Enhanced Images MVP Route with Quota Enforcement
 * Integrates the 3-tier quota enforcement system
 */

import type { Express, Request, Response } from 'express';
import { enforceFreeQuota } from '../middleware/free-quota';

/**
 * Register enhanced Images MVP routes with quota enforcement
 * This wraps the existing routes with our quota system
 */
export function registerEnhancedImagesMvpRoutes(app: Express): void {
  // Apply quota enforcement to the main extraction endpoint
  app.post('/api/images_mvp/extract', enforceFreeQuota);
  
  // The quota enforcement will call the original handler if within limits
  // or return appropriate error responses if quota exceeded
}

/**
 * Alternative: Modify the existing route registration
 * This approach integrates directly into the existing route
 */
export function enhanceExistingImagesMvpRoutes(app: Express): void {
  // Store original route handler
  const originalRoute = app._router.stack.find(
    (layer: any) => layer.route && layer.route.path === '/api/images_mvp/extract'
  );
  
  if (originalRoute) {
    // Apply quota enforcement to existing route
    app.use('/api/images_mvp/extract', enforceFreeQuota);
  }
}