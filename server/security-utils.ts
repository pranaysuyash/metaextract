/**
 * MetaExtract Security Utilities
 * Centralized security functions used across the application
 */

import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';
import path from 'path';

// ============================================================================
// IP Address Validation and Extraction
// ============================================================================

/**
 * Get the real client IP address, properly handling proxy headers
 * Only trusts X-Forwarded-For if the request comes from a known proxy
 */
export function getClientIP(req: Request): string {
  const trustedProxies = [
    '127.0.0.1',
    '::1',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
  ];

  const forwardedFor = req.headers['x-forwarded-for'];
  const remoteAddress = req.socket.remoteAddress || req.ip || 'unknown';

  // If behind a trusted proxy, use X-Forwarded-For
  if (forwardedFor && isTrustedProxy(remoteAddress, trustedProxies)) {
    // X-Forwarded-For can be comma-separated, take the first (original client)
    const ips = Array.isArray(forwardedFor)
      ? forwardedFor
      : forwardedFor.split(',').map(ip => ip.trim());
    return ips[0];
  }

  return remoteAddress;
}

/**
 * Check if the request comes from a trusted proxy
 */
function isTrustedProxy(
  remoteAddress: string,
  trustedProxies: string[]
): boolean {
  for (const proxy of trustedProxies) {
    if (proxy.includes('/')) {
      // CIDR notation
      if (isIPInCIDR(remoteAddress, proxy)) {
        return true;
      }
    } else if (remoteAddress === proxy) {
      return true;
    }
  }
  return false;
}

/**
 * Check if an IP is within a CIDR range
 */
function isIPInCIDR(ip: string, cidr: string): boolean {
  const [range, bits] = cidr.split('/');
  const mask = ~(2 ** (32 - parseInt(bits)) - 1);

  const ipNum = ipToNumber(ip);
  const rangeNum = ipToNumber(range);

  return (ipNum & mask) === (rangeNum & mask);
}

function ipToNumber(ip: string): number {
  const parts = ip.split('.').map(Number);
  return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3];
}

// ============================================================================
// Request Sanitization
// ============================================================================

/**
 * Sanitize string input to prevent injection attacks
 */
export function sanitizeString(
  input: string,
  maxLength: number = 1000
): string {
  // Remove null bytes and control characters
  // eslint-disable-next-line no-control-regex
  let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }

  return sanitized;
}

/**
 * Validate that a string is safe for use as a filename
 */
export function sanitizeFilename(filename: string): string {
  // Remove path separators and dangerous characters
  // eslint-disable-next-line no-control-regex
  const dangerous = /[<>:"/\\|?*\x00-\x1f]/g;
  let sanitized = filename.replace(dangerous, '_');

  // Remove leading/trailing dots and spaces
  sanitized = sanitized.trim().replace(/^\.+|\.+$/g, '');

  // Limit length
  if (sanitized.length > 255) {
    const ext = filename.includes('.')
      ? filename.slice(filename.lastIndexOf('.'))
      : '';
    sanitized = sanitized.slice(0, 250) + ext;
  }

  return sanitized || 'file';
}

/**
 * Validate file path is within allowed directories
 */
export function isPathSafe(filePath: string, allowedDirs: string[]): boolean {
  try {
    const resolved = path.resolve(filePath);
    for (const dir of allowedDirs) {
      const allowed = path.resolve(dir);
      if (resolved.startsWith(allowed + path.sep)) {
        return true;
      }
    }
    return false;
  } catch {
    return false;
  }
}

// ============================================================================
// Rate Limiting Storage (In-memory for single instance)
// ============================================================================

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

const rateLimitStore = new Map<string, RateLimitEntry>();

/**
 * Check if request should be rate limited
 * Returns true if over limit, false if allowed
 */
export function checkRateLimit(
  key: string,
  maxRequests: number,
  windowMs: number
): { allowed: boolean; remaining: number; resetTime: number } {
  const now = Date.now();

  let entry = rateLimitStore.get(key);

  if (!entry || now > entry.resetTime) {
    entry = { count: 1, resetTime: now + windowMs };
    rateLimitStore.set(key, entry);
    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetTime: entry.resetTime,
    };
  }

  if (entry.count >= maxRequests) {
    return { allowed: false, remaining: 0, resetTime: entry.resetTime };
  }

  entry.count++;
  return {
    allowed: true,
    remaining: maxRequests - entry.count,
    resetTime: entry.resetTime,
  };
}

/**
 * Clean up expired rate limit entries
 */
export function cleanupRateLimitStore(): void {
  const now = Date.now();
  for (const [key, entry] of rateLimitStore.entries()) {
    if (now > entry.resetTime) {
      rateLimitStore.delete(key);
    }
  }
}

// ============================================================================
// Security Headers
// ============================================================================

/**
 * Security headers to include in all responses
 */
const IS_DEV = process.env.NODE_ENV !== 'production';
const DEV_HTTP_ORIGINS = [
  'http://localhost:3000',
  'http://127.0.0.1:3000',
  'http://localhost:5173',
  'http://127.0.0.1:5173',
  'http://localhost:5174',
  'http://127.0.0.1:5174',
  'http://localhost:5175',
  'http://127.0.0.1:5175',
];
const VITE_DEV_WS = [
  'ws://localhost:3000',
  'ws://127.0.0.1:3000',
  'ws://localhost:5173',
  'ws://127.0.0.1:5173',
  'ws://localhost:5174',
  'ws://127.0.0.1:5174',
  'ws://localhost:5175',
  'ws://127.0.0.1:5175',
];

function buildCsp(isDevLike: boolean): string {
  const scriptSrcValue = isDevLike
    ? "'self' 'unsafe-inline' 'unsafe-eval' blob:"
    : "'self'";
  const scriptSrc = `script-src ${scriptSrcValue}`;
  const scriptSrcElem = `script-src-elem ${scriptSrcValue}`;

  const styleSrcValue = "'self' 'unsafe-inline' https://fonts.googleapis.com";
  const styleSrc = `style-src ${styleSrcValue}`;
  const styleSrcElem = `style-src-elem ${styleSrcValue}`;

  const connectSrc = isDevLike
    ? `connect-src 'self' ${DEV_HTTP_ORIGINS.join(' ')} ${VITE_DEV_WS.join(' ')}`
    : "connect-src 'self'";

  return [
    "default-src 'self'",
    scriptSrc,
    scriptSrcElem,
    styleSrc,
    styleSrcElem,
    "img-src 'self' data: https:",
    "font-src 'self' https://fonts.gstatic.com",
    connectSrc,
    "frame-ancestors 'none'",
    "worker-src 'self' blob:",
  ].join('; ');
}

export const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  // Content-Security-Policy is set dynamically in applySecurityHeaders()
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
};

/**
 * Apply security headers to response
 */
export function applySecurityHeaders(res: Response, req?: { headers?: any }): void {
  for (const [header, value] of Object.entries(SECURITY_HEADERS)) {
    res.setHeader(header, value);
  }

  // CSP needs to adapt for local dev (Vite injects inline module scripts and uses WS)
  const hostHeader =
    typeof req?.headers?.host === 'string' ? req.headers.host : '';
  const isLocalhost =
    hostHeader.startsWith('localhost') ||
    hostHeader.startsWith('127.0.0.1') ||
    hostHeader.startsWith('0.0.0.0');

  const isDevLike = IS_DEV || isLocalhost;
  const csp = buildCsp(isDevLike);
  res.setHeader('Content-Security-Policy', csp);
}

// ============================================================================
// CSRF Token Generation and Validation
// ============================================================================

const CSRF_SECRET = process.env.CSRF_SECRET || crypto.randomUUID();
const CSRF_TOKEN_EXPIRY_MS = 60 * 60 * 1000; // 1 hour

interface CSRFEntry {
  token: string;
  expiresAt: number;
}

/**
 * Generate a CSRF token for a user session
 */
export function generateCSRFToken(): string {
  const token = crypto.randomBytes(32).toString('hex');
  const expiresAt = Date.now() + CSRF_TOKEN_EXPIRY_MS;
  return `${token}.${expiresAt}`;
}

/**
 * Validate a CSRF token
 */
export function validateCSRFToken(token: string): boolean {
  try {
    const [tokenValue, expiresAt] = token.split('.');
    if (!tokenValue || !expiresAt) return false;

    const expiry = parseInt(expiresAt, 10);
    if (isNaN(expiry) || Date.now() > expiry) return false;

    // Token format validation
    if (tokenValue.length !== 64) return false;

    return true;
  } catch {
    return false;
  }
}

// ============================================================================
// Secure Random Generation
// ============================================================================

/**
 * Generate a cryptographically secure random string
 */
export function secureRandom(length: number = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

/**
 * Generate a secure confirmation code (numeric)
 */
export function secureConfirmationCode(length: number = 6): string {
  const digits = '0123456789';
  let code = '';
  const randomBytes = crypto.randomBytes(length);
  for (let i = 0; i < length; i++) {
    code += digits[randomBytes[i] % 10];
  }
  return code;
}

// ============================================================================
// Error Message Sanitization
// ============================================================================

/**
 * Sanitize error messages to prevent information disclosure
 */
export function sanitizeErrorMessage(
  error: unknown,
  context: 'production' | 'development'
): string {
  const message = error instanceof Error ? error.message : String(error);

  if (context === 'production') {
    // Remove potential sensitive information
    return message
      .replace(/password[:\s]*\S+/gi, 'password: [REDACTED]')
      .replace(/token[:\s]*\S+/gi, 'token: [REDACTED]')
      .replace(/key[:\s]*\S+/gi, 'key: [REDACTED]')
      .replace(/secret[:\s]*\S+/gi, 'secret: [REDACTED]')
      .replace(/Bearer\s+\S+/gi, 'Bearer [REDACTED]')
      .replace(/authorization[:\s]*\S+/gi, 'authorization: [REDACTED]')
      .replace(
        /(?:DATABASE_URL|JWT_SECRET|TOKEN_SECRET)[^\s]*/gi,
        '[REDACTED]'
      );
  }

  return message;
}

// ============================================================================
// Brute Force Protection
// ============================================================================

interface BruteForceEntry {
  attempts: number;
  resetTime: number;
}

const bruteForceStore = new Map<string, BruteForceEntry>();

/**
 * Check if an identifier is locked out due to too many failed attempts
 */
export function isLockedOut(
  identifier: string,
  maxAttempts: number = 5,
  lockoutMs: number = 15 * 60 * 1000 // 15 minutes
): { locked: boolean; remainingAttempts: number; resetTime: number } {
  const now = Date.now();
  const entry = bruteForceStore.get(identifier);

  if (!entry || now > entry.resetTime) {
    return {
      locked: false,
      remainingAttempts: maxAttempts,
      resetTime: now + lockoutMs,
    };
  }

  if (entry.attempts >= maxAttempts) {
    return { locked: true, remainingAttempts: 0, resetTime: entry.resetTime };
  }

  return {
    locked: false,
    remainingAttempts: maxAttempts - entry.attempts,
    resetTime: entry.resetTime,
  };
}

/**
 * Record a failed attempt
 */
export function recordFailedAttempt(
  identifier: string,
  maxAttempts: number = 5,
  lockoutMs: number = 15 * 60 * 1000
): void {
  const now = Date.now();
  const entry = bruteForceStore.get(identifier);

  if (!entry || now > entry.resetTime) {
    bruteForceStore.set(identifier, {
      attempts: 1,
      resetTime: now + lockoutMs,
    });
  } else {
    entry.attempts++;
  }
}

/**
 * Clear failed attempts on successful login
 */
export function clearFailedAttempts(identifier: string): void {
  bruteForceStore.delete(identifier);
}

// ============================================================================
// PII Redaction for Logging
// ============================================================================

/**
 * Redact PII from objects before logging
 */
export function redactPII(
  obj: Record<string, unknown>
): Record<string, unknown> {
  const sensitiveFields = [
    'password',
    'email',
    'token',
    'secret',
    'key',
    'creditCard',
    'ssn',
    'socialSecurity',
    'phone',
    'address',
    'birthDate',
  ];

  const result: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();

    if (sensitiveFields.some(field => lowerKey.includes(field))) {
      result[key] = '[REDACTED]';
    } else if (typeof value === 'object' && value !== null) {
      result[key] = redactPII(value as Record<string, unknown>);
    } else {
      result[key] = value;
    }
  }

  return result;
}
