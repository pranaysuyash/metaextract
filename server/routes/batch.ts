/**
 * Batch Processing Routes Module
 *
 * Handles batch processing operations:
 * - Batch job management
 * - Batch results retrieval
 * - Batch reprocessing
 * - Batch export functionality
 */

import type { Express, Response } from 'express';
import { storage } from '../storage/index';
import type { AuthRequest } from '../auth';
import {
  sendInvalidRequestError,
  sendInternalServerError,
  sendForbiddenError,
} from '../utils/error-response';

// ============================================================================
// Types
// ============================================================================

interface BatchJob {
  id: string;
  userId: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  totalFiles: number;
  processedFiles: number;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  errorMessage?: string;
}

interface BatchResult {
  id: string;
  batchId: string;
  filename: string;
  status: 'success' | 'error' | 'processing' | 'pending';
  extractionDate: string;
  fieldsExtracted: number;
  fileSize: number;
  fileType: string;
  authenticityScore?: number;
  metadata: Record<string, any>;
  processingTime?: number;
  errorMessage?: string;
  createdAt: string;
}

// ============================================================================
// Helper Functions
// ============================================================================

function generateBatchId(): string {
  return `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateResultId(): string {
  return `result_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// ============================================================================
// Route Handlers
// ============================================================================

/**
 * Get all batch jobs for the current user
 */
async function getBatchJobs(req: AuthRequest, res: Response) {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return sendForbiddenError(res, 'Authentication required');
    }

    // Get batch jobs from storage
    const batchJobs = await storage.getBatchJobs(userId);
    
    res.json({
      success: true,
      jobs: batchJobs,
      total: batchJobs.length,
    });
  } catch (error) {
    console.error('Error fetching batch jobs:', error);
    sendInternalServerError(res, 'Failed to fetch batch jobs');
  }
}

/**
 * Get detailed results for a specific batch job
 */
async function getBatchResults(req: AuthRequest, res: Response) {
  try {
    const userId = req.user?.id;
    const { jobId } = req.params;

    if (!userId) {
      return sendForbiddenError(res, 'Authentication required');
    }

    if (!jobId) {
      return sendInvalidRequestError(res, 'Job ID is required');
    }

    // Verify the job belongs to the user
    const batchJob = await storage.getBatchJob(jobId);
    if (!batchJob || batchJob.userId !== userId) {
      return sendInvalidRequestError(res, 'Batch job not found');
    }

    // Get results for this batch job
    const results = await storage.getBatchResults(jobId);
    
    res.json({
      success: true,
      job: batchJob,
      results,
      total: results.length,
    });
  } catch (error) {
    console.error('Error fetching batch results:', error);
    sendInternalServerError(res, 'Failed to fetch batch results');
  }
}

/**
 * Reprocess selected files in a batch
 */
async function reprocessFiles(req: AuthRequest, res: Response) {
  try {
    const userId = req.user?.id;
    const { fileIds, batchId } = req.body;

    if (!userId) {
      return sendForbiddenError(res, 'Authentication required');
    }

    if (!fileIds || !Array.isArray(fileIds) || fileIds.length === 0) {
      return sendInvalidRequestError(res, 'File IDs are required');
    }

    if (!batchId) {
      return sendInvalidRequestError(res, 'Batch ID is required');
    }

    // Verify the batch job belongs to the user
    const batchJob = await storage.getBatchJob(batchId);
    if (!batchJob || batchJob.userId !== userId) {
      return sendInvalidRequestError(res, 'Batch job not found');
    }

    // Get the files to reprocess
    const filesToReprocess = await storage.getBatchResults(batchId);
    const validFiles = filesToReprocess.filter(result => 
      fileIds.includes(result.id) && result.status === 'error'
    );

    if (validFiles.length === 0) {
      return sendInvalidRequestError(res, 'No valid files to reprocess');
    }

    // Update file status to pending for reprocessing
    for (const file of validFiles) {
      await storage.updateBatchResult(file.id, {
        status: 'pending',
        errorMessage: undefined,
      });
    }

    // Update batch job status if needed
    if (batchJob.status === 'completed') {
      await storage.updateBatchJob(batchId, {
        status: 'processing',
        processedFiles: batchJob.processedFiles - validFiles.length,
        updatedAt: new Date().toISOString(),
      });
    }

    res.json({
      success: true,
      message: `${validFiles.length} files queued for reprocessing`,
      reprocessedFiles: validFiles.length,
    });
  } catch (error) {
    console.error('Error reprocessing files:', error);
    sendInternalServerError(res, 'Failed to reprocess files');
  }
}

/**
 * Export batch results
 */
