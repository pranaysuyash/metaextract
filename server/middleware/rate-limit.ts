/**
 * Rate Limiting Middleware
 * Implements IP-based and client-based rate limiting
 */

import { Request, Response, NextFunction } from 'express';
import { storage } from '../storage/index';
import { verifyClientToken } from '../utils/free-quota-enforcement';

const CONFIG = {
  // IP Rate Limits
  IP_DAILY_LIMIT: 10,
  IP_MINUTE_LIMIT: 2,

  // Client Rate Limits
  CLIENT_MINUTE_LIMIT: 2,

  // Cleanup intervals
  DAILY_RESET_HOUR: 0, // Midnight UTC
  CLEANUP_INTERVAL_MS: 60 * 60 * 1000, // 1 hour
};

/**
 * IP-based rate limiting middleware
 * Tracks requests per IP address
 */
export async function ipRateLimitMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const ip = req.ip || req.connection.remoteAddress || 'unknown';

    // Skip rate limiting for development/testing ONLY
    // SECURITY: This must NEVER be enabled in production
    if (
      process.env.NODE_ENV !== 'production' &&
      process.env.SKIP_RATE_LIMITS === 'true'
    ) {
      next();
      return;
    }

    // Get current counts
    const dailyCount = await getIPDailyCount(ip);
    const minuteCount = await getIPMinuteCount(ip);

    // Check limits
    if (dailyCount >= CONFIG.IP_DAILY_LIMIT) {
      res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Daily limit reached. Please try again tomorrow.',
        limit_type: 'daily',
        limit: CONFIG.IP_DAILY_LIMIT,
        current: dailyCount,
        reset_time: getNextResetTime('daily'),
      });
      return;
    }

    if (minuteCount >= CONFIG.IP_MINUTE_LIMIT) {
      res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Too many requests. Please slow down.',
        limit_type: 'minute',
        limit: CONFIG.IP_MINUTE_LIMIT,
        current: minuteCount,
        reset_time: getNextResetTime('minute'),
      });
      return;
    }

    // Increment counters
    await incrementIPCounts(ip);

    // Allow request
    next();
  } catch (error) {
    console.error('Rate limiting error:', error);
    // Don't break the app - allow request but log error
    next();
  }
}

/**
 * Client-based rate limiting middleware
 * Tracks requests per client/device
 */
export async function clientRateLimitMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const clientToken = req.cookies?.metaextract_client;
    const decoded = verifyClientToken(clientToken);

    if (!decoded) {
      // No valid client token - allow but don't count
      next();
      return;
    }

    const clientId = decoded.clientId;

    // Get current minute count
    const minuteCount = await getClientMinuteCount(clientId);

    // Check limit
    if (minuteCount >= CONFIG.CLIENT_MINUTE_LIMIT) {
      res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Too many requests from this device. Please slow down.',
        limit_type: 'client_minute',
        limit: CONFIG.CLIENT_MINUTE_LIMIT,
        current: minuteCount,
        reset_time: getNextResetTime('minute'),
      });
      return;
    }

    // Increment counter
    await incrementClientCount(clientId);

    // Allow request
    next();
  } catch (error) {
    console.error('Client rate limiting error:', error);
    // Don't break the app - allow request but log error
    next();
  }
}

/**
 * Get IP daily count
 */
async function getIPDailyCount(ip: string): Promise<number> {
  try {
    // Fallback to Redis/storage
    const key = `ip_daily:${ip}:${getCurrentDateKey()}`;
    const count = await storage.get(key);
    return count ? parseInt(count, 10) : 0;
  } catch (error) {
    console.error('Error getting IP daily count:', error);
    return 0;
  }
}

/**
 * Get IP minute count
 */
async function getIPMinuteCount(ip: string): Promise<number> {
  try {
    // Fallback to Redis/storage
    const key = `ip_minute:${ip}:${getCurrentMinuteKey()}`;
    const count = await storage.get(key);
    return count ? parseInt(count, 10) : 0;
  } catch (error) {
    console.error('Error getting IP minute count:', error);
    return 0;
  }
}

/**
 * Get client minute count
 */
async function getClientMinuteCount(clientId: string): Promise<number> {
  try {
    const key = `client_minute:${clientId}:${getCurrentMinuteKey()}`;
    const count = await storage.get(key);
    return count ? parseInt(count, 10) : 0;
  } catch (error) {
    console.error('Error getting client minute count:', error);
    return 0;
  }
}

/**
 * Increment IP counts
 */
async function incrementIPCounts(ip: string): Promise<void> {
  try {
    // Daily count
    const dailyKey = `ip_daily:${ip}:${getCurrentDateKey()}`;
    await storage.incr(dailyKey);
    await storage.expire(dailyKey, 24 * 60 * 60); // 24 hours

    // Minute count
    const minuteKey = `ip_minute:${ip}:${getCurrentMinuteKey()}`;
    await storage.incr(minuteKey);
    await storage.expire(minuteKey, 60); // 1 minute
  } catch (error) {
    console.error('Error incrementing IP counts:', error);
  }
}

/**
 * Increment client count
 */
async function incrementClientCount(clientId: string): Promise<void> {
  try {
    const key = `client_minute:${clientId}:${getCurrentMinuteKey()}`;
    await storage.incr(key);
    await storage.expire(key, 60); // 1 minute
  } catch (error) {
    console.error('Error incrementing client count:', error);
  }
}

/**
 * Get current date key for daily tracking
 */
function getCurrentDateKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
}

/**
 * Get current minute key for minute tracking
 */
function getCurrentMinuteKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}-${now.getHours()}-${now.getMinutes()}`;
}

/**
 * Get next reset time for rate limits
 */
function getNextResetTime(limitType: 'daily' | 'minute'): string {
  const now = new Date();

  if (limitType === 'daily') {
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    return tomorrow.toISOString();
  } else {
    const nextMinute = new Date(now);
    nextMinute.setMinutes(nextMinute.getMinutes() + 1);
    nextMinute.setSeconds(0, 0);
    return nextMinute.toISOString();
  }
}
