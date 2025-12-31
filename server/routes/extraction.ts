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
import { storage } from '../storage';
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

// ============================================================================
// Types
// ============================================================================

interface PythonMetadataResponse {
  extraction_info: {
    timestamp: string;
    tier: string;
    engine_version: string;
    libraries: Record<string, boolean>;
    fields_extracted: number;
    locked_categories: number;
    processing_ms?: number;
  };
  file: {
    path: string;
    name: string;
    stem: string;
    extension: string;
    mime_type: string;
  };
  summary: Record<string, any>;
  filesystem: Record<string, any>;
  hashes: Record<string, any>;
  image: Record<string, any> | null;
  exif: Record<string, any> | null;
  gps: Record<string, any> | null;
  video: Record<string, any> | null;
  audio: Record<string, any> | null;
  pdf: Record<string, any> | null;
  svg: Record<string, any> | null;
  extended_attributes: Record<string, any> | null;
  calculated: Record<string, any>;
  forensic: Record<string, any>;
  makernote: Record<string, any> | null;
  iptc: Record<string, any> | null;
  xmp: Record<string, any> | null;
  normalized?: Record<string, any> | null;
  web_metadata?: Record<string, any> | null;
  social_media?: Record<string, any> | null;
  mobile_metadata?: Record<string, any> | null;
  forensic_security?: Record<string, any> | null;
  action_camera?: Record<string, any> | null;
  print_publishing?: Record<string, any> | null;
  workflow_dam?: Record<string, any> | null;
  audio_advanced?: Record<string, any> | null;
  video_advanced?: Record<string, any> | null;
  steganography_analysis?: Record<string, any> | null;
  manipulation_detection?: Record<string, any> | null;
  ai_detection?: Record<string, any> | null;
  timeline_analysis?: Record<string, any> | null;
  iptc_raw?: Record<string, any> | null;
  xmp_raw?: Record<string, any> | null;
  thumbnail?: Record<string, any> | null;
  perceptual_hashes?: Record<string, any> | null;
  locked_fields: string[];
  burned_metadata?: Record<string, any> | null;
  metadata_comparison?: Record<string, any> | null;
  error?: string;
}

interface FrontendMetadataResponse {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  tier: string;
  fields_extracted: number;
  fields_available: number;
  processing_ms: number;
  file_integrity: Record<string, string>;
  filesystem: Record<string, any>;
  calculated: Record<string, any>;
  gps: Record<string, any> | null;
  summary: Record<string, any>;
  forensic: Record<string, any>;
  exif: Record<string, any>;
  image: Record<string, any> | null;
  video: Record<string, any> | null;
  audio: Record<string, any> | null;
  pdf: Record<string, any> | null;
  svg: Record<string, any> | null;
  makernote: Record<string, any> | null;
  iptc: Record<string, any> | null;
  xmp: Record<string, any> | null;
  normalized?: Record<string, any> | null;
  locked_fields: string[];
  extraction_info: Record<string, any>;
  advanced_analysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  };
  [key: string]: any;
}

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

const trialUsageByEmail = new Map<string, { usedAt: number; ip?: string }>();

function normalizeEmail(email: string | null | undefined): string | null {
  if (!email || typeof email !== 'string') return null;
  const trimmed = email.trim().toLowerCase();
  return trimmed.length > 3 && trimmed.includes('@') ? trimmed : null;
}

function getSessionId(req: AuthRequest): string | null {
  const bodySession =
    typeof req.body?.session_id === 'string' ? req.body.session_id : null;
  const querySession =
    typeof req.query?.session_id === 'string' ? req.query.session_id : null;
  const headerSession = typeof req.headers['x-session-id'] === 'string'
    ? req.headers['x-session-id']
    : null;
  return bodySession || querySession || headerSession || null;
}

// ============================================================================
// Helper Functions
// ============================================================================