async function exportBatchResults(req: AuthRequest, res: Response) {
  try {
    const userId = req.user?.id;
    const { jobId, format, scope, options } = req.body;

    if (!userId) {
      return sendForbiddenError(res, 'Authentication required');
    }

    if (!jobId) {
      return sendInvalidRequestError(res, 'Job ID is required');
    }

    if (!['json', 'csv', 'pdf'].includes(format)) {
      return sendInvalidRequestError(res, 'Invalid export format');
    }

    if (!['all', 'selected', 'successful'].includes(scope)) {
      return sendInvalidRequestError(res, 'Invalid export scope');
    }

    // Verify the batch job belongs to the user
    const batchJob = await storage.getBatchJob(jobId);
    if (!batchJob || batchJob.userId !== userId) {
      return sendInvalidRequestError(res, 'Batch job not found');
    }

    // Get results for this batch job
    let results = await storage.getBatchResults(jobId);

    // Apply scope filtering
    if (scope === 'selected' && options?.fileIds) {
      results = results.filter(result => options.fileIds.includes(result.id));
    } else if (scope === 'successful') {
      results = results.filter(result => result.status === 'success');
    }

    if (results.length === 0) {
      return sendInvalidRequestError(res, 'No results to export');
    }

    // Prepare export data
    const exportData: Record<string, any> = {
      exportInfo: {
        timestamp: new Date().toISOString(),
        totalFiles: results.length,
        format,
        scope,
        options: options || {},
      },
      batchJob: {
        id: batchJob.id,
        name: batchJob.name,
        status: batchJob.status,
        createdAt: batchJob.createdAt,
        completedAt: batchJob.completedAt,
      },
      files: results.map(result => ({
        id: result.id,
        filename: result.filename,
        status: result.status,
        extractionDate: result.extractionDate,
        fileType: result.fileType,
        fileSize: result.fileSize,
        fieldsExtracted: result.fieldsExtracted,
        processingTime: result.processingTime,
        authenticityScore: result.authenticityScore,
        errorMessage: result.errorMessage,
        metadata: options?.includeMetadata ? result.metadata : undefined,
      })),
    };

    // Add statistics if requested
    if (options?.includeStatistics) {
      const totalFields = results.reduce((sum, r) => sum + r.fieldsExtracted, 0);
      const totalSize = results.reduce((sum, r) => sum + r.fileSize, 0);
      const processingTimes = results.flatMap(result =>
        typeof result.processingTime === 'number' ? [result.processingTime] : []
      );
      const avgProcessingTime =
        processingTimes.length > 0
          ? processingTimes.reduce((sum, time) => sum + time, 0) /
            processingTimes.length
          : 0;

      exportData.statistics = {
        totalFiles: results.length,
        successfulFiles: results.filter(r => r.status === 'success').length,
        errorFiles: results.filter(r => r.status === 'error').length,
        processingFiles: results.filter(r => r.status === 'processing').length,
        pendingFiles: results.filter(r => r.status === 'pending').length,
        totalFields,
        avgFields: Math.round(totalFields / results.length),
        totalSize,
        avgSize: totalSize / results.length,
        avgProcessingTime,
        successRate: (results.filter(r => r.status === 'success').length / results.length) * 100,
        fileTypeDistribution: getFileTypeDistribution(results),
        statusDistribution: getStatusDistribution(results),
      };
    }

    // Add timeline if requested
    if (options?.includeTimeline) {
      exportData.timeline = {
        startTime: results.length > 0 ? results[0].extractionDate : null,
        endTime: results.length > 0 ? results[results.length - 1].extractionDate : null,
        events: results.map(result => ({
          timestamp: result.extractionDate,
          filename: result.filename,
          status: result.status,
          processingTime: result.processingTime,
          fieldsExtracted: result.fieldsExtracted,
        })),
      };
    }

    res.json({
      success: true,
      exportData,
      message: `Exported ${results.length} files`,
    });
  } catch (error) {
    console.error('Error exporting batch results:', error);
    sendInternalServerError(res, 'Failed to export batch results');
  }
}

// Helper functions for statistics
function getFileTypeDistribution(results: BatchResult[]): Record<string, number> {
  const distribution: Record<string, number> = {};
  results.forEach(result => {
    const mainType = result.fileType.split('/')[0];
    distribution[mainType] = (distribution[mainType] || 0) + 1;
  });
  return distribution;
}

function getStatusDistribution(results: BatchResult[]): Record<string, number> {
  const distribution: Record<string, number> = {
    success: 0,
    error: 0,
    processing: 0,
    pending: 0,
  };
  results.forEach(result => {
    distribution[result.status]++;
  });
  return distribution;
}

// ============================================================================
// Route Registration
// ============================================================================

export function registerBatchRoutes(app: Express) {
  // Batch job management
  app.get('/api/batch/jobs', getBatchJobs);
  app.get('/api/batch/jobs/:jobId/results', getBatchResults);
  
  // Batch operations
  app.post('/api/batch/reprocess', reprocessFiles);
  app.post('/api/batch/export', exportBatchResults);

  console.log('✅ Batch routes registered');
}
