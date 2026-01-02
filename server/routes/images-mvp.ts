import type { Express, Request, Response } from 'express';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { eq } from 'drizzle-orm';
import DodoPayments from 'dodopayments';
import { db } from '../db';
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
import { IMAGES_MVP_CREDIT_PACKS, DODO_IMAGES_MVP_PRODUCTS } from '../payments';

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

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB Limit for images
  },
});

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

// ============================================================================
// Routes
// ============================================================================

export function registerImagesMvpRoutes(app: Express) {
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
        if (mimeType !== 'image/jpeg' && mimeType !== 'image/png') {
          // Return a 400 with specific message
          return res.status(400).json({
            error: 'Invalid file type',
            message: 'Only JPG and PNG files are supported in this version.',
            code: 'INVALID_FILE_TYPE',
          });
        }

        const trialEmail = normalizeEmail(req.body?.trial_email);
        sessionId = getSessionId(req); // Raw session ID

        // Check Trial Status
        let trialUses = 0;
        if (trialEmail) {
          if (db) {
            const result = await db
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

        // Extract
        // We force 'super' or 'enterprise' tier to get data, but filter it later for trial
        const pythonTier = 'super';
        const rawMetadata = await extractMetadataWithPython(
          tempPath,
          pythonTier,
          true, // performance
          true, // advanced (needed for authenticity signals)
          req.query.store === 'true'
        );

        const processingMs = Date.now() - startTime;
        rawMetadata.extraction_info.processing_ms = processingMs;

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
        const fileExt =
          path.extname(req.file.originalname).toLowerCase().slice(1) ||
          'unknown';

        // 1. Log extraction analytics (generic)
        storage
          .logExtractionUsage({
            tier: useTrial ? 'free' : 'professional',
            fileExtension: fileExt,
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

        // 2. Charge credits
        if (chargeCredits && creditBalanceId) {
          storage
            .useCredits(
              creditBalanceId,
              creditCost,
              `Extraction: ${fileExt} (Images MVP)`,
              mimeType
            )
            .catch(console.error);
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

        res.json(metadata);
      } catch (error) {
        console.error('Images MVP extraction error:', error);
        sendInternalServerError(res, 'Failed to extract metadata');
      } finally {
        await cleanupTempFile(tempPath);
      }
    }
  );
}
