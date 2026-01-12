/**
 * Upload Rate Limiting Middleware
 * 
 * Provides rate limiting specifically for file upload endpoints
 * to prevent DoS attacks and abuse.
 */

import { Request, Response, NextFunction } from 'express';
import rateLimit, { RateLimitRequestHandler, ipKeyGenerator } from 'express-rate-limit';
import { storage } from '../storage/index';
import { securityEventLogger } from '../monitoring/security-events';

// Configuration
const UPLOAD_LIMITS = {
  // Per IP address
  IP_WINDOW_MS: 15 * 60 * 1000, // 15 minutes
  IP_MAX_REQUESTS: 50, // Max 50 uploads per IP per 15 minutes
  
  // Per session/device (more generous for legitimate users)
  SESSION_WINDOW_MS: 60 * 60 * 1000, // 1 hour
  SESSION_MAX_REQUESTS: 100, // Max 100 uploads per session per hour
  
  // Burst protection (short term)
  BURST_WINDOW_MS: 60 * 1000, // 1 minute
  BURST_MAX_REQUESTS: 10, // Max 10 uploads per minute
};

/**
 * Get rate limit key for a request
 * Priority: User ID > Session ID > IP Address
 * Uses the built-in ipKeyGenerator helper to handle IPv6 properly
 */
export function getRateLimitKey(req: Request): string {
  // Authenticated users get their own rate limit bucket
  if ((req as any).user?.id) {
    return `user:${(req as any).user.id}`;
  }
  
  // Session-based rate limiting for anonymous users
  const sessionId = req.cookies?.metaextract_session_id || req.headers['x-session-id'];
  if (sessionId) {
    return `session:${sessionId}`;
  }
  
  // Fallback to IP-based rate limiting - use built-in helper for IPv6 safety
  // This prevents IPv6 bypass attacks
  const ip = req.ip || req.connection.remoteAddress || 'unknown';
  return `ip:${ipKeyGenerator(ip)}`;
}

/**
 * Check if request should bypass rate limiting
 */
function shouldBypassRateLimit(req: Request): boolean {
  // Development/testing bypass
  if (process.env.NODE_ENV === 'development' && process.env.BYPASS_RATE_LIMIT === 'true') {
    return true;
  }
  
  // Admin bypass (if admin authentication is implemented)
  if ((req as any).user?.role === 'admin') {
    return true;
  }
  
  // Health check bypass
  if (req.path.includes('/health') || req.path.includes('/status')) {
    return true;
  }
  
  return false;
}

/**
 * Enhanced rate limiter with Redis/memory fallback
 */
export const uploadRateLimit = rateLimit({
  windowMs: UPLOAD_LIMITS.IP_WINDOW_MS,
  max: async (req: Request) => {
    // Dynamic limit based on authentication status
    if ((req as any).user?.id) {
      // Authenticated users get higher limits
      return UPLOAD_LIMITS.SESSION_MAX_REQUESTS;
    }
    
    // Anonymous users get standard limits
    return UPLOAD_LIMITS.IP_MAX_REQUESTS;
  },
  
  keyGenerator: getRateLimitKey,
  
  skip: shouldBypassRateLimit,
  
  // Disable IPv6 validation warning - we're handling this correctly
  validate: { 
    ipv6SubnetOrKeyGenerator: false 
  },
  
  handler: async (req: Request, res: Response) => {
    const key = getRateLimitKey(req);
    const isAuthenticated = !!(req as any).user?.id;
    const limitType = isAuthenticated ? 'authenticated user' : 'IP address';
    
    // Log security event for rate limit violation
    await securityEventLogger.logRateLimitViolation(
      req,
      'rate',
      isAuthenticated ? UPLOAD_LIMITS.SESSION_MAX_REQUESTS : UPLOAD_LIMITS.IP_MAX_REQUESTS,
      `${Math.round(UPLOAD_LIMITS.IP_WINDOW_MS / (60 * 1000))} minutes`
    );
    
    res.status(429).json({
      error: 'Rate limit exceeded',
      message: `Too many upload attempts from this ${limitType}. Please try again later.`,
      limit_type: isAuthenticated ? 'user' : 'ip',
      window_minutes: Math.round(UPLOAD_LIMITS.IP_WINDOW_MS / (60 * 1000)),
      max_requests: isAuthenticated ? UPLOAD_LIMITS.SESSION_MAX_REQUESTS : UPLOAD_LIMITS.IP_MAX_REQUESTS,
      retry_after_seconds: Math.round(req.rateLimit.resetTime / 1000),
      suggestions: [
        'Wait a few minutes before trying again',
        'Consider creating an account for higher limits',
        'Contact support if you believe this is an error'
      ],
    });
  },
  
  standardHeaders: true,
  legacyHeaders: false,
  
  // Store configuration - use memory store for now
  // Redis store can be added later when Redis is properly configured
});

/**
 * Burst protection - very short-term rate limiting
 */
export const burstRateLimit = rateLimit({
  windowMs: UPLOAD_LIMITS.BURST_WINDOW_MS,
  max: UPLOAD_LIMITS.BURST_MAX_REQUESTS,
  
  keyGenerator: getRateLimitKey,
  
  skip: (req: Request) => {
    return shouldBypassRateLimit(req) || (req as any).user?.id !== undefined;
  },
  
  // Disable IPv6 validation warning - we're handling this correctly
  validate: { 
    ipv6SubnetOrKeyGenerator: false 
  },
  
  handler: async (req: Request, res: Response) => {
    // Log security event for burst rate limit violation
    await securityEventLogger.logRateLimitViolation(
      req,
      'burst',
      UPLOAD_LIMITS.BURST_MAX_REQUESTS,
      `${Math.round(UPLOAD_LIMITS.BURST_WINDOW_MS / 1000)} seconds`
    );
    
    res.status(429).json({
      error: 'Burst rate limit exceeded',
      message: 'Too many rapid upload attempts. Please slow down.',
      limit_type: 'burst',
      window_seconds: Math.round(UPLOAD_LIMITS.BURST_WINDOW_MS / 1000),
      max_requests: UPLOAD_LIMITS.BURST_MAX_REQUESTS,
      retry_after_seconds: Math.round(req.rateLimit.resetTime / 1000),
    });
  },
  
  standardHeaders: true,
  legacyHeaders: false,
  
  // Use memory store for burst protection
});

/**
 * Combined rate limiting middleware
 * Apply burst protection first, then main rate limiting
 */
export function applyUploadRateLimiting(app: any): void {
  // Apply main rate limiting first (more generous, longer window)
  app.use('/api/images_mvp/extract', uploadRateLimit);
  
  // Apply burst protection second (stricter, shorter window, only for anonymous users)
  app.use('/api/images_mvp/extract', burstRateLimit);
  
  console.log('[RateLimit] Upload rate limiting applied to /api/images_mvp/extract');
}