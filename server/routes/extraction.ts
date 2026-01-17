/**
 * Extraction Routes Module
 *
 * Handles all metadata extraction endpoints:
 * - Single file extraction
 * - Batch extraction
 * - Advanced forensic analysis
 */

import type { Express, Response } from 'express';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { spawn } from 'child_process';
import { fileTypeFromBuffer } from 'file-type';
import {
  PythonMetadataResponse,
  FrontendMetadataResponse,
  normalizeEmail,
  getSessionId,
  transformMetadataForFrontend,
  extractMetadataWithPython,
  cleanupTempFile,
  pythonExecutable,
  PYTHON_SCRIPT_PATH,
} from '../utils/extraction-helpers';
import { storage } from '../storage/index';
import {
  getTierConfig,
  isFileTypeAllowed,
  isFileSizeAllowed,
  getRequiredTierForFileType,
  TIER_CONFIGS,
  normalizeTier,
  toPythonTier,
  getCreditCost,
} from '@shared/tierConfig';
import type { AuthRequest } from '../auth';
import { requireAuth } from '../auth';
import {
  sendFileTooLargeError,
  sendFileTooLargeForTier,
  sendInvalidFileTypeError,
  sendTierInsufficientError,
  sendQuotaExceededError,
  sendInvalidRequestError,
  sendInternalServerError,
  sendServiceUnavailableError,
} from '../utils/error-response';
import { getOrSetSessionId } from '../utils/session-id';

// ============================================================================
// Multer Configuration
// ============================================================================

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 2000 * 1024 * 1024, // 2GB max (enterprise/super tier)
  },
});

// ============================================================================
// Trial Tracking (in-memory; replace with DB for production)
// ============================================================================

// Removed in-memory trial map - now using database-backed storage.hasTrialUsage()

const EXTRACTION_HEALTH_TIMEOUT_MS = Number(
  process.env.EXTRACTION_HEALTH_TIMEOUT_MS ??
    process.env.HEALTH_CHECK_TIMEOUT_MS ??
    (process.env.NODE_ENV === 'test' ? 500 : 10000)
);

function guessMimeTypeFromFilename(filename: string): string | null {
  const ext = path.extname(filename || '').toLowerCase();
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
    '.cur': 'image/x-icon',
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

    // Camera RAW (best-effort; actual decoding handled by Python/ExifTool)
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
    '.rwl': 'image/x-leica-rwl',
    '.3fr': 'image/x-hasselblad-3fr',
    '.iiq': 'image/x-phaseone-iiq',
    '.x3f': 'image/x-sigma-x3f',
  };
  return map[ext] ?? null;
}

function getCoreBalanceKeyForSession(sessionId: string): string {
  return `credits:core:session:${sessionId}`;
}

function getCoreBalanceKeyForUser(userId: string): string {
  return `credits:core:user:${userId}`;
}

function shouldBypassCredits(req: AuthRequest): boolean {
  // DEV MODE: opt-in bypass for development testing (disabled by default)
  const bypassInDev =
    process.env.NODE_ENV === 'development' &&
    String(process.env.BYPASS_CREDITS_IN_DEV ?? '').toLowerCase() === 'true';
  if (bypassInDev) return true;

  // Allow deterministic route testing by bypassing credits gates.
  // Never enable this in production.
  if (process.env.NODE_ENV !== 'test') return false;
  const value = String(
    req.headers['x-test-bypass-credits'] ?? ''
  ).toLowerCase();
  return value === '1' || value === 'true';
}

// ============================================================================
// Route Registration
// ============================================================================

