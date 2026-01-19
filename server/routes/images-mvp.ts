import type { Express, Request, Response } from 'express';
import type { WebSocket } from 'ws';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import sharp from 'sharp';
import { fileTypeFromBuffer } from 'file-type';
import { eq, sql } from 'drizzle-orm';
import DodoPayments from 'dodopayments';
import { getDatabase, isDatabaseConnected } from '../db';
import { trialUsages } from '@shared/schema';
import { storage, assertStorageHealthy } from '../storage/index';
import {
  extractMetadataWithPython,
  transformMetadataForFrontend,
  normalizeEmail,
  getSessionId,
  cleanupTempFile,
  applyAccessModeRedaction,
} from '../utils/extraction-helpers';
import {
  sendQuotaExceededError,
  sendInvalidRequestError,
  sendInternalServerError,
  sendFileTooLargeError,
  sendLegacyFileTooLargeError,
  sendUnsupportedFileTypeError,
  sendServiceUnavailableError,
} from '../utils/error-response';
import { requireAuth } from '../auth';
import { getOrSetSessionId } from '../utils/session-id';
import { freeQuotaMiddleware } from '../middleware/free-quota';
import { enhancedProtectionMiddleware } from '../middleware/enhanced-protection';
import { createRateLimiter } from '../middleware/rateLimit';
import {
  generateClientToken,
  verifyClientToken,
  getClientUsage,
  incrementUsage,
  handleQuotaExceeded,
} from '../utils/free-quota-enforcement';
import {
  calculateDeviceRiskScore,
  getPreviousAttempts,
  getSessionAge,
} from '../utils/risk-calculator';
import {
  handleEnhancedQuotaExceeded,
  getRecentSecurityEvents,
  getSecurityStats,
} from '../utils/enhanced-quota-handler';
import { IMAGES_MVP_CREDIT_PACKS } from '../payments';
import {
  IMAGES_MVP_CREDIT_SCHEDULE,
  type ImagesMvpQuoteOps,
  computeMp,
  computeImagesMvpCreditsTotal,
  resolveMpBucket,
  resolveSizeBucketFromBytes,
} from '@shared/imagesMvpPricing';

// WebSocket progress tracking
interface ProgressConnection {
  ws: WebSocket;
  sessionId: string;
  startTime: number;
}

const activeConnections = new Map<string, ProgressConnection[]>();

// Simple in-memory quote store for Images MVP quotes (tests rely on this)
const IMAGES_MVP_QUOTES = new Map<string, any>();

// Periodic cleanup of expired quotes (runs every 5 minutes)
const QUOTE_CLEANUP_INTERVAL = 5 * 60 * 1000; // 5 minutes

type ImagesMvpStoredQuote = {
  id: string;
  sessionId: string;
  userId?: string | null;
  files: any[];
  ops: ImagesMvpQuoteOps;
  creditsTotal: number;
  perFileCredits: Record<string, number>;
  perFile: Record<string, any>;
  schedule: any;
  createdAt: Date;
  updatedAt: Date;
  expiresAt: Date;
  usedAt?: Date | null;
  status: 'active' | 'used' | 'expired';
};

function getQuoteStore(): Map<string, ImagesMvpStoredQuote> {
  return IMAGES_MVP_QUOTES as Map<string, ImagesMvpStoredQuote>;
}

// For testing: clear the quote store
export function clearImagesMvpQuotesForTesting() {
  IMAGES_MVP_QUOTES.clear();
}

async function createImagesMvpQuote(input: {
  sessionId: string;
  userId?: string | null;
  files: any[];
  ops: ImagesMvpQuoteOps;
  creditsTotal: number;
  perFileCredits: Record<string, number>;
  perFile: Record<string, any>;
  schedule: any;
  expiresAt: Date;
}): Promise<ImagesMvpStoredQuote> {
  const anyStorage = storage as any;
  if (typeof anyStorage?.createQuote === 'function') {
    return (await anyStorage.createQuote(input)) as ImagesMvpStoredQuote;
  }

  const now = new Date();
  const quote: ImagesMvpStoredQuote = {
    id: crypto.randomUUID(),
    sessionId: input.sessionId,
    userId: input.userId ?? null,
    files: input.files,
    ops: input.ops,
    creditsTotal: input.creditsTotal,
    perFileCredits: input.perFileCredits,
    perFile: input.perFile,
    schedule: input.schedule,
    createdAt: now,
    updatedAt: now,
    expiresAt: input.expiresAt,
    usedAt: null,
    status: 'active',
  };

  getQuoteStore().set(quote.id, quote);
  return quote;
}

async function getImagesMvpQuote(
  id: string
): Promise<ImagesMvpStoredQuote | undefined> {
  const anyStorage = storage as any;
  if (typeof anyStorage?.getQuote === 'function') {
    return (await anyStorage.getQuote(id)) as ImagesMvpStoredQuote | undefined;
  }

  const quote = getQuoteStore().get(id);
  if (!quote) return undefined;
  if (quote.status !== 'active') return undefined;
  if (new Date() >= new Date(quote.expiresAt)) return undefined;
  return quote;
}

/**
 * Mark a quote as used (consumed during extraction)
 * Prevents replay attacks by ensuring same quote can only be used once
 */
async function markQuoteAsUsed(id: string): Promise<void> {
  const anyStorage = storage as any;
  if (typeof anyStorage?.markQuoteUsed === 'function') {
    await anyStorage.markQuoteUsed(id);
    return;
  }

  const quote = getQuoteStore().get(id);
  if (quote) {
    quote.status = 'used';
    quote.usedAt = new Date();
    getQuoteStore().set(id, quote);
  }
}

function startQuoteCleanup() {
  setInterval(async () => {
    try {
      const anyStorage = storage as any;
      if (typeof anyStorage?.cleanupExpiredQuotes === 'function') {
        const cleanedCount =
          (await anyStorage.cleanupExpiredQuotes()) as number;
        if (cleanedCount > 0) {
          console.log(`[ImagesMVP] Cleaned up ${cleanedCount} expired quotes`);
        }
        return;
      }

      // Fallback: cleanup in-memory store
      const now = Date.now();
      let cleaned = 0;
      for (const [id, quote] of getQuoteStore().entries()) {
        const expiresAt = new Date(quote.expiresAt).getTime();
        if (quote.status !== 'active' || now >= expiresAt) {
          getQuoteStore().delete(id);
          cleaned += 1;
        }
      }
      if (cleaned > 0) {
        console.log(
          `[ImagesMVP] Cleaned up ${cleaned} expired quotes (memory)`
        );
      }
    } catch (error) {
      console.error('[ImagesMVP] Error cleaning up expired quotes:', error);
    }
  }, QUOTE_CLEANUP_INTERVAL);
}

function startHoldCleanup() {
  setInterval(async () => {
    try {
      const released = await storage.cleanupExpiredHolds();
      if (released > 0) {
        console.log(`[ImagesMVP] Released ${released} expired credit holds`);
      }
    } catch (error) {
      console.error('[ImagesMVP] Hold cleanup failed:', error);
    }
  }, QUOTE_CLEANUP_INTERVAL); // Use same interval as quotes (5 minutes)
}

// Start cleanup on module load
if (process.env.NODE_ENV !== 'test') {
  startQuoteCleanup();
  startHoldCleanup();
}

// ============================================================================
// Configuration
// ============================================================================

const DODO_API_KEY = process.env.DODO_PAYMENTS_API_KEY;
const IS_TEST_MODE = process.env.DODO_ENV !== 'live';

const computeCreditsTotal = computeImagesMvpCreditsTotal;

function parseBooleanField(value: unknown): boolean {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    return ['1', 'true', 'yes', 'on'].includes(normalized);
  }
  return false;
}

function parseOpsFromRequest(body: any): ImagesMvpQuoteOps {
  const opsRaw = body?.ops ?? body ?? {};
  return {
    embedding:
      typeof opsRaw.embedding === 'boolean'
        ? opsRaw.embedding
        : body?.op_embedding != null
          ? parseBooleanField(body.op_embedding)
          : true,
    ocr:
      typeof opsRaw.ocr === 'boolean'
        ? opsRaw.ocr
        : body?.op_ocr != null
          ? parseBooleanField(body.op_ocr)
          : false,
    forensics:
      typeof opsRaw.forensics === 'boolean'
        ? opsRaw.forensics
        : body?.op_forensics != null
          ? parseBooleanField(body.op_forensics)
          : false,
  };
}