function transformMetadataForFrontend(
  raw: PythonMetadataResponse,
  originalFilename: string,
  tier: string
): FrontendMetadataResponse {
  const normalizedTier = normalizeTier(tier);
  const fieldsAvailableByTier: Record<string, number> = {
    free: 200,
    professional: 1000,
    forensic: 15000,
    enterprise: 45000,
  };
  const fieldsAvailable = fieldsAvailableByTier[normalizedTier] ?? 45000;

  return {
    filename: originalFilename,
    filesize: raw.filesystem?.size_human || raw.summary?.filesize || 'Unknown',
    filetype:
      raw.file?.extension?.toUpperCase().replace('.', '') ||
      raw.summary?.filetype ||
      'Unknown',
    mime_type:
      raw.file?.mime_type ||
      raw.summary?.mime_type ||
      'application/octet-stream',
    tier: tier,
    fields_extracted: raw.extraction_info?.fields_extracted || 0,
    fields_available: fieldsAvailable,
    processing_ms: raw.extraction_info?.processing_ms || 0,
    file_integrity: raw.hashes?._locked ? { _locked: true } : raw.hashes || {},
    filesystem: raw.filesystem || {},
    calculated: raw.calculated || {},
    gps: raw.gps,
    summary: { ...raw.summary, filename: originalFilename },
    forensic: raw.forensic || {},
    exif: raw.exif || {},
    image: raw.image,
    video: raw.video,
    audio: raw.audio,
    pdf: raw.pdf,
    svg: raw.svg,
    makernote: raw.makernote,
    iptc: raw.iptc,
    xmp: raw.xmp,
    normalized: raw.normalized,
    web_metadata: raw.web_metadata ?? null,
    social_media: raw.social_media ?? null,
    mobile_metadata: raw.mobile_metadata ?? null,
    forensic_security: raw.forensic_security ?? null,
    action_camera: raw.action_camera ?? null,
    print_publishing: raw.print_publishing ?? null,
    workflow_dam: raw.workflow_dam ?? null,
    audio_advanced: raw.audio_advanced ?? null,
    video_advanced: raw.video_advanced ?? null,
    steganography_analysis: raw.steganography_analysis ?? null,
    manipulation_detection: raw.manipulation_detection ?? null,
    ai_detection: raw.ai_detection ?? null,
    timeline_analysis: raw.timeline_analysis ?? null,
    iptc_raw: raw.iptc_raw,
    xmp_raw: raw.xmp_raw,
    thumbnail: raw.thumbnail,
    perceptual_hashes: raw.perceptual_hashes,
    extended_attributes: raw.extended_attributes,
    extended: raw.extended_attributes,
    burned_metadata: raw.burned_metadata ?? null,
    metadata_comparison: raw.metadata_comparison ?? null,
    locked_fields: raw.locked_fields || [],
    extraction_info: raw.extraction_info || {},
  };
}

async function extractMetadataWithPython(
  filePath: string,
  tier: string,
  includePerformanceMetrics: boolean = false,
  enableAdvancedAnalysis: boolean = false,
  storeMetadata: boolean = false
): Promise<PythonMetadataResponse> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(
      __dirname,
      '..',
      'extractor',
      'comprehensive_metadata_engine.py'
    );

    const args = [pythonScript, filePath, '--tier', tier];

    if (includePerformanceMetrics) {
      args.push('--performance');
    }

    if (enableAdvancedAnalysis) {
      args.push('--advanced');
    }

    if (storeMetadata) {
      args.push('--store');
    }

    const python = spawn('python3', args);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        console.error('Comprehensive Python extractor error:', stderr);
        reject(
          new Error(
            `Comprehensive Python extractor failed: ${stderr || 'Unknown error'}`
          )
        );
        return;
      }

      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        console.error('Failed to parse comprehensive Python output:', e);
        console.error('Raw output:', stdout.substring(0, 500));
        reject(
          new Error('Failed to parse comprehensive metadata extraction result')
        );
      }
    });

    python.on('error', (err) => {
      console.error('Failed to spawn comprehensive Python:', err);
      reject(
        new Error(
          `Failed to start comprehensive Python extractor: ${err.message}`
        )
      );
    });

    // Timeout after 180 seconds
    setTimeout(() => {
      python.kill();
      reject(new Error('Comprehensive metadata extraction timed out'));
    }, 180000);
  });
}

