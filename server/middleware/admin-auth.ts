/**
 * Admin Authentication Middleware
 * Protects admin endpoints with authentication and rate limiting
 */

import { Request, Response, NextFunction } from 'express';
import { verifyToken } from '../auth';
import {
  checkRateLimit,
  isLockedOut,
  recordFailedAttempt,
  clearFailedAttempts,
} from '../security-utils';

// Admin API key for programmatic access (should be set in environment)
const ADMIN_API_KEY = process.env.ADMIN_API_KEY;

/**
 * Admin authentication middleware
 * Supports both JWT token and API key authentication
 */
export function adminAuthMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Check for API key first (for programmatic access)
  const apiKey = req.headers['x-admin-api-key'] as string;
  if (apiKey && ADMIN_API_KEY && apiKey === ADMIN_API_KEY) {
    (req as any).isAdmin = true;
    next();
    return;
  }

  // Check for JWT token
  const authHeader = req.headers.authorization;
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.slice(7);
    const user = verifyToken(token);

    if (user && user.tier === 'enterprise') {
      (req as any).isAdmin = true;
      (req as any).user = user;
      next();
      return;
    }
  }

  res.status(401).json({
    error: 'Unauthorized',
    message: 'Admin authentication required',
  });
}

/**
 * Admin rate limiting middleware
 * Stricter limits for admin endpoints
 */
export function adminRateLimitMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const adminKey = 'admin:' + (req.ip || 'unknown');

  // Check if locked out
  const lockStatus = isLockedOut(adminKey, 10, 15 * 60 * 1000);
  if (lockStatus.locked) {
    res.setHeader(
      'Retry-After',
      Math.ceil((lockStatus.resetTime - Date.now()) / 1000)
    );
    res.status(429).json({
      error: 'Too Many Requests',
      message: 'Admin rate limit exceeded. Please try again later.',
      retryAfter: Math.ceil((lockStatus.resetTime - Date.now()) / 1000),
    });
    return;
  }

  // Check rate limit (10 requests per minute for admin)
  const rateLimitResult = checkRateLimit(adminKey, 10, 60 * 1000);
  res.setHeader('X-RateLimit-Limit', '10');
  res.setHeader('X-RateLimit-Remaining', rateLimitResult.remaining);
  res.setHeader(
    'X-RateLimit-Reset',
    new Date(rateLimitResult.resetTime).toISOString()
  );

  if (!rateLimitResult.allowed) {
    recordFailedAttempt(adminKey, 10, 15 * 60 * 1000);
    res.setHeader(
      'Retry-After',
      Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000)
    );
    res.status(429).json({
      error: 'Too Many Requests',
      message: 'Admin rate limit exceeded',
      retryAfter: Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000),
    });
    return;
  }

  next();
}

/**
 * Combine admin auth and rate limit middleware
 */
export function adminProtectionMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  adminAuthMiddleware(req, res, (err?: unknown) => {
    if (err) {
      next(err as Error);
      return;
    }
    adminRateLimitMiddleware(req, res, next);
  });
}

/**
 * Health check - no auth required
 */
export function healthCheckAuth(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  next();
}

/**
 * Get admin API key status
 */
export function getAdminApiKeyStatus(): { configured: boolean } {
  return {
    configured: !!ADMIN_API_KEY,
  };
}
