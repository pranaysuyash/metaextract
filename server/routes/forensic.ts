/**
 * Forensic Analysis Routes Module
 *
 * Handles forensic-specific endpoints:
 * - Metadata comparison
 * - Timeline reconstruction
 * - Forensic capabilities
 * - Forensic reports
 */

import type { Express } from 'express';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import {
  getTierConfig,
  isFileTypeAllowed,
  isFileSizeAllowed,
  normalizeTier,
  toPythonTier,
  getRateLimits,
} from '@shared/tierConfig';
import {
  extractMetadataWithPython,
  transformMetadataForFrontend,
} from './extraction';

// ============================================================================
// Multer Configuration
// ============================================================================

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 2000 * 1024 * 1024, // 2GB max
  },
});

// ============================================================================
// Helper Functions
// ============================================================================

async function cleanupTempFiles(tempPaths: string[]): Promise<void> {
  for (const tempPath of tempPaths) {
    try {
      await fs.unlink(tempPath);
    } catch (error) {
      console.error('Failed to delete temp file:', tempPath, error);
    }
  }
}

// ============================================================================
// Route Registration
// ============================================================================

export function registerForensicRoutes(app: Express): void {
  // Forensic capabilities endpoint
  app.get('/api/forensic/capabilities', (req, res) => {
    const requestedTier = (req.query.tier as string) || 'enterprise';
    const normalizedTier = normalizeTier(requestedTier);
    const tierConfig = getTierConfig(normalizedTier);

    const capabilities = {
      tier: normalizedTier,
      advanced_analysis_available: process.env.NODE_ENV === 'development' || normalizedTier !== 'free',
      modules: {
        steganography_detection: {
          available: process.env.NODE_ENV === 'development' || 
            normalizedTier === 'professional' ||
            normalizedTier === 'forensic' ||
            normalizedTier === 'enterprise',
          description:
            'Detect hidden data using LSB analysis, frequency domain analysis, and entropy calculation',
          methods: [
            'LSB Analysis',
            'FFT Analysis',
            'Entropy Calculation',
            'Visual Attack Detection',
          ],
        },
        manipulation_detection: {
          available: process.env.NODE_ENV === 'development' ||
            normalizedTier === 'professional' ||
            normalizedTier === 'forensic' ||
            normalizedTier === 'enterprise',
          description:
            'Detect image manipulation using JPEG analysis, noise patterns, and edge inconsistencies',
          methods: [
            'JPEG Compression Analysis',
            'Noise Pattern Analysis',
            'Edge Inconsistency Detection',
            'Copy-Move Detection',
          ],
        },
        ai_content_detection: {
          available: process.env.NODE_ENV === 'development' ||
            normalizedTier === 'professional' ||
            normalizedTier === 'forensic' ||
            normalizedTier === 'enterprise',
          description: 'Detect AI-generated content in images and text',
          methods: [
            'Neural Network Analysis',
            'Pattern Recognition',
            'Metadata Analysis',
          ],
        },
        metadata_comparison: {
          available: process.env.NODE_ENV === 'development' ||
            normalizedTier === 'professional' ||
            normalizedTier === 'forensic' ||
            normalizedTier === 'enterprise',
          description:
            'Compare metadata across multiple files for consistency analysis',
          methods: [
            'Field-by-field Comparison',
            'Similarity Scoring',
            'Pattern Detection',
          ],
        },
        timeline_reconstruction: {
          available: process.env.NODE_ENV === 'development' ||
            normalizedTier === 'professional' ||
            normalizedTier === 'forensic' ||
            normalizedTier === 'enterprise',
          description: 'Reconstruct chronological timeline from multiple files',
          methods: ['Timestamp Correlation', 'Gap Analysis', 'Chain of Custody'],
        },
        batch_processing: {
          available: process.env.NODE_ENV === 'development' || tierConfig.features.batchUpload,
          description: 'Process multiple files simultaneously',
          max_files: process.env.NODE_ENV === 'development' ? 100 :
            normalizedTier === 'enterprise'
              ? 100
              : normalizedTier === 'forensic'
              ? 50
              : normalizedTier === 'professional'
              ? 25
              : 0,
        },
      },
      reporting: {
        pdf_reports: process.env.NODE_ENV === 'development' || normalizedTier === 'enterprise',
        forensic_reports: process.env.NODE_ENV === 'development' || normalizedTier === 'enterprise',
        expert_witness_format: process.env.NODE_ENV === 'development' || normalizedTier === 'enterprise',
      },
      api_access: {
        available: process.env.NODE_ENV === 'development' || normalizedTier === 'enterprise',
        rate_limits: getRateLimits(normalizedTier),
      },
    };

    res.json(capabilities);
  });

  // Batch metadata comparison endpoint
  app.post('/api/compare/batch', upload.array('files', 50), async (req, res) => {
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
      const pythonTier = toPythonTier(normalizedTier);

      // Comparison requires Professional+ tier (disabled in dev)
      if (process.env.NODE_ENV !== 'development' && normalizedTier === 'free') {
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
            totalFields > 0 ? Math.round((matchCount / totalFields) * 100) : 0;

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
        comparison_id: crypto.randomUUID(),
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
      await cleanupTempFiles(tempPaths);
    }
  });

  // Timeline reconstruction endpoint
  app.post(
    '/api/timeline/reconstruct',
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
          return res.status(400).json({
            error: 'No files uploaded for timeline reconstruction',
          });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);

        // Timeline reconstruction requires Professional+ tier (disabled in dev)
        if (process.env.NODE_ENV !== 'development' && normalizedTier === 'free') {
          return res.status(403).json({
            error: 'Timeline reconstruction not available for your plan',
            current_tier: normalizedTier,
            required_tier: 'professional',
          });
        }

        // Write files to temp locations
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

          const metadata = transformMetadataForFrontend(
            rawMetadata,
            file.originalname,
            normalizedTier
          );

          // Extract timeline events from metadata
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
          timeline_id: crypto.randomUUID(),
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
        await cleanupTempFiles(tempPaths);
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
        if (
          !req.files ||
          !Array.isArray(req.files) ||
          req.files.length === 0
        ) {
          return res.status(400).json({
            error: 'No files uploaded for forensic analysis',
          });
        }

        const requestedTier = (req.query.tier as string) || 'enterprise';
        const normalizedTier = normalizeTier(requestedTier);
        const pythonTier = toPythonTier(normalizedTier);

        // Forensic reports require Enterprise tier (disabled in dev)
        if (process.env.NODE_ENV !== 'development' && normalizedTier !== 'enterprise') {
          return res.status(403).json({
            error: 'Forensic reports not available for your plan',
            current_tier: normalizedTier,
            required_tier: 'enterprise',
            upgrade_message:
              'Upgrade to Enterprise tier for professional forensic reports',
          });
        }

        // Process files and generate report
        const tempDir = '/tmp/metaextract';
        await fs.mkdir(tempDir, { recursive: true });

        const fileAnalyses: any[] = [];

        for (const file of req.files) {
          const tempPath = path.join(
            tempDir,
            `${Date.now()}-${crypto.randomUUID()}-${file.originalname}`
          );
          await fs.writeFile(tempPath, file.buffer);
          tempPaths.push(tempPath);

          try {
            const rawMetadata = await extractMetadataWithPython(
              tempPath,
              pythonTier,
              true,
              true, // Advanced analysis
              false
            );

            const metadata = transformMetadataForFrontend(
              rawMetadata,
              file.originalname,
              normalizedTier
            );

            let authenticityScore = 100;
            const forensicFindings: string[] = [];
            let riskLevel = 'low';

            // Analyze forensic indicators
            if (
              rawMetadata.steganography_analysis?.suspicious_score &&
              rawMetadata.steganography_analysis.suspicious_score > 0.3
            ) {
              forensicFindings.push('Potential steganography detected');
              authenticityScore -= 30;
              riskLevel = 'medium';
            }

            if (
              rawMetadata.manipulation_detection?.manipulation_probability &&
              rawMetadata.manipulation_detection.manipulation_probability > 0.5
            ) {
              forensicFindings.push('Image manipulation indicators found');
              authenticityScore -= 50;
              riskLevel = 'high';
            }

            if (
              rawMetadata.ai_detection?.ai_probability &&
              rawMetadata.ai_detection.ai_probability > 0.7
            ) {
              forensicFindings.push('AI-generated content detected');
              authenticityScore -= 20;
            }

            fileAnalyses.push({
              file_name: file.originalname,
              file_size: file.size,
              metadata,
              forensic_findings: forensicFindings,
              authenticity_score: Math.max(0, authenticityScore),
              risk_level: riskLevel,
            });
          } catch (error) {
            console.error(`Error analyzing ${file.originalname}:`, error);
            fileAnalyses.push({
              file_name: file.originalname,
              file_size: file.size,
              error: error instanceof Error ? error.message : 'Unknown error',
              forensic_findings: [],
              authenticity_score: 0,
              risk_level: 'unknown',
            });
          }
        }

        // Generate conclusions
        const highRiskFiles = fileAnalyses.filter(
          (f) => f.risk_level === 'high'
        );
        const mediumRiskFiles = fileAnalyses.filter(
          (f) => f.risk_level === 'medium'
        );

        const recommendations: string[] = [];
        if (highRiskFiles.length > 0) {
          recommendations.push(
            'Immediate investigation recommended for high-risk files'
          );
        }
        if (mediumRiskFiles.length > 0) {
          recommendations.push(
            'Further analysis recommended for medium-risk files'
          );
        }
        if (highRiskFiles.length === 0 && mediumRiskFiles.length === 0) {
          recommendations.push('No significant forensic concerns detected');
        }

        const report = {
          report_id: crypto.randomUUID(),
          generated_at: new Date().toISOString(),
          analyst: 'MetaExtract Forensic Engine v4.0',
          case_summary: {
            total_files: req.files.length,
            file_names: fileAnalyses.map((f) => f.file_name),
            analysis_scope: 'Comprehensive forensic metadata analysis',
          },
          files: fileAnalyses,
          conclusions: {
            overall_assessment: highRiskFiles.length
              ? 'high'
              : mediumRiskFiles.length
              ? 'medium'
              : 'low',
            files_analyzed: fileAnalyses.length,
            high_risk_files: highRiskFiles.length,
            medium_risk_files: mediumRiskFiles.length,
            average_authenticity_score:
              fileAnalyses.length > 0
                ? Math.round(
                    fileAnalyses.reduce(
                      (sum, f) => sum + f.authenticity_score,
                      0
                    ) / fileAnalyses.length
                  )
                : 0,
          },
          recommendations,
          processing_time_ms: Date.now() - startTime,
        };

        res.json(report);
      } catch (error) {
        console.error('Forensic report error:', error);
        res.status(500).json({
          error: 'Forensic report generation failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      } finally {
        await cleanupTempFiles(tempPaths);
      }
    }
  );

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

      // Advanced extraction requires Professional+ tier (disabled in dev)
      if (process.env.NODE_ENV !== 'development' && normalizedTier === 'free') {
        return res.status(403).json({
          error: 'Advanced extraction not available for your plan',
          current_tier: normalizedTier,
          required_tier: 'professional',
        });
      }

      // Validate file type for tier
      if (!isFileTypeAllowed(normalizedTier, mimeType)) {
        return res.status(403).json({
          error: `File type not allowed: ${req.file.originalname}`,
          file_type: mimeType,
        });
      }

      // Validate file size for tier
      if (!isFileSizeAllowed(normalizedTier, req.file.size)) {
        return res.status(403).json({
          error: `File size exceeds limit: ${req.file.originalname}`,
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

      // Extract metadata with advanced analysis enabled
      const rawMetadata = await extractMetadataWithPython(
        tempPath,
        pythonTier,
        false, // includePerformanceMetrics
        true   // enableAdvancedAnalysis
      );

      const metadata = transformMetadataForFrontend(
        rawMetadata,
        req.file.originalname,
        normalizedTier
      );

      // Add advanced analysis summary
      const advancedAnalysis = rawMetadata.advanced_analysis;
      metadata.advanced_analysis = {
        enabled: true,
        processing_time_ms: advancedAnalysis?.processing_time_ms || 0,
        modules_run: advancedAnalysis?.modules_run || [],
        forensic_score: advancedAnalysis?.forensic_score || 0,
        authenticity_assessment: advancedAnalysis?.authenticity_assessment || 'Unknown',
      };

      const processingMs = Date.now() - startTime;

      res.json({
        ...metadata,
        advanced_enabled: true,
        processing_time_ms: processingMs,
      });
    } catch (error) {
      const processingMs = Date.now() - startTime;
      console.error('Advanced extraction error:', error);
      res.status(500).json({
        error: 'Advanced extraction failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        processing_time_ms: processingMs,
      });
    } finally {
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (error) {
          console.error('Failed to delete temp file:', tempPath, error);
        }
      }
    }
  });
}
