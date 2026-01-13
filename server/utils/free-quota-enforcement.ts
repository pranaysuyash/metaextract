/**
 * MetaExtract Free Quota Enforcement System
 * Implements "2 Free Images per Device" with 4-tier protection
 *
 * Tier 1: Server-issued device tokens (not client-controllable)
 * Tier 2: IP rate limiting with fail-closed Redis fallback
 * Tier 3: Advanced fingerprinting and abuse scoring
 * Tier 4: Circuit breaker for load shedding
 *
 * Security changelog:
 * - 2026-01-07: Added server-issued device tokens (device-token.ts)
 * - 2026-01-07: Fixed fail-open Redis to use in-memory fallback
 * - 2026-01-07: Added circuit breaker for load shedding
 */

import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';
import { eq, sql } from 'drizzle-orm';
import { getDatabase } from '../db';
import { clientUsage } from '@shared/schema';
import { storage } from '../storage/index';
import { circuitBreaker } from './circuit-breaker';
import {
  getOrCreateDeviceToken,
  verifyDeviceToken as verifyServerDeviceToken,
  isDeviceSuspicious,
} from './device-token';
import { sendQuotaExceededError } from '../utils/error-response';
import { getOrSetSessionId } from './session-id';
// import { trackImagesMvpEvent } from '../lib/images-mvp-analytics';

// Token secret validation - fail fast if not set
const TOKEN_SECRET = process.env.TOKEN_SECRET ?? '';
if (!TOKEN_SECRET) {
  throw new Error(
    'CRITICAL: TOKEN_SECRET environment variable is required for security. ' +
      'Please set this in your .env file before starting the server. ' +
      'Generate a strong random secret: openssl rand -hex 32'
  );
}

// Configuration
const CONFIG = {
  // Tier 1: Device Quota
  FREE_LIMIT: 2,
  TOKEN_EXPIRY_HOURS: 24 * 30, // 30 days
  COOKIE_NAME: 'metaextract_client',
  COOKIE_OPTIONS: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    // Lax so device quota survives external checkout redirects.
    sameSite: 'lax' as const,
    maxAge: 1000 * 60 * 60 * 24 * 7, // 7 days - reduced for security
  },

  // Tier 2: Rate Limiting
  IP_DAILY_LIMIT: 10,
  IP_MINUTE_LIMIT: 2,
  CLIENT_MINUTE_LIMIT: 2,

  // Tier 3: Abuse Detection
  ABUSE_SCORE_THRESHOLD: 0.7,
  FINGERPRINT_COMPONENTS: [
    'userAgent',
    'platform',
    'timezone',
    'language',
    'screenSize',
  ],
};

/**
 * Generate cryptographically secure client token
 * Includes client_id, expiry, and HMAC signature
 */
export function generateClientToken(): string {
  const clientId = crypto.randomUUID();
  const expiry = Date.now() + CONFIG.TOKEN_EXPIRY_HOURS * 60 * 60 * 1000;
  const payload = `${clientId}.${expiry}`;

  // Create HMAC signature using validated TOKEN_SECRET
  const signature = crypto
    .createHmac('sha256', TOKEN_SECRET)
    .update(payload)
    .digest('hex');

  return `${payload}.${signature}`;
}

/**
 * Verify and decode client token
 * Returns null if invalid or expired
 */
export function verifyClientToken(
  token: unknown
): { clientId: string; expiry: number } | null {
  try {
    if (typeof token !== 'string' || token.length === 0) return null;
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const [clientId, expiryStr, signature] = parts;
    const payload = `${clientId}.${expiryStr}`;

    // Verify signature using validated TOKEN_SECRET
    const expectedSignature = crypto
      .createHmac('sha256', TOKEN_SECRET)
      .update(payload)
      .digest('hex');

    if (signature !== expectedSignature) return null;

    // Parse expiry
    const expiry = parseInt(expiryStr, 10);
    if (isNaN(expiry)) return null;

    // Check expiry
    if (Date.now() > expiry) return null;

    return { clientId, expiry };
  } catch (error) {
    console.error('Token verification failed:', error);
    return null;
  }
}