export function registerExtractionRoutes(app: Express): void {
  // Main extraction endpoint
  app.post(
    '/api/extract',
    upload.single('file'),
    async (req: AuthRequest, res) => {
      const startTime = Date.now();
      let tempPath: string | null = null;
      let sessionId: string | null = null;
      let creditCost = 0;
      let chargeCredits = false;
      let trialEmail: string | null = null;
      let creditBalanceId: string | null = null;

      try {
        if (!req.file) {
          return sendInvalidRequestError(res, 'No file uploaded');
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);
        // Do not trust browser-provided mimetype for gating; detect from bytes when possible.
        const detected = await fileTypeFromBuffer(req.file.buffer);
        const guessed = guessMimeTypeFromFilename(req.file.originalname);
        const mimeType =
          detected?.mime ||
          guessed ||
          req.file.mimetype ||
          'application/octet-stream';
        const tierConfig = getTierConfig(normalizedTier);
        // Credits + trial tracking use a stable cookie session id (shared across localhost ports).
        // Prefer an explicitly provided session id (query param or header). Do NOT auto-generate a new session id here
        // because callers without a session_id should be asked to purchase credits rather than having a server-generated id.
        sessionId = req.user?.id ? null : (getSessionId(req as any) ?? null);
        trialEmail = normalizeEmail(req.body?.trial_email);
        creditCost = getCreditCost(mimeType);
        const bypassCredits = shouldBypassCredits(req);

        // Validate file type for tier
        if (!isFileTypeAllowed(normalizedTier, mimeType)) {
          const requiredTier = getRequiredTierForFileType(mimeType);
          return sendInvalidFileTypeError(
            res,
            mimeType,
            requiredTier,
            normalizedTier
          );
        }

        // Validate file size for tier (do this before any payment gating)
        if (!isFileSizeAllowed(normalizedTier, req.file.size)) {
          const fileSizeMB =
            Math.round((req.file.size / (1024 * 1024)) * 100) / 100;
          return sendFileTooLargeForTier(
            res,
            fileSizeMB,
            tierConfig.maxFileSizeMB,
            normalizedTier
          );
        }

        const hasTrialAvailable =
          !!trialEmail && !(await storage.hasTrialUsage(trialEmail));

        if (!bypassCredits && !hasTrialAvailable) {
          // If unauthenticated and no explicit session id was provided, ask user to purchase credits
          if (!req.user?.id && !sessionId) {
            return sendQuotaExceededError(
              res,
              'Purchase credits to unlock a full report.'
            );
          }

          let balanceKey: string;
          if (req.user?.id) {
            balanceKey = getCoreBalanceKeyForUser(req.user.id);
          } else {
            // Back-compat: if an older balance exists keyed by raw sessionId, keep using it.
            const legacy = await storage.getCreditBalanceBySessionId(
              sessionId!
            );
            balanceKey = legacy
              ? sessionId!
              : getCoreBalanceKeyForSession(sessionId!);
          }

          const balance = await storage.getOrCreateCreditBalance(
            balanceKey,
            req.user?.id
          );
          creditBalanceId = balance?.id ?? null;
          if (!balance || balance.credits < creditCost) {
            return sendQuotaExceededError(
              res,
              `Insufficient credits (required: ${creditCost}, available: ${balance?.credits ?? 0})`
            );
          }

          chargeCredits = true;
        }

        // Write file to temp location
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });
        tempPath = path.join(
          tempDir,
          `${Date.now()}-${crypto.randomUUID()}-${req.file.originalname}`
        );
        await fs.writeFile(tempPath, req.file.buffer);

        // Extract metadata
        // Automatically enable advanced analysis for forensic and enterprise tiers (Phase 3.1)
        const shouldEnableAdvancedAnalysis =
          ['forensic', 'enterprise'].includes(normalizedTier) ||
          req.query.advanced === 'true';

        const rawMetadata = await extractMetadataWithPython(
          tempPath,
          pythonTier,
          true,
          shouldEnableAdvancedAnalysis,
          req.query.store === 'true'
        );

        const processingMs = Date.now() - startTime;
        rawMetadata.extraction_info.processing_ms = processingMs;

        const metadata = transformMetadataForFrontend(
          rawMetadata,
          req.file.originalname,
          normalizedTier
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
        metadata.access = {
          trial_email_present: !!trialEmail,
          trial_granted: bypassCredits
            ? false
            : hasTrialAvailable
              ? true
              : false,
          credits_charged: chargeCredits ? creditCost : 0,
          credits_required: creditCost,
        };

        // Log analytics (non-critical, error doesn't block response)
        const fileExt =
          path.extname(req.file.originalname).toLowerCase().slice(1) ||
          'unknown';
        try {
          await storage.logExtractionUsage({
            tier: normalizedTier,
            fileExtension: fileExt,
            mimeType,
            fileSizeBytes: req.file.size,
            isVideo: mimeType.startsWith('video/'),
            isImage: mimeType.startsWith('image/'),
            isPdf: mimeType === 'application/pdf',
            isAudio: mimeType.startsWith('audio/'),
            fieldsExtracted: metadata.fields_extracted || 0,
            processingMs,
            success: true,
            ipAddress: req.ip || req.socket.remoteAddress || null,
            userAgent: req.headers['user-agent'] || null,
          });
        } catch (err) {
          console.error('[Extraction] Failed to log usage:', err);
          // Continue - analytics failure is not blocking
        }

        // ✅ CRITICAL: Deduct credits (must complete before responding to user)
        if (chargeCredits && creditBalanceId) {
          try {
            const txn = await storage.useCredits(
              creditBalanceId,
              creditCost,
              `Extraction: ${fileExt}`,
              mimeType
            );

            if (!txn) {
              // useCredits returns null if balance insufficient
              // (safety check in case balance changed between validation and deduction)
              return sendQuotaExceededError(
                res,
                'Credit deduction failed (insufficient balance)'
              );
            }
          } catch (err) {
            console.error('[Extraction] Failed to deduct credits:', err);
            return sendInternalServerError(
              res,
              'Unable to process credit transaction. Please try again.'
            );
          }
        }

        if (!bypassCredits && hasTrialAvailable && trialEmail) {
          // Record trial usage in database
          try {
            await storage.recordTrialUsage({
              email: trialEmail,
              ipAddress: req.ip || req.socket.remoteAddress || undefined,
              userAgent: req.get('user-agent') || undefined,
              sessionId: sessionId || undefined,
            });
          } catch (err) {
            console.error('Failed to record trial usage:', err);
          }
        }

        // Persist results to database (Fix for QuotaExceededError)
        try {
          const savedRecord = await storage.saveMetadata({
            userId: req.user?.id,
            fileName: metadata.filename,
            fileSize: String(req.file.size),
            mimeType: metadata.mime_type,
            metadata,
          });

          if (savedRecord && savedRecord.id) {
            metadata.id = savedRecord.id;
            metadata.storage = {
              provider: savedRecord.metadataRef?.provider ?? 'summary-only',
              has_full_blob: !!savedRecord.metadataRef,
            };
            console.log(
              `[Extraction] Saved metadata summary + blob with ID: ${savedRecord.id}`
            );
          } else {
            // savedRecord could be null/undefined in degraded modes; proceed without failing
            console.warn(
              '[Extraction] saveMetadata returned no saved record; proceeding without DB record'
            );
            metadata.storage = {
              provider: 'summary-only',
              has_full_blob: false,
            };
          }
        } catch (dbError) {
          console.error('[Extraction] Failed to save metadata to DB:', dbError);
          // Continue anyway - frontend will use memory fallback
          metadata.storage = { provider: 'summary-only', has_full_blob: false };
        }

        res.json(metadata);
      } catch (error) {
        const processingMs = Date.now() - startTime;
        const failureReason =
          error instanceof Error ? error.message : 'Unknown error';

        console.error('Metadata extraction error:', error);

        // Log failed extraction
        if (req.file) {
          const fileExt =
            path.extname(req.file.originalname).toLowerCase().slice(1) ||
            'unknown';
          const fallbackTier = normalizeTier(
            (req.query.tier as string) || 'enterprise'
          );
          storage
            .logExtractionUsage({
              tier: fallbackTier,
              fileExtension: fileExt,
              mimeType: req.file.mimetype || 'application/octet-stream',
              fileSizeBytes: req.file.size,
              isVideo: false,
              isImage: false,
              isPdf: false,
              isAudio: false,
              fieldsExtracted: 0,
              processingMs,
              success: false,
              failureReason,
              ipAddress: req.ip || req.socket.remoteAddress || null,
              userAgent: req.headers['user-agent'] || null,
            })
            .catch(err => console.error('Failed to log usage:', err));
        }

        sendInternalServerError(
          res,
          'Failed to extract metadata',
          failureReason
        );
      } finally {
        await cleanupTempFile(tempPath);
      }
    }
  );

  // Batch processing endpoint
  app.post(
    '/api/extract/batch',
    upload.array('files', 100),
    async (req: AuthRequest, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length === 0) {
          return sendInvalidRequestError(res, 'No files uploaded');
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);
        const tierConfig = getTierConfig(normalizedTier);

        if (!tierConfig.features.batchUpload) {
          return sendTierInsufficientError(res, 'forensic', normalizedTier);
        }

        // Validate all files first
        for (const file of req.files) {
          const mimeType = file.mimetype || 'application/octet-stream';

          if (!isFileTypeAllowed(normalizedTier, mimeType)) {
            const requiredTier = getRequiredTierForFileType(mimeType);
            return sendInvalidFileTypeError(res, mimeType, requiredTier);
          }

          if (!isFileSizeAllowed(normalizedTier, file.size)) {
            const fileSizeMB =
              Math.round((file.size / (1024 * 1024)) * 100) / 100;
            return sendFileTooLargeError(
              res,
              fileSizeMB,
              tierConfig.maxFileSizeMB
            );
          }
        }

        // Write all files to temp locations
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });

        const fileInfos = [];
        for (const file of req.files) {
          const tempPath = path.join(
            tempDir,
            `${Date.now()}-${crypto.randomUUID()}-${file.originalname}`
          );
          await fs.writeFile(tempPath, file.buffer);
          tempPaths.push(tempPath);
          fileInfos.push({
            tempPath,
            originalName: file.originalname,
            size: file.size,
            mimeType: file.mimetype,
          });
        }

        // Process batch using Python engine
        const pythonScript = PYTHON_SCRIPT_PATH;
        const batchResults = await new Promise<any>((resolve, reject) => {
          const pythonArgs = [
            pythonScript,
            '--batch',
            '--tier',
            pythonTier,
            ...tempPaths,
          ];
          if (req.query.store === 'true') {
            pythonArgs.push('--store');
          }
          const python = spawn(pythonExecutable, pythonArgs);

          let stdout = '';
          let stderr = '';

          python.stdout.on('data', data => {
            stdout += data.toString();
          });

          python.stderr.on('data', data => {
            stderr += data.toString();
          });

          python.on('close', code => {
            if (code !== 0) {
              reject(new Error(`Batch processing failed: ${stderr}`));
              return;
            }

            try {
              resolve(JSON.parse(stdout));
            } catch (e) {
              reject(new Error('Failed to parse batch results'));
            }
          });

          // Longer timeout for batch processing
          setTimeout(() => {
            python.kill();
            reject(new Error('Batch processing timed out'));
          }, 300000); // 5 minutes
        });

        // Transform results for frontend
        const transformedResults: Record<string, any> = {};
        for (const fileInfo of fileInfos) {
          const directResult = batchResults.results?.[fileInfo.tempPath];
          const fallbackKey =
            !directResult && batchResults.results
              ? Object.keys(batchResults.results).find(key =>
                  key.includes(fileInfo.originalName)
                )
              : undefined;
          const result =
            directResult ||
            (fallbackKey ? batchResults.results[fallbackKey] : undefined);
          if (result) {
            transformedResults[fileInfo.originalName] =
              transformMetadataForFrontend(
                result,
                fileInfo.originalName,
                normalizedTier
              );
          }
        }

        const processingMs = Date.now() - startTime;

        res.json({
          success: true,
          batch_id: crypto.randomUUID(),
          total_files: fileInfos.length,
          successful_files: Object.keys(transformedResults).length,
          processing_time_ms: processingMs,
          results: transformedResults,
          summary: batchResults.summary,
        });
      } catch (error) {
        const processingMs = Date.now() - startTime;
        console.error('Batch processing error:', error);

        res.status(500).json({
          error: 'Batch processing failed',
          details: error instanceof Error ? error.message : 'Unknown error',
          processing_time_ms: processingMs,
        });
      } finally {
        // Clean up all temp files
        for (const tempPath of tempPaths) {
          await cleanupTempFile(tempPath);
        }
      }
    }
  );

  // Advanced extraction with forensic analysis
  app.post(
    '/api/extract/advanced',
    upload.single('file'),
    async (req: AuthRequest, res) => {
      const startTime = Date.now();
      let tempPath: string | null = null;

      try {
        if (!req.file) {
          return sendInvalidRequestError(res, 'No file uploaded');
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);
        const mimeType = req.file.mimetype || 'application/octet-stream';
        const tierConfig = getTierConfig(normalizedTier);

        // Advanced analysis requires Forensic+ tier (bypass in development)
        if (
          process.env.NODE_ENV !== 'development' &&
          !['forensic', 'enterprise'].includes(normalizedTier)
        ) {
          return res.status(403).json({
            error: 'Advanced analysis requires Forensic or Enterprise tier',
            current_tier: normalizedTier,
            required_tier: 'forensic',
            upgrade_message:
              'Upgrade to Forensic tier for advanced analysis capabilities',
          });
        }

        // Validate file type and size
        if (!isFileTypeAllowed(normalizedTier, mimeType)) {
          const requiredTier = getRequiredTierForFileType(mimeType);
          return res.status(403).json({
            error: 'File type not allowed',
            file_type: mimeType,
            required_tier: requiredTier,
          });
        }

        if (!isFileSizeAllowed(normalizedTier, req.file.size)) {
          return res.status(403).json({
            error: 'File size exceeds limit',
            file_size_mb:
              Math.round((req.file.size / (1024 * 1024)) * 100) / 100,
            max_size_mb: tierConfig.maxFileSizeMB,
          });
        }

        // Write file to temp location
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });
        tempPath = path.join(
          tempDir,
          `${Date.now()}-${crypto.randomUUID()}-${req.file.originalname}`
        );
        await fs.writeFile(tempPath, req.file.buffer);

        // Extract with advanced analysis enabled
        const rawMetadata = await extractMetadataWithPython(
          tempPath,
          pythonTier,
          true,
          true, // Enable advanced analysis
          req.query.store === 'true'
        );

        const processingMs = Date.now() - startTime;
        rawMetadata.extraction_info.processing_ms = processingMs;

        const metadata = transformMetadataForFrontend(
          rawMetadata,
          req.file.originalname,
          normalizedTier
        );

        // Calculate forensic score
        let forensicScore = 100;
        if (rawMetadata.steganography_analysis?.suspicious_score) {
          forensicScore -=
            rawMetadata.steganography_analysis.suspicious_score * 30;
        }
        if (rawMetadata.manipulation_detection?.manipulation_probability) {
          forensicScore -=
            rawMetadata.manipulation_detection.manipulation_probability * 50;
        }
        if (rawMetadata.ai_detection?.ai_probability) {
          forensicScore -= rawMetadata.ai_detection.ai_probability * 20;
        }

        metadata.advanced_analysis = {
          enabled: true,
          processing_time_ms: processingMs,
          modules_run: [
            'steganography_detection',
            'manipulation_detection',
            'ai_detection',
            'timeline_analysis',
          ],
          forensic_score: Math.max(0, Math.round(forensicScore)),
          authenticity_assessment:
            forensicScore > 80
              ? 'authentic'
              : forensicScore > 50
                ? 'questionable'
                : 'suspicious',
        };

        res.json(metadata);
      } catch (error) {
        console.error('Advanced extraction error:', error);
        res.status(500).json({
          error: 'Advanced analysis failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        await cleanupTempFile(tempPath);
      }
    }
  );

  // Health check endpoint for Python extraction engine
  app.get('/api/extract/health', async (_req, res) => {
    try {
      // Test the Python extraction engine by running a simple check
      const pythonScript = PYTHON_SCRIPT_PATH;

      // Create a temporary empty file to test with
      const tempDir = '/tmp/metaextract';
      await fs.mkdir(tempDir, { recursive: true });
      const testFilePath = path.join(tempDir, 'health_check_test.txt');
      await fs.writeFile(testFilePath, 'health check');
      const args = [pythonScript, testFilePath, '--tier', 'free'];

      const python = spawn(pythonExecutable, args);

      let responded = false;
      const safeRespond = (fn: () => void) => {
        if (responded) return;
        responded = true;
        if (res.headersSent) return;
        fn();
      };

      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });

      python.on('close', async (code: number | null) => {
        if (responded) return;
        // Clean up the test file
        try {
          await fs.unlink(testFilePath);
        } catch (cleanupError) {
          console.error(
            'Failed to clean up health check test file:',
            cleanupError
          );
        }

        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            safeRespond(() =>
              res.json({
                status: 'healthy',
                python_engine: 'available',
                engine_version:
                  result.extraction_info?.engine_version || 'unknown',
                timestamp: new Date().toISOString(),
                message: 'Python extraction engine is responding correctly',
              })
            );
          } catch (parseError) {
            safeRespond(() =>
              res.json({
                status: 'healthy',
                python_engine: 'available',
                timestamp: new Date().toISOString(),
                message:
                  'Python extraction engine is responding but output format may be unexpected',
                warning: 'Could not parse Python output as JSON',
              })
            );
          }
        } else {
          safeRespond(() =>
            res.status(503).json({
              status: 'unhealthy',
              python_engine: 'unavailable',
              error_code: code,
              error_message: stderr || 'Unknown error',
              timestamp: new Date().toISOString(),
              message: 'Python extraction engine is not responding correctly',
            })
          );
        }
      });

      python.on('error', async (err: Error) => {
        if (responded) return;
        // Clean up the test file
        try {
          await fs.unlink(testFilePath);
        } catch (cleanupError) {
          console.error(
            'Failed to clean up health check test file:',
            cleanupError
          );
        }

        safeRespond(() =>
          res.status(503).json({
            status: 'unhealthy',
            python_engine: 'unavailable',
            error: err.message,
            timestamp: new Date().toISOString(),
            message: 'Failed to start Python extraction engine',
          })
        );
      });

      // Set timeout for health check
      const timeoutId = setTimeout(() => {
        if (!python.killed) {
          python.kill();
        }
        // Clean up the test file
        fs.unlink(testFilePath).catch(err =>
          console.error('Failed to clean up health check test file:', err)
        );

        safeRespond(() =>
          res.status(503).json({
            status: 'timeout',
            python_engine: 'unresponsive',
            timestamp: new Date().toISOString(),
            message:
              'Python extraction engine did not respond within timeout period',
          })
        );
      }, EXTRACTION_HEALTH_TIMEOUT_MS);

      python.on('close', () => clearTimeout(timeoutId));
      python.on('error', () => clearTimeout(timeoutId));
    } catch (error) {
      console.error('Health check error:', error);
      sendServiceUnavailableError(
        res,
        'Health check failed with internal error'
      );
    }
  });

  // Full image extraction health check (ensures EXIF/RAW pipeline stays intact)
  app.get('/api/extract/health/image', async (_req, res) => {
    const samplePath =
      process.env.IMAGE_HEALTHCHECK_PATH ||
      path.join(process.cwd(), 'sample_with_meta.jpg');

    try {
      await fs.access(samplePath);
    } catch {
      return res.status(503).json({
        status: 'unhealthy',
        reason: 'sample_not_found',
        samplePath,
        message:
          'Health check sample image is missing; set IMAGE_HEALTHCHECK_PATH or add sample_with_meta.jpg',
      });
    }

    try {
      const raw = await extractMetadataWithPython(
        samplePath,
        'super',
        true,
        true,
        false
      );
      const metadata = transformMetadataForFrontend(
        raw,
        path.basename(samplePath),
        'super'
      );

      const exifCount = metadata.exif ? Object.keys(metadata.exif).length : 0;
      const fieldsExtracted = metadata.fields_extracted || 0;

      return res.json({
        status: 'healthy',
        python_engine: 'available',
        samplePath,
        exif_fields: exifCount,
        fields_extracted: fieldsExtracted,
        engine_version: raw.extraction_info?.engine_version ?? 'unknown',
        timestamp: new Date().toISOString(),
        message:
          'Full image extractor (EXIF/RAW) responded successfully using the sample image.',
      });
    } catch (error) {
      console.error('[HealthCheck] Full image extractor failed:', error);
      return res.status(503).json({
        status: 'unhealthy',
        python_engine: 'error',
        samplePath,
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString(),
      });
    }
  });

  // Retrieve saved extraction result
  app.get(
    '/api/extract/results/:id',
    requireAuth,
    async (req: AuthRequest, res) => {
      try {
        // Verify user owns this result
        const result = await storage.getMetadata(req.params.id);
        if (!result) {
          return res.status(404).json({ error: 'Result not found' });
        }

        // Check if user owns this result
        if (result.userId !== req.user?.id) {
          return res.status(403).json({ error: 'Access denied' });
        }

        res.json(result.metadata);
      } catch (error) {
        console.error('Failed to retrieve metadata:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  );
}

export { extractMetadataWithPython, transformMetadataForFrontend };