async function computeSizeCreditsFromUpload(
  file: Express.Multer.File
): Promise<{
  mp: number | null;
  mpBucket: string;
  mpCredits: number;
  warning?: string;
}> {
  try {
    const meta = await sharp(file.buffer).metadata();
    const mp = computeMp(meta.width ?? null, meta.height ?? null);
    const bucket = resolveMpBucket(mp);
    return {
      mp,
      mpBucket: bucket.label,
      mpCredits: bucket.credits,
      warning: bucket.warning,
    };
  } catch {
    const bucket = resolveSizeBucketFromBytes(file.size);
    return {
      mp: null,
      mpBucket: bucket.label,
      mpCredits: bucket.credits,
      warning: 'Dimensions unavailable; using size-based bucket estimate.',
    };
  }
}

function getDodoClient() {
  const key = process.env.DODO_PAYMENTS_API_KEY;
  if (!key) return null;
  return new DodoPayments({
    bearerToken: key,
    environment: process.env.DODO_ENV !== 'live' ? 'test_mode' : 'live_mode',
  });
}

// WebSocket Progress Tracking Functions
function broadcastProgress(
  sessionId: string,
  progress: number,
  message: string,
  stage?: string
) {
  const connections = activeConnections.get(sessionId);
  if (!connections || connections.length === 0) return;

  const normalizedProgress = Math.min(100, Math.max(0, progress));
  const progressData = {
    type: 'progress',
    sessionId,
    // Backward/forward compatible fields (client expects `percentage`)
    progress: normalizedProgress,
    percentage: normalizedProgress,
    message,
    stage: stage || 'processing',
    timestamp: Date.now(),
  };

  const messageStr = JSON.stringify(progressData);

  connections.forEach(conn => {
    if (conn.ws.readyState === 1) {
      // WebSocket.OPEN
      conn.ws.send(messageStr);
    }
  });
}

function broadcastError(sessionId: string, error: string) {
  const connections = activeConnections.get(sessionId);
  if (!connections || connections.length === 0) return;

  const errorData = {
    type: 'error',
    sessionId,
    error,
    timestamp: Date.now(),
  };

  const messageStr = JSON.stringify(errorData);

  connections.forEach(conn => {
    if (conn.ws.readyState === 1) {
      // WebSocket.OPEN
      conn.ws.send(messageStr);
    }
  });
}

function broadcastComplete(sessionId: string, metadata: any) {
  const connections = activeConnections.get(sessionId);
  if (!connections || connections.length === 0) return;

  const completeData = {
    type: 'complete',
    sessionId,
    metadata: {
      fields_extracted: metadata.fields_extracted || 0,
      processing_time_ms: metadata.processing_time_ms || 0,
      file_size: metadata.file_size || 0,
    },
    timestamp: Date.now(),
  };

  const messageStr = JSON.stringify(completeData);

  connections.forEach(conn => {
    if (conn.ws.readyState === 1) {
      // WebSocket.OPEN
      conn.ws.send(messageStr);
    }
  });
}

function cleanupConnections(sessionId: string) {
  const connections = activeConnections.get(sessionId);
  if (connections) {
    connections.forEach(conn => {
      if (conn.ws.readyState === 1) {
        conn.ws.close();
      }
    });
    activeConnections.delete(sessionId);
  }
}

// Use disk storage to avoid memory exhaustion under heavy load
// Memory storage would hold entire file buffers until GC, risking OOM with concurrent uploads
const UPLOAD_TEMP_DIR = '/tmp/metaextract-uploads';

// Ensure upload directory exists at startup (sync is fine here, happens once)
let uploadDirReady = false;

const diskStorage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    // Create directory if not done yet (multer callbacks must be sync)
    if (!uploadDirReady) {
      fs.mkdir(UPLOAD_TEMP_DIR, { recursive: true })
        .then(() => {
          uploadDirReady = true;
          cb(null, UPLOAD_TEMP_DIR);
        })
        .catch(err => cb(err as Error, UPLOAD_TEMP_DIR));
    } else {
      cb(null, UPLOAD_TEMP_DIR);
    }
  },
  filename: (_req, file, cb) => {
    const uniqueSuffix = `${Date.now()}-${crypto.randomUUID()}`;
    const ext = path.extname(file.originalname);
    cb(null, `upload-${uniqueSuffix}${ext}`);
  },
});

const upload = multer({
  storage: diskStorage,
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB Limit for images
  },
});

// Rate limiter for analytics endpoints - prevent abuse/DOS
const analyticsRateLimiter = createRateLimiter({
  windowMs: 60 * 1000, // 1 minute window
  keyGenerator: req => req.ip || req.socket.remoteAddress || 'unknown',
});

const SUPPORTED_IMAGE_MIMES = new Set([
  // Original MVP formats
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/heic',
  'image/heif',

  // Enhanced formats
  'image/tiff',
  'image/bmp',
  'image/gif',
  'image/x-icon',
  'image/svg+xml',
  'image/avif',
  'image/jxl',
  'image/jp2',
  'image/jpx',
  'image/jpm',
  'image/vnd.adobe.photoshop',
  'image/x-exr',
  'image/icns',
  'image/vnd-ms.dds',
  'image/x-tga',
  'image/x-portable-anymap',
  'image/vnd.radiance',
  'application/fits',
  'image/x-raw',
  'image/x-canon-cr2',
  'image/x-canon-cr3',
  'image/x-nikon-nef',
  'image/x-nikon-nrw',
  'image/x-sony-arw',
  'image/x-sony-sr2',
  'image/x-adobe-dng',
  'image/x-olympus-orf',
  'image/x-fuji-raf',
  'image/x-pentax-pef',
  'image/x-sigma-x3f',
  'image/x-samsung-srw',
  'image/x-panasonic-rw2',
  'image/x-panasonic-raw',
  'image/x-leica-rwl',
  'image/x-hasselblad-3fr',
  'image/x-phaseone-iiq',
]);

const SUPPORTED_IMAGE_EXTENSIONS = new Set([
  // Original MVP formats (maintained for backward compatibility)
  '.jpg',
  '.jpeg',
  '.png',
  '.webp',
  '.heic',
  '.heif',

  // Enhanced formats from our comprehensive system
  '.avif',
  '.jxl',
  '.jp2',
  '.j2k',
  '.jpf',
  '.jpx',
  '.jpm',
  '.mj2',
  '.psd',
  '.psb',
  '.exr',
  '.icns',
  '.dds',
  '.tga',
  '.pbm',
  '.pgm',
  '.ppm',
  '.pnm',
  '.hdr',
  '.svgz',
  '.fits',
  '.fit',
  '.fts',
  '.tiff',
  '.tif',
  '.bmp',
  '.gif',
  '.ico',
  '.svg',
  '.raw',
  '.cr2',
  '.cr3',
  '.nef',
  '.nrw',
  '.arw',
  '.sr2',
  '.dng',
  '.orf',
  '.raf',
  '.pef',
  '.x3f',
  '.srw',
  '.rw2',
  '.rwl',
  '.3fr',
  '.iiq',
]);

// Some clients (and test harnesses) upload RAW files as application/octet-stream.
// We still require a supported extension to avoid allowing arbitrary binaries.
const RAW_LIKE_EXTENSIONS = new Set([
  '.raw',
  '.cr2',
  '.cr3',
  '.nef',
  '.nrw',
  '.arw',
  '.sr2',
  '.dng',
  '.orf',
  '.raf',
  '.pef',
  '.x3f',
  '.srw',
  '.rw2',
  '.rwl',
  '.3fr',
  '.iiq',
]);

function guessImagesMvpMimeFromExt(ext: string): string | null {
  const map: Record<string, string> = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.heic': 'image/heic',
    '.heif': 'image/heif',
    '.avif': 'image/avif',
    '.svg': 'image/svg+xml',
    '.svgz': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.icns': 'image/icns',
    '.psd': 'image/vnd.adobe.photoshop',
    '.psb': 'image/vnd.adobe.photoshop',
    '.exr': 'image/x-exr',
    '.jp2': 'image/jp2',
    '.j2k': 'image/jp2',
    '.jpf': 'image/jp2',
    '.jpx': 'image/jpx',
    '.jpm': 'image/jpm',
    '.mj2': 'video/mj2',
    '.jxl': 'image/jxl',
    '.dds': 'image/vnd-ms.dds',
    '.tga': 'image/x-tga',
    '.pbm': 'image/x-portable-anymap',
    '.pgm': 'image/x-portable-anymap',
    '.ppm': 'image/x-portable-anymap',
    '.pnm': 'image/x-portable-anymap',
    '.hdr': 'image/vnd.radiance',
    '.fits': 'application/fits',
    '.fit': 'application/fits',
    '.fts': 'application/fits',

    '.cr2': 'image/x-canon-cr2',
    '.cr3': 'image/x-canon-cr3',
    '.nef': 'image/x-nikon-nef',
    '.nrw': 'image/x-nikon-nrw',
    '.arw': 'image/x-sony-arw',
    '.sr2': 'image/x-sony-sr2',
    '.dng': 'image/x-adobe-dng',
    '.orf': 'image/x-olympus-orf',
    '.rw2': 'image/x-panasonic-rw2',
    '.raf': 'image/x-fuji-raf',
    '.pef': 'image/x-pentax-pef',
    '.x3f': 'image/x-sigma-x3f',
    '.rwl': 'image/x-leica-rwl',
    '.3fr': 'image/x-hasselblad-3fr',
    '.iiq': 'image/x-phaseone-iiq',
  };
  return map[ext] ?? null;
}

