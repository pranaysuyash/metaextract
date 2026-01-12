import type { Express, Request, Response, NextFunction } from 'express';
import type { WebSocket } from 'ws';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import { fileTypeFromBuffer } from 'file-type';
import { eq } from 'drizzle-orm';
import DodoPayments from 'dodopayments';
import { createClient, type RedisClientType } from 'redis';
import { getDatabase, isDatabaseConnected } from '../db';
import { trialUsages } from '@shared/schema';
import { storage } from '../storage/index';
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
} from '../utils/error-response';
import { freeQuotaMiddleware } from '../middleware/free-quota';
import { securityEventLogger } from '../monitoring/security-events';
import {
  generateClientToken,
  verifyClientToken,
  getClientUsage,
  incrementUsage,
  handleQuotaExceeded,
  checkCircuitBreaker,
  getServerDeviceId,
  checkDeviceSuspicious,
} from '../utils/free-quota-enforcement';
import { circuitBreaker } from '../utils/circuit-breaker';
import { IMAGES_MVP_CREDIT_PACKS, DODO_IMAGES_MVP_PRODUCTS } from '../payments';
import { getClientIP, sanitizeFilename } from '../security-utils';
import { rateLimitExtraction } from '../rateLimitMiddleware';
// Utility available for future "Safe Export" feature (stripping metadata for privacy)
import { processImageBuffer } from '../utils/exif-stripper';
import { type AuthRequest as ServerAuthRequest, requireAuth } from '../auth';
import { getOrSetSessionId } from '../utils/session-id';

// WebSocket progress tracking
interface ProgressConnection {
  ws: WebSocket;
  sessionId: string;
  startTime: number;
}

const activeConnections = new Map<string, ProgressConnection[]>();

type ProgressBusMessage = {
  instanceId: string;
  sessionId: string;
  payload: Record<string, unknown>;
};

const PROGRESS_CHANNEL = 'images_mvp:progress';
const PROGRESS_INSTANCE_ID = crypto.randomUUID();
let progressPublisher: any = null;
let progressSubscriber: any = null;
let progressBusReady = false;
let progressBusInit: Promise<void> | null = null;

async function initProgressBus(): Promise<void> {
  if (progressBusReady || progressBusInit) {
    return progressBusInit ?? Promise.resolve();
  }

  if (process.env.IMAGES_MVP_PROGRESS_BUS !== 'redis') {
    return;
  }

  const redisUrl = process.env.REDIS_URL;
  if (!redisUrl) {
    return;
  }

  progressBusInit = (async () => {
    try {
      const publisher = createClient({ url: redisUrl });
      const subscriber = publisher.duplicate();

      publisher.on('error', err => {
        console.error('Progress bus Redis publisher error:', err);
        progressBusReady = false;
      });
      subscriber.on('error', err => {
        console.error('Progress bus Redis subscriber error:', err);
        progressBusReady = false;
      });

      await publisher.connect();
      await subscriber.connect();

      await subscriber.subscribe(PROGRESS_CHANNEL, message => {
        try {
          const parsed = JSON.parse(message) as ProgressBusMessage;
          if (!parsed || parsed.instanceId === PROGRESS_INSTANCE_ID) {
            return;
          }
          if (!parsed.sessionId || !parsed.payload) {
            return;
          }
          sendToConnections(parsed.sessionId, parsed.payload);
        } catch (error) {
          console.error('Progress bus message parse error:', error);
        }
      });

      progressPublisher = publisher;
      progressSubscriber = subscriber;
      progressBusReady = true;
    } catch (error) {
      console.error('Failed to initialize progress bus:', error);
      progressPublisher = null;
      progressSubscriber = null;
      progressBusReady = false;
      progressBusInit = null;
    }
  })();

  return progressBusInit;
}

function sendToConnections(
  sessionId: string,
  payload: Record<string, unknown>
): void {
  const connections = activeConnections.get(sessionId);
  if (!connections || connections.length === 0) return;

  const messageStr = JSON.stringify(payload);
  connections.forEach(conn => {
    if (conn.ws.readyState === 1) {
      conn.ws.send(messageStr);
    }
  });
}

function publishProgressPayload(
  sessionId: string,
  payload: Record<string, unknown>
): void {
  if (!progressPublisher || !progressBusReady) return;

  const message: ProgressBusMessage = {
    instanceId: PROGRESS_INSTANCE_ID,
    sessionId,
    payload,
  };

  progressPublisher
    .publish(PROGRESS_CHANNEL, JSON.stringify(message))
    .catch((error: any) => {
      console.error('Failed to publish progress event:', error);
    });
}

// ============================================================================
// Configuration
// ============================================================================

type AuthRequest = ServerAuthRequest;

function getDodoClient() {
  const apiKey = process.env.DODO_PAYMENTS_API_KEY || process.env.DOOD_API_KEY;
  const env =
    (process.env.DODO_ENV || process.env.DOOD_ENV) !== 'live'
      ? 'test_mode'
      : 'live_mode';
  if (!apiKey) return null;

  const cacheKey = `${apiKey}:${env}`;
  const cached = (getDodoClient as any)._cached as
    | { cacheKey: string; client: any }
    | undefined;
  if (cached?.cacheKey === cacheKey) return cached.client;

  const client = new DodoPayments({ bearerToken: apiKey, environment: env });
  (getDodoClient as any)._cached = { cacheKey, client };
  return client;
}

