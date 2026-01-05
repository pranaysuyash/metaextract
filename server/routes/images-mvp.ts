import type { Express, Request, Response } from 'express';
import type { WebSocket } from 'ws';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { eq } from 'drizzle-orm';
import DodoPayments from 'dodopayments';
import { getDatabase, isDatabaseConnected } from '../db';
import { trialUsages } from '@shared/schema';
import { storage } from '../storage/index';
import {
  extractMetadataWithPython,
  transformMetadataForFrontend,
  normalizeEmail,
  getSessionId,
  cleanupTempFile,
} from '../utils/extraction-helpers';
import {
  sendQuotaExceededError,
  sendInvalidRequestError,
  sendInternalServerError,
} from '../utils/error-response';
import { freeQuotaMiddleware } from '../middleware/free-quota';
import { generateClientToken, verifyClientToken, getClientUsage, incrementUsage, handleQuotaExceeded } from '../utils/free-quota-enforcement';
import { IMAGES_MVP_CREDIT_PACKS, DODO_IMAGES_MVP_PRODUCTS } from '../payments';

// WebSocket progress tracking
interface ProgressConnection {
  ws: WebSocket;
  sessionId: string;
  startTime: number;
}

const activeConnections = new Map<string, ProgressConnection[]>();

// ============================================================================
// Configuration
// ============================================================================

const DODO_API_KEY = process.env.DODO_PAYMENTS_API_KEY;
const IS_TEST_MODE = process.env.DODO_ENV !== 'live';

const dodoClient = DODO_API_KEY
  ? new DodoPayments({
      bearerToken: DODO_API_KEY,
      environment: IS_TEST_MODE ? 'test_mode' : 'live_mode',
    })
  : null;