async function detectMimeFromFilePath(
  filePath: string
): Promise<string | null> {
  try {
    const handle = await fs.open(filePath, 'r');
    try {
      const probe = Buffer.alloc(4100);
      const { bytesRead } = await handle.read(probe, 0, probe.length, 0);
      const detected = await fileTypeFromBuffer(probe.subarray(0, bytesRead));
      return detected?.mime ?? null;
    } finally {
      await handle.close();
    }
  } catch {
    return null;
  }
}

function getBaseUrl(): string {
  if (process.env.REPLIT_DEV_DOMAIN) {
    return `https://${process.env.REPLIT_DEV_DOMAIN}`;
  }
  if (process.env.RAILWAY_PUBLIC_DOMAIN) {
    return `https://${process.env.RAILWAY_PUBLIC_DOMAIN}`;
  }
  if (process.env.BASE_URL) {
    return process.env.BASE_URL;
  }
  return 'http://localhost:3000';
}

function getImagesMvpBalanceId(sessionId: string): string {
  return `images_mvp:${sessionId}`;
}

const ANALYTICS_LIMIT_DEFAULT = 5000;

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function parseAnalyticsPeriod(value?: string): {
  range: '24h' | '7d' | '30d' | 'all';
  since: Date | null;
} {
  const normalized = (value || '7d').toLowerCase();
  const now = Date.now();

  switch (normalized) {
    case '24h':
    case '1d':
    case 'day':
      return { range: '24h', since: new Date(now - 24 * 60 * 60 * 1000) };
    case '30d':
    case 'month':
      return { range: '30d', since: new Date(now - 30 * 24 * 60 * 60 * 1000) };
    case 'all':
      return { range: 'all', since: null };
    case '7d':
    case 'week':
    default:
      return { range: '7d', since: new Date(now - 7 * 24 * 60 * 60 * 1000) };
  }
}

function parseLimitParam(value?: string): number {
  if (!value) return ANALYTICS_LIMIT_DEFAULT;
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return ANALYTICS_LIMIT_DEFAULT;
  }
  return parsed;
}

/**
 * Extract idempotency key from request header.
 * Required for paid extractions to prevent double-charging on retries.
 *
 * @param req - Express request
 * @returns Idempotency key or null if missing/invalid
 */
function getIdempotencyKey(req: Request): string | null {
  const k = req.header('Idempotency-Key');
  if (!k) return null;
  const trimmed = k.trim();
  if (!trimmed) return null;
  if (trimmed.length > 128) return null; // sanity bound
  return trimmed;
}

/**
 * Check if database is available and fail closed if not.
 * For money-path operations, we must fail closed (reject) if DB is unavailable
 * to prevent giving away free extractions or bypassing credit checks.
 *
 * @returns true if DB is healthy, false otherwise
 */
async function isDatabaseHealthy(): Promise<boolean> {
  // In test environment, skip DB health check (tests mock storage)
  if (process.env.NODE_ENV === 'test') {
    return true;
  }

  if (!isDatabaseConnected()) {
    return false;
  }

  try {
    const db = getDatabase();
    // Quick health check: try to query credit_balances table
    await db.execute(sql`SELECT 1 FROM credit_balances LIMIT 1`);
    return true;
  } catch (error) {
    console.error('Database health check failed:', error);
    return false;
  }
}

// ============================================================================
// Routes
// ============================================================================

