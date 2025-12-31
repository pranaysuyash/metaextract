import type { Express, Response } from 'express';
import { createServer, type Server } from 'http';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { spawn } from 'child_process';
import { storage } from './storage';

// Helper function to get current directory (ES module compatible)
function getCurrentDir(): string {
  return dirname(fileURLToPath(import.meta.url));
}
import {
  getTierConfig,
  isFileTypeAllowed,
  isFileSizeAllowed,
  getRequiredTierForFileType,
  TIER_CONFIGS,
  normalizeTier,
  toPythonTier,
  CREDIT_PACKS,
  getRateLimits,
} from '@shared/tierConfig';
import { registerPaymentRoutes } from './payments';
import { registerForensicRoutes } from './routes/forensic';
import { type AuthRequest, getEffectiveTier } from './auth';

// ============================================================================
// Enhanced Python Metadata Engine Integration
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

// Frontend-compatible format
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
  extended_attributes: Record<string, any> | null;
  extended?: Record<string, any> | null;
  burned_metadata?: Record<string, any> | null;
  metadata_comparison?: Record<string, any> | null;
  locked_fields: string[];
  extraction_info: Record<string, any>;
  advanced_analysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  };
}

function transformMetadataForFrontend(
  raw: PythonMetadataResponse,
  originalFilename: string,
  tier: string
): FrontendMetadataResponse {
  // Count total available fields based on comprehensive engine capabilities
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

    // File integrity / hashes
    file_integrity: raw.hashes?._locked ? { _locked: true } : raw.hashes || {},

    // Filesystem details
    filesystem: raw.filesystem || {},

    // Calculated/inferred fields
    calculated: raw.calculated || {},

    // GPS data
    gps: raw.gps,

    // Summary (quick overview)
    summary: {
      ...raw.summary,
      filename: originalFilename,
    },

    // Forensic details
    forensic: raw.forensic || {},

    // EXIF data
    exif: raw.exif || {},

    // Image properties
    image: raw.image,

    // Video properties
    video: raw.video,

    // Audio properties
    audio: raw.audio,

    // PDF properties
    pdf: raw.pdf,

    // SVG properties
    svg: raw.svg,

    // MakerNote (vendor-specific)
    makernote: raw.makernote,

    // IPTC metadata
    iptc: raw.iptc,

    // XMP metadata
    xmp: raw.xmp,

    // Normalized/search fields
    normalized: raw.normalized,

    // Optional analysis categories
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

    // Raw IPTC/XMP (fallback)
    iptc_raw: raw.iptc_raw,
    xmp_raw: raw.xmp_raw,

    // Image-derived extras
    thumbnail: raw.thumbnail,
    perceptual_hashes: raw.perceptual_hashes,

    // Extended attributes
    extended_attributes: raw.extended_attributes,
    extended: raw.extended_attributes,

    // Burned-in overlay metadata (OCR)
    burned_metadata: raw.burned_metadata ?? null,
    metadata_comparison: raw.metadata_comparison ?? null,

    // Locked fields list
    locked_fields: raw.locked_fields || [],

    // Full extraction info
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
    // Use comprehensive metadata engine for configurable comprehensive field support
    const currentDir = getCurrentDir();
    const pythonScript = path.join(
      currentDir,
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
            `Comprehensive Python extractor failed: ${
              stderr || 'Unknown error'
            }`
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

    // Timeout after 180 seconds (increased for comprehensive analysis)
    setTimeout(() => {
      python.kill();
      reject(new Error('Comprehensive metadata extraction timed out'));
    }, 180000);
  });
}