// WebSocket Progress Tracking Functions
function broadcastProgress(
  sessionId: string,
  progress: number,
  message: string,
  stage?: string
) {
  const progressData = {
    type: 'progress',
    sessionId,
    progress: Math.min(100, Math.max(0, progress)),
    message,
    stage: stage || 'processing',
    timestamp: Date.now(),
  };
  sendToConnections(sessionId, progressData);
  publishProgressPayload(sessionId, progressData);
}

function broadcastError(sessionId: string, error: string) {
  const errorData = {
    type: 'error',
    sessionId,
    error,
    timestamp: Date.now(),
  };
  sendToConnections(sessionId, errorData);
  publishProgressPayload(sessionId, errorData);
}

function broadcastComplete(sessionId: string, metadata: any) {
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
  sendToConnections(sessionId, completeData);
  publishProgressPayload(sessionId, completeData);
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

const IMAGES_MVP_MAX_BYTES = 100 * 1024 * 1024;
const IMAGES_MVP_MAX_FILES = 1;
const IMAGES_MVP_QUOTE_TTL_MS = 10 * 60 * 1000;
const IMAGES_MVP_QUOTE_VERSION = 'images_mvp_quote_v1';

const IMAGES_MVP_MP_BUCKETS = [
  { label: 'standard', maxMp: 12, credits: 0 },
  { label: 'large', maxMp: 24, credits: 1 },
  { label: 'xl', maxMp: 48, credits: 3 },
  { label: 'xxl', maxMp: 96, credits: 7 },
] as const;

const IMAGES_MVP_CREDIT_SCHEDULE = {
  base: 1,
  embedding: 3,
  ocr: 6,
  forensics: 4,
  mpBuckets: IMAGES_MVP_MP_BUCKETS,
  standardCreditsPerImage: 4,
} as const;

type ImagesMvpQuoteOps = {
  embedding?: boolean;
  ocr?: boolean;
  forensics?: boolean;
};

type ImagesMvpQuoteFile = {
  id: string;
  name: string;
  mime?: string | null;
  sizeBytes: number;
  width?: number | null;
  height?: number | null;
};

type ImagesMvpQuoteEntry = {
  accepted: boolean;
  reason?: string;
  detected_type?: string | null;
  creditsTotal?: number;
  mp?: number | null;
  mpBucket?: string | null;
  breakdown?: {
    base: number;
    embedding: number;
    ocr: number;
    forensics: number;
    mp: number;
  };
  warnings?: string[];
  sizeBytes?: number;
  name?: string;
};

const imagesMvpQuoteStore = new Map<
  string,
  {
    expiresAt: number;
    signature: string;
    files: ImagesMvpQuoteFile[];
    ops: ImagesMvpQuoteOps;
    perFile: Record<string, ImagesMvpQuoteEntry>;
  }
>();

function getExtensionFromName(name: string): string | null {
  const idx = name.lastIndexOf('.');
  if (idx <= 0) return null;
  return name.slice(idx).toLowerCase();
}

function computeMp(
  width?: number | null,
  height?: number | null
): number | null {
  if (!width || !height || width <= 0 || height <= 0) return null;
  const mp = (width * height) / 1_000_000;
  return Number.isFinite(mp) ? Math.round(mp * 10) / 10 : null;
}

function resolveMpBucket(mp: number | null): {
  label: string;
  credits: number;
  maxMp: number;
  warning?: string;
  invalid?: boolean;
} {
  const maxBucket = IMAGES_MVP_MP_BUCKETS[IMAGES_MVP_MP_BUCKETS.length - 1];
  if (mp === null) {
    return {
      label: 'unknown',
      credits: maxBucket.credits,
      maxMp: maxBucket.maxMp,
      warning: 'Dimensions unknown; using conservative size bucket.',
    };
  }
  for (const bucket of IMAGES_MVP_MP_BUCKETS) {
    if (mp <= bucket.maxMp) {
      return {
        label: bucket.label,
        credits: bucket.credits,
        maxMp: bucket.maxMp,
      };
    }
  }
  return {
    label: 'oversize',
    credits: maxBucket.credits,
    maxMp: maxBucket.maxMp,
    invalid: true,
  };
}

function buildQuoteSignature(payload: unknown): string {
  return crypto
    .createHash('sha256')
    .update(JSON.stringify(payload))
    .digest('hex');
}

function getStoredQuote(quoteId: string) {
  const stored = imagesMvpQuoteStore.get(quoteId);
  if (!stored) return null;
  if (Date.now() > stored.expiresAt) {
    imagesMvpQuoteStore.delete(quoteId);
    return null;
  }
  return stored;
}

// Use disk storage to prevent DoS via memory exhaustion
const uploadDir = path.join(os.tmpdir(), 'metaextract-uploads');
fs.mkdir(uploadDir, { recursive: true }).catch(e =>
  console.warn('Failed to create upload dir:', e)
);

const upload = multer({
  storage: multer.diskStorage({
    destination: uploadDir,
    filename: (req, file, cb) => {
      const hash = crypto.randomBytes(8).toString('hex');
      const sanitized = sanitizeFilename(file.originalname).replace(
        /[^a-z0-9._-]/gi,
        '_'
      );
      cb(null, `${hash}-${Date.now()}-${sanitized}`);
    },
  }),
  limits: {
    fileSize: IMAGES_MVP_MAX_BYTES,
  },
  fileFilter: (req, file, cb) => {
    // SECURITY: Reject invalid file types before disk write
    const mimeType = file.mimetype;
    const fileExt = path.extname(file.originalname).toLowerCase();
    
    // Check MIME type against supported list
    const isSupportedMime = SUPPORTED_IMAGE_MIMES.has(mimeType);
    
    // Check file extension as additional validation
    const isSupportedExt = fileExt ? SUPPORTED_IMAGE_EXTENSIONS.has(fileExt) : false;
    
    // Allow if either MIME type or extension is supported (defensive)
    if (isSupportedMime || isSupportedExt) {
      return cb(null, true);
    }
    
    // Reject with descriptive error
    // Provide a concise, security-minded error message for clients
    const errorMessage = 'File type not permitted';
    const error = new Error(errorMessage);
    (error as any).code = 'UNSUPPORTED_FILE_TYPE';

    // Log the detailed reason at debug level for diagnostics
    console.debug(`Rejected upload - unsupported file type: ${mimeType} (extension: ${fileExt})`);

    cb(error as any, false);
  },
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
  'image/x-raw',
  'image/x-canon-cr2',
  'image/x-nikon-nef',
  'image/x-sony-arw',
  'image/x-adobe-dng',
  'image/x-olympus-orf',
  'image/x-fuji-raf',
  'image/x-pentax-pef',
  'image/x-sigma-x3f',
  'image/x-samsung-srw',
  'image/x-panasonic-rw2',
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
  '.tiff',
  '.tif',
  '.bmp',
  '.gif',
  '.ico',
  '.svg',
  '.raw',
  '.cr2',
  '.nef',
  '.arw',
  '.dng',
  '.orf',
  '.raf',
  '.pef',
  '.x3f',
  '.srw',
  '.rw2',
]);

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

function getImagesMvpBalanceKeyForSession(sessionId: string): string {
  return `images_mvp:${sessionId}`;
}

function getImagesMvpBalanceKeyForUser(userId: string): string {
  return `images_mvp:user:${userId}`;
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

// ============================================================================
// Routes
// ============================================================================

export function registerImagesMvpRoutes(app: Express) {
  void initProgressBus();
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

        // Validate session ID format
        const sanitizedSessionId = sanitizeFilename(sessionId);
        if (sanitizedSessionId !== sessionId) {
          ws.close(1008, 'Invalid session ID format');
          return;
        }

        // Optional: Validate client token for WebSocket connection
        const clientToken = req.cookies?.metaextract_client;
        const clientId = req.query?.clientId as string;

        if (clientId && clientToken) {
          const decoded = verifyClientToken(clientToken);
          if (!decoded || decoded.clientId !== clientId) {
            ws.close(1008, 'Client token validation failed');
            return;
          }
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
  }

  // ---------------------------------------------------------------------------
  // Analytics: Track UI Events (Images MVP)
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/analytics/track',
    async (req: Request, res: Response) => {
      try {
        const event = typeof req.body?.event === 'string' ? req.body.event : '';
        let properties =
          req.body?.properties && typeof req.body.properties === 'object'
            ? req.body.properties
            : {};
        const sessionId =
          typeof req.body?.sessionId === 'string' ? req.body.sessionId : null;

        // Validate event name
        if (!event) {
          return sendInvalidRequestError(res, 'Event name is required');
        }

        // Limit properties size to 10KB
        const propertiesString = JSON.stringify(properties);
        if (propertiesString.length > 10 * 1024) {
          // Truncate properties if too large
          properties = {
            _truncated: true,
            _originalSize: propertiesString.length,
          };
        }

        // Sanitize event name
        const sanitizedEvent = event
          .replace(/[^a-zA-Z0-9_-]/g, '')
          .substring(0, 100);

        try {
          await storage.logUiEvent({
            product: 'images_mvp',
            eventName: event,
            sessionId,
            userId: null,
            properties,
            ipAddress: req.ip || req.socket.remoteAddress || null,
            userAgent: req.headers['user-agent'] || null,
          });
        } catch (error) {
          // Analytics is non-critical; fail open for unsigned users
          console.warn(
            '[ImagesMVP] Analytics log failed (non-blocking):',
            (error as Error).message || error
          );
        }

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
  app.get(
    '/api/images_mvp/analytics/report',
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
  // Quote: Preflight credits + limits
  // ---------------------------------------------------------------------------
  app.post('/api/images_mvp/quote', async (req: Request, res: Response) => {
    try {
      const rawFiles = Array.isArray(req.body?.files) ? req.body.files : [];
      const ops: ImagesMvpQuoteOps = {
        embedding:
          typeof req.body?.ops?.embedding === 'boolean'
            ? req.body.ops.embedding
            : true,
        ocr: typeof req.body?.ops?.ocr === 'boolean' ? req.body.ops.ocr : false,
        forensics:
          typeof req.body?.ops?.forensics === 'boolean'
            ? req.body.ops.forensics
            : false,
      };

      if (rawFiles.length === 0) {
        return res.status(400).json({ error: 'No files provided' });
      }
      if (rawFiles.length > IMAGES_MVP_MAX_FILES) {
        return res.status(400).json({
          error: 'Too many files',
          maxFiles: IMAGES_MVP_MAX_FILES,
        });
      }

      const files: ImagesMvpQuoteFile[] = rawFiles
        .map((file: any) => ({
          id: typeof file?.id === 'string' ? file.id : '',
          name: typeof file?.name === 'string' ? file.name : '',
          mime: typeof file?.mime === 'string' ? file.mime : null,
          sizeBytes:
            typeof file?.sizeBytes === 'number'
              ? file.sizeBytes
              : Number(file?.sizeBytes ?? 0),
          width:
            typeof file?.width === 'number'
              ? file.width
              : file?.width
                ? Number(file.width)
                : null,
          height:
            typeof file?.height === 'number'
              ? file.height
              : file?.height
                ? Number(file.height)
                : null,
        }))
        .filter((file: any) => file.id && file.name);

      if (files.length === 0) {
        return res.status(400).json({ error: 'Invalid file metadata' });
      }

      const perFile: Record<string, ImagesMvpQuoteEntry> = {};
      let totalCredits = 0;
      const warnings: string[] = [];

      for (const file of files) {
        const ext = getExtensionFromName(file.name);
        const mimeType = file.mime?.toLowerCase() ?? '';
        const hasValidMime = mimeType
          ? SUPPORTED_IMAGE_MIMES.has(mimeType)
          : false;
        const hasValidExt = ext ? SUPPORTED_IMAGE_EXTENSIONS.has(ext) : false;

        if (!hasValidMime && !hasValidExt) {
          perFile[file.id] = {
            accepted: false,
            reason: 'unsupported_type',
            detected_type: mimeType || null,
            name: file.name,
            sizeBytes: file.sizeBytes,
          };
          continue;
        }

        if (!Number.isFinite(file.sizeBytes) || file.sizeBytes <= 0) {
          perFile[file.id] = {
            accepted: false,
            reason: 'invalid_size',
            detected_type: mimeType || null,
            name: file.name,
            sizeBytes: file.sizeBytes,
          };
          continue;
        }

        if (file.sizeBytes > IMAGES_MVP_MAX_BYTES) {
          perFile[file.id] = {
            accepted: false,
            reason: 'file_too_large',
            detected_type: mimeType || null,
            name: file.name,
            sizeBytes: file.sizeBytes,
          };
          continue;
        }

        const mp = computeMp(file.width, file.height);
        const bucket = resolveMpBucket(mp);
        if (bucket.invalid) {
          perFile[file.id] = {
            accepted: false,
            reason: 'megapixels_exceed_limit',
            detected_type: mimeType || null,
            name: file.name,
            sizeBytes: file.sizeBytes,
            mp,
            mpBucket: bucket.label,
          };
          continue;
        }

        const fileWarnings: string[] = [];
        if (bucket.warning) {
          fileWarnings.push(bucket.warning);
          warnings.push(bucket.warning);
        }

        const breakdown = {
          base: IMAGES_MVP_CREDIT_SCHEDULE.base,
          embedding: ops.embedding ? IMAGES_MVP_CREDIT_SCHEDULE.embedding : 0,
          ocr: ops.ocr ? IMAGES_MVP_CREDIT_SCHEDULE.ocr : 0,
          forensics: ops.forensics ? IMAGES_MVP_CREDIT_SCHEDULE.forensics : 0,
          mp: bucket.credits,
        };

        const creditsTotal =
          breakdown.base +
          breakdown.embedding +
          breakdown.ocr +
          breakdown.forensics +
          breakdown.mp;

        totalCredits += creditsTotal;

        perFile[file.id] = {
          accepted: true,
          detected_type: mimeType || null,
          creditsTotal,
          breakdown,
          mp,
          mpBucket: bucket.label,
          warnings: fileWarnings,
          name: file.name,
          sizeBytes: file.sizeBytes,
        };
      }

      const signaturePayload = {
        files: files.map(file => ({
          id: file.id,
          name: file.name,
          mime: file.mime ?? null,
          sizeBytes: file.sizeBytes,
          width: file.width ?? null,
          height: file.height ?? null,
        })),
        ops,
        scheduleVersion: IMAGES_MVP_QUOTE_VERSION,
      };

      const signature = buildQuoteSignature(signaturePayload);
      const quoteId = `q_${crypto.randomUUID()}`;
      const expiresAt = Date.now() + IMAGES_MVP_QUOTE_TTL_MS;

      imagesMvpQuoteStore.set(quoteId, {
        expiresAt,
        signature,
        files,
        ops,
        perFile,
      });

      res.json({
        limits: {
          maxBytes: IMAGES_MVP_MAX_BYTES,
          allowedMimes: Array.from(SUPPORTED_IMAGE_MIMES),
          maxFiles: IMAGES_MVP_MAX_FILES,
        },
        creditSchedule: IMAGES_MVP_CREDIT_SCHEDULE,
        quote: {
          perFile: files.map(file => ({
            id: file.id,
            ...perFile[file.id],
          })),
          totalCredits,
          standardEquivalents:
            IMAGES_MVP_CREDIT_SCHEDULE.standardCreditsPerImage > 0
              ? Number(
                  (
                    totalCredits /
                    IMAGES_MVP_CREDIT_SCHEDULE.standardCreditsPerImage
                  ).toFixed(2)
                )
              : null,
        },
        quoteId,
        expiresAt: new Date(expiresAt).toISOString(),
        warnings,
      });
    } catch (error) {
      console.error('Images MVP quote error:', error);
      res.status(500).json({ error: 'Failed to generate quote' });
    }
  });

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
        const authReq = req as AuthRequest;

        const balanceKey = authReq.user?.id
          ? getImagesMvpBalanceKeyForUser(authReq.user.id)
          : getImagesMvpBalanceKeyForSession(getOrSetSessionId(req, res));

        const balance = await storage.getOrCreateCreditBalance(
          balanceKey,
          authReq.user?.id
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
  // Credits: Transactions
  // ---------------------------------------------------------------------------
  app.get(
    '/api/images_mvp/credits/transactions',
    async (req: Request, res: Response) => {
      try {
        const balanceId =
          typeof req.query.balanceId === 'string' ? req.query.balanceId : null;
        if (!balanceId) return res.json({ transactions: [] });
        const transactions = await storage.getCreditTransactions(balanceId);
        return res.json({ transactions });
      } catch (error) {
        console.error('Get images_mvp credit transactions error:', error);
        return res
          .status(500)
          .json({ error: 'Failed to get credit transactions' });
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
        const authReq = req as AuthRequest;
        if (!authReq.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        const rawSessionId = getOrSetSessionId(req, res);

        const fromKey = getImagesMvpBalanceKeyForSession(rawSessionId);
        const toKey = getImagesMvpBalanceKeyForUser(authReq.user.id);

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
          'Claimed Images MVP credits to account'
        );

        return res.json({ transferred: amount });
      } catch (error) {
        console.error('Images MVP claim credits error:', error);
        return res.status(500).json({ error: 'Failed to claim credits' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Credits: Dev grant (testing helper)
  // ---------------------------------------------------------------------------
  app.post(
    '/api/dev/images_mvp/credits/grant',
    async (req: Request, res: Response) => {
      try {
        if (process.env.NODE_ENV === 'production') {
          return res.status(404).json({ error: 'Not found' });
        }

        const authReq = req as AuthRequest;
        const amount =
          typeof req.body?.credits === 'number'
            ? req.body.credits
            : typeof req.body?.credits === 'string'
              ? Number(req.body.credits)
              : 100;
        if (!Number.isFinite(amount) || amount <= 0) {
          return res
            .status(400)
            .json({ error: 'credits must be a positive number' });
        }

        const balanceKey = authReq.user?.id
          ? getImagesMvpBalanceKeyForUser(authReq.user.id)
          : getImagesMvpBalanceKeyForSession(getOrSetSessionId(req, res));

        const balance = await storage.getOrCreateCreditBalance(
          balanceKey,
          authReq.user?.id
        );

        await storage.addCredits(
          balance.id,
          amount,
          `Dev grant (${amount} credits)`
        );

        const updated = await storage.getCreditBalance(balance.id);
        return res.json({
          ok: true,
          balanceId: balance.id,
          credits: updated?.credits ?? balance.credits,
        });
      } catch (error) {
        console.error('Images MVP dev grant credits error:', error);
        return res.status(500).json({ error: 'Failed to grant credits' });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Credits: Purchase
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/credits/purchase',
    requireAuth,
    async (req: Request, res: Response) => {
      try {
        const dodoClient = getDodoClient();
        if (!dodoClient) {
          return res.status(503).json({
            error: 'Payment system not configured',
            message: 'Please add DODO_PAYMENTS_API_KEY to enable payments',
          });
        }

        const authReq = req as AuthRequest;
        const { pack, email } = req.body;

        if (!pack || !['starter', 'pro'].includes(pack)) {
          return res.status(400).json({ error: 'Invalid credit pack' });
        }

        if (!authReq.user?.id) {
          return res.status(401).json({
            error: 'Authentication required',
            message:
              'Please sign in to purchase credits so they are available across devices.',
          });
        }

        const balanceKey = getImagesMvpBalanceKeyForUser(authReq.user.id);

        const balance = await storage.getOrCreateCreditBalance(
          balanceKey,
          authReq.user?.id
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

        const session = await dodoClient.checkoutSessions.create({
          product_cart: [
            {
              product_id: packInfo.productId,
              quantity: 1,
            },
          ],
          allowed_payment_method_types: [
            'credit',
            'debit',
            'apple_pay',
            'google_pay',
          ],
          billing_currency: 'USD',
          customer: email ? { email } : undefined,
          // Redirect to specialized success page
          return_url: `${baseUrl}/images_mvp/credits/success?pack=${pack}&balanceId=${balance.id}`,
          metadata: {
            type: 'credit_purchase',
            product: 'images_mvp', // Marker for webhook logic
            pack,
            credits: packInfo.credits.toString(),
            balance_id: balance.id,
            balance_key: balanceKey,
            user_id: authReq.user?.id || null,
            purchaser_email: email || null,
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
  // Extraction Endpoint
  // ---------------------------------------------------------------------------
  // Allow unauthenticated free extractions — quota enforcement handles anonymous limits
  app.post(
    '/api/images_mvp/extract',
    freeQuotaMiddleware,
    rateLimitExtraction(), // Rate limit: per-IP/user throttling
    upload.single('file'),
    // Multer error handling middleware
    async (err: any, req: Request, res: Response, next: Function) => {
      if (err) {
        // Handle multer-specific errors
        if (err.code === 'UNSUPPORTED_FILE_TYPE') {
          // Log security event for file type rejection
          await securityEventLogger.logUploadRejection(req, err.message, {
            filename: req.file?.originalname || 'unknown',
            mimetype: req.file?.mimetype || 'unknown',
            size: req.file?.size || 0,
            extension: path.extname(req.file?.originalname || '').toLowerCase() || 'unknown',
          });
          
          return res.status(403).json({
            error: 'Unsupported file type',
            message: err.message,
            code: 'UNSUPPORTED_FILE_TYPE',
          });
        }
        
        if (err.code === 'LIMIT_FILE_SIZE') {
          return res.status(413).json({
            error: 'File too large',
            message: `File size exceeds the maximum allowed size of ${IMAGES_MVP_MAX_BYTES / (1024 * 1024)}MB`,
            code: 'FILE_TOO_LARGE',
          });
        }
        
        if (err.code === 'LIMIT_UNEXPECTED_FILE') {
          return res.status(400).json({
            error: 'Invalid file upload',
            message: 'Only one file can be uploaded at a time',
            code: 'LIMIT_UNEXPECTED_FILE',
          });
        }
        
        // Generic multer error
        return res.status(400).json({
          error: 'File upload failed',
          message: err.message || 'Unknown upload error',
          code: err.code || 'UPLOAD_ERROR',
        });
      }
      
      // No error, proceed to main handler
      next();
    },
    async (req: Request, res: Response) => {
      const startTime = Date.now();
      // Correlation ID for observability (traces request through pipeline)
      const requestId = `req_${Date.now()}_${crypto.randomUUID().slice(0, 8)}`;
      res.setHeader('X-Request-Id', requestId);

      let tempPath: string | null = null;
      let sessionId: string | null = null;
      let creditBalanceId: string | null = null;
      const useTrial = false;
      let chargeCredits = false;

      // Access mode: device_free | trial_limited | paid
      let accessMode: 'device_free' | 'trial_limited' | 'paid' = 'paid';

      let creditCost = 1;
      let runOcr = true;
      const quoteId =
        typeof req.body?.quote_id === 'string' ? req.body.quote_id : null;
      const clientFileId =
        typeof req.body?.client_file_id === 'string'
          ? req.body.client_file_id
          : null;

      try {
        const authReq = req as AuthRequest;
        if (!req.file) {
          return sendInvalidRequestError(res, 'No file uploaded');
        }

        // Enforce file type (MIME + extension check)
        const mimeType = req.file.mimetype;
        const fileExt = path.extname(req.file.originalname).toLowerCase();
        const isSupportedMime = SUPPORTED_IMAGE_MIMES.has(mimeType);
        const isSupportedExt = fileExt
          ? SUPPORTED_IMAGE_EXTENSIONS.has(fileExt)
          : false;
        if (!isSupportedMime && !isSupportedExt) {
          // Return a 403 Forbidden for unsupported files as per security policy
          return res.status(403).json({
            error: 'File type not permitted',
            message:
              'For security reasons, we only support standard photo formats: JPG, PNG, HEIC, and WebP. Please upload a supported image file.',
            code: 'FILE_TYPE_FORBIDDEN',
            supported: ['JPG', 'JPEG', 'PNG', 'HEIC', 'HEIF', 'WebP'],
          });
        }

        // Magic-byte validation: verify actual file content matches claimed type
        const fileBuffer =
          req.file.buffer || (await fs.readFile(req.file.path));
        const detectedType = await fileTypeFromBuffer(fileBuffer);
        if (detectedType && !SUPPORTED_IMAGE_MIMES.has(detectedType.mime)) {
          // File content doesn't match a supported image type - potential spoofing attempt
          return res.status(403).json({
            error: 'Invalid file content',
            message:
              'The uploaded file content does not match a supported image type. Please upload a genuine photo file.',
            code: 'INVALID_MAGIC_BYTES_FORBIDDEN',
            detected: detectedType.mime,
          });
        }

        if (quoteId) {
          const storedQuote = getStoredQuote(quoteId);
          if (!storedQuote) {
            return res.status(400).json({
              error: 'Quote expired or invalid',
              code: 'QUOTE_INVALID',
            });
          }
          if (!clientFileId) {
            return res.status(400).json({
              error: 'Missing client file id for quote validation',
              code: 'QUOTE_MISSING_FILE_ID',
            });
          }
          const quotedFile = storedQuote.perFile[clientFileId];
          if (!quotedFile || !quotedFile.accepted) {
            return res.status(400).json({
              error: 'Quote does not match uploaded file',
              code: 'QUOTE_MISMATCH',
            });
          }
          if (
            typeof quotedFile.sizeBytes === 'number' &&
            quotedFile.sizeBytes !== req.file.size
          ) {
            return res.status(400).json({
              error: 'Quote does not match uploaded file size',
              code: 'QUOTE_SIZE_MISMATCH',
            });
          }
          if (
            typeof quotedFile.creditsTotal !== 'number' ||
            !Number.isFinite(quotedFile.creditsTotal)
          ) {
            return res.status(400).json({
              error: 'Quote missing credit total',
              code: 'QUOTE_MISSING_CREDITS',
            });
          }
          creditCost = quotedFile.creditsTotal;
          runOcr = (quotedFile.breakdown?.ocr ?? 0) > 0;
        }

        const trialEmail = normalizeEmail(req.body?.trial_email);
        // WebSocket progress uses `session_id` (client-provided). Credits use the stable cookie session.
        sessionId = getSessionId(req); // progress session id
        const cookieSessionId = authReq.user?.id
          ? null
          : getOrSetSessionId(req, res);

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

        // Determine Access
        // Security is enforced in all environments
        // For testing, use accounts with sufficient credits
        if (hasTrialAvailable) {
          // Email trial grants a restricted "trial_limited" mode (heavy redaction)
          accessMode = 'trial_limited';
        } else {
          if (trialEmail) {
            // Trial email provided but trial is exhausted: require credits (do not stack free quota).

            const balanceKey = authReq.user?.id
              ? getImagesMvpBalanceKeyForUser(authReq.user.id)
              : getImagesMvpBalanceKeyForSession(cookieSessionId!);

            const balance = await storage.getOrCreateCreditBalance(
              balanceKey,
              authReq.user?.id
            );
            creditBalanceId = balance?.id ?? null;

            if (!balance || balance.credits < creditCost) {
              return sendQuotaExceededError(
                res,
                `Insufficient credits (required: ${creditCost}, available: ${balance?.credits ?? 0})`
              );
            }
            chargeCredits = true;
            accessMode = 'paid';
          } else {
            // No trial available: allow up to 2 free extractions per device, then require credits.
            const ip = req.ip || req.socket.remoteAddress || 'unknown';

            // Use SERVER-ISSUED device token (resistant to cookie clearing)
            // Falls back to old client token for backward compatibility
            let deviceId: string;
            try {
              deviceId = getServerDeviceId(req, res);
            } catch {
              // Fallback to legacy client token
              let clientToken = req.cookies?.metaextract_client;
              let decoded = verifyClientToken(clientToken ?? '');

              if (!decoded) {
                clientToken = generateClientToken();
                res.cookie('metaextract_client', clientToken, {
                  maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
                  path: '/',
                  httpOnly: true,
                  sameSite: 'lax',
                });
                decoded = verifyClientToken(clientToken);
              }

              if (!decoded) {
                return res.status(429).json({
                  error: 'Invalid session',
                  message: 'Please refresh the page to continue.',
                  requires_refresh: true,
                });
              }
              deviceId = decoded.clientId;
            }

            // Check for suspicious device behavior
            const isSuspicious = await checkDeviceSuspicious(req, deviceId);
            if (isSuspicious) {
              console.warn(
                `[Security] Suspicious device detected: ${deviceId} from IP ${ip}`
              );
              // For now, just log - in future, could require CAPTCHA
            }

            // Check circuit breaker for free tier load shedding
            const loadCheck = checkCircuitBreaker(false); // isPaid = false
            if (loadCheck.delayed && loadCheck.estimatedWaitSeconds > 60) {
              // Under extreme load, suggest purchasing
              return res.status(503).json({
                error: 'High demand',
                message: loadCheck.message,
                estimated_wait_seconds: loadCheck.estimatedWaitSeconds,
                upgrade_available: true,
              });
            }

            const usage = await getClientUsage(deviceId);
            const freeUsed = usage?.freeUsed || 0;
            const freeLimit = 2;

            if (freeUsed < freeLimit) {
              await incrementUsage(deviceId, ip);
              // Device-level free check: show high-value data but redact sensitive identifiers
              accessMode = 'device_free';
              chargeCredits = false;

              // reflect usage count in response (n of freeLimit)
              // freeUsed is prior to increment; record nextFreeUsed for response
              (req as any)._nextFreeUsed = (freeUsed || 0) + 1;

              // Record success for circuit breaker recovery
              circuitBreaker.recordSuccess();
            } else {
              // Free quota exhausted: require credits.
              const balanceKey = authReq.user?.id
                ? getImagesMvpBalanceKeyForUser(authReq.user.id)
                : getImagesMvpBalanceKeyForSession(cookieSessionId!);

              const balance = await storage.getOrCreateCreditBalance(
                balanceKey,
                authReq.user?.id
              );
              creditBalanceId = balance?.id ?? null;

              if (!balance || balance.credits < creditCost) {
                await handleQuotaExceeded(req, res, deviceId, ip);
                return;
              }
              chargeCredits = true;
              accessMode = 'paid';
            }
          }
        }

        // Proceed with Extraction
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });
        const sanitizedFilename = sanitizeFilename(req.file.originalname);
        tempPath = path.join(
          tempDir,
          `${crypto.randomUUID()}-${sanitizedFilename}`
        );
        // If file is already on disk (diskStorage), move it; otherwise write from buffer
        if (req.file.path) {
          await fs.copyFile(req.file.path, tempPath);
        } else {
          await fs.writeFile(tempPath, req.file.buffer);
        }

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
        // Use full engine tier for device_free to provide high-value fields; reserve `free` for trial_limited
        const engineTier = accessMode === 'trial_limited' ? 'free' : 'super';

        // Send progress update before extraction
        if (sessionId) {
          broadcastProgress(
            sessionId,
            20,
            'Starting metadata extraction',
            'extraction_start'
          );
        }

        const rawMetadata = await extractMetadataWithPython(
          tempPath,
          engineTier,
          true, // performance
          true, // advanced (needed for authenticity signals)
          req.query.store === 'true',
          {
            ocr: runOcr,
            maxDim: 2048,
          }
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
          tier: engineTier,
          enhanced_extraction: true,
          total_fields_extracted:
            rawMetadata.extraction_info?.fields_extracted || 0,
          streaming_enabled: false, // Will be enabled when we add streaming support
          fallback_extraction: false,
        } as any; // Type assertion to allow additional properties

        const metadata = transformMetadataForFrontend(
          rawMetadata,
          req.file.originalname,
          engineTier
        );
        delete (metadata as any).tier;
        if (process.env.NODE_ENV !== 'production') {
          metadata.debug = {
            ...(metadata.debug || {}),
            engine_tier: engineTier,
          };
        }

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

        // Apply access-mode redactions
        // 'trial_limited' = heavy redaction (email trial)
        // 'device_free' = hybrid redaction (show high-value data, redact sensitive identifiers)
        if (accessMode === 'trial_limited') {
          applyAccessModeRedaction(metadata, 'trial_limited');
        } else if (accessMode === 'device_free') {
          // Ensure we don't mark trial-limited and apply hybrid redactions
          delete (metadata as any)._trial_limited;
          applyAccessModeRedaction(metadata, 'device_free');
        }

        metadata.access = {
          trial_email_present: !!trialEmail,
          trial_granted: accessMode === 'trial_limited',
          credits_charged: chargeCredits ? creditCost : 0,
          credits_required: chargeCredits ? creditCost : 0,
          mode: accessMode,
          free_used: (req as any)._nextFreeUsed ?? undefined,
        };

        // Record Usage
        const fileExtension = fileExt?.slice(1) || 'unknown';

        // 1. Log extraction analytics (generic) - fire-and-forget is OK for analytics
        storage
          .logExtractionUsage({
            tier: useTrial ? 'free' : 'enterprise',
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

        // 2. ✅ Charge credits - MUST await before responding (critical for billing)
        if (chargeCredits && creditBalanceId) {
          try {
            await storage.useCredits(
              creditBalanceId,
              creditCost,
              `Extraction: ${fileExtension} (Images MVP)`,
              mimeType
            );
          } catch (error) {
            console.error('Failed to charge credits:', error);
            return res.status(402).json({
              error: 'Payment failed',
              message: 'Could not charge credits for this extraction',
              requiresRefresh: true,
            });
          }
        }

        // 3. Record Trial Usage
        if (accessMode === 'trial_limited' && trialEmail) {
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

        res.json(metadata);
      } catch (error) {
        console.error('Images MVP extraction error:', error);

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

  // ---------------------------------------------------------------------------
  // Job Status Endpoint (Async Processing Support)
  // ---------------------------------------------------------------------------
  app.get(
    '/api/images_mvp/jobs/:jobId/status',
    async (req: Request, res: Response) => {
      try {
        const { jobId } = req.params;

        if (!jobId) {
          return res.status(400).json({ error: 'Job ID is required' });
        }

        // For now, check metadata_results as the "completed" indicator
        // Full async queue implementation is in short-term roadmap
        const metadata = await storage.getMetadata(jobId);

        if (metadata) {
          return res.json({
            jobId,
            status: 'complete',
            progress: 100,
            message: 'Extraction complete',
            result: {
              id: metadata.id,
              fileName: metadata.fileName,
              createdAt: metadata.createdAt,
            },
          });
        }

        // Job not found - could be pending or invalid
        return res.status(404).json({
          jobId,
          status: 'not_found',
          message:
            'Job not found. It may still be processing or the ID is invalid.',
        });
      } catch (error) {
        console.error('Error fetching job status:', error);
        return res.status(500).json({
          error: 'Failed to fetch job status',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Thumbnail Endpoint with Format Negotiation (CDN Optimization)
  // ---------------------------------------------------------------------------
  app.get(
    '/api/images_mvp/thumbnail/:resultId',
    async (req: Request, res: Response) => {
      try {
        const { resultId } = req.params;
        const acceptHeader = req.headers.accept || '';

        // Format negotiation based on client capabilities
        let preferredFormat: 'avif' | 'webp' | 'jpeg' = 'jpeg';
        if (acceptHeader.includes('image/avif')) {
          preferredFormat = 'avif';
        } else if (acceptHeader.includes('image/webp')) {
          preferredFormat = 'webp';
        }

        // Get metadata result to find original image
        const metadata = await storage.getMetadata(resultId);
        if (!metadata) {
          return res.status(404).json({ error: 'Result not found' });
        }

        // For now, return format info - actual thumbnail generation
        // requires object storage integration (short-term roadmap)
        return res.json({
          resultId,
          preferredFormat,
          message: 'Thumbnail endpoint ready. CDN integration pending.',
          thumbnailUrl: `/api/images_mvp/thumbnail/${resultId}/image.${preferredFormat}`,
          formats: {
            avif: acceptHeader.includes('image/avif'),
            webp: acceptHeader.includes('image/webp'),
            jpeg: true,
          },
        });
      } catch (error) {
        console.error('Error generating thumbnail:', error);
        return res.status(500).json({
          error: 'Failed to generate thumbnail',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );
}