/**
 * Generate lightweight device fingerprint
 * Used as additional abuse signal (not hard ban)
 */
export function generateDeviceFingerprint(req: Request): string {
  const components = [
    req.headers['user-agent'] || '',
    req.headers['accept-language'] || '',
    req.headers['accept'] || '',
    // Add screen size if available from client
    (req.body as any)?._screenSize || '',
    // Add timezone if available
    (req.body as any)?._timezone || '',
  ];

  const fingerprint = components.join('|');
  return crypto.createHash('sha256').update(fingerprint).digest('hex');
}

/**
 * Calculate abuse score based on various signals
 * Score 0-1, where 1 is highest risk
 */
export function calculateAbuseScore(
  clientId: string,
  ip: string,
  fingerprint: string,
  recentActivity: any[]
): number {
  let score = 0;

  // Signal 1: Multiple client IDs from same IP
  const uniqueClientsFromIP = new Set(
    recentActivity.filter(a => a.ip === ip).map(a => a.clientId)
  ).size;
  if (uniqueClientsFromIP > 3) score += 0.3;
  if (uniqueClientsFromIP > 10) score += 0.2;

  // Signal 2: High velocity
  const recentRequests = recentActivity.filter(
    a => a.timestamp > Date.now() - 60000
  ); // Last minute
  if (recentRequests.length > 10) score += 0.2;
  if (recentRequests.length > 30) score += 0.2;

  // Signal 3: Repeated quota hits with new tokens
  const quotaHits = recentActivity.filter(a => a.action === 'quota_hit');
  const newTokens = recentActivity.filter(a => a.action === 'new_token');
  if (quotaHits.length > 2 && newTokens.length > 3) score += 0.2;

  // Signal 4: Datacenter/Cloud IPs (optional enhancement)
  // Could add IP reputation checking here

  return Math.min(score, 1.0);
}

/**
 * Main quota enforcement middleware
 * Implements all 3 tiers of protection
 */
export async function enforceFreeQuota(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const startTime = Date.now();
    const ip = req.ip || req.connection.remoteAddress || 'unknown';
    const userAgent = req.headers['user-agent'] || 'unknown';

    // Get or create client token (defensive: req.cookies may be undefined in some test environments)
    let clientToken = req.cookies?.[CONFIG.COOKIE_NAME];
    let clientId: string;
    let isNewToken = false;

    if (!clientToken) {
      // New visitor - generate token
      clientToken = generateClientToken();
      res.cookie(CONFIG.COOKIE_NAME, clientToken, CONFIG.COOKIE_OPTIONS);
      const decoded = verifyClientToken(clientToken);
      clientId = decoded!.clientId;
      isNewToken = true;
    } else {
      // Existing visitor - verify token
      const decoded = verifyClientToken(clientToken);
      if (!decoded) {
        // Invalid token - generate new one
        clientToken = generateClientToken();
        res.cookie(CONFIG.COOKIE_NAME, clientToken, CONFIG.COOKIE_OPTIONS);
        const newDecoded = verifyClientToken(clientToken);
        clientId = newDecoded!.clientId;
        isNewToken = true;
      } else {
        clientId = decoded.clientId;
      }
    }

    // Track this request for analytics
    await trackRequest(clientId, ip, userAgent, startTime);

    // Check if this is an extraction request (not just page view)
    if (req.method === 'POST' && req.path === '/api/images_mvp/extract') {
      await handleExtractionRequest(req, res, next, {
        clientId,
        ip,
        userAgent,
        isNewToken,
        startTime,
      });
    } else {
      // Non-extraction request - allow but track
      next();
    }
  } catch (error) {
    console.error('Quota enforcement error:', error);
    // Don't break the app - allow request but log error
    next();
  }
}

/**
 * Handle extraction requests with full quota enforcement
 */
