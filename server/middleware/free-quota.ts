/**
 * Free Quota Middleware for Images MVP
 * Integrates the quota enforcement system with Express routes
 */

import { Request, Response, NextFunction } from 'express';
import { enforceFreeQuota, verifyClientToken, getClientUsage } from '../utils/free-quota-enforcement';

/**
 * Main quota enforcement middleware for Images MVP routes
 * Apply this to POST /api/images_mvp/extract
 */
export function freeQuotaMiddleware(req: Request, res: Response, next: NextFunction): void {
  enforceFreeQuota(req, res, next);
}

/**
 * Rate limiting middleware for general protection
 * Apply this to all API routes
 */
export function rateLimitMiddleware(req: Request, res: Response, next: NextFunction): void {
  // Implementation for general rate limiting
  // This would be a separate, simpler rate limiter
  next();
}

/**
 * Helper to check if user has free quota remaining
 * Useful for UI display
 */
export async function getFreeQuotaRemaining(req: Request): Promise<number> {
  const clientToken = req.cookies?.metaextract_client;
  if (!clientToken) return 2; // Default for new users
  
  const decoded = verifyClientToken(clientToken);
  if (!decoded) return 2; // Invalid token = new user
  
  // Get usage from storage
  const usage = await getClientUsage(decoded.clientId);
  const used = usage?.free_used || 0;
  
  return Math.max(0, 2 - used);
}