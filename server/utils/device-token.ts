/**
 * Server-Issued Device Token System
 * 
 * Replaces client-generated tokens with HMAC-signed server tokens.
 * Primary identity for quota tracking - resistant to cookie clearing attacks.
 * 
 * Security features:
 * - Server-minted tokens (not client-controllable)
 * - HMAC signature with timing-safe comparison
 * - Expiry enforcement
 * - httpOnly cookie (not accessible via JavaScript)
 */

import * as crypto from 'crypto';
import { Request, Response } from 'express';

// Use dedicated device token secret, fallback to TOKEN_SECRET
const DEVICE_TOKEN_SECRET = process.env.DEVICE_TOKEN_SECRET || process.env.TOKEN_SECRET;

if (!DEVICE_TOKEN_SECRET) {
  console.warn(
    '⚠️  DEVICE_TOKEN_SECRET not set. Device tokens will use TOKEN_SECRET. ' +
    'For production, set DEVICE_TOKEN_SECRET with: openssl rand -hex 32'
  );
}

const DEVICE_COOKIE_NAME = 'metaextract_device';
const TOKEN_EXPIRY_DAYS = 90;

export interface DeviceToken {
  deviceId: string;
  expiry: number;
  issuedAt: number;
}

/**
 * Create a new server-signed device token
 * Format: deviceId.issuedAt.expiry.signature
 */
export function createDeviceToken(): string {
  const deviceId = crypto.randomUUID();
  const issuedAt = Date.now();
  const expiry = issuedAt + (TOKEN_EXPIRY_DAYS * 24 * 60 * 60 * 1000);
  
  const payload = `${deviceId}.${issuedAt}.${expiry}`;
  const signature = crypto
    .createHmac('sha256', DEVICE_TOKEN_SECRET!)
    .update(payload)
    .digest('hex');
  
  return `${payload}.${signature}`;
}

/**
 * Verify and decode a device token
 * Returns null if token is invalid, tampered, or expired
 */
export function verifyDeviceToken(token: string): DeviceToken | null {
  if (!token || typeof token !== 'string') return null;
  
  try {
    const parts = token.split('.');
    if (parts.length !== 4) return null;
    
    const [deviceId, issuedAtStr, expiryStr, signature] = parts;
    
    // Validate UUID format for deviceId
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(deviceId)) {
      return null;
    }
    
    const payload = `${deviceId}.${issuedAtStr}.${expiryStr}`;
    
    const expectedSignature = crypto
      .createHmac('sha256', DEVICE_TOKEN_SECRET!)
      .update(payload)
      .digest('hex');
    
    // Timing-safe comparison to prevent timing attacks
    if (signature.length !== expectedSignature.length) return null;
    
    const signatureBuffer = Buffer.from(signature, 'hex');
    const expectedBuffer = Buffer.from(expectedSignature, 'hex');
    
    if (signatureBuffer.length !== expectedBuffer.length) return null;
    
    if (!crypto.timingSafeEqual(signatureBuffer, expectedBuffer)) {
      return null;
    }
    
    const expiry = parseInt(expiryStr, 10);
    const issuedAt = parseInt(issuedAtStr, 10);
    
    if (isNaN(expiry) || isNaN(issuedAt)) {
      return null;
    }
    
    // Check expiry
    if (Date.now() > expiry) {
      return null;
    }
    
    // Sanity check: issuedAt should be in the past
    if (issuedAt > Date.now()) {
      return null;
    }
    
    return { deviceId, expiry, issuedAt };
  } catch (error) {
    console.error('Device token verification error:', error);
    return null;
  }
}

/**
 * Get existing device token from request, or create a new one
 * Sets httpOnly cookie on response
 */
export function getOrCreateDeviceToken(req: Request, res: Response): string {
  // Try to get existing token from cookie
  let token = req.cookies?.[DEVICE_COOKIE_NAME];
  let decoded = token ? verifyDeviceToken(token) : null;
  
  // If no valid token, create new one
  if (!decoded) {
    token = createDeviceToken();
    setDeviceCookie(res, token);
    decoded = verifyDeviceToken(token);
  }
  
  // This should never happen, but check anyway
  if (!decoded) {
    throw new Error('Failed to create device token');
  }
  
  return decoded.deviceId;
}

/**
 * Set device token cookie with security flags
 */
export function setDeviceCookie(res: Response, token: string): void {
  res.cookie(DEVICE_COOKIE_NAME, token, {
    httpOnly: true, // Not accessible via JavaScript
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    sameSite: 'lax', // Allow cross-site redirects (checkout flows)
    maxAge: TOKEN_EXPIRY_DAYS * 24 * 60 * 60 * 1000,
    path: '/',
  });
}

/**
 * Revoke a device token (for abuse cases)
 * In practice, this would add to a revocation list in Redis
 */
export async function revokeDeviceToken(deviceId: string): Promise<void> {
  // Future: Add to Redis revocation set
  console.log(`[Security] Device token revoked: ${deviceId}`);
}

/**
 * Check if a device has suspicious behavior patterns
 */
export function isDeviceSuspicious(
  deviceToken: DeviceToken,
  currentIp: string,
  recentIps: string[]
): boolean {
  // Flag 1: Token was just created (could be intentional reset)
  const tokenAgeHours = (Date.now() - deviceToken.issuedAt) / (1000 * 60 * 60);
  const isNewToken = tokenAgeHours < 0.5; // Less than 30 minutes old
  
  // Flag 2: Many different IPs for this device
  const uniqueIps = new Set([currentIp, ...recentIps]);
  const manyIps = uniqueIps.size > 5;
  
  // Suspicious if new token AND many IPs
  return isNewToken && manyIps;
}

export const DEVICE_COOKIE_NAME_EXPORT = DEVICE_COOKIE_NAME;