async function handleExtractionRequest(
  req: Request,
  res: Response,
  next: NextFunction,
  context: {
    clientId: string;
    ip: string;
    userAgent: string;
    isNewToken: boolean;
    startTime: number;
  }
): Promise<void> {
  const { clientId, ip } = context;

  try {
    // Check if user has trial email (bypasses free limits)
    const trialEmail = req.body?.trial_email;
    if (trialEmail) {
      // Trial users bypass free limits - let them through
      next();
      return;
    }

    // Remove SKIP_FREE_LIMITS bypass - security must be enforced in all environments
    // Development testing should use test accounts with credits, not bypass security

    // Get current usage for this client
    const usage = await getClientUsage(clientId);
    const currentCount = usage?.freeUsed || 0;

    // Check quota
    if (currentCount >= CONFIG.FREE_LIMIT) {
      const hasCredits = await hasCreditsAvailable(req, res);
      if (hasCredits) {
        next();
        return;
      }
      // Quota exceeded - handle based on abuse score
      await handleQuotaExceeded(req, res, clientId, ip);
      return;
    }

    // Within quota - proceed but track usage
    await incrementUsage(clientId, ip);

    // Log successful free usage
    // trackImagesMvpEvent('free_extraction_used', {
    //   client_id: clientId,
    //   ip: ip,
    //   usage_count: currentCount + 1,
    //   is_new_token: isNewToken,
    // });

    // Allow the extraction
    next();
  } catch (error) {
    console.error('Extraction handling error:', error);
    // Allow request but log error - don't break the app
    next();
  }
}

async function hasCreditsAvailable(
  req: Request,
  res: Response
): Promise<boolean> {
  try {
    const userId = (req as any).user?.id as string | undefined;
    const balanceKey = userId
      ? `images_mvp:user:${userId}`
      : `images_mvp:${getOrSetSessionId(req, res)}`;
    const balance = await storage.getOrCreateCreditBalance(balanceKey, userId);
    return (balance?.credits ?? 0) > 0;
  } catch (error) {
    console.error('Credit availability check failed:', error);
    return false;
  }
}

/**
 * Handle quota exceeded situations
 * Escalates based on abuse score
 */
export async function handleQuotaExceeded(
  req: Request,
  res: Response,
  clientId: string,
  ip: string
): Promise<void> {
  try {
    // Calculate abuse score
    const recentActivity = await getRecentActivity(clientId, ip);
    const fingerprint = generateDeviceFingerprint(req);
    const abuseScore = calculateAbuseScore(
      clientId,
      ip,
      fingerprint,
      recentActivity
    );

    // Log quota exceeded event
    // trackImagesMvpEvent('quota_exceeded', {
    //   client_id: clientId,
    //   ip: ip,
    //   abuse_score: abuseScore,
    //   recent_activity_count: recentActivity.length,
    // });

    // Respond based on abuse score
    if (abuseScore > CONFIG.ABUSE_SCORE_THRESHOLD) {
      // High abuse score - require CAPTCHA (treat as quota exceeded for now)
      sendQuotaExceededError(
        res,
        'Free limit reached on this device. Complete verification to continue.'
      );
      return;
    } else {
      // Normal quota exceeded - show paywall
      sendQuotaExceededError(
        res,
        'Free limit reached on this device. Purchase credits to continue.'
      );
      return;
    }
  } catch (error) {
    console.error('Quota exceeded handling error:', error);
    // Fallback response
    res.status(429).json({
      error: 'Quota exceeded',
      message:
        'Free limit reached on this device. Purchase credits to continue.',
      credits_required: 1,
    });
  }
}

/**
 * Database operations for usage tracking
 */

