/**
 * Abuse Throttle System
 *
 * Centralizes abuse prevention mechanisms:
 * 1. Per-IP rate limits (already in rateLimitRedis.ts)
 * 2. Per-account rate limits
 * 3. File size limits
 * 4. Concurrency caps
 * 5. Same-file-hash deduplication (prevents hammering same file)
 */

import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';
import { rateLimitManager } from '../rateLimitRedis';
import { storage } from '../storage/index';

const MAX_CONCURRENT_EXTRACTIONS = 10;
const MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024; // 100MB
const DEDUPE_WINDOW_MS = 60 * 1000; // 1 minute

const activeExtractions = new Map<
  string,
  { sessionId: string; startTime: number; fileHash: string }
>();
const recentFileHashes = new Map<
  string,
  { count: number; firstSeen: number }
>();

export interface AbuseThrottleResult {
  allowed: boolean;
  reason:
    | 'OK'
    | 'RATE_LIMITED'
    | 'FILE_TOO_LARGE'
    | 'CONCURRENT_LIMIT'
    | 'DUPLICATE_FILE';
  retryAfter?: number;
  message?: string;
}

/**
 * Get client identifier for throttling
 */
function getClientIdentifier(req: Request): string {
  if ((req as any).user?.id) {
    return `user:${(req as any).user.id}`;
  }
  const ip = req.ip || req.socket.remoteAddress || 'unknown';
  return `ip:${ip}`;
}

/**
 * Calculate file hash for deduplication
 */
function calculateFileHash(buffer: Buffer): string {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

/**
 * Check and acquire concurrency slot
 */
async function checkConcurrency(
  clientId: string
): Promise<{ allowed: boolean; currentCount: number }> {
  const now = Date.now();

  for (const [key, value] of activeExtractions.entries()) {
    if (now - value.startTime > 5 * 60 * 1000) {
      activeExtractions.delete(key);
    }
  }

  const clientExtractions = Array.from(activeExtractions.values()).filter(e =>
    e.sessionId.startsWith(clientId.split(':')[1] || clientId)
  );

  const currentCount = clientExtractions.length;

  if (currentCount >= MAX_CONCURRENT_EXTRACTIONS) {
    return { allowed: false, currentCount };
  }

  return { allowed: true, currentCount };
}

/**
 * Clean up old file hash entries
 */
function cleanupFileHashes(): void {
  const now = Date.now();
  for (const [hash, value] of recentFileHashes.entries()) {
    if (now - value.firstSeen > DEDUPE_WINDOW_MS) {
      recentFileHashes.delete(hash);
    }
  }
}

/**
 * Check file hash for deduplication
 */
function checkFileHashDedupe(fileHash: string): {
  allowed: boolean;
  count: number;
} {
  cleanupFileHashes();

  const existing = recentFileHashes.get(fileHash);
  if (existing) {
    existing.count++;
    return { allowed: existing.count <= 3, count: existing.count };
  }

  recentFileHashes.set(fileHash, { count: 1, firstSeen: Date.now() });
  return { allowed: true, count: 1 };
}

/**
 * Main abuse throttle check
 */
export async function checkAbuseThrottle(
  req: Request,
  fileBuffer?: Buffer
): Promise<AbuseThrottleResult> {
  const clientId = getClientIdentifier(req);
  const now = Date.now();

  // 1. Check rate limits
  const ip = req.ip || req.socket.remoteAddress || 'unknown';
  const rateLimitResult = await rateLimitManager.checkIPRateLimit(ip);

  if (!rateLimitResult.allowed) {
    return {
      allowed: false,
      reason: 'RATE_LIMITED',
      retryAfter: rateLimitResult.retryAfter,
      message: 'Rate limit exceeded. Please try again later.',
    };
  }

  // 2. Check file size (if file provided)
  if (fileBuffer && fileBuffer.length > MAX_FILE_SIZE_BYTES) {
    return {
      allowed: false,
      reason: 'FILE_TOO_LARGE',
      message: `File too large. Maximum size is ${MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB.`,
    };
  }

  // 3. Check concurrency
  const concurrency = await checkConcurrency(clientId);
  if (!concurrency.allowed) {
    return {
      allowed: false,
      reason: 'CONCURRENT_LIMIT',
      retryAfter: 30,
      message: `Too many concurrent extractions (${concurrency.currentCount}/${MAX_CONCURRENT_EXTRACTIONS}). Please wait.`,
    };
  }

  // 4. Check file hash deduplication
  if (fileBuffer) {
    const fileHash = calculateFileHash(fileBuffer);
    const dedupe = checkFileHashDedupe(fileHash);

    if (!dedupe.allowed) {
      return {
        allowed: false,
        reason: 'DUPLICATE_FILE',
        retryAfter: 10,
        message:
          'Same file submitted too many times. Please wait before resubmitting.',
      };
    }
  }

  return { allowed: true, reason: 'OK' };
}

/**
 * Acquire extraction slot (call before processing, release after)
 */
export async function acquireExtractionSlot(
  sessionId: string,
  fileHash: string
): Promise<{ acquired: boolean; slotId: string }> {
  const clientId = getClientIdentifier({ ip: 'unknown' } as Request);
  const concurrency = await checkConcurrency(clientId);

  if (!concurrency.allowed) {
    return { acquired: false, slotId: '' };
  }

  const slotId = `${sessionId}:${Date.now()}`;
  activeExtractions.set(slotId, { sessionId, startTime: Date.now(), fileHash });

  return { acquired: true, slotId };
}

/**
 * Release extraction slot
 */
export function releaseExtractionSlot(slotId: string): void {
  activeExtractions.delete(slotId);
}

/**
 * Get current abuse stats for monitoring
 */
export function getAbuseStats(): {
  activeExtractions: number;
  recentFileHashes: number;
  concurrencyLimit: number;
} {
  cleanupFileHashes();

  return {
    activeExtractions: activeExtractions.size,
    recentFileHashes: recentFileHashes.size,
    concurrencyLimit: MAX_CONCURRENT_EXTRACTIONS,
  };
}