// WebSocket Progress Tracking Functions
function broadcastProgress(sessionId: string, progress: number, message: string, stage?: string) {
  const connections = activeConnections.get(sessionId);
  if (!connections || connections.length === 0) return;

  const progressData = {
    type: 'progress',
    sessionId,
    progress: Math.min(100, Math.max(0, progress)),
    message,
    stage: stage || 'processing',
    timestamp: Date.now()
  };

  const messageStr = JSON.stringify(progressData);
  
  connections.forEach(conn => {
    if (conn.ws.readyState === 1) { // WebSocket.OPEN
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
    timestamp: Date.now()
  };

  const messageStr = JSON.stringify(errorData);
  
  connections.forEach(conn => {
    if (conn.ws.readyState === 1) { // WebSocket.OPEN
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
      file_size: metadata.file_size || 0
    },
    timestamp: Date.now()
  };

  const messageStr = JSON.stringify(completeData);
  
  connections.forEach(conn => {
    if (conn.ws.readyState === 1) { // WebSocket.OPEN
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

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB Limit for images
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
  'image/x-panasonic-rw2'
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
  '.rw2'
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

// ============================================================================
// Routes
// ============================================================================

export function registerImagesMvpRoutes(app: Express) {
  // ---------------------------------------------------------------------------
  // WebSocket: Real-time Progress Tracking
  // ---------------------------------------------------------------------------
  (app as any).ws('/api/images_mvp/progress/:sessionId', (ws: WebSocket, req: Request) => {
    const sessionId = req.params.sessionId;
    if (!sessionId) {
      ws.close(1002, 'Session ID required');
      return;
    }

    // Add connection to active connections
    const connection: ProgressConnection = {
      ws,
      sessionId,
      startTime: Date.now()
    };

    if (!activeConnections.has(sessionId)) {
      activeConnections.set(sessionId, []);
    }
    activeConnections.get(sessionId)!.push(connection);

    // Send initial connection confirmation
    ws.send(JSON.stringify({
      type: 'connected',
      sessionId,
      timestamp: Date.now()
    }));

    // Handle incoming messages (if needed for client acknowledgments)
    ws.on('message', (data) => {
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
    ws.on('error', (error) => {
      console.error('WebSocket error for session', sessionId, ':', error);
      cleanupConnections(sessionId);
    });

    // Send periodic progress updates (every 2 seconds)
    const progressInterval = setInterval(() => {
      if (ws.readyState === 1) { // WebSocket.OPEN
        ws.send(JSON.stringify({
          type: 'heartbeat',
          sessionId,
          timestamp: Date.now()
        }));
      } else {
        clearInterval(progressInterval);
      }
    }, 2000);

    ws.on('close', () => {
      clearInterval(progressInterval);
    });
  });

  // ---------------------------------------------------------------------------
  // Analytics: Track UI Events (Images MVP)
  // ---------------------------------------------------------------------------
  app.post(
    '/api/images_mvp/analytics/track',
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
                ? Math.round(analysisProcessingMsTotal / analysisProcessingCount)
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
        // But we will internally look up the namespaced session
        const rawSessionId = req.query.sessionId as string;

        if (!rawSessionId) {
          return res.json({ credits: 0, balanceId: null });
        }

        // Use the namespaced ID for looking up balance
        const namespacedSessionId = getImagesMvpBalanceId(rawSessionId);
        const balance =
          await storage.getOrCreateCreditBalance(namespacedSessionId);

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
        if (!dodoClient) {
          return res.status(503).json({
            error: 'Payment system not configured',
            message: 'Please add DODO_PAYMENTS_API_KEY to enable payments',
          });
        }

        const { pack, sessionId, email } = req.body;

        if (!pack || !['starter', 'pro'].includes(pack)) {
          return res.status(400).json({ error: 'Invalid credit pack' });
        }

        if (!sessionId) {
          return res.status(400).json({ error: 'Session ID required' });
        }

        const namespacedSessionId = getImagesMvpBalanceId(sessionId);
        const balance =
          await storage.getOrCreateCreditBalance(namespacedSessionId);
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
  app.post(
    '/api/images_mvp/extract',
    upload.single('file'),
    async (req: Request, res: Response) => {
      const startTime = Date.now();
      let tempPath: string | null = null;
      let sessionId: string | null = null;
      let creditBalanceId: string | null = null;
      let useTrial = false;
      let chargeCredits = false;

      // Fixed cost for MVP
      const creditCost = 1;

      try {
        if (!req.file) {
          return sendInvalidRequestError(res, 'No file uploaded');
        }

        // Enforce file type
        const mimeType = req.file.mimetype;
        const fileExt = path.extname(req.file.originalname).toLowerCase();
        const isSupportedMime = SUPPORTED_IMAGE_MIMES.has(mimeType);
        const isSupportedExt = fileExt
          ? SUPPORTED_IMAGE_EXTENSIONS.has(fileExt)
          : false;
        if (!isSupportedMime && !isSupportedExt) {
          // Return a 400 with specific message
          return res.status(400).json({
            error: 'Invalid file type',
            message:
              'We support popular photo formats: JPG, PNG, HEIC (iPhone), WebP, and more. Please upload a standard photo.',
            code: 'INVALID_FILE_TYPE',
            supported: ['JPG', 'JPEG', 'PNG', 'HEIC', 'HEIF', 'WebP'],
          });
        }

        const trialEmail = normalizeEmail(req.body?.trial_email);
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

        // Determine Access
        // In development, skip all restrictions for easier testing
        if (process.env.NODE_ENV === 'development') {
          useTrial = false;
          chargeCredits = false;
        } else if (hasTrialAvailable) {
          useTrial = true;
        } else {
          // Check Credits
          if (!sessionId) {
            return sendQuotaExceededError(
              res,
              'Trial limit reached. Purchase credits to continue.'
            );
          }

          const namespacedSessionId = getImagesMvpBalanceId(sessionId);
          const balance =
            await storage.getOrCreateCreditBalance(namespacedSessionId);
          creditBalanceId = balance?.id ?? null;

          if (!balance || balance.credits < creditCost) {
            return sendQuotaExceededError(
              res,
              `Insufficient credits (required: ${creditCost}, available: ${balance?.credits ?? 0})`
            );
          }
          chargeCredits = true;
        }

        // Proceed with Extraction
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });
        tempPath = path.join(
          tempDir,
          `${Date.now()}-${crypto.randomUUID()}-${req.file.originalname}`
        );
        await fs.writeFile(tempPath, req.file.buffer);

        // Send initial progress update
        if (sessionId) {
          broadcastProgress(sessionId, 10, 'File uploaded successfully', 'upload_complete');
        }

        // Extract with enhanced features
        const pythonTier = 'super';
        
        // Send progress update before extraction
        if (sessionId) {
          broadcastProgress(sessionId, 20, 'Starting metadata extraction', 'extraction_start');
        }
        
        const rawMetadata = await extractMetadataWithPython(
          tempPath,
          pythonTier,
          true, // performance
          true, // advanced (needed for authenticity signals)
          req.query.store === 'true'
        );
        
        // Send progress update after extraction
        if (sessionId) {
          broadcastProgress(sessionId, 90, 'Metadata extraction complete', 'extraction_complete');
        }

        const processingMs = Date.now() - startTime;
        rawMetadata.extraction_info.processing_ms = processingMs;

        // Add enhanced processing insights
        rawMetadata.extraction_info = {
          ...rawMetadata.extraction_info,
          enhanced_extraction: true,
          total_fields_extracted: rawMetadata.extraction_info?.fields_extracted || 0,
          streaming_enabled: false, // Will be enabled when we add streaming support
          fallback_extraction: false
        } as any; // Type assertion to allow additional properties

      const metadata = transformMetadataForFrontend(
          rawMetadata, 
          req.file.originalname, 
          useTrial ? 'free' : 'professional'
      );

      const clientLastModifiedRaw = req.body?.client_last_modified;
      const clientLastModifiedMs = clientLastModifiedRaw ? Number(clientLastModifiedRaw) : null;
      if (clientLastModifiedMs && Number.isFinite(clientLastModifiedMs)) {
          metadata.client_last_modified_iso = new Date(clientLastModifiedMs).toISOString();
      }

      // Send final progress update
      if (sessionId) {
        broadcastProgress(sessionId, 100, 'Processing complete', 'complete');
        broadcastComplete(sessionId, {
          fields_extracted: rawMetadata.extraction_info.fields_extracted || 0,
          processing_time_ms: processingMs,
          file_size: req.file.size
        });
      }

      // Add quality metrics and processing insights for enhanced user experience
      // Use the extraction_info data structure from the Python backend
      metadata.quality_metrics = {
        confidence_score: 0.85, // High confidence for successful extraction
        extraction_completeness: Math.min(1.0, (rawMetadata.extraction_info.fields_extracted || 0) / 100), // Completeness based on field count
        processing_efficiency: 0.88, // Good efficiency for successful extraction
        format_support_level: 'comprehensive', // We support comprehensive formats
        recommended_actions: [], // No specific recommendations for successful extraction
        enhanced_extraction: true,
        streaming_enabled: false
      };

      metadata.processing_insights = {
        total_fields_extracted: rawMetadata.extraction_info.fields_extracted || 0,
        processing_time_ms: processingMs,
        memory_usage_mb: 0, // Memory usage not tracked yet
        streaming_enabled: false,
        fallback_extraction: false,
        progress_updates: []
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
              sameSite: 'strict'
            });
            decoded = verifyClientToken(clientToken);
            isNewToken = true;
          }
          
          if (!decoded) {
            // Should not happen, but just in case
            return res.status(429).json({
              error: 'Invalid session',
              message: 'Please refresh the page to continue.',
              requires_refresh: true
            });
          }
          
          // Check quota
          const usage = await getClientUsage(decoded.clientId);
          const currentCount = usage?.free_used || 0;
          
          if (currentCount >= 2) { // CONFIG.FREE_LIMIT
            // Quota exceeded - show appropriate response
            await handleQuotaExceeded(req, res, decoded.clientId, ip);
            return;
          }
          
          // Within quota - proceed but track usage
          await incrementUsage(decoded.clientId, ip);
          
          // Log successful free usage
          // trackImagesMvpEvent('free_extraction_used', {
          //   client_id: decoded.clientId,
          //   ip: ip,
          //   usage_count: currentCount + 1,
          //   is_new_token: !clientToken,
          // });
        }

        res.json(metadata);
      } catch (error) {
        console.error('Images MVP extraction error:', error);
        
        // Send error notification via WebSocket
        if (sessionId) {
          broadcastError(sessionId, error instanceof Error ? error.message : 'Extraction failed');
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