export async function getClientUsage(
  clientId: string
): Promise<{ freeUsed: number } | null> {
  try {
    // Try to get from database first
    if (isDatabaseConnected()) {
      try {
        const db = getDatabase() as any;
        if (typeof db.select !== 'function') {
          throw new Error('Database client missing select()');
        }
        const result = await db
          .select({ freeUsed: clientUsage.freeUsed })
          .from(clientUsage)
          .where(eq(clientUsage.clientId, clientId))
          .limit(1);

        return result[0] || null;
      } catch {
        // Fall back to storage in test / partial-mock environments.
      }
    }

    // Fallback to Redis/storage
    const key = `quota:${clientId}`;
    const data = await storage.get(key);
    if (!data) return null;
    try {
      const parsed = JSON.parse(data);
      if (typeof parsed === 'number') {
        return { freeUsed: parsed };
      }
      if (parsed && typeof parsed === 'object' && 'freeUsed' in parsed) {
        const value = Number((parsed as { freeUsed: number }).freeUsed);
        return { freeUsed: Number.isNaN(value) ? 0 : value };
      }
    } catch {
      const numeric = Number(data);
      if (!Number.isNaN(numeric)) {
        return { freeUsed: numeric };
      }
    }
    return null;
  } catch (error) {
    console.error('Error getting client usage:', error);
    return null;
  }
}

export async function incrementUsage(
  clientId: string,
  ip: string
): Promise<void> {
  try {
    // Update database
    if (isDatabaseConnected()) {
      try {
        const db = getDatabase() as any;
        console.log(`[QuotaDebug] Incrementing usage in DB for ${clientId}`);
        await db
          .insert(clientUsage)
          .values({
            clientId,
            freeUsed: 1,
            lastIp: ip,
            lastUsed: new Date(),
          })
          .onConflictDoUpdate({
            target: clientUsage.clientId,
            set: {
              freeUsed: sql`${clientUsage.freeUsed} + 1`,
              lastIp: ip,
              lastUsed: new Date(),
            },
          });
        console.log(
          `[QuotaDebug] Successfully incremented usage in DB for ${clientId}`
        );
        return;
      } catch (dbError) {
        console.warn(
          '[QuotaDebug] Database increment failed, falling back:',
          dbError
        );
      }
    }

    // Fallback to storage
    const key = `quota:${clientId}`;
    if (typeof (storage as any).get === 'function') {
      const current = await (storage as any).get(key);
      let count = 0;
      if (current) {
        try {
          const parsed = JSON.parse(current);
          if (typeof parsed === 'number') {
            count = parsed;
          } else if (
            parsed &&
            typeof parsed === 'object' &&
            'freeUsed' in parsed
          ) {
            count = Number((parsed as { freeUsed: number }).freeUsed) || 0;
          } else {
            count = Number(current) || 0;
          }
        } catch {
          count = Number(current) || 0;
        }
      }
      const next = count + 1;
      await (storage as any).set(key, JSON.stringify({ freeUsed: next }));
      console.log(
        `[QuotaDebug] Incremented usage in fallback storage for ${clientId}: ${next}`
      );
    } else {
      console.warn('[QuotaDebug] Fallback storage does not support get/set');
    }
  } catch (error) {
    console.error('Error incrementing usage:', error);
  }
}

async function trackRequest(
  clientId: string,
  ip: string,
  userAgent: string,
  timestamp: number
): Promise<void> {
  try {
    // Track for analytics and abuse detection
    // await trackImagesMvpEvent('request_tracked', {
    //   client_id: clientId,
    //   ip: ip,
    //   user_agent: userAgent,
    //   timestamp: timestamp,
    // });

    // Store for abuse detection (keep last 1000 requests per client)
    const key = `activity:${clientId}`;
    const activity = {
      client_id: clientId,
      ip,
      user_agent: userAgent,
      timestamp,
      action: 'request',
    };

    // Prefer native list ops when available (Redis-like). Fall back to best-effort get/set if not.
    if (
      typeof (storage as any).lpush === 'function' &&
      typeof (storage as any).ltrim === 'function'
    ) {
      await (storage as any).lpush(key, JSON.stringify(activity));
      await (storage as any).ltrim(key, 0, 999); // Keep last 1000
      if (typeof (storage as any).expire === 'function') {
        await (storage as any).expire(key, 3600); // Expire after 1 hour
      }
    } else if (
      typeof (storage as any).rpush === 'function' &&
      typeof (storage as any).ltrim === 'function'
    ) {
      await (storage as any).rpush(key, JSON.stringify(activity));
      await (storage as any).ltrim(key, 0, 999);
      if (typeof (storage as any).expire === 'function') {
        await (storage as any).expire(key, 3600);
      }
    } else {
      // Best-effort fallback: use get/set to persist a JSON array of recent activities if storage supports it
      try {
        if (
          typeof (storage as any).get === 'function' &&
          typeof (storage as any).set === 'function'
        ) {
          const existing = await (storage as any).get(key);
          let arr: any[] = [];
          if (existing) {
            try {
              arr = JSON.parse(existing);
            } catch {
              arr = [existing];
            }
          }
          arr.unshift(activity);
          arr = arr.slice(0, 1000);
          await (storage as any).set(key, JSON.stringify(arr));
          if (typeof (storage as any).expire === 'function') {
            await (storage as any).expire(key, 3600);
          }
        } else {
          // Storage backend lacks list-like semantics; skip activity persistence quietly in tests or constrained envs
          console.debug(
            '[QuotaDebug] Storage lacks list ops; skipping activity persistence'
          );
        }
      } catch (fallbackError) {
        console.debug(
          '[QuotaDebug] Activity tracking fallback failed:',
          fallbackError
        );
      }
    }
  } catch (error) {
    // Reduce noise in test environments where storage may be a partial mock.
    console.debug('Error tracking request (non-fatal):', error);
  }
}

