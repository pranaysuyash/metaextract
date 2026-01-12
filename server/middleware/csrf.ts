/**
 * CSRF Protection Middleware
 * Implements CSRF token generation and validation for state-changing operations
 */

import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

// CSRF token storage (in-memory for single instance, Redis recommended for production)
const csrfTokens = new Map<string, CSRFToken>();

interface CSRFToken {
  token: string;
  userId: string;
  expiresAt: number;
  used: boolean;
}

const CSRF_CONFIG = {
  TOKEN_LENGTH: 32,
  TOKEN_EXPIRY_MS: 60 * 60 * 1000, // 1 hour
  HEADER_NAME: 'X-CSRF-Token',
  COOKIE_NAME: 'csrf_token',
  SECRET_LENGTH: 64,
};

/**
 * Generate a CSRF token for a user session
 */
export function generateCSRFToken(userId: string): string {
  const token = crypto.randomBytes(CSRF_CONFIG.TOKEN_LENGTH).toString('hex');
  const secret = crypto.randomBytes(CSRF_CONFIG.SECRET_LENGTH).toString('hex');
  const expiresAt = Date.now() + CSRF_CONFIG.TOKEN_EXPIRY_MS;

  const csrfToken: CSRFToken = {
    token: `${token}.${secret}`,
    userId,
    expiresAt,
    used: false,
  };

  csrfTokens.set(token, csrfToken);

  // Clean up expired tokens
  cleanupExpiredTokens();

  return csrfToken.token;
}

/**
 * Validate a CSRF token
 */
export function validateCSRFToken(token: string, userId: string): boolean {
  try {
    if (!token || !userId) return false;

    const [tokenId, secret] = token.split('.');
    if (!tokenId || !secret) return false;

    const csrfToken = csrfTokens.get(tokenId);
    if (!csrfToken) return false;

    // Check if token matches and hasn't been used
    if (csrfToken.token !== token) return false;
    if (csrfToken.userId !== userId) return false;
    if (csrfToken.used) return false;
    if (Date.now() > csrfToken.expiresAt) return false;

    // Mark token as used (one-time use)
    csrfToken.used = true;

    return true;
  } catch (error) {
    console.error('CSRF validation error:', error);
    return false;
  }
}

/**
 * CSRF middleware for state-changing operations
 */
export function csrfProtection(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Skip CSRF for GET, HEAD, OPTIONS requests
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    return next();
  }

  // Check for CSRF token in header
  const csrfToken = req.headers[CSRF_CONFIG.HEADER_NAME.toLowerCase()];
  if (!csrfToken || typeof csrfToken !== 'string') {
    res.status(403).json({
      error: 'CSRF token required',
      message: 'Please include X-CSRF-Token header',
    });
    return;
  }

  // Get user ID from authenticated request
  const userId = (req as any).user?.id;
  if (!userId) {
    res.status(401).json({
      error: 'Authentication required',
      message: 'Please authenticate before performing this action',
    });
    return;
  }

  // Validate CSRF token
  if (!validateCSRFToken(csrfToken, userId)) {
    res.status(403).json({
      error: 'Invalid CSRF token',
      message: 'Please refresh the page and try again',
    });
    return;
  }

  next();
}

/**
 * Generate CSRF token endpoint
 */
export function csrfTokenEndpoint(req: Request, res: Response): void {
  const userId = (req as any).user?.id;
  if (!userId) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  const token = generateCSRFToken(userId);

  // Set CSRF token in cookie for client-side access
  res.cookie(CSRF_CONFIG.COOKIE_NAME, token, {
    httpOnly: false, // Allow client-side JavaScript to read for AJAX requests
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: CSRF_CONFIG.TOKEN_EXPIRY_MS,
  });

  res.json({
    token,
    expiresAt: Date.now() + CSRF_CONFIG.TOKEN_EXPIRY_MS,
  });
}

/**
 * Clean up expired CSRF tokens
 */
function cleanupExpiredTokens(): void {
  const now = Date.now();
  for (const [tokenId, token] of csrfTokens.entries()) {
    if (now > token.expiresAt) {
      csrfTokens.delete(tokenId);
    }
  }
}

/**
 * Enhanced CSRF protection with double-submit cookie pattern
 */
export function enhancedCSRFProtection(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Skip CSRF for safe methods
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    return next();
  }

  const userId = (req as any).user?.id;
  if (!userId) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  // Check both header and cookie (double-submit pattern)
  const headerToken = req.headers[CSRF_CONFIG.HEADER_NAME.toLowerCase()];
  const cookieToken = req.cookies?.[CSRF_CONFIG.COOKIE_NAME];

  if (!headerToken || !cookieToken) {
    res.status(403).json({
      error: 'CSRF tokens required',
      message: 'Please include both X-CSRF-Token header and CSRF cookie',
    });
    return;
  }

  // Both tokens must match
  if (headerToken !== cookieToken) {
    res.status(403).json({
      error: 'CSRF token mismatch',
      message: 'Header and cookie tokens do not match',
    });
    return;
  }

  // Validate the token
  if (!validateCSRFToken(headerToken as string, userId)) {
    res.status(403).json({
      error: 'Invalid CSRF token',
      message: 'Token is invalid or expired',
    });
    return;
  }

  next();
}

/**
 * CORS configuration for CSRF protection
 */
export const csrfCorsConfig = {
  origin (origin: string, callback: Function) {
    // Allow same-origin requests
    if (!origin) return callback(null, true);

    // Allow specific origins in development
    const allowedOrigins = [
      'http://localhost:3000',
      'http://localhost:5173',
      'http://localhost:5174',
      'http://localhost:5175',
    ];

    if (
      process.env.NODE_ENV === 'development' &&
      allowedOrigins.includes(origin)
    ) {
      return callback(null, true);
    }

    // In production, only allow exact matches
    if (process.env.NODE_ENV === 'production') {
      // Add your production domains here
      return callback(null, true);
    }

    callback(new Error('Not allowed by CORS'));
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token'],
};
