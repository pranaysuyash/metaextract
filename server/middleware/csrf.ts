/**
 * CSRF Protection Middleware
 * Provides CSRF token generation and validation for state-changing requests
 */

import { Request, Response, NextFunction } from 'express';
import { generateCSRFToken, validateCSRFToken } from '../security-utils';

// CSRF token storage (in production, use Redis or session store)
const csrfTokenStore = new Map<string, { token: string; expiresAt: number }>();

const CSRF_TOKEN_EXPIRY_MS = 60 * 60 * 1000; // 1 hour

/**
 * Generate and store CSRF token for a session
 */
export function generateCSRF(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const sessionId = getSessionId(req);

  if (!sessionId) {
    next();
    return;
  }

  const token = generateCSRFToken();
  const expiresAt = Date.now() + CSRF_TOKEN_EXPIRY_MS;

  csrfTokenStore.set(sessionId, { token, expiresAt });

  // Send token to client via cookie (HTTP-only) and header
  res.cookie('csrf_token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    // Lax so token cookie survives external checkout redirects.
    sameSite: 'lax',
    maxAge: CSRF_TOKEN_EXPIRY_MS,
  });

  res.setHeader('X-CSRF-Token', token);

  next();
}

/**
 * Validate CSRF token from request
 */
export function validateCSRF(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Skip CSRF for safe methods
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    next();
    return;
  }

  // Get token from header or cookie
  const tokenFromHeader = req.headers['x-csrf-token'] as string;
  const tokenFromCookie = req.cookies?.csrf_token;
  const token = tokenFromHeader || tokenFromCookie;

  if (!token) {
    res.status(403).json({
      error: 'CSRF token missing',
      message: 'A valid CSRF token is required for this request',
    });
    return;
  }

  // Validate token format and signature
  if (!validateCSRFToken(token)) {
    res.status(403).json({
      error: 'Invalid CSRF token',
      message: 'The provided CSRF token is invalid or expired',
    });
    return;
  }

  // Check against stored token
  const sessionId = getSessionId(req);
  if (sessionId) {
    const stored = csrfTokenStore.get(sessionId);

    if (!stored || stored.token !== token) {
      res.status(403).json({
        error: 'CSRF token mismatch',
        message: 'The CSRF token does not match the session',
      });
      return;
    }

    // Check expiry
    if (Date.now() > stored.expiresAt) {
      csrfTokenStore.delete(sessionId);
      res.status(403).json({
        error: 'CSRF token expired',
        message: 'The CSRF token has expired. Please refresh the page.',
      });
      return;
    }
  }

  next();
}

/**
 * Get session ID from request
 */
function getSessionId(req: Request): string | null {
  // Try various sources for session ID
  const sessionId =
    req.cookies?.session_id ||
    (req.headers['x-session-id'] as string) ||
    (req as any).user?.id;

  return sessionId || null;
}

/**
 * Clean up expired CSRF tokens
 */
export function cleanupCSRFStore(): void {
  const now = Date.now();
  for (const [sessionId, entry] of csrfTokenStore.entries()) {
    if (now > entry.expiresAt) {
      csrfTokenStore.delete(sessionId);
    }
  }
}