async function getRecentActivity(
  clientId: string,
  ip: string,
  minutes: number = 60
): Promise<any[]> {
  try {
    const key = `activity:${clientId}`;

    // Prefer list ops, fall back to stored JSON array if list ops are unavailable
    let activitiesRaw: any[] = [];
    if (typeof (storage as any).lrange === 'function') {
      activitiesRaw = await (storage as any).lrange(key, 0, -1);
    } else if (typeof (storage as any).get === 'function') {
      const value = await (storage as any).get(key);
      if (value) {
        try {
          activitiesRaw = Array.isArray(value) ? value : JSON.parse(value);
        } catch {
          activitiesRaw = [];
        }
      }
    } else {
      return [];
    }

    const cutoff = Date.now() - minutes * 60 * 1000;
    return activitiesRaw
      .map(a => (typeof a === 'string' ? JSON.parse(a) : a))
      .filter(a => a && a.timestamp && a.timestamp > cutoff);
  } catch (error) {
    console.debug('Error getting recent activity (non-fatal):', error);
    return [];
  }
}

function isDatabaseConnected(): boolean {
  try {
    // Check if database connection is available
    return !!getDatabase();
  } catch {
    return false;
  }
}

/**
 * Check circuit breaker for free tier requests
 * Returns delay info if system is under load
 */
export function checkCircuitBreaker(isPaid: boolean): {
  allowed: boolean;
  delayed: boolean;
  message: string;
  estimatedWaitSeconds: number;
} {
  if (isPaid) {
    const result = circuitBreaker.checkPaidTier();
    return {
      allowed: result.allowed,
      delayed: result.delayed,
      message: result.message,
      estimatedWaitSeconds: result.estimatedWaitSeconds,
    };
  }

  const result = circuitBreaker.checkFreeTier();
  return {
    allowed: result.allowed,
    delayed: result.delayed,
    message: result.message,
    estimatedWaitSeconds: result.estimatedWaitSeconds,
  };
}

/**
 * Get server-issued device ID for quota tracking
 * Uses the new secure device token system
 */
export function getServerDeviceId(req: Request, res: Response): string {
  return getOrCreateDeviceToken(req, res);
}

/**
 * Check if device shows suspicious behavior patterns
 */
export async function checkDeviceSuspicious(
  req: Request,
  deviceId: string
): Promise<boolean> {
  const ip = req.ip || req.connection.remoteAddress || 'unknown';

  // Get recent IPs for this device
  const recentActivity = await getRecentActivity(deviceId, ip, 15); // Last 15 minutes
  const recentIps = recentActivity.map(a => a.ip).filter(Boolean);

  // Get device token for age check
  const token = req.cookies?.metaextract_device;
  if (!token) return false;

  const decoded = verifyServerDeviceToken(token);
  if (!decoded) return false;

  return isDeviceSuspicious(decoded, ip, recentIps);
}