async function runMetadataDbCli(args: string[]): Promise<any> {
  return new Promise((resolve, reject) => {
    const currentDir = getCurrentDir();
    const pythonScript = path.join(
      currentDir,
      'extractor',
      'metadata_db_cli.py'
    );
    const python = spawn('python3', [pythonScript, ...args]);

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
        reject(new Error(stderr || 'metadata db cli failed'));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (error) {
        reject(new Error('failed to parse metadata db cli output'));
      }
    });

    python.on('error', (err) => {
      reject(new Error(`failed to start metadata db cli: ${err.message}`));
    });

    setTimeout(() => {
      python.kill();
      reject(new Error('metadata db cli timed out'));
    }, 15000);
  });
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
// API Routes
// ============================================================================

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  // Batch processing endpoint (Forensic/Enterprise tiers)
  app.post(
    '/api/extract/batch',
    upload.array('files', 100),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length === 0) {
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
              file_size_mb: Math.round((file.size / (1024 * 1024)) * 100) / 100,
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

        // Process batch using enhanced Python engine
        const currentDir = getCurrentDir();
        const pythonScript = path.join(
          currentDir,
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
        const transformedResults = {};
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

        // Log batch analytics
        for (const fileInfo of fileInfos) {
          const fileExt =
            path.extname(fileInfo.originalName).toLowerCase().slice(1) ||
            'unknown';
          storage
            .logExtractionUsage({
              tier: normalizedTier,
              fileExtension: fileExt,
              mimeType: fileInfo.mimeType || 'application/octet-stream',
              fileSizeBytes: fileInfo.size,
              isVideo: fileInfo.mimeType?.startsWith('video/') || false,
              isImage: fileInfo.mimeType?.startsWith('image/') || false,
              isPdf: fileInfo.mimeType === 'application/pdf',
              isAudio: fileInfo.mimeType?.startsWith('audio/') || false,
              fieldsExtracted: 0, // Will be updated per file
              processingMs: processingMs / fileInfos.length, // Average per file
              success: true,
              ipAddress: req.ip || req.socket.remoteAddress || null,
              userAgent: req.headers['user-agent'] || null,
            })
            .catch((err) => console.error('Failed to log batch usage:', err));
        }

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
          try {
            await fs.unlink(tempPath);
          } catch (error) {
            console.error('Failed to delete temp file:', tempPath, error);
          }
        }
      }
    }
  );

  // Main extraction endpoint
  app.post('/api/extract', upload.single('file'), async (req, res) => {
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

      // Extract metadata using Comprehensive Python engine (v4.0)
      const rawMetadata = await extractMetadataWithPython(
        tempPath,
        pythonTier,
        true,
        true,
        req.query.store === 'true'
      );

      // Calculate processing time and add to raw metadata
      const processingMs = Date.now() - startTime;
      rawMetadata.extraction_info.processing_ms = processingMs;

      // Transform for frontend
      const metadata = transformMetadataForFrontend(
        rawMetadata,
        req.file.originalname,
        normalizedTier
      );

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
      // Clean up temp file
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (error) {
          console.error('Failed to delete temp file:', error);
        }
      }
    }
  });

  // Tier configuration endpoints
  app.get('/api/tiers', (req, res) => {
    res.json(TIER_CONFIGS);
  });

  app.get('/api/tiers/:tier', (req, res) => {
    const tierConfig = getTierConfig(req.params.tier);
    res.json(tierConfig);
  });

  // Field information endpoint
  app.get('/api/fields', (req, res) => {
    res.json({
      total_possible_fields: 'configurable',
      comprehensive_engine_version: '4.0.0',
      tiers: {
        free: {
          fields: '~200',
          categories: [
            'summary',
            'basic_exif',
            'basic_image',
            'gps',
            'hashes',
            'calculated',
          ],
          file_types: ['Images (JPEG, PNG, GIF, WebP)'],
          max_size_mb: 10,
          locked: [
            'makernote',
            'iptc',
            'xmp',
            'extended_attributes',
            'serial_numbers',
            'video',
            'audio',
            'pdf',
            'advanced_analysis',
          ],
        },
        professional: {
          fields: '~1000',
          categories: [
            'summary',
            'exif',
            'image',
            'gps',
            'filesystem',
            'hashes',
            'calculated',
            'forensic',
            'audio',
            'pdf',
          ],
          file_types: ['Images + RAW + HEIC'],
          max_size_mb: 100,
          locked: [
            'video',
            'audio',
            'pdf',
            'advanced_analysis',
            'timeline_analysis',
          ],
        },
        forensic: {
          fields: '~15000',
          categories: ['all_fields'],
          file_types: ['Images + RAW + Video + Audio + PDF + SVG'],
          max_size_mb: 500,
          locked: [
            'medical_imaging',
            'astronomical_data',
            'scientific_data',
            'blockchain_provenance',
          ],
        },
        enterprise: {
          fields: 'configurable',
          categories: ['all_fields', 'batch_processing', 'api_access'],
          file_types: ['All file types'],
          max_size_mb: 2000,
          locked: [],
        },
      },
      categories: {
        summary: 'Basic file information (name, size, type)',
        exif: 'Camera settings, dates, software',
        image: 'Resolution, color mode, format details',
        gps: 'GPS coordinates with Google Maps links',
        filesystem: 'Permissions, ownership, timestamps',
        hashes: 'MD5, SHA256, SHA1, CRC32 checksums',
        calculated: 'Aspect ratio, megapixels, file age',
        forensic: 'Device identification, modification detection',
        makernote: 'Vendor-specific camera data (Canon, Nikon, Sony, etc.)',
        iptc: 'News/photo agency metadata (copyright, keywords, captions)',
        xmp: 'Adobe metadata (editing history, keywords)',
        video: 'Codec, streams, chapters, HDR metadata',
        audio: 'Tags, album art, bitrate, format details',
        pdf: 'Pages, author, encryption, forms',
        svg: 'Elements, viewBox, scripts detection',
        extended_attributes: 'macOS Finder tags, Spotlight metadata',
        normalized: 'Normalized/searchable fields (camera/lens/exposure)',
        web_metadata: 'Open Graph, schema.org, and web metadata',
        social_media: 'Platform-specific social metadata',
        mobile_metadata: 'Smartphone computational photography fields',
        forensic_security: 'C2PA, signatures, provenance indicators',
        action_camera: 'GoPro/Action cam specific tags',
        print_publishing: 'Print/publishing workflow metadata',
        workflow_dam: 'DAM/workflow metadata',
        audio_advanced: 'ReplayGain and advanced audio analysis',
        video_advanced: 'HDR and professional video analysis',
        steganography_analysis: 'Hidden data detection signals',
        manipulation_detection: 'Tampering detection indicators',
        ai_detection: 'AI-generated content indicators',
        timeline_analysis: 'Forensic timeline reconstruction',
      },
    });
  });

  // Metadata search/storage endpoints
  app.get('/api/metadata/search', async (req, res) => {
    try {
      const query = (req.query.q || req.query.query) as string | undefined;
      if (!query) {
        return res.status(400).json({ error: 'query required' });
      }
      const limit = req.query.limit ? Number(req.query.limit) : 100;
      const offset = req.query.offset ? Number(req.query.offset) : 0;
      const results = await runMetadataDbCli([
        'search',
        '--query',
        query,
        '--limit',
        String(limit),
        '--offset',
        String(offset),
      ]);
      res.json(results);
    } catch (error) {
      res.status(500).json({ error: 'metadata search failed' });
    }
  });

  app.get('/api/metadata/history', async (req, res) => {
    try {
      const fileId = req.query.file_id as string | undefined;
      const filePath = req.query.file_path as string | undefined;
      if (!fileId && !filePath) {
        return res.status(400).json({ error: 'file_id or file_path required' });
      }
      const args = ['history'];
      if (fileId) {
        args.push('--file-id', fileId);
      } else if (filePath) {
        args.push('--file-path', filePath);
      }
      const history = await runMetadataDbCli(args);
      res.json(history);
    } catch (error) {
      res.status(500).json({ error: 'history lookup failed' });
    }
  });

  app.get('/api/metadata/stats', async (req, res) => {
    try {
      const stats = await runMetadataDbCli(['stats']);
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: 'metadata stats failed' });
    }
  });

  app.get('/api/metadata/favorites', async (req, res) => {
    try {
      const favorites = await runMetadataDbCli(['favorites', '--list']);
      res.json(favorites);
    } catch (error) {
      res.status(500).json({ error: 'favorites lookup failed' });
    }
  });

  app.post('/api/metadata/favorites', async (req, res) => {
    try {
      const { file_id, notes, tags } = req.body || {};
      if (!file_id) {
        return res.status(400).json({ error: 'file_id required' });
      }
      const args = ['favorites', '--toggle', '--file-id', String(file_id)];
      if (notes) {
        args.push('--notes', String(notes));
      }
      if (tags && Array.isArray(tags)) {
        args.push('--tags', tags.join(','));
      } else if (typeof tags === 'string') {
        args.push('--tags', tags);
      }
      const result = await runMetadataDbCli(args);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: 'favorites toggle failed' });
    }
  });

  app.get('/api/metadata/similar', async (req, res) => {
    try {
      const phash = req.query.phash as string | undefined;
      if (!phash) {
        return res.status(400).json({ error: 'phash required' });
      }
      const threshold = req.query.threshold ? Number(req.query.threshold) : 5;
      const limit = req.query.limit ? Number(req.query.limit) : 20;
      const result = await runMetadataDbCli([
        'similar',
        '--phash',
        phash,
        '--threshold',
        String(threshold),
        '--limit',
        String(limit),
      ]);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: 'similarity search failed' });
    }
  });

  // ============================================================================
  // Advanced Forensic Analysis Endpoints
  // ============================================================================

  // Advanced single file extraction with forensic analysis
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

      // Check if tier supports advanced analysis (disabled in dev)
      if (process.env.NODE_ENV !== 'development' && normalizedTier === 'free') {
        return res.status(403).json({
          error: 'Advanced analysis not available for your plan',
          current_tier: normalizedTier,
          required_tier: 'professional',
          upgrade_message:
            'Upgrade to Professional or higher for advanced analysis capabilities',
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

      res.json({
        ...metadata,
        advanced_analysis: {
          enabled: true,
          modules_run: [
            'steganography_detection',
            'manipulation_detection',
            'ai_detection',
            'timeline_analysis',
          ],
        },
      });
    } catch (error) {
      console.error('Advanced extraction error:', error);
      res.status(500).json({
        error: 'Advanced analysis failed',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (error) {
          console.error('Failed to delete temp file:', error);
        }
      }
    }
  });

  // Batch metadata comparison endpoint
  app.post(
    '/api/compare/batch',
    upload.array('files', 10),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length < 2) {
          return res
            .status(400)
            .json({ error: 'At least 2 files required for comparison' });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);

        // Check tier supports comparison (disabled in dev)
        if (
          process.env.NODE_ENV !== 'development' &&
          !['professional', 'forensic', 'enterprise'].includes(normalizedTier)
        ) {
          return res.status(403).json({
            error: 'Metadata comparison requires Professional or higher tier',
            current_tier: normalizedTier,
            required_tier: 'professional',
          });
        }

        // Write files to temp
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
          fileInfos.push({ tempPath, originalName: file.originalname });
        }

        // Extract metadata for all files
        const metadataResults: Record<string, any> = {};
        for (const fileInfo of fileInfos) {
          const rawMetadata = await extractMetadataWithPython(
            fileInfo.tempPath,
            pythonTier,
            false,
            false,
            false
          );
          metadataResults[fileInfo.originalName] = transformMetadataForFrontend(
            rawMetadata,
            fileInfo.originalName,
            normalizedTier
          );
        }

        // Compare metadata between files
        const fileNames = Object.keys(metadataResults);
        const comparisons: any[] = [];

        for (let i = 0; i < fileNames.length; i++) {
          for (let j = i + 1; j < fileNames.length; j++) {
            const file1 = fileNames[i];
            const file2 = fileNames[j];
            const meta1 = metadataResults[file1];
            const meta2 = metadataResults[file2];

            const differences: any[] = [];
            const allKeys = new Set([
              ...Object.keys(meta1.exif || {}),
              ...Object.keys(meta2.exif || {}),
            ]);

            let matchCount = 0;
            let diffCount = 0;

            for (const key of allKeys) {
              const val1 = meta1.exif?.[key];
              const val2 = meta2.exif?.[key];

              if (val1 === val2) {
                matchCount++;
                differences.push({
                  field: key,
                  file1_value: val1,
                  file2_value: val2,
                  status: 'match',
                });
              } else if (val1 === undefined) {
                diffCount++;
                differences.push({
                  field: key,
                  file1_value: null,
                  file2_value: val2,
                  status: 'only_in_file2',
                });
              } else if (val2 === undefined) {
                diffCount++;
                differences.push({
                  field: key,
                  file1_value: val1,
                  file2_value: null,
                  status: 'only_in_file1',
                });
              } else {
                diffCount++;
                differences.push({
                  field: key,
                  file1_value: val1,
                  file2_value: val2,
                  status: 'different',
                });
              }
            }

            const totalFields = matchCount + diffCount;
            const similarityScore =
              totalFields > 0
                ? Math.round((matchCount / totalFields) * 100)
                : 0;

            comparisons.push({
              file1,
              file2,
              similarity_score: similarityScore,
              matching_fields: matchCount,
              different_fields: diffCount,
              differences: differences.slice(0, 100), // Limit to prevent huge responses
            });
          }
        }

        res.json({
          success: true,
          files_compared: fileNames.length,
          comparisons,
          processing_time_ms: Date.now() - startTime,
        });
      } catch (error) {
        console.error('Comparison error:', error);
        res.status(500).json({
          error: 'Comparison failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        for (const tempPath of tempPaths) {
          try {
            await fs.unlink(tempPath);
          } catch (error) {
            console.error('Failed to delete temp file:', error);
          }
        }
      }
    }
  );

  // Timeline reconstruction endpoint
  app.post(
    '/api/timeline/reconstruct',
    upload.array('files', 50),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length === 0) {
          return res.status(400).json({ error: 'At least 1 file required' });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);

        if (
          process.env.NODE_ENV !== 'development' &&
          !['professional', 'forensic', 'enterprise'].includes(normalizedTier)
        ) {
          return res.status(403).json({
            error:
              'Timeline reconstruction requires Professional or higher tier',
            current_tier: normalizedTier,
            required_tier: 'professional',
          });
        }

        // Write files to temp
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });

        const allEvents: any[] = [];

        for (const file of req.files) {
          const tempPath = path.join(
            tempDir,
            `${Date.now()}-${crypto.randomUUID()}-${file.originalname}`
          );
          await fs.writeFile(tempPath, file.buffer);
          tempPaths.push(tempPath);

          const rawMetadata = await extractMetadataWithPython(
            tempPath,
            pythonTier,
            false,
            false,
            false
          );

          // Extract timeline events from metadata
          const metadata = transformMetadataForFrontend(
            rawMetadata,
            file.originalname,
            normalizedTier
          );

          if (metadata.exif?.DateTimeOriginal) {
            allEvents.push({
              timestamp: metadata.exif.DateTimeOriginal,
              event_type: 'capture',
              source: 'EXIF:DateTimeOriginal',
              file: file.originalname,
            });
          }
          if (metadata.exif?.CreateDate) {
            allEvents.push({
              timestamp: metadata.exif.CreateDate,
              event_type: 'created',
              source: 'EXIF:CreateDate',
              file: file.originalname,
            });
          }
          if (metadata.exif?.ModifyDate) {
            allEvents.push({
              timestamp: metadata.exif.ModifyDate,
              event_type: 'modified',
              source: 'EXIF:ModifyDate',
              file: file.originalname,
            });
          }
          if (metadata.filesystem?.created) {
            allEvents.push({
              timestamp: metadata.filesystem.created,
              event_type: 'file_created',
              source: 'Filesystem',
              file: file.originalname,
            });
          }
          if (metadata.filesystem?.modified) {
            allEvents.push({
              timestamp: metadata.filesystem.modified,
              event_type: 'file_modified',
              source: 'Filesystem',
              file: file.originalname,
            });
          }
        }

        // Sort events chronologically
        allEvents.sort(
          (a, b) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );

        // Detect gaps (events more than 24 hours apart)
        const gaps: any[] = [];
        for (let i = 0; i < allEvents.length - 1; i++) {
          const current = new Date(allEvents[i].timestamp).getTime();
          const next = new Date(allEvents[i + 1].timestamp).getTime();
          const diffMs = next - current;
          const diffHours = diffMs / (1000 * 60 * 60);

          if (diffHours > 24) {
            gaps.push({
              start: allEvents[i].timestamp,
              end: allEvents[i + 1].timestamp,
              duration_hours: Math.round(diffHours),
              duration_readable:
                diffHours > 24
                  ? `${Math.round(diffHours / 24)} days`
                  : `${Math.round(diffHours)} hours`,
              suspicious: diffHours > 168, // More than a week
            });
          }
        }

        res.json({
          success: true,
          files_analyzed: req.files.length,
          events: allEvents,
          gaps,
          chain_of_custody_complete:
            gaps.filter((g) => g.suspicious).length === 0,
          first_event: allEvents[0] || null,
          last_event: allEvents[allEvents.length - 1] || null,
          processing_time_ms: Date.now() - startTime,
        });
      } catch (error) {
        console.error('Timeline reconstruction error:', error);
        res.status(500).json({
          error: 'Timeline reconstruction failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        for (const tempPath of tempPaths) {
          try {
            await fs.unlink(tempPath);
          } catch (error) {
            console.error('Failed to delete temp file:', error);
          }
        }
      }
    }
  );

  // Performance monitoring endpoint
  app.get('/api/performance/stats', async (req, res) => {
    try {
      // Get cache statistics if Redis is available
      const currentDir = getCurrentDir();
      const pythonScript = path.join(
        currentDir,
        'extractor',
        'utils',
        'cache.py'
      );
      const cacheStats = await new Promise<any>((resolve) => {
        const python = spawn('python3', [
          '-c',
          `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from cache import get_cache_stats
import json
print(json.dumps(get_cache_stats()))
        `,
        ]);

        let stdout = '';
        python.stdout.on('data', (data) => (stdout += data.toString()));
        python.on('close', () => {
          try {
            resolve(JSON.parse(stdout));
          } catch {
            resolve({ available: false });
          }
        });

        setTimeout(() => {
          python.kill();
          resolve({ available: false, error: 'timeout' });
        }, 5000);
      });

      res.json({
        cache: cacheStats,
        server: {
          uptime_seconds: process.uptime(),
          memory_usage: process.memoryUsage(),
          node_version: process.version,
          platform: process.platform,
        },
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to get performance stats' });
    }
  });

  // Cache management endpoint (admin only)
  app.post('/api/performance/cache/clear', async (req, res) => {
    try {
      const pattern = req.body.pattern || 'metadata:*';

      const currentDir = getCurrentDir();
      const pythonScript = path.join(
        currentDir,
        'extractor',
        'utils',
        'cache.py'
      );
      const result = await new Promise<number>((resolve) => {
        const python = spawn('python3', [
          '-c',
          `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from cache import clear_cache_pattern
print(clear_cache_pattern('${pattern}'))
        `,
        ]);

        let stdout = '';
        python.stdout.on('data', (data) => (stdout += data.toString()));
        python.on('close', () => {
          resolve(parseInt(stdout.trim()) || 0);
        });

        setTimeout(() => {
          python.kill();
          resolve(0);
        }, 10000);
      });

      res.json({
        success: true,
        cleared_entries: result,
        pattern: pattern,
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to clear cache' });
    }
  });

  // Sample files endpoint for onboarding
  app.get('/api/samples', (req, res) => {
    const samples = [
      {
        id: 'sample_photo',
        name: 'Standard Photo',
        filename: 'sample_photo.jpg',
        description: 'JPEG with basic EXIF data - perfect for beginners',
        size: '2.3 MB',
        type: 'image/jpeg',
        highlights: ['Camera settings', 'Timestamp', 'Resolution'],
        tier_required: 'free',
      },
      {
        id: 'sample_gps',
        name: 'GPS Photo',
        filename: 'sample_gps.jpg',
        description: 'Photo with embedded GPS coordinates',
        size: '3.1 MB',
        type: 'image/jpeg',
        highlights: ['GPS coordinates', 'Google Maps link', 'Location data'],
        tier_required: 'professional',
      },
      {
        id: 'sample_raw',
        name: 'Canon RAW',
        filename: 'sample_raw.cr2',
        description: 'Canon RAW file with extensive MakerNotes',
        size: '24.5 MB',
        type: 'image/x-canon-cr2',
        highlights: ['Canon MakerNotes', 'Lens data', 'Camera serial'],
        tier_required: 'professional',
      },
      {
        id: 'sample_video',
        name: 'Video Sample',
        filename: 'sample_video.mp4',
        description: 'MP4 video with codec and stream information',
        size: '15.2 MB',
        type: 'video/mp4',
        highlights: ['Video codecs', 'Stream data', 'Duration'],
        tier_required: 'forensic',
      },
      {
        id: 'sample_audio',
        name: 'Audio File',
        filename: 'sample_audio.mp3',
        description: 'MP3 with ID3 tags and album art',
        size: '4.8 MB',
        type: 'audio/mpeg',
        highlights: ['ID3 tags', 'Album art', 'Audio quality'],
        tier_required: 'forensic',
      },
      {
        id: 'sample_pdf',
        name: 'PDF Document',
        filename: 'sample_document.pdf',
        description: 'PDF with document metadata and form fields',
        size: '1.2 MB',
        type: 'application/pdf',
        highlights: ['Document info', 'Page count', 'Creation software'],
        tier_required: 'forensic',
      },
    ];

    res.json({
      samples,
      total_count: samples.length,
      description: 'Sample files for demonstrating MetaExtract capabilities',
    });
  });

  // Sample file download endpoint
  app.get('/api/samples/:sampleId/download', async (req, res) => {
    try {
      const sampleId = req.params.sampleId;
      const currentDir = getCurrentDir();
      const samplePath = path.join(
        currentDir,
        'sample-files',
        `${sampleId}.bin`
      );

      // Check if sample file exists
      try {
        await fs.access(samplePath);
      } catch {
        return res.status(404).json({ error: 'Sample file not found' });
      }

      // Get sample info
      const samples = [
        {
          id: 'sample_photo',
          filename: 'sample_photo.jpg',
          type: 'image/jpeg',
        },
        { id: 'sample_gps', filename: 'sample_gps.jpg', type: 'image/jpeg' },
        {
          id: 'sample_raw',
          filename: 'sample_raw.cr2',
          type: 'image/x-canon-cr2',
        },
        { id: 'sample_video', filename: 'sample_video.mp4', type: 'video/mp4' },
        {
          id: 'sample_audio',
          filename: 'sample_audio.mp3',
          type: 'audio/mpeg',
        },
        {
          id: 'sample_pdf',
          filename: 'sample_document.pdf',
          type: 'application/pdf',
        },
      ];

      const sample = samples.find((s) => s.id === sampleId);
      if (!sample) {
        return res.status(404).json({ error: 'Sample not found' });
      }

      res.setHeader('Content-Type', sample.type);
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="${sample.filename}"`
      );

      const fileStream = require('fs').createReadStream(samplePath);
      fileStream.pipe(res);
    } catch (error) {
      console.error('Sample download error:', error);
      res.status(500).json({ error: 'Failed to download sample file' });
    }
  });

  // ============================================================================
  // Advanced Analysis Endpoints (Phase 3)
  // ============================================================================

  // Advanced single file analysis with forensic capabilities
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

      // Advanced analysis requires Professional+ tier (disabled in dev)
      if (process.env.NODE_ENV !== 'development' && normalizedTier === 'free') {
        return res.status(403).json({
          error: 'Advanced analysis not available for your plan',
          current_tier: normalizedTier,
          required_tier: 'professional',
          upgrade_message:
            'Upgrade to Professional or higher for advanced forensic analysis',
        });
      }

      // Validate file type and size
      if (!isFileTypeAllowed(normalizedTier, mimeType)) {
        const requiredTier = getRequiredTierForFileType(mimeType);
        return res.status(403).json({
          error: 'File type not allowed for your plan',
          file_type: mimeType,
          current_tier: normalizedTier,
          required_tier: requiredTier,
        });
      }

      if (!isFileSizeAllowed(normalizedTier, req.file.size)) {
        return res.status(403).json({
          error: 'File size exceeds plan limit',
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

      // Run advanced analysis using comprehensive engine
      const currentDir = getCurrentDir();
      const pythonScript = path.join(
        currentDir,
        'extractor',
        'comprehensive_metadata_engine.py'
      );
      const advancedResult = await new Promise<any>((resolve, reject) => {
        const args = [
          pythonScript,
          tempPath,
          '--tier',
          pythonTier,
          '--advanced',
          '--performance',
        ];

        if (req.query.store === 'true') {
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
            reject(new Error(`Advanced analysis failed: ${stderr}`));
            return;
          }

          try {
            resolve(JSON.parse(stdout));
          } catch (e) {
            reject(new Error('Failed to parse advanced analysis result'));
          }
        });

        // Extended timeout for advanced analysis
        setTimeout(() => {
          python.kill();
          reject(new Error('Advanced analysis timed out'));
        }, 300000); // 5 minutes
      });

      const processingMs = Date.now() - startTime;
      advancedResult.extraction_info.processing_ms = processingMs;

      // Transform for frontend
      const metadata = transformMetadataForFrontend(
        advancedResult,
        req.file.originalname,
        normalizedTier
      );

      // Add advanced analysis summary
      metadata.advanced_analysis = {
        enabled: true,
        processing_time_ms: processingMs,
        modules_run: [],
        forensic_score: 0,
        authenticity_assessment: 'unknown',
      };

      // Extract advanced analysis results
      if (advancedResult.steganography_analysis) {
        metadata.advanced_analysis.modules_run.push('steganography');
        metadata.steganography_analysis = advancedResult.steganography_analysis;
      }

      if (advancedResult.manipulation_detection) {
        metadata.advanced_analysis.modules_run.push('manipulation_detection');
        metadata.manipulation_detection = advancedResult.manipulation_detection;
      }

      if (advancedResult.ai_detection) {
        metadata.advanced_analysis.modules_run.push('ai_detection');
        metadata.ai_detection = advancedResult.ai_detection;
      }

      // Calculate overall forensic score
      let forensicScore = 100;
      if (metadata.steganography_analysis?.suspicious_score) {
        forensicScore -= metadata.steganography_analysis.suspicious_score * 30;
      }
      if (metadata.manipulation_detection?.manipulation_probability) {
        forensicScore -=
          metadata.manipulation_detection.manipulation_probability * 50;
      }
      if (metadata.ai_detection?.ai_probability) {
        forensicScore -= metadata.ai_detection.ai_probability * 20;
      }

      metadata.advanced_analysis.forensic_score = Math.max(
        0,
        Math.round(forensicScore)
      );
      metadata.advanced_analysis.authenticity_assessment =
        forensicScore > 80
          ? 'authentic'
          : forensicScore > 50
          ? 'questionable'
          : 'suspicious';

      res.json(metadata);
    } catch (error) {
      const processingMs = Date.now() - startTime;
      console.error('Advanced analysis error:', error);

      res.status(500).json({
        error: 'Advanced analysis failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        processing_time_ms: processingMs,
      });
    } finally {
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (error) {
          console.error('Failed to delete temp file:', error);
        }
      }
    }
  });

  // Batch metadata comparison endpoint
  app.post(
    '/api/compare/batch',
    upload.array('files', 50),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length < 2) {
          return res.status(400).json({
            error: 'At least 2 files required for comparison',
          });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const tierConfig = getTierConfig(normalizedTier);

        // Comparison requires Professional+ tier (disabled in dev)
        if (
          process.env.NODE_ENV !== 'development' &&
          normalizedTier === 'free'
        ) {
          return res.status(403).json({
            error: 'Batch comparison not available for your plan',
            current_tier: normalizedTier,
            required_tier: 'professional',
          });
        }

        // Validate all files
        for (const file of req.files) {
          const mimeType = file.mimetype || 'application/octet-stream';
          if (!isFileTypeAllowed(normalizedTier, mimeType)) {
            return res.status(403).json({
              error: `File type not allowed: ${file.originalname}`,
              file_type: mimeType,
            });
          }
          if (!isFileSizeAllowed(normalizedTier, file.size)) {
            return res.status(403).json({
              error: `File size exceeds limit: ${file.originalname}`,
            });
          }
        }

        // Write files to temp locations
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
          });
        }

        // Run comparison using Python module
        const currentDir = getCurrentDir();
        const pythonScript = path.join(
          currentDir,
          'extractor',
          'modules',
          'comparison.py'
        );
        const comparisonResult = await new Promise<any>((resolve, reject) => {
          const python = spawn('python3', [
            '-c',
            `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from comparison import compare_metadata_files
from comprehensive_metadata_engine import extract_comprehensive_metadata
import json

# Extract metadata for all files
file_metadata = []
filepaths = ${JSON.stringify(tempPaths)}
for filepath in filepaths:
    try:
        metadata = extract_comprehensive_metadata(filepath, tier='${toPythonTier(
          normalizedTier
        )}')
        file_metadata.append(metadata)
    except Exception as e:
        print(f"Error extracting {filepath}: {e}", file=sys.stderr)

# Compare metadata
if len(file_metadata) >= 2:
    comparison = compare_metadata_files(file_metadata, comparison_mode="detailed")
    print(json.dumps(comparison))
else:
    print(json.dumps({"error": "Insufficient metadata extracted"}))
          `,
          ]);

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
              reject(new Error(`Comparison failed: ${stderr}`));
              return;
            }

            try {
              resolve(JSON.parse(stdout));
            } catch (e) {
              reject(new Error('Failed to parse comparison result'));
            }
          });

          setTimeout(() => {
            python.kill();
            reject(new Error('Comparison timed out'));
          }, 120000); // 2 minutes
        });

        const processingMs = Date.now() - startTime;

        res.json({
          success: true,
          comparison_id: crypto.randomUUID(),
          total_files: fileInfos.length,
          processing_time_ms: processingMs,
          file_names: fileInfos.map((f) => f.originalName),
          comparison_result: comparisonResult,
        });
      } catch (error) {
        console.error('Batch comparison error:', error);
        res.status(500).json({
          error: 'Batch comparison failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        for (const tempPath of tempPaths) {
          try {
            await fs.unlink(tempPath);
          } catch (error) {
            console.error('Failed to delete temp file:', tempPath, error);
          }
        }
      }
    }
  );

  // Timeline reconstruction endpoint
  app.post(
    '/api/timeline/reconstruct',
    upload.array('files', 100),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length === 0) {
          return res.status(400).json({
            error: 'No files uploaded for timeline reconstruction',
          });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);

        // Timeline reconstruction requires Professional+ tier (disabled in dev)
        if (
          process.env.NODE_ENV !== 'development' &&
          normalizedTier === 'free'
        ) {
          return res.status(403).json({
            error: 'Timeline reconstruction not available for your plan',
            current_tier: normalizedTier,
            required_tier: 'professional',
          });
        }

        // Write files to temp locations
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
          });
        }

        // Run timeline reconstruction
        const currentDir = getCurrentDir();
        const pythonScript = path.join(
          currentDir,
          'extractor',
          'modules',
          'timeline.py'
        );
        const timelineResult = await new Promise<any>((resolve, reject) => {
          const python = spawn('python3', [
            '-c',
            `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from timeline import reconstruct_timeline
from comprehensive_metadata_engine import extract_comprehensive_metadata
import json

# Extract metadata for all files
file_metadata = []
filepaths = ${JSON.stringify(tempPaths)}
for filepath in filepaths:
    try:
        metadata = extract_comprehensive_metadata(filepath, tier='${toPythonTier(
          normalizedTier
        )}')
        file_metadata.append(metadata)
    except Exception as e:
        print(f"Error extracting {filepath}: {e}", file=sys.stderr)

# Reconstruct timeline
if file_metadata:
    timeline = reconstruct_timeline(file_metadata, analysis_mode="comprehensive")
    print(json.dumps(timeline))
else:
    print(json.dumps({"error": "No metadata extracted"}))
          `,
          ]);

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
              reject(new Error(`Timeline reconstruction failed: ${stderr}`));
              return;
            }

            try {
              resolve(JSON.parse(stdout));
            } catch (e) {
              reject(new Error('Failed to parse timeline result'));
            }
          });

          setTimeout(() => {
            python.kill();
            reject(new Error('Timeline reconstruction timed out'));
          }, 180000); // 3 minutes
        });

        const processingMs = Date.now() - startTime;

        res.json({
          success: true,
          timeline_id: crypto.randomUUID(),
          total_files: fileInfos.length,
          processing_time_ms: processingMs,
          file_names: fileInfos.map((f) => f.originalName),
          timeline: timelineResult,
        });
      } catch (error) {
        console.error('Timeline reconstruction error:', error);
        res.status(500).json({
          error: 'Timeline reconstruction failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        for (const tempPath of tempPaths) {
          try {
            await fs.unlink(tempPath);
          } catch (error) {
            console.error('Failed to delete temp file:', tempPath, error);
          }
        }
      }
    }
  );

  // Comprehensive forensic report endpoint
  app.post(
    '/api/forensic/report',
    upload.array('files', 100),
    async (req, res) => {
      const startTime = Date.now();
      const tempPaths: string[] = [];

      try {
        if (!req.files || !Array.isArray(req.files) || req.files.length === 0) {
          return res.status(400).json({
            error: 'No files uploaded for forensic analysis',
          });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);

        // Forensic reports require Enterprise tier (disabled in dev)
        if (
          process.env.NODE_ENV !== 'development' &&
          normalizedTier !== 'enterprise'
        ) {
          return res.status(403).json({
            error: 'Forensic reports not available for your plan',
            current_tier: normalizedTier,
            required_tier: 'enterprise',
            upgrade_message:
              'Upgrade to Enterprise tier for professional forensic reports',
          });
        }

        // Process files and generate comprehensive forensic report
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
          });
        }

        // Generate comprehensive forensic analysis
        const reportResult = await new Promise<any>((resolve, reject) => {
          const python = spawn('python3', [
            '-c',
            `
import sys
import json
from datetime import datetime
sys.path.append('${path.join(getCurrentDir(), 'extractor')}')
from comprehensive_metadata_engine import extract_comprehensive_metadata

# Generate forensic report
file_names = ${JSON.stringify(fileInfos.map((f) => f.originalName))}
file_sizes = ${JSON.stringify(fileInfos.map((f) => f.size))}
filepaths = ${JSON.stringify(tempPaths)}

report = {
    "report_id": "${crypto.randomUUID()}",
    "generated_at": datetime.now().isoformat(),
    "analyst": "MetaExtract Forensic Engine v4.0",
    "case_summary": {
        "total_files": ${fileInfos.length},
        "file_names": file_names,
        "analysis_scope": "Comprehensive forensic metadata analysis"
    },
    "files": [],
    "cross_file_analysis": {},
    "conclusions": {},
    "recommendations": []
}

# Analyze each file
for i, filepath in enumerate(filepaths):
    try:
        metadata = extract_comprehensive_metadata(filepath, tier='enterprise')
        
        file_analysis = {
            "file_name": file_names[i],
            "file_size": file_sizes[i],
            "metadata": metadata,
            "forensic_findings": [],
            "authenticity_score": 100,
            "risk_level": "low"
        }
        
        # Analyze forensic indicators
        if metadata.get('steganography_analysis', {}).get('suspicious_score', 0) > 0.3:
            file_analysis["forensic_findings"].append("Potential steganography detected")
            file_analysis["authenticity_score"] -= 30
            file_analysis["risk_level"] = "medium"
            
        if metadata.get('manipulation_detection', {}).get('manipulation_probability', 0) > 0.5:
            file_analysis["forensic_findings"].append("Image manipulation indicators found")
            file_analysis["authenticity_score"] -= 50
            file_analysis["risk_level"] = "high"
            
        if metadata.get('ai_detection', {}).get('ai_probability', 0) > 0.7:
            file_analysis["forensic_findings"].append("AI-generated content detected")
            file_analysis["authenticity_score"] -= 20
            
        report["files"].append(file_analysis)
        
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)

# Generate conclusions
high_risk_files = [f for f in report["files"] if f["risk_level"] == "high"]
medium_risk_files = [f for f in report["files"] if f["risk_level"] == "medium"]

report["conclusions"] = {
    "overall_assessment": "high" if high_risk_files else "medium" if medium_risk_files else "low",
    "files_analyzed": len(report["files"]),
    "high_risk_files": len(high_risk_files),
    "medium_risk_files": len(medium_risk_files),
    "average_authenticity_score": sum(f["authenticity_score"] for f in report["files"]) / len(report["files"]) if report["files"] else 0
}

if high_risk_files:
    report["recommendations"].append("Immediate investigation recommended for high-risk files")
if medium_risk_files:
    report["recommendations"].append("Further analysis recommended for medium-risk files")
if not high_risk_files and not medium_risk_files:
    report["recommendations"].append("No significant forensic concerns detected")

print(json.dumps(report))
          `,
          ]);

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
              reject(new Error(`Forensic report generation failed: ${stderr}`));
              return;
            }

            try {
              resolve(JSON.parse(stdout));
            } catch (e) {
              reject(new Error('Failed to parse forensic report'));
            }
          });

          setTimeout(() => {
            python.kill();
            reject(new Error('Forensic report generation timed out'));
          }, 600000); // 10 minutes for comprehensive analysis
        });

        const processingMs = Date.now() - startTime;
        reportResult.processing_time_ms = processingMs;

        res.json(reportResult);
      } catch (error) {
        console.error('Forensic report error:', error);
        res.status(500).json({
          error: 'Forensic report generation failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        for (const tempPath of tempPaths) {
          try {
            await fs.unlink(tempPath);
          } catch (error) {
            console.error('Failed to delete temp file:', tempPath, error);
          }
        }
      }
    }
  );

  // Health check
  app.get('/api/health', (req, res) => {
    res.json({
      status: 'ok',
      service: 'MetaExtract API',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
    });
  });

  // Analytics endpoints (admin)
  app.get('/api/admin/analytics', async (req, res) => {
    try {
      const summary = await storage.getAnalyticsSummary();
      res.json(summary);
    } catch (error) {
      console.error('Analytics error:', error);
      res.status(500).json({ error: 'Failed to fetch analytics' });
    }
  });

  app.get('/api/admin/extractions', async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 50;
      const extractions = await storage.getRecentExtractions(limit);
      res.json(extractions);
    } catch (error) {
      console.error('Extractions history error:', error);
      res.status(500).json({ error: 'Failed to fetch extractions' });
    }
  });

  // Register payment routes
  registerPaymentRoutes(app);

  // Register forensic routes
  registerForensicRoutes(app);

  return httpServer;
}