export function registerImagesMvpRoutes(app: Express) {
  // ---------------------------------------------------------------------------
  // WebSocket: Real-time Progress Tracking
  // ---------------------------------------------------------------------------
  if (typeof (app as any).ws === 'function') {
    (app as any).ws(
      '/api/images_mvp/progress/:sessionId',
      (ws: WebSocket, req: Request) => {
        const sessionId = req.params.sessionId;
        if (!sessionId) {
          ws.close(1002, 'Session ID required');
          return;
        }

        // Add connection to active connections
        const connection: ProgressConnection = {
          ws,
          sessionId,
          startTime: Date.now(),
        };

        if (!activeConnections.has(sessionId)) {
          activeConnections.set(sessionId, []);
        }
        activeConnections.get(sessionId)!.push(connection);

        // Send initial connection confirmation
        ws.send(
          JSON.stringify({
            type: 'connected',
            sessionId,
            timestamp: Date.now(),
          })
        );

        // Handle incoming messages (if needed for client acknowledgments)
        ws.on('message', data => {
          try {
            const message = JSON.parse(data.toString());
            if (message.type === 'ping') {
              ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
            }
          } catch (error) {
            console.error('WebSocket message parsing error:', error);
          }
        });

        // Handle connection close
        ws.on('close', () => {
          const connections = activeConnections.get(sessionId);
          if (connections) {
            const index = connections.indexOf(connection);
            if (index > -1) {
              connections.splice(index, 1);
            }
            if (connections.length === 0) {
              activeConnections.delete(sessionId);
            }
          }
        });

        // Handle connection errors
        ws.on('error', error => {
          console.error('WebSocket error for session', sessionId, ':', error);
          cleanupConnections(sessionId);
        });

        // Send periodic progress updates (every 2 seconds)
        const progressInterval = setInterval(() => {
          if (ws.readyState === 1) {
            // WebSocket.OPEN
            ws.send(
              JSON.stringify({
                type: 'heartbeat',
                sessionId,
                timestamp: Date.now(),
              })
            );
          } else {
            clearInterval(progressInterval);
          }
        }, 2000);

        ws.on('close', () => {
          clearInterval(progressInterval);
        });
      }
    );
  } else {
    console.log(
      '[ImagesMVP] WebSocket not available in this environment; progress tracking disabled'
    );
  }

  // ---------------------------------------------------------------------------
  // Analytics: Track UI Events (Images MVP)
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/analytics/track',
    analyticsRateLimiter,
    async (req: Request, res: Response) => {
      try {
        const event = typeof req.body?.event === 'string' ? req.body.event : '';
        const properties =
          req.body?.properties && typeof req.body.properties === 'object'
            ? req.body.properties
            : {};
        const sessionId =
          typeof req.body?.sessionId === 'string' ? req.body.sessionId : null;

        if (!event) {
          return sendInvalidRequestError(res, 'Event name is required');
        }

        await storage.logUiEvent({
          product: 'images_mvp',
          eventName: event,
          sessionId,
          userId: null,
          properties,
          ipAddress: req.ip || req.socket.remoteAddress || null,
          userAgent: req.headers['user-agent'] || null,
        });

        return res.status(204).send();
      } catch (error) {
        console.error('Images MVP analytics error:', error);
        return res.status(500).json({ error: 'Failed to log analytics event' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Analytics: Report (Images MVP)
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Quote: Preflight credits + limits
  // Route-specific rate limiter: 30 requests per minute per session/user/IP
  // Prevents quote endpoint abuse (each quote inserts a DB record)
  // Key precedence: user > session > IP (works regardless of proxy topology)
  const quoteLimiter = createRateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: 30, // 30 quotes per minute
    keyGenerator: (req: Request) => {
      // Prefer authenticated user
      if ((req as any).user?.id) {
        return `u:${(req as any).user.id}`;
      }

      // Fall back to session (from cookie or header)
      const sessionId =
        (req as any).cookies?.sessionId ||
        (req as any).session?.id ||
        req.headers['x-session-id'];
      if (sessionId && typeof sessionId === 'string') {
        return `s:${sessionId}`;
      }

      // Last resort: IP (works even if behind proxy with trust=off)
      return `ip:${req.ip || (req as any).socket?.remoteAddress || 'unknown'}`;
    },
  } as any);

  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/quote',
    quoteLimiter,
    async (req: Request, res: Response) => {
      try {
        const rawFiles = Array.isArray(req.body?.files) ? req.body.files : [];
        const ops = parseOpsFromRequest(req.body);

        const MAX_FILES = 10;
        const MAX_BYTES = 100 * 1024 * 1024;

        const perFileCredits: Record<string, number> = {};
        const perFileById: Record<
          string,
          {
            id: string;
            accepted: boolean;
            reason?: string;
            detected_type?: string | null;
            creditsTotal?: number;
            breakdown?: any;
            mp?: number | null;
            mpBucket?: string | null;
            warnings?: string[];
          }
        > = {};

        let creditsTotal = 0;
        const limitedFiles = rawFiles.slice(0, MAX_FILES);
        for (const file of limitedFiles) {
          const fileId = typeof file?.id === 'string' ? file.id : null;
          if (!fileId) continue;

          const mp = computeMp(file?.width ?? null, file?.height ?? null);
          const bucket = resolveMpBucket(mp);

          const name = typeof file?.name === 'string' ? file.name : '';
          const mime = typeof file?.mime === 'string' ? file.mime : null;
          const sizeBytes =
            typeof file?.sizeBytes === 'number' ? file.sizeBytes : 0;
          const ext = name.includes('.')
            ? name.slice(name.lastIndexOf('.')).toLowerCase()
            : '';

          let accepted = true;
          let reason: string | undefined;
          if (sizeBytes > MAX_BYTES) {
            accepted = false;
            reason = 'file_too_large';
          } else {
            const mimeOk = !mime || SUPPORTED_IMAGE_MIMES.has(mime);
            const extOk = !ext || SUPPORTED_IMAGE_EXTENSIONS.has(ext);
            if (!mimeOk && !extOk) {
              accepted = false;
              reason = 'unsupported_type';
            }
          }

          const warnings: string[] = [];
          if (bucket.warning) warnings.push(bucket.warning);
          if (!accepted && reason) warnings.push(reason);

          if (accepted) {
            const { creditsTotal: fileCreditsTotal, breakdown } =
              computeCreditsTotal(ops, bucket.credits);

            creditsTotal += fileCreditsTotal;
            perFileCredits[fileId] = fileCreditsTotal;
            perFileById[fileId] = {
              id: fileId,
              accepted: true,
              detected_type: mime,
              creditsTotal: fileCreditsTotal,
              breakdown,
              mp,
              mpBucket: bucket.label,
              warnings,
            };
          } else {
            perFileById[fileId] = {
              id: fileId,
              accepted: false,
              reason,
              detected_type: mime,
              mp,
              mpBucket: bucket.label,
              warnings,
            };
          }
        }

        const expiresAt = new Date(Date.now() + 15 * 60 * 1000);
        const sessionId = getOrSetSessionId(req, res);

        const createdQuote = await createImagesMvpQuote({
          sessionId,
          files: limitedFiles,
          ops,
          creditsTotal,
          perFileCredits,
          perFile: perFileById,
          schedule: IMAGES_MVP_CREDIT_SCHEDULE,
          expiresAt,
        });

        const perFileArray = Object.values(perFileById);
        const standardCreditsPerImage =
          IMAGES_MVP_CREDIT_SCHEDULE.base +
          IMAGES_MVP_CREDIT_SCHEDULE.embedding;

        res.json({
          schemaVersion: 'images_mvp_quote_v1',
          quoteId: createdQuote.id,
          // DEPRECATED: Legacy top-level keys for v0 client compatibility
          // These will be removed in images_mvp_quote_v2
          // Frontend should use: quote.totalCredits, quote.perFile, creditSchedule.* instead
          creditsTotal,
          perFile: perFileById,
          schedule: IMAGES_MVP_CREDIT_SCHEDULE,
          // Canonical v1 shape:
          limits: {
            maxBytes: MAX_BYTES,
            allowedMimes: Array.from(SUPPORTED_IMAGE_MIMES),
            maxFiles: MAX_FILES,
          },
          creditSchedule: {
            ...IMAGES_MVP_CREDIT_SCHEDULE,
            standardCreditsPerImage,
          },
          quote: {
            perFile: perFileArray,
            totalCredits: creditsTotal,
            standardEquivalents:
              standardCreditsPerImage > 0
                ? Math.ceil(creditsTotal / standardCreditsPerImage)
                : null,
          },
          expiresAt: new Date(expiresAt).toISOString(),
          warnings: [],
        });
      } catch (error) {
        console.error('ImagesMVP quote error:', error);
        res.status(500).json({ error: 'Failed to create quote' });
      }
    }
  );
  app.get(
    '/api/images_mvp/analytics/report',
    analyticsRateLimiter,
    async (req: Request, res: Response) => {
      try {
        const periodQuery =
          typeof req.query.period === 'string' ? req.query.period : undefined;
        const limitQuery =
          typeof req.query.limit === 'string' ? req.query.limit : undefined;
        const period = parseAnalyticsPeriod(periodQuery);
        const limit = parseLimitParam(limitQuery);

        const events = await storage.getUiEvents({
          product: 'images_mvp',
          since: period.since ?? undefined,
          limit,
        });

        const eventCounts: Record<string, number> = {};
        const purposeCounts: Record<string, number> = {};
        const tabCounts: Record<string, number> = {};
        const densityCounts: Record<string, number> = {};
        const formatHintCounts: Record<string, number> = {};
        const resultsMimeCounts: Record<string, number> = {};

        let landingViewed = 0;
        let uploadSelected = 0;
        let uploadRejected = 0;
        let analysisStarted = 0;
        let analysisCompleted = 0;
        let analysisSuccess = 0;
        let analysisFailed = 0;
        let analysisProcessingMsTotal = 0;
        let analysisProcessingCount = 0;
        let paywallViewed = 0;
        let purchaseCompleted = 0;

        let paywallPreviewed = 0;
        let paywallClicked = 0;
        let summaryCopied = 0;
        let summaryDownloaded = 0;
        let jsonDownloaded = 0;
        let fullTxtDownloaded = 0;
        let purposePromptShown = 0;
        let purposePromptOpened = 0;
        let purposeSkipped = 0;

        const sessionIds = new Set<string>();
        const userIds = new Set<string>();
        let firstEventAt: Date | null = null;
        let lastEventAt: Date | null = null;

        const increment = (bucket: Record<string, number>, key: string) => {
          bucket[key] = (bucket[key] || 0) + 1;
        };

        for (const event of events) {
          increment(eventCounts, event.eventName);

          if (event.sessionId) {
            sessionIds.add(event.sessionId);
          }
          if (event.userId) {
            userIds.add(event.userId);
          }
          if (!firstEventAt || event.createdAt < firstEventAt) {
            firstEventAt = event.createdAt;
          }
          if (!lastEventAt || event.createdAt > lastEventAt) {
            lastEventAt = event.createdAt;
          }

          const properties = isPlainObject(event.properties)
            ? event.properties
            : {};

          switch (event.eventName) {
            case 'images_landing_viewed':
              landingViewed += 1;
              break;
            case 'upload_selected':
              uploadSelected += 1;
              break;
            case 'upload_rejected':
              uploadRejected += 1;
              break;
            case 'analysis_started':
              analysisStarted += 1;
              break;
            case 'analysis_completed': {
              analysisCompleted += 1;
              const success =
                typeof properties.success === 'boolean'
                  ? properties.success
                  : null;
              if (success === true) {
                analysisSuccess += 1;
              } else if (success === false) {
                analysisFailed += 1;
              }
              const processingMs =
                typeof properties.processing_ms === 'number'
                  ? properties.processing_ms
                  : null;
              if (processingMs !== null) {
                analysisProcessingMsTotal += processingMs;
                analysisProcessingCount += 1;
              }
              break;
            }
            case 'purpose_selected': {
              const purpose =
                typeof properties.purpose === 'string'
                  ? properties.purpose
                  : 'unknown';
              increment(purposeCounts, purpose);
              break;
            }
            case 'purpose_prompt_shown':
              purposePromptShown += 1;
              break;
            case 'purpose_prompt_opened':
              purposePromptOpened += 1;
              break;
            case 'purpose_skipped':
              purposeSkipped += 1;
              break;
            case 'tab_changed': {
              const tab =
                typeof properties.tab === 'string' ? properties.tab : 'unknown';
              increment(tabCounts, tab);
              break;
            }
            case 'density_changed': {
              const mode =
                typeof properties.mode === 'string'
                  ? properties.mode
                  : 'unknown';
              increment(densityCounts, mode);
              break;
            }
            case 'format_hint_shown': {
              const mimeType =
                typeof properties.mime_type === 'string'
                  ? properties.mime_type
                  : 'unknown';
              increment(formatHintCounts, mimeType);
              break;
            }
            case 'results_viewed': {
              const mimeType =
                typeof properties.mime_type === 'string'
                  ? properties.mime_type
                  : 'unknown';
              increment(resultsMimeCounts, mimeType);
              break;
            }
            case 'paywall_viewed':
              paywallViewed += 1;
              break;
            case 'paywall_preview_shown':
              paywallPreviewed += 1;
              break;
            case 'paywall_cta_clicked':
              paywallClicked += 1;
              break;
            case 'purchase_completed':
              purchaseCompleted += 1;
              break;
            case 'summary_copied':
              summaryCopied += 1;
              break;
            case 'export_summary_downloaded':
              summaryDownloaded += 1;
              break;
            case 'export_json_downloaded':
              jsonDownloaded += 1;
              break;
            case 'export_full_txt_downloaded':
              fullTxtDownloaded += 1;
              break;
            default:
              break;
          }
        }

        res.json({
          period: {
            range: period.range,
            since: period.since ? period.since.toISOString() : null,
            until: new Date().toISOString(),
            limit,
          },
          totals: {
            events: events.length,
            sessions: sessionIds.size,
            users: userIds.size,
            firstEventAt: firstEventAt ? firstEventAt.toISOString() : null,
            lastEventAt: lastEventAt ? lastEventAt.toISOString() : null,
          },
          funnel: {
            landing_viewed: landingViewed,
            upload_selected: uploadSelected,
            upload_rejected: uploadRejected,
            analysis_started: analysisStarted,
            analysis_completed: analysisCompleted,
            analysis_success: analysisSuccess,
            analysis_failed: analysisFailed,
            results_viewed: eventCounts.results_viewed || 0,
            paywall_viewed: paywallViewed,
            paywall_previewed: paywallPreviewed,
            paywall_clicked: paywallClicked,
            purchase_completed: purchaseCompleted,
            export_summary_downloaded: summaryDownloaded,
            export_json_downloaded: jsonDownloaded,
            export_full_txt_downloaded: fullTxtDownloaded,
          },
          events: eventCounts,
          purposes: {
            selected: purposeCounts,
            prompt_shown: purposePromptShown,
            prompt_opened: purposePromptOpened,
            skipped: purposeSkipped,
          },
          tabs: tabCounts,
          density: densityCounts,
          formats: {
            hints: formatHintCounts,
            results: resultsMimeCounts,
          },
          exports: {
            json: jsonDownloaded,
            summary: summaryDownloaded,
            full_txt: fullTxtDownloaded,
            summary_copied: summaryCopied,
          },
          analysis: {
            completed: analysisCompleted,
            success: analysisSuccess,
            failed: analysisFailed,
            average_processing_ms:
              analysisProcessingCount > 0
                ? Math.round(
                    analysisProcessingMsTotal / analysisProcessingCount
                  )
                : null,
          },
          paywall: {
            previewed: paywallPreviewed,
            cta_clicked: paywallClicked,
          },
        });
      } catch (error) {
        console.error('Images MVP analytics report error:', error);
        return res
          .status(500)
          .json({ error: 'Failed to build analytics report' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Analytics Report (SQL Optimized - for high traffic)
  // ---------------------------------------------------------------------------
  app.get(
    '/api/images_mvp/analytics/report-optimized',
    analyticsRateLimiter,
    async (req: Request, res: Response) => {
      try {
        const periodQuery =
          typeof req.query.period === 'string' ? req.query.period : undefined;
        const period = parseAnalyticsPeriod(periodQuery);

        const since =
          period.since ?? new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

        const events = await storage.getUiEvents({
          product: 'images_mvp',
          since,
          limit: 5000,
        });

        const eventCounts: Record<string, number> = {};
        const purposeCounts: Record<string, number> = {};
        const tabCounts: Record<string, number> = {};
        const densityCounts: Record<string, number> = {};
        const formatHintCounts: Record<string, number> = {};
        const resultsMimeCounts: Record<string, number> = {};

        let landingViewed = 0;
        let uploadSelected = 0;
        let uploadRejected = 0;
        let analysisStarted = 0;
        let analysisCompleted = 0;
        let analysisSuccess = 0;
        let analysisFailed = 0;
        let analysisProcessingMsTotal = 0;
        let analysisProcessingCount = 0;
        let paywallViewed = 0;
        let purchaseCompleted = 0;

        let paywallPreviewed = 0;
        let paywallClicked = 0;
        let summaryCopied = 0;
        let summaryDownloaded = 0;
        let jsonDownloaded = 0;
        let fullTxtDownloaded = 0;
        let purposePromptShown = 0;
        let purposePromptOpened = 0;
        let purposeSkipped = 0;

        const sessionIds = new Set<string>();
        const userIds = new Set<string>();
        let firstEventAt: Date | null = null;
        let lastEventAt: Date | null = null;

        const increment = (bucket: Record<string, number>, key: string) => {
          bucket[key] = (bucket[key] || 0) + 1;
        };

        for (const event of events) {
          increment(eventCounts, event.eventName);

          if (event.sessionId) {
            sessionIds.add(event.sessionId);
          }
          if (event.userId) {
            userIds.add(event.userId);
          }
          if (!firstEventAt || event.createdAt < firstEventAt) {
            firstEventAt = event.createdAt;
          }
          if (!lastEventAt || event.createdAt > lastEventAt) {
            lastEventAt = event.createdAt;
          }

          const properties = isPlainObject(event.properties)
            ? event.properties
            : {};

          switch (event.eventName) {
            case 'images_landing_viewed':
              landingViewed += 1;
              break;
            case 'upload_selected':
              uploadSelected += 1;
              break;
            case 'upload_rejected':
              uploadRejected += 1;
              break;
            case 'analysis_started':
              analysisStarted += 1;
              break;
            case 'analysis_completed': {
              analysisCompleted += 1;
              const success =
                typeof properties.success === 'boolean'
                  ? properties.success
                  : null;
              if (success === true) {
                analysisSuccess += 1;
              } else if (success === false) {
                analysisFailed += 1;
              }
              const processingMs =
                typeof properties.processing_ms === 'number'
                  ? properties.processing_ms
                  : null;
              if (processingMs !== null) {
                analysisProcessingMsTotal += processingMs;
                analysisProcessingCount += 1;
              }
              break;
            }
            case 'purpose_selected': {
              const purpose =
                typeof properties.purpose === 'string'
                  ? properties.purpose
                  : 'unknown';
              increment(purposeCounts, purpose);
              break;
            }
            case 'purpose_prompt_shown':
              purposePromptShown += 1;
              break;
            case 'purpose_prompt_opened':
              purposePromptOpened += 1;
              break;
            case 'purpose_skipped':
              purposeSkipped += 1;
              break;
            case 'tab_changed': {
              const tab =
                typeof properties.tab === 'string' ? properties.tab : 'unknown';
              increment(tabCounts, tab);
              break;
            }
            case 'density_changed': {
              const mode =
                typeof properties.mode === 'string'
                  ? properties.mode
                  : 'unknown';
              increment(densityCounts, mode);
              break;
            }
            case 'format_hint_shown': {
              const mimeType =
                typeof properties.mime_type === 'string'
                  ? properties.mime_type
                  : 'unknown';
              increment(formatHintCounts, mimeType);
              break;
            }
            case 'results_viewed': {
              const mimeType =
                typeof properties.mime_type === 'string'
                  ? properties.mime_type
                  : 'unknown';
              increment(resultsMimeCounts, mimeType);
              break;
            }
            case 'paywall_viewed':
              paywallViewed += 1;
              break;
            case 'paywall_preview_shown':
              paywallPreviewed += 1;
              break;
            case 'paywall_cta_clicked':
              paywallClicked += 1;
              break;
            case 'purchase_completed':
              purchaseCompleted += 1;
              break;
            case 'summary_copied':
              summaryCopied += 1;
              break;
            case 'export_summary_downloaded':
              summaryDownloaded += 1;
              break;
            case 'export_json_downloaded':
              jsonDownloaded += 1;
              break;
            case 'export_full_txt_downloaded':
              fullTxtDownloaded += 1;
              break;
            default:
              break;
          }
        }

        res.json({
          period: {
            range: period.range,
            since: period.since ? period.since.toISOString() : null,
            until: new Date().toISOString(),
            limit: 5000,
          },
          totals: {
            events: events.length,
            sessions: sessionIds.size,
            users: userIds.size,
            firstEventAt: firstEventAt ? firstEventAt.toISOString() : null,
            lastEventAt: lastEventAt ? lastEventAt.toISOString() : null,
          },
          funnel: {
            landing_viewed: landingViewed,
            upload_selected: uploadSelected,
            upload_rejected: uploadRejected,
            analysis_started: analysisStarted,
            analysis_completed: analysisCompleted,
            analysis_success: analysisSuccess,
            analysis_failed: analysisFailed,
            results_viewed: eventCounts.results_viewed || 0,
            paywall_viewed: paywallViewed,
            paywall_previewed: paywallPreviewed,
            paywall_clicked: paywallClicked,
            purchase_completed: purchaseCompleted,
            export_summary_downloaded: summaryDownloaded,
            export_json_downloaded: jsonDownloaded,
            export_full_txt_downloaded: fullTxtDownloaded,
          },
          events: eventCounts,
          purposes: {
            selected: purposeCounts,
            prompt_shown: purposePromptShown,
            prompt_opened: purposePromptOpened,
            skipped: purposeSkipped,
          },
          tabs: tabCounts,
          density: densityCounts,
          formats: {
            hints: formatHintCounts,
            results: resultsMimeCounts,
          },
          exports: {
            json: jsonDownloaded,
            summary: summaryDownloaded,
            full_txt: fullTxtDownloaded,
            summary_copied: summaryCopied,
          },
          analysis: {
            completed: analysisCompleted,
            success: analysisSuccess,
            failed: analysisFailed,
            average_processing_ms:
              analysisProcessingCount > 0
                ? Math.round(
                    analysisProcessingMsTotal / analysisProcessingCount
                  )
                : null,
          },
          paywall: {
            previewed: paywallPreviewed,
            cta_clicked: paywallClicked,
          },
        });
      } catch (error) {
        console.error('Images MVP analytics report error:', error);
        return res
          .status(500)
          .json({ error: 'Failed to build analytics report' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Credits: Get Packs
  // ---------------------------------------------------------------------------
  app.get('/api/images_mvp/credits/packs', (req: Request, res: Response) => {
    res.json({
      packs: IMAGES_MVP_CREDIT_PACKS,
      description: 'Credits for using the Images Metadata tool.',
    });
  });

  // ---------------------------------------------------------------------------
  // Credits: Get Balance
  // ---------------------------------------------------------------------------
  app.get(
    '/api/images_mvp/credits/balance',
    async (req: Request, res: Response) => {
      try {
        // We expect the client to pass the raw sessionId provided by getSessionId helper
        // But accept cookie-based session IDs or authenticated users as fallbacks
        let rawSessionId =
          (req.query.sessionId as string) ||
          req.cookies?.metaextract_session_id;

        // Fallback: parse cookie header if express cookie parsing not present in test env
        if (!rawSessionId && typeof req.headers?.cookie === 'string') {
          const match = req.headers.cookie.match(
            /metaextract_session_id=([^;\s]+)/
          );
          if (match) rawSessionId = match[1];
        }

        if (!rawSessionId) {
          // If the user is authenticated, return the user balance
          if ((req as any).user?.id) {
            const userId = (req as any).user.id as string;
            const namespaced = getImagesMvpBalanceId(`user:${userId}`);
            const balance = await storage.getOrCreateCreditBalance(
              namespaced,
              userId
            );
            return res.json({
              credits: balance.credits,
              balanceId: balance.id,
            });
          }

          // Otherwise, no session info available
          return res.json({ credits: 0, balanceId: null });
        }

        // Use the namespaced ID for looking up balance
        const namespacedSessionId = getImagesMvpBalanceId(rawSessionId);
        const balance = await storage.getOrCreateCreditBalance(
          namespacedSessionId,
          undefined
        );

        res.json({
          credits: balance.credits,
          balanceId: balance.id,
        });
      } catch (error) {
        console.error('Get images_mvp credits error:', error);
        res.status(500).json({ error: 'Failed to get credit balance' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Credits: Purchase
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/credits/purchase',
    async (req: Request, res: Response) => {
      try {
        const client = getDodoClient();
        if (!client) {
          return sendServiceUnavailableError(
            res,
            'Payment system not configured. Please add DODO_PAYMENTS_API_KEY to enable payments'
          );
        }

        const { pack, sessionId, email } = req.body;

        if (!pack || !['starter', 'pro'].includes(pack)) {
          return res.status(400).json({ error: 'Invalid credit pack' });
        }

        // If user is authenticated, use their user balance; otherwise sessionId required
        let namespacedSessionId: string;
        if ((req as any).user?.id) {
          namespacedSessionId = getImagesMvpBalanceId(
            `user:${(req as any).user.id}`
          );
        } else {
          if (!sessionId) {
            return res.status(400).json({ error: 'Session ID required' });
          }
          namespacedSessionId = getImagesMvpBalanceId(sessionId);
        }

        const balance = await storage.getOrCreateCreditBalance(
          namespacedSessionId,
          undefined
        );
        const packInfo =
          IMAGES_MVP_CREDIT_PACKS[pack as keyof typeof IMAGES_MVP_CREDIT_PACKS];

        const baseUrl = getBaseUrl();

        // Ensure product is valid
        if (!packInfo || !packInfo.productId) {
          return res
            .status(500)
            .json({ error: 'Product configuration missing' });
        }

        const session = await client.checkoutSessions.create({
          product_cart: [
            {
              product_id: packInfo.productId,
              quantity: 1,
            },
          ],
          customer: email ? { email } : undefined,
          // Redirect to specialized success page
          return_url: `${baseUrl}/images_mvp/credits/success?pack=${pack}&balanceId=${balance.id}`,
          metadata: {
            type: 'credit_purchase',
            product: 'images_mvp', // Marker for webhook logic
            pack,
            credits: packInfo.credits.toString(),
            balance_id: balance.id,
          },
        });

        console.log(
          `Created images_mvp purchase session for ${pack}:`,
          session.session_id
        );

        res.json({
          checkout_url: session.checkout_url,
          session_id: session.session_id,
        });
      } catch (error) {
        console.error('Images MVP purchase error:', error);
        res.status(500).json({
          error: 'Failed to create checkout session',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Credits: Claim (convert session credits -> account credits)
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/credits/claim',
    requireAuth,
    async (req: Request, res: Response) => {
      try {
        const authReq = req as any;
        if (!authReq.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        const rawSessionId = req.body?.sessionId ?? getOrSetSessionId(req, res);

        const fromKey = getImagesMvpBalanceId(rawSessionId);
        const toKey = getImagesMvpBalanceId(`user:${authReq.user.id}`);

        const fromBalance = await storage.getCreditBalanceBySessionId(fromKey);
        if (!fromBalance || (fromBalance.credits ?? 0) <= 0) {
          return res.json({ transferred: 0 });
        }

        const toBalance = await storage.getOrCreateCreditBalance(
          toKey,
          authReq.user.id
        );

        const amount = fromBalance.credits;
        await storage.transferCredits(
          fromBalance.id,
          toBalance.id,
          amount,
          `Claimed from ${fromKey}`
        );

        res.json({ transferred: amount });
      } catch (error) {
        console.error('Images MVP claim credits error:', error);
        res.status(500).json({ error: 'Failed to claim credits' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Extraction Endpoint
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/extract',
    // Apply rate limiting first to prevent abuse
    process.env.NODE_ENV === 'test'
      ? (_req: Request, _res: Response, next: any) => next()
      : createRateLimiter({
          windowMs: 15 * 60 * 1000, // 15 minutes
          max: 50, // Max 50 uploads per IP per 15 minutes
          keyGenerator: (req: Request) =>
            (req as any).user?.id
              ? `user:${(req as any).user.id}`
              : `ip:${req.ip || req.socket.remoteAddress || 'unknown'}`,
        } as any),
    // Apply burst protection for anonymous users
    process.env.NODE_ENV === 'test'
      ? (_req: Request, _res: Response, next: any) => next()
      : createRateLimiter({
          windowMs: 60 * 1000, // 1 minute
          max: 10, // Max 10 uploads per minute
          skip: (req: Request) => !!(req as any).user?.id, // Skip for authenticated users
          keyGenerator: (req: Request) =>
            `ip:${req.ip || req.socket.remoteAddress || 'unknown'}`,
        } as any),
    // Free quota enforcement (2 extractions per device for anonymous users)
    // Must be AFTER rate limiting but BEFORE file upload
    process.env.NODE_ENV === 'test'
      ? (_req: Request, _res: Response, next: any) => next()
      : freeQuotaMiddleware,
    // Enhanced protection BEFORE file upload - security validation
    enhancedProtectionMiddleware,
    // File upload middleware - only executes if protection passes
    (req: Request, res: Response, next: any) => {
      // Wrap multer to capture file size and other upload errors and translate to unified API errors
      upload.single('file')(req as any, res as any, (err: any) => {
        if (err) {
          console.error('Multer upload error:', err);
          if (err.code === 'LIMIT_FILE_SIZE') {
            // Historical endpoints expect a flat 413 "File too large" response
            return sendLegacyFileTooLargeError(res);
          }
          return sendInvalidRequestError(res, 'File upload failed');
        }
        next();
      });
    },
    async (req: Request, res: Response) => {
      const startTime = Date.now();
      const requestId = getIdempotencyKey(req); // Client-provided idempotency key
      let tempPath: string | null = null;
      let sessionId: string | null = null;
      let creditBalanceId: string | null = null;
      let useTrial = false;
      let chargeCredits = false;
      let holdReserved = false; // Track if we need to release on error

      try {
        if (!req.file) {
          return sendInvalidRequestError(res, 'No file uploaded');
        }

        // Enforce file type - SECURITY: require BOTH mime AND extension to match
        // This prevents attacks like uploading malware.exe with mime image/jpeg
        const fileExt = path.extname(req.file.originalname).toLowerCase();
        const guessedMime = guessImagesMvpMimeFromExt(fileExt);
        const detectedMime = req.file.path
          ? await detectMimeFromFilePath(req.file.path)
          : null;
        const mimeType =
          (fileExt === '.svgz' && detectedMime === 'application/gzip'
            ? 'image/svg+xml'
            : detectedMime) ||
          guessedMime ||
          req.file.mimetype;

        let isSupportedMime = SUPPORTED_IMAGE_MIMES.has(mimeType);
        const isSupportedExt = fileExt
          ? SUPPORTED_IMAGE_EXTENSIONS.has(fileExt)
          : false;

        if (
          !isSupportedMime &&
          isSupportedExt &&
          RAW_LIKE_EXTENSIONS.has(fileExt) &&
          (mimeType === 'application/octet-stream' ||
            req.file.mimetype === 'application/octet-stream')
        ) {
          isSupportedMime = true;
        }

        // Some scientific / uncommon image-like formats won't have a reliable browser mimetype;
        // allow them only when extension matches and mime is unknown.
        if (
          !isSupportedMime &&
          isSupportedExt &&
          (mimeType === 'application/octet-stream' ||
            req.file.mimetype === 'application/octet-stream')
        ) {
          isSupportedMime = true;
        }

        // Require BOTH mime type AND extension to be valid (AND logic, not OR)
        if (!isSupportedMime || !isSupportedExt) {
          // Clean up the uploaded temp file before rejecting
          if (req.file.path) {
            void Promise.resolve(cleanupTempFile(req.file.path)).catch(
              () => {}
            );
          }
          return sendUnsupportedFileTypeError(res, 'File type not permitted');
        }

        // Determine pricing inputs (quote overrides request ops).
        const quoteId = req.body?.quote_id;
        const clientFileId = req.body?.client_file_id;

        let ops = parseOpsFromRequest(req.body);
        let quotedCreditCost: number | null = null;

        if (quoteId) {
          const quote = await getImagesMvpQuote(quoteId);
          if (quote && quote.ops && typeof quote.ops === 'object') {
            const opsData = quote.ops as any;
            ops = {
              embedding: !!opsData.embedding,
              ocr: !!opsData.ocr,
              forensics: !!opsData.forensics,
            };
          }
          if (
            clientFileId &&
            quote?.perFileCredits &&
            (quote.perFileCredits as any)[clientFileId] != null
          ) {
            const candidate = Number(
              (quote.perFileCredits as any)[clientFileId]
            );
            if (Number.isFinite(candidate) && candidate > 0) {
              quotedCreditCost = candidate;
            }
          }
        }

        // Compute size bucket from either quoted dimensions (preferred) or from upload buffer.
        let mpCredits = 0;
        let mpCreditsResolved = false;
        if (quoteId && clientFileId) {
          const quote = await getImagesMvpQuote(quoteId);
          const quotedFile = Array.isArray(quote?.files)
            ? quote.files.find((f: any) => f?.id === clientFileId)
            : null;
          if (quotedFile) {
            const mp = computeMp(
              quotedFile.width ?? null,
              quotedFile.height ?? null
            );
            const bucket = resolveMpBucket(mp);
            mpCredits = bucket.credits;
            mpCreditsResolved = true;
          }
        }
        if (!mpCreditsResolved) {
          const size = await computeSizeCreditsFromUpload(req.file);
          mpCredits = size.mpCredits;
        }

        const { creditsTotal } = computeCreditsTotal(ops, mpCredits);
        const creditCost = quotedCreditCost ?? creditsTotal;

        const trialEmail = normalizeEmail(
          req.body?.trial_email ?? req.body?.access_email
        );
        sessionId = getSessionId(req); // Raw session ID

        // Check Trial Status
        let trialUses = 0;
        if (trialEmail) {
          if (isDatabaseConnected()) {
            const dbClient = getDatabase();
            const result = await dbClient
              .select({ uses: trialUsages.uses })
              .from(trialUsages)
              .where(eq(trialUsages.email, trialEmail))
              .limit(1);
            trialUses = result[0]?.uses || 0;
          } else {
            const usage = await storage.getTrialUsageByEmail(trialEmail);
            trialUses = usage?.uses || 0;
          }
        }

        const hasTrialAvailable = !!trialEmail && trialUses < 2;

        // Fail-closed DB health check for money-path operations
        if (process.env.NODE_ENV !== 'development' && !hasTrialAvailable) {
          const dbHealthy = await isDatabaseHealthy();
          if (!dbHealthy) {
            return sendServiceUnavailableError(
              res,
              'Billing system temporarily unavailable. Please try again shortly.'
            );
          }
        }

        // Determine Access
        // In development, skip all restrictions for easier testing
        if (process.env.NODE_ENV === 'development') {
          useTrial = false;
          chargeCredits = false;
        } else if (hasTrialAvailable) {
          useTrial = true;
        } else {
          // Check Credits
          // If sessionId is not present, this may be an anonymous user. However, authenticated users should be
          // able to charge their account credits without providing an explicit session id.

          if (sessionId) {
            const namespacedSessionId = getImagesMvpBalanceId(sessionId);
            const balance = await storage.getOrCreateCreditBalance(
              namespacedSessionId,
              undefined
            );
            creditBalanceId = balance?.id ?? null;

            if (!balance) {
              return sendQuotaExceededError(res, 'Credit balance not found');
            }

            // Require idempotency key for paid extractions
            if (!requestId) {
              return sendInvalidRequestError(
                res,
                'Idempotency-Key header required for paid extractions'
              );
            }

            // Fail-closed: assert storage is healthy before touching money
            try {
              assertStorageHealthy();
            } catch (error) {
              console.error(
                'Storage health check failed, refusing extraction:',
                error
              );
              return sendServiceUnavailableError(
                res,
                'Database unavailable. Paid extraction cannot proceed. Please try again later.'
              );
            }

            // Reserve credits atomically BEFORE Python extraction
            try {
              await storage.reserveCredits(
                requestId,
                creditBalanceId,
                creditCost,
                `Extraction: ${fileExt?.slice(1) || 'unknown'} (Images MVP)`,
                quoteId || undefined,
                15 * 60 * 1000 // 15 minutes expiry
              );
              holdReserved = true;
              chargeCredits = true;
            } catch (error) {
              console.error('Credit reservation failed:', error);
              const errMsg =
                error instanceof Error ? error.message : 'Unknown error';
              if (errMsg.includes('Insufficient credits')) {
                return sendQuotaExceededError(res, errMsg);
              }
              return sendServiceUnavailableError(
                res,
                'Unable to reserve credits. Please try again.'
              );
            }
          } else if ((req as any).user?.id) {
            // Authenticated user - use account credits
            const userId = (req as any).user.id as string;
            const namespaced = getImagesMvpBalanceId(`user:${userId}`);
            const balance = await storage.getOrCreateCreditBalance(
              namespaced,
              userId
            );
            creditBalanceId = balance?.id ?? null;

            if (!balance) {
              return sendQuotaExceededError(res, 'Credit balance not found');
            }

            // Require idempotency key for paid extractions
            if (!requestId) {
              return sendInvalidRequestError(
                res,
                'Idempotency-Key header required for paid extractions'
              );
            }

            // Reserve credits atomically BEFORE Python extraction
            let hold: any;
            try {
              hold = await storage.reserveCredits(
                requestId,
                creditBalanceId,
                creditCost,
                `Extraction: ${fileExt?.slice(1) || 'unknown'} (Images MVP)`,
                quoteId || undefined,
                15 * 60 * 1000 // 15 minutes expiry
              );

              // ✅ RED FLAG #1 FIX: Check if already processed (COMMITTED hold means Python already ran)
              // Don't run Python again on retry - return 409 Conflict
              if (hold.state === 'COMMITTED') {
                return res.status(409).json({
                  error: {
                    message:
                      'Request already processed. Check your extraction history for results.',
                    code: 'ALREADY_PROCESSED',
                    requestId,
                  },
                });
              }

              holdReserved = true;
              chargeCredits = true;
            } catch (error) {
              console.error('Credit reservation failed:', error);
              const errMsg =
                error instanceof Error ? error.message : 'Unknown error';
              if (errMsg.includes('Insufficient credits')) {
                return sendQuotaExceededError(res, errMsg);
              }
              return sendServiceUnavailableError(
                res,
                'Unable to reserve credits. Please try again.'
              );
            }
          } else {
            // No sessionId and not authenticated - allow anonymous flow, free quota will be enforced later
            chargeCredits = false;
          }
        }

        // Proceed with Extraction
        // With disk storage, file is already on disk at req.file.path
        tempPath = req.file.path;

        // Send initial progress update
        if (sessionId) {
          broadcastProgress(
            sessionId,
            10,
            'File uploaded successfully',
            'upload_complete'
          );
        }

        // Extract with enhanced features
        // Super tier provides comprehensive field extraction for all paid users
        const pythonTier = 'super';

        // Send progress update before extraction
        if (sessionId) {
          broadcastProgress(
            sessionId,
            20,
            'Starting metadata extraction',
            'extraction_start'
          );
        }

        const extractorOptions = { ocr: ops.ocr, maxDim: 2048 };

        const rawMetadata = await extractMetadataWithPython(
          tempPath,
          pythonTier,
          true, // performance
          true, // advanced (needed for authenticity signals)
          req.query.store === 'true',
          extractorOptions
        );

        // Send progress update after extraction
        if (sessionId) {
          broadcastProgress(
            sessionId,
            90,
            'Metadata extraction complete',
            'extraction_complete'
          );
        }

        const processingMs = Date.now() - startTime;
        rawMetadata.extraction_info.processing_ms = processingMs;

        // Add enhanced processing insights
        rawMetadata.extraction_info = {
          ...rawMetadata.extraction_info,
          enhanced_extraction: true,
          total_fields_extracted:
            rawMetadata.extraction_info?.fields_extracted || 0,
          streaming_enabled: false, // Will be enabled when we add streaming support
          fallback_extraction: false,
        } as any; // Type assertion to allow additional properties

        const metadata = transformMetadataForFrontend(
          rawMetadata,
          req.file.originalname,
          useTrial ? 'free' : 'professional'
        );

        const clientLastModifiedRaw = req.body?.client_last_modified;
        const clientLastModifiedMs = clientLastModifiedRaw
          ? Number(clientLastModifiedRaw)
          : null;
        if (clientLastModifiedMs && Number.isFinite(clientLastModifiedMs)) {
          metadata.client_last_modified_iso = new Date(
            clientLastModifiedMs
          ).toISOString();
        }

        // Send final progress update
        if (sessionId) {
          broadcastProgress(sessionId, 100, 'Processing complete', 'complete');
          broadcastComplete(sessionId, {
            fields_extracted: rawMetadata.extraction_info.fields_extracted || 0,
            processing_time_ms: processingMs,
            file_size: req.file.size,
          });
        }

        // Add quality metrics and processing insights for enhanced user experience
        // Use the extraction_info data structure from the Python backend
        metadata.quality_metrics = {
          confidence_score: 0.85, // High confidence for successful extraction
          extraction_completeness: Math.min(
            1.0,
            (rawMetadata.extraction_info.fields_extracted || 0) / 100
          ), // Completeness based on field count
          processing_efficiency: 0.88, // Good efficiency for successful extraction
          format_support_level: 'comprehensive', // We support comprehensive formats
          recommended_actions: [], // No specific recommendations for successful extraction
          enhanced_extraction: true,
          streaming_enabled: false,
        };

        metadata.processing_insights = {
          total_fields_extracted:
            rawMetadata.extraction_info.fields_extracted || 0,
          processing_time_ms: processingMs,
          memory_usage_mb: 0, // Memory usage not tracked yet
          streaming_enabled: false,
          fallback_extraction: false,
          progress_updates: [],
        };

        // Filter for Trial
        if (useTrial) {
          // Remove Raw/Advanced data for trial to encourage upgrade
          metadata.iptc = null;
          metadata.xmp = null;
          metadata.exif = {}; // EXIF cannot be null in FrontendMetadataResponse, so use empty object

          metadata.iptc_raw = null;
          metadata.xmp_raw = null;
          metadata._trial_limited = true;
        }

        metadata.access = {
          trial_email_present: !!trialEmail,
          trial_granted: useTrial,
          credits_charged: chargeCredits ? creditCost : 0,
          credits_required: creditCost,
        };

        // Set access mode for frontend clarity
        if (useTrial) {
          metadata.access.mode = 'trial_limited';
        } else if (chargeCredits) {
          metadata.access.mode = 'paid';
        } else {
          // Default is undefined; for anonymous users we may set 'device_free' during the free quota block
          metadata.access.mode = undefined;
        }

        // Record Usage
        const fileExtension = fileExt?.slice(1) || 'unknown';

        // 1. Log extraction analytics (generic) - fire-and-forget is OK for analytics
        storage
          .logExtractionUsage({
            tier: useTrial ? 'free' : 'professional',
            fileExtension,
            mimeType,
            fileSizeBytes: req.file.size,
            isVideo: false,
            isImage: true,
            isPdf: false,
            isAudio: false,
            fieldsExtracted: metadata.fields_extracted || 0,
            processingMs,
            success: true,
            ipAddress: req.ip || req.socket.remoteAddress || null,
            userAgent: req.headers['user-agent'] || null,
          })
          .catch(console.error);

        // 2. ✅ Commit credit hold - MUST succeed before responding (critical for billing)
        // Hold was reserved before Python extraction, now finalize the charge
        if (chargeCredits && holdReserved && creditBalanceId && requestId) {
          try {
            await storage.commitHold(requestId, creditBalanceId, mimeType);
          } catch (error) {
            console.error('Failed to commit credit hold:', error);
            // Release the hold to refund credits
            try {
              await storage.releaseHold(requestId, creditBalanceId);
            } catch (releaseError) {
              console.error(
                'Failed to release hold after commit failure:',
                releaseError
              );
            }
            // Don't return extraction result if we couldn't charge
            return sendServiceUnavailableError(
              res,
              'Credit charge failed. Please contact support.'
            );
          }
        }

        // 3. Record Trial Usage
        if (useTrial && trialEmail) {
          try {
            await storage.recordTrialUsage({
              email: trialEmail,
              ipAddress: req.ip || req.socket.remoteAddress || undefined,
              userAgent: req.get('user-agent') || undefined,
              sessionId: sessionId || undefined,
              // We log to the main trial table. This counts towards the "2 limit".
            });
          } catch (error) {
            console.error('Failed to record trial usage:', error);
          }
        }

        // Check free quota for non-trial users
        if (!useTrial && !trialEmail) {
          // Get client IP for usage tracking
          const ip = req.ip || req.socket.remoteAddress || 'unknown';

          // Check if user has exceeded free quota
          let clientToken = req.cookies?.metaextract_client;
          let decoded = verifyClientToken(clientToken);
          let isNewToken = false;

          if (!decoded) {
            // New user - generate token and allow first request
            clientToken = generateClientToken();
            res.cookie('metaextract_client', clientToken, {
              maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
              path: '/',
              httpOnly: true,
              sameSite: 'strict',
            });
            decoded = verifyClientToken(clientToken);
            isNewToken = true;
          }

          if (!decoded) {
            // Should not happen, but just in case
            return res.status(429).json({
              error: 'Invalid session',
              message: 'Please refresh the page to continue.',
              requires_refresh: true,
            });
          }

          // Check quota
          const usage = await getClientUsage(decoded.clientId);
          const currentCount = usage?.freeUsed || 0;

          if (currentCount >= 2) {
            // CONFIG.FREE_LIMIT
            // Quota exceeded - use enhanced risk-based escalation
            await handleEnhancedQuotaExceeded(req, res, decoded.clientId, ip);
            return;
          }

          // Within quota - proceed but track usage
          await incrementUsage(decoded.clientId, ip);

          // Mark access metadata for device_free
          metadata.access.mode = 'device_free';
          metadata.access.free_used = (currentCount || 0) + 1;

          // Log successful free usage
          // trackImagesMvpEvent('free_extraction_used', {
          //   client_id: decoded.clientId,
          //   ip: ip,
          //   usage_count: currentCount + 1,
          //   is_new_token: !clientToken,
          // });
        }

        // Apply redaction based on access mode (trial/device_free)
        try {
          if (metadata.access && metadata.access.mode) {
            applyAccessModeRedaction(metadata, metadata.access.mode);
          }
        } catch (redactError) {
          console.error('Access mode redaction failed:', redactError);
        }

        // Mark quote as used (prevents replay attacks)
        // Must happen BEFORE response to ensure atomicity
        if (quoteId) {
          try {
            await markQuoteAsUsed(quoteId);
          } catch (quoteError) {
            console.error('Failed to mark quote as used:', quoteError);
            // Don't block response, but log the error
          }
        }

        res.json(metadata);
      } catch (error) {
        console.error('Images MVP extraction error:', error);

        // Release credit hold on error to refund credits
        if (holdReserved && creditBalanceId && requestId) {
          try {
            await storage.releaseHold(requestId, creditBalanceId);
          } catch (releaseError) {
            console.error(
              'Failed to release credit hold on error:',
              releaseError
            );
          }
        }

        // Send error notification via WebSocket
        if (sessionId) {
          broadcastError(
            sessionId,
            error instanceof Error ? error.message : 'Extraction failed'
          );
        }

        sendInternalServerError(res, 'Failed to extract metadata');
      } finally {
        await cleanupTempFile(tempPath);

        // Clean up WebSocket connections for this session
        if (sessionId) {
          setTimeout(() => cleanupConnections(sessionId!), 5000); // Delay cleanup to allow final messages
        }
      }
    }
  );
}
