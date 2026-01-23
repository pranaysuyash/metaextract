/**
 * Tests for Batch Processing Routes
 *
 * Tests batch job management, results retrieval, reprocessing, and export
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { registerBatchRoutes } from './batch';

// Mock the storage module
const mockGetBatchJobs = jest.fn();
const mockGetBatchJob = jest.fn();
const mockGetBatchResults = jest.fn();
const mockUpdateBatchResult = jest.fn();
const mockUpdateBatchJob = jest.fn();

jest.mock('../storage/index', () => ({
  storage: {
    getBatchJobs: (...args: any[]) => mockGetBatchJobs(...args),
    getBatchJob: (...args: any[]) => mockGetBatchJob(...args),
    getBatchResults: (...args: any[]) => mockGetBatchResults(...args),
    updateBatchResult: (...args: any[]) => mockUpdateBatchResult(...args),
    updateBatchJob: (...args: any[]) => mockUpdateBatchJob(...args),
  },
}));

// Mock auth - routes need requireAuth middleware
jest.mock('../auth', () => ({
  requireAuth: (req: any, _res: any, next: any) => {
    req.user = { id: 'test-user-123' };
    next();
  },
}));

describe('Batch Routes', () => {
  let app: Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    registerBatchRoutes(app);
    jest.clearAllMocks();
  });

  describe('GET /api/batch/jobs', () => {
    it('should return batch jobs for authenticated user', async () => {
      const mockJobs = [
        { id: 'job-1', name: 'Test Batch 1', status: 'completed' },
        { id: 'job-2', name: 'Test Batch 2', status: 'processing' },
      ];
      mockGetBatchJobs.mockResolvedValue(mockJobs);

      const response = await request(app).get('/api/batch/jobs').expect(200);

      expect(response.body).toEqual({
        success: true,
        jobs: mockJobs,
        total: mockJobs.length,
      });
    });

    it('should return empty array when no jobs exist', async () => {
      mockGetBatchJobs.mockResolvedValue([]);

      const response = await request(app).get('/api/batch/jobs').expect(200);

      expect(response.body).toEqual({
        success: true,
        jobs: [],
        total: 0,
      });
    });
  });

  describe('GET /api/batch/jobs/:jobId/results', () => {
    it('should return results for valid batch job', async () => {
      const mockJob = { id: 'job-123', userId: 'test-user-123', name: 'Test' };
      const mockResults = [
        { id: 'result-1', filename: 'test1.jpg', status: 'success' },
        { id: 'result-2', filename: 'test2.jpg', status: 'error' },
      ];
      mockGetBatchJob.mockResolvedValue(mockJob);
      mockGetBatchResults.mockResolvedValue(mockResults);

      const response = await request(app)
        .get('/api/batch/jobs/job-123/results')
        .expect(200);

      expect(response.body).toEqual({
        success: true,
        job: mockJob,
        results: mockResults,
        total: mockResults.length,
      });
    });

    it('should return 400 when job not found', async () => {
      mockGetBatchJob.mockResolvedValue(null);

      const response = await request(app)
        .get('/api/batch/jobs/unknown-job/results')
        .expect(400);

      expect(response.body.error.message).toBe('Batch job not found');
    });
  });

  describe('POST /api/batch/reprocess', () => {
    it('should reprocess valid error files', async () => {
      const mockBatchJob = {
        id: 'batch-123',
        userId: 'test-user-123',
        status: 'completed',
        processedFiles: 5,
      };
      const mockResults = [
        { id: 'result-1', status: 'error' },
        { id: 'result-2', status: 'error' },
      ];

      mockGetBatchJob.mockResolvedValue(mockBatchJob);
      mockGetBatchResults.mockResolvedValue(mockResults);
      mockUpdateBatchResult.mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/batch/reprocess')
        .send({ fileIds: ['result-1', 'result-2'], batchId: 'batch-123' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.reprocessedFiles).toBe(2);
      expect(mockUpdateBatchResult).toHaveBeenCalledTimes(2);
    });

    it('should return 400 when fileIds is not an array', async () => {
      const response = await request(app)
        .post('/api/batch/reprocess')
        .send({ fileIds: 'not-an-array', batchId: 'batch-123' })
        .expect(400);

      expect(response.body.error.message).toBe('File IDs are required');
    });

    it('should return 400 when fileIds array is empty', async () => {
      const response = await request(app)
        .post('/api/batch/reprocess')
        .send({ fileIds: [], batchId: 'batch-123' })
        .expect(400);

      expect(response.body.error.message).toBe('File IDs are required');
    });

    it('should return 400 when no valid files to reprocess', async () => {
      const mockBatchJob = {
        id: 'batch-123',
        userId: 'test-user-123',
        status: 'completed',
      };
      mockGetBatchJob.mockResolvedValue(mockBatchJob);
      mockGetBatchResults.mockResolvedValue([
        { id: 'result-1', status: 'success' },
      ]);

      const response = await request(app)
        .post('/api/batch/reprocess')
        .send({ fileIds: ['result-1'], batchId: 'batch-123' })
        .expect(400);

      expect(response.body.error.message).toBe('No valid files to reprocess');
    });
  });

  describe('POST /api/batch/export', () => {
    it('should export results in json format', async () => {
      const mockBatchJob = {
        id: 'batch-123',
        userId: 'test-user-123',
        name: 'Test Batch',
        status: 'completed',
        createdAt: '2024-01-01T00:00:00Z',
      };
      const mockResults = [
        {
          id: 'result-1',
          filename: 'test1.jpg',
          status: 'success',
          extractionDate: '2024-01-01T00:01:00Z',
          fileType: 'image/jpeg',
          fileSize: 1024,
          fieldsExtracted: 50,
          processingTime: 100,
          authenticityScore: 0.95,
          metadata: {},
        },
      ];

      mockGetBatchJob.mockResolvedValue(mockBatchJob);
      mockGetBatchResults.mockResolvedValue(mockResults);

      const response = await request(app)
        .post('/api/batch/export')
        .send({ jobId: 'batch-123', format: 'json', scope: 'all', options: {} })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Exported 1 files');
    });

    it('should export only successful results', async () => {
      const mockBatchJob = { id: 'batch-123', userId: 'test-user-123' };
      const mockResults = [
        { id: 'result-1', status: 'success' },
        { id: 'result-2', status: 'error' },
        { id: 'result-3', status: 'success' },
      ];

      mockGetBatchJob.mockResolvedValue(mockBatchJob);
      mockGetBatchResults.mockResolvedValue(mockResults);

      const response = await request(app)
        .post('/api/batch/export')
        .send({ jobId: 'batch-123', format: 'json', scope: 'successful' })
        .expect(200);

      expect(response.body.success).toBe(true);
    });

    it('should return 400 for invalid format', async () => {
      const response = await request(app)
        .post('/api/batch/export')
        .send({ jobId: 'batch-123', format: 'invalid', scope: 'all' })
        .expect(400);

      expect(response.body.error.message).toBe('Invalid export format');
    });

    it('should return 400 for invalid scope', async () => {
      const response = await request(app)
        .post('/api/batch/export')
        .send({ jobId: 'batch-123', format: 'json', scope: 'invalid' })
        .expect(400);

      expect(response.body.error.message).toBe('Invalid export scope');
    });

    it('should return 400 when no results to export', async () => {
      mockGetBatchJob.mockResolvedValue({
        id: 'batch-123',
        userId: 'test-user-123',
      });
      mockGetBatchResults.mockResolvedValue([]);

      const response = await request(app)
        .post('/api/batch/export')
        .send({ jobId: 'batch-123', format: 'json', scope: 'all' })
        .expect(400);

      expect(response.body.error.message).toBe('No results to export');
    });

    it('should include statistics when requested', async () => {
      const mockBatchJob = { id: 'batch-123', userId: 'test-user-123' };
      const mockResults = [
        {
          id: 'result-1',
          status: 'success',
          fileSize: 1024,
          fieldsExtracted: 50,
          processingTime: 100,
          fileType: 'image/jpeg',
          extractionDate: '2024-01-01T00:00:00Z',
          metadata: {},
        },
      ];

      mockGetBatchJob.mockResolvedValue(mockBatchJob);
      mockGetBatchResults.mockResolvedValue(mockResults);

      const response = await request(app)
        .post('/api/batch/export')
        .send({
          jobId: 'batch-123',
          format: 'json',
          scope: 'all',
          options: { includeStatistics: true },
        })
        .expect(200);

      expect(response.body.exportData.statistics).toBeDefined();
      expect(response.body.exportData.statistics.totalFiles).toBe(1);
      expect(response.body.exportData.statistics.successfulFiles).toBe(1);
    });

    it('should filter by selected fileIds', async () => {
      const mockBatchJob = { id: 'batch-123', userId: 'test-user-123' };
      const mockResults = [
        { id: 'result-1', status: 'success', metadata: {} },
        { id: 'result-2', status: 'success', metadata: {} },
        { id: 'result-3', status: 'success', metadata: {} },
      ];

      mockGetBatchJob.mockResolvedValue(mockBatchJob);
      mockGetBatchResults.mockResolvedValue(mockResults);

      const response = await request(app)
        .post('/api/batch/export')
        .send({
          jobId: 'batch-123',
          format: 'json',
          scope: 'selected',
          options: { fileIds: ['result-1', 'result-2'] },
        })
        .expect(200);

      expect(response.body.success).toBe(true);
    });
  });
});