async function cleanupTempFile(tempPath: string | null): Promise<void> {
  if (tempPath) {
    try {
      await fs.unlink(tempPath);
    } catch (error) {
      console.error('Failed to delete temp file:', error);
    }
  }
}

// ============================================================================
// Route Registration
// ============================================================================

export function registerExtractionRoutes(app: Express): void {
  // Main extraction endpoint
  app.post('/api/extract', upload.single('file'), async (req, res) => {
    const startTime = Date.now();
    let tempPath: string | null = null;
    let sessionId: string | null = null;
    let creditCost = 0;
    let chargeCredits = false;
    let trialEmail: string | null = null;
    let creditBalanceId: string | null = null;

    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const requestedTier = (req.query.tier as string) || 'enterprise';
      const normalizedTier = normalizeTier(requestedTier);
      const pythonTier = toPythonTier(normalizedTier);
      const mimeType = req.file.mimetype || 'application/octet-stream';
      const tierConfig = getTierConfig(normalizedTier);
      sessionId = getSessionId(req);
      trialEmail = normalizeEmail(req.body?.trial_email);
      creditCost = getCreditCost(mimeType);

      // Validate file type for tier
      if (!isFileTypeAllowed(normalizedTier, mimeType)) {
        const requiredTier = getRequiredTierForFileType(mimeType);
        return res.status(403).json({
          error: 'File type not allowed for your plan',
          file_type: mimeType,
          current_tier: normalizedTier,
          required_tier: requiredTier,
          upgrade_message: `Upgrade to ${
            TIER_CONFIGS[requiredTier].displayName
          } (${TIER_CONFIGS[requiredTier].priceLabel}) to process ${
            mimeType.split('/')[0]
          } files`,
        });
      }

      const hasTrialAvailable = !!trialEmail && !trialUsageByEmail.has(trialEmail);

      if (!hasTrialAvailable) {
        if (!sessionId) {
          return res.status(402).json({
            error: 'Payment required',
            message: 'Purchase credits to unlock a full report.',
            required_credits: creditCost,
          });
        }

        const balance = await storage.getOrCreateCreditBalance(sessionId);
        creditBalanceId = balance.id;
        if (balance.credits < creditCost) {
          return res.status(402).json({
            error: 'Insufficient credits',
            required: creditCost,
            available: balance.credits,
          });
        }

        chargeCredits = true;
      }

      // Validate file size for tier
      if (!isFileSizeAllowed(normalizedTier, req.file.size)) {
        return res.status(403).json({
          error: 'File size exceeds plan limit',
          file_size_mb: Math.round((req.file.size / (1024 * 1024)) * 100) / 100,
          max_size_mb: tierConfig.maxFileSizeMB,
          current_tier: normalizedTier,
          upgrade_message: `Upgrade to a higher plan for larger file support`,
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

      // Extract metadata
      const rawMetadata = await extractMetadataWithPython(
        tempPath,
        pythonTier,
        true,
        true,
        req.query.store === 'true'
      );

      const processingMs = Date.now() - startTime;
      rawMetadata.extraction_info.processing_ms = processingMs;

      const metadata = transformMetadataForFrontend(
        rawMetadata,
        req.file.originalname,
        normalizedTier
      );
      metadata.access = {
        trial_email_present: !!trialEmail,
        trial_granted: hasTrialAvailable ? true : false,
        credits_charged: chargeCredits ? creditCost : 0,
        credits_required: creditCost,
      };

      // Log analytics
      const fileExt =
        path.extname(req.file.originalname).toLowerCase().slice(1) || 'unknown';
      storage
        .logExtractionUsage({
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
        })
          .catch((err) => console.error('Failed to log usage:', err));

      if (chargeCredits && creditBalanceId) {
        storage
          .useCredits(
            creditBalanceId,
            creditCost,
            `Extraction: ${fileExt}`,
            mimeType
          )
          .catch((err) => console.error('Failed to use credits:', err));
      }

      if (hasTrialAvailable && trialEmail) {
        trialUsageByEmail.set(trialEmail, {
          usedAt: Date.now(),
          ip: req.ip || req.socket.remoteAddress || undefined,
        });
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
          .catch((err) => console.error('Failed to log usage:', err));
      }

      res.status(500).json({
        error: 'Failed to extract metadata',
        details: failureReason,
      });
    } finally {
      await cleanupTempFile(tempPath);
    }
  });

  // Batch processing endpoint
  app.post(
    '/api/extract/batch',
    upload.array('files', 100),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (
          !req.files ||
          !Array.isArray(req.files) ||
          req.files.length === 0
        ) {
          return res.status(400).json({ error: 'No files uploaded' });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);
        const tierConfig = getTierConfig(normalizedTier);

        // Check if tier supports batch processing
        if (!tierConfig.features.batchUpload) {
          return res.status(403).json({
            error: 'Batch processing not available for your plan',
            current_tier: normalizedTier,
            required_tier: 'forensic',
            upgrade_message:
              'Upgrade to Forensic or Enterprise for batch processing',
          });
        }

        // Validate all files first
        for (const file of req.files) {
          const mimeType = file.mimetype || 'application/octet-stream';

          if (!isFileTypeAllowed(normalizedTier, mimeType)) {
            const requiredTier = getRequiredTierForFileType(mimeType);
            return res.status(403).json({
              error: `File type not allowed: ${file.originalname}`,
              file_type: mimeType,
              current_tier: normalizedTier,
              required_tier: requiredTier,
            });
          }

          if (!isFileSizeAllowed(normalizedTier, file.size)) {
            return res.status(403).json({
              error: `File size exceeds limit: ${file.originalname}`,
              file_size_mb:
                Math.round((file.size / (1024 * 1024)) * 100) / 100,
              max_size_mb: tierConfig.maxFileSizeMB,
            });
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
        const pythonScript = path.join(
          __dirname,
          '..',
          'extractor',
          'comprehensive_metadata_engine.py'
        );
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
          const python = spawn('python3', pythonArgs);

          let stdout = '';
          let stderr = '';

          python.stdout.on('data', (data) => {
            stdout += data.toString();
          });

          python.stderr.on('data', (data) => {
            stderr += data.toString();
          });

          python.on('close', (code) => {
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
          const result = batchResults.results[fileInfo.tempPath];
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
  app.post('/api/extract/advanced', upload.single('file'), async (req, res) => {
    const startTime = Date.now();
    let tempPath: string | null = null;

    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const requestedTier = (req.query.tier as string) || 'enterprise';
      const normalizedTier = normalizeTier(requestedTier);
      const pythonTier = toPythonTier(normalizedTier);
      const mimeType = req.file.mimetype || 'application/octet-stream';
      const tierConfig = getTierConfig(normalizedTier);

      // Advanced analysis requires Forensic+ tier
      if (!['forensic', 'enterprise'].includes(normalizedTier)) {
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
          file_size_mb: Math.round((req.file.size / (1024 * 1024)) * 100) / 100,
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
        forensicScore -= rawMetadata.steganography_analysis.suspicious_score * 30;
      }
      if (rawMetadata.manipulation_detection?.manipulation_probability) {
        forensicScore -= rawMetadata.manipulation_detection.manipulation_probability * 50;
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
  });
}

export { extractMetadataWithPython, transformMetadataForFrontend };
