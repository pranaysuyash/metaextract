/** @jest-environment node */

/**
 * API Endpoint Tests for MetaExtract
 *
 * Tests all metadata extraction endpoints:
 * - /api/extract (single file)
 * - /api/extract/batch (batch processing)
 * - /api/extract/advanced (forensic analysis)
 * - /api/extract/health (health check)
 */

import request from 'supertest';
import express, { type Express } from 'express';
import multer from 'multer';
import { spawn } from 'child_process';
import { registerExtractionRoutes } from './extraction';
import { storage } from '../storage/index';
import { stopCleanupInterval } from '../middleware/rateLimit';

// Mock the storage module
jest.mock('../storage/index');

// Mock child_process spawn
jest.mock('child_process', () => ({
  spawn: jest.fn(),
}));

// Mock fs operations
jest.mock('fs/promises', () => ({
  mkdir: jest.fn().mockResolvedValue(undefined),
  writeFile: jest.fn().mockResolvedValue(undefined),
  unlink: jest.fn().mockResolvedValue(undefined),
  access: jest.fn().mockResolvedValue(undefined),
}));

describe('API Endpoint Tests', () => {
  let app: Express;

  const uniqueTrialEmail = () =>
    `test+${Date.now()}-${Math.random()}@example.com`;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    registerExtractionRoutes(app);
    jest.clearAllMocks();
  });

  afterAll(() => {
    stopCleanupInterval();
  });

  // Set a global timeout for all tests to prevent hanging
  jest.setTimeout(10000);

  describe('POST /api/extract - Single File Extraction', () => {
    const mockPythonResponse = {
      extraction_info: {
        timestamp: '2025-12-31T12:00:00Z',
        tier: 'enterprise',
        engine_version: '4.0.0',
        libraries: { PIL: true, exifread: true },
        fields_extracted: 245,
        locked_categories: 0,
        processing_ms: 1234,
      },
      file: {
        path: '/tmp/test.jpg',
        name: 'test.jpg',
        stem: 'test',
        extension: '.jpg',
        mime_type: 'image/jpeg',
      },
      summary: {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
      },
      filesystem: {
        size: 2411724,
        size_human: '2.3 MB',
        created: '2025-12-31T12:00:00Z',
        modified: '2025-12-31T12:00:00Z',
      },
      hashes: {
        md5: 'abc123',
        sha256: 'def456',
      },
      exif: {
        DateTimeOriginal: '2025-12-31 12:00:00',
        Make: 'Canon',
        Model: 'EOS R5',
      },
      gps: null,
      video: null,
      audio: null,
      pdf: null,
      svg: null,
      image: {
        width: 4096,
        height: 3072,
      },
      makernote: null,
      iptc: null,
      xmp: null,
      forensic: {},
      calculated: {
        aspect_ratio: '4:3',
        megapixels: 12.6,
      },
      extended_attributes: null,
      locked_fields: [],
    };

    it('should successfully extract metadata from JPEG file', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(mockPythonResponse)));
            }
          }),
        },
        stderr: {
          on: jest.fn(),
        },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') {
            callback(0);
          }
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .set('x-test-bypass-credits', '1')
        .expect(200);

      expect(response.body).toHaveProperty('filename', 'test.jpg');
      expect(response.body).toHaveProperty('tier', 'enterprise');
      expect(response.body).toHaveProperty('fields_extracted', 245);
      expect(response.body).toHaveProperty('exif');
      expect(response.body.exif).toHaveProperty('Make', 'Canon');
      expect(spawn).toHaveBeenCalledWith(
        'python3',
        expect.arrayContaining([
          expect.stringContaining('comprehensive_metadata_engine.py'),
          expect.stringContaining('test'),
          '--tier',
          'super',
          '--performance',
          '--advanced',
        ])
      );
    });

    it('should enforce tier-based file type restrictions', async () => {
      const response = await request(app)
        .post('/api/extract?tier=free')
        .attach('file', Buffer.from('fake video'), {
          filename: 'test.mp4',
          contentType: 'video/mp4',
        })
        .set('Content-Type', 'multipart/form-data')
        .expect(403);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toHaveProperty('context');
      expect(response.body.error.context).toHaveProperty('current_tier', 'free');
      expect(response.body.error).toHaveProperty('details');
      expect(response.body.error.details).toHaveProperty('required_tier');
      expect(response.body.error.message).toContain('File type not allowed');
    });

    it('should enforce tier-based file size limits', async () => {
      const largeFile = Buffer.alloc(15 * 1024 * 1024); // 15MB

      const response = await request(app)
        .post('/api/extract?tier=free')
        .attach('file', largeFile, 'large.jpg')
        .expect(403);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.message).toContain('File size exceeds limit');
      expect(response.body.error).toHaveProperty('details');
      expect(response.body.error.details).toHaveProperty('max_size_mb', 10);
    });

    it('should require session_id or trial_email for extraction', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(mockPythonResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.getOrCreateCreditBalance as jest.Mock).mockResolvedValue({
        id: 'balance-123',
        credits: 0,
      });

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .expect(402);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.message).toContain('Purchase credits');
    });

    it('should accept trial_email for one-time extraction', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(mockPythonResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const email = uniqueTrialEmail();

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .field('trial_email', email)
        .expect(200);

      expect(response.body).toHaveProperty('filename', 'test.jpg');
      expect(response.body).toHaveProperty('access');
      expect(response.body.access).toHaveProperty('trial_granted', true);
    });

    it('should handle Python extraction errors gracefully', async () => {
      const mockPythonProcess = {
        stdout: { on: jest.fn() },
        stderr: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from('Python extraction failed'));
            }
          }),
        },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(1);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .set('x-test-bypass-credits', '1')
        .expect(500);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.message).toContain('Failed to extract metadata');
    });

    it('should validate required file upload', async () => {
      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .expect(400);

      expect(response.body.error).toHaveProperty('message', 'No file uploaded');
    });
  });

  describe('POST /api/extract/batch - Batch Processing', () => {
    const mockBatchResponse = {
      results: {
        '/tmp/file1.jpg': {
          extraction_info: { fields_extracted: 245, tier: 'enterprise' },
          file: {
            name: 'file1.jpg',
            extension: '.jpg',
            mime_type: 'image/jpeg',
          },
          summary: { filename: 'file1.jpg' },
          filesystem: {},
          hashes: {},
          exif: {},
          gps: null,
          video: null,
          audio: null,
          pdf: null,
          svg: null,
          image: null,
          makernote: null,
          iptc: null,
          xmp: null,
          forensic: {},
          calculated: {},
          extended_attributes: null,
          locked_fields: [],
        },
        '/tmp/file2.jpg': {
          extraction_info: { fields_extracted: 189, tier: 'enterprise' },
          file: {
            name: 'file2.jpg',
            extension: '.jpg',
            mime_type: 'image/jpeg',
          },
          summary: { filename: 'file2.jpg' },
          filesystem: {},
          hashes: {},
          exif: {},
          gps: null,
          video: null,
          audio: null,
          pdf: null,
          svg: null,
          image: null,
          makernote: null,
          iptc: null,
          xmp: null,
          forensic: {},
          calculated: {},
          extended_attributes: null,
          locked_fields: [],
        },
      },
      summary: {
        total_files: 2,
        total_fields: 434,
      },
    };

    it('should process batch of files successfully', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(mockBatchResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract/batch?tier=enterprise')
        .attach('files', Buffer.from('file1'), 'file1.jpg')
        .attach('files', Buffer.from('file2'), 'file2.jpg')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('total_files', 2);
      expect(response.body).toHaveProperty('successful_files', 2);
      expect(response.body).toHaveProperty('batch_id');
      expect(response.body).toHaveProperty('results');
      expect(Object.keys(response.body.results)).toContain('file1.jpg');
      expect(Object.keys(response.body.results)).toContain('file2.jpg');
    });

    it('should restrict batch processing to forensic+ tiers', async () => {
      const response = await request(app)
        .post('/api/extract/batch?tier=free')
        .attach('files', Buffer.from('file1'), 'file1.jpg')
        .attach('files', Buffer.from('file2'), 'file2.jpg')
        .expect(403);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.message).toContain('requires forensic tier');
      expect(response.body.error.details).toHaveProperty('current_tier', 'free');
      expect(response.body.error.details).toHaveProperty('required_tier', 'forensic');
    });

    it('should validate all file types in batch', async () => {
      const response = await request(app)
        .post('/api/extract/batch?tier=forensic')
        .attach('files', Buffer.from('file1'), 'file1.jpg')
        .attach('files', Buffer.from('file2'), {
          filename: 'file2.exe',
          contentType: 'application/x-msdownload',
        })
        .expect(403);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.message).toContain('File type not allowed');
    });

    it('should handle batch processing errors', async () => {
      const mockPythonProcess = {
        stdout: { on: jest.fn() },
        stderr: {
          on: jest.fn().mockImplementation((event, callback) => {
            callback(Buffer.from('Batch processing error'));
          }),
        },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(1);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract/batch?tier=forensic')
        .attach('files', Buffer.from('file1'), 'file1.jpg')
        .expect(500);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('Batch processing failed');
    });

    it('should require at least one file for batch processing', async () => {
      const response = await request(app)
        .post('/api/extract/batch?tier=forensic')
        .expect(400);

      expect(response.body.error).toHaveProperty('message', 'No files uploaded');
    });
  });

  describe('POST /api/extract/advanced - Advanced Forensic Analysis', () => {
    const mockAdvancedResponse = {
      extraction_info: {
        fields_extracted: 1567,
        tier: 'enterprise',
        processing_ms: 5678,
      },
      file: {
        name: 'test.jpg',
        extension: '.jpg',
        mime_type: 'image/jpeg',
      },
      summary: {},
      filesystem: {},
      hashes: {},
      exif: {},
      gps: null,
      video: null,
      audio: null,
      pdf: null,
      svg: null,
      image: null,
      makernote: null,
      iptc: null,
      xmp: null,
      forensic: {},
      calculated: {},
      extended_attributes: null,
      steganography_analysis: {
        suspicious_score: 0.15,
        indicators: [],
      },
      manipulation_detection: {
        manipulation_probability: 0.05,
        detected_regions: [],
      },
      ai_detection: {
        ai_probability: 0.1,
        confidence: 0.85,
      },
      locked_fields: [],
    };

    it('should perform advanced forensic analysis', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(mockAdvancedResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract/advanced?tier=enterprise')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .expect(200);

      expect(response.body).toHaveProperty('advanced_analysis');
      expect(response.body.advanced_analysis).toHaveProperty('enabled', true);
      expect(response.body.advanced_analysis).toHaveProperty('forensic_score');
      expect(response.body.advanced_analysis).toHaveProperty('modules_run');
      expect(response.body.advanced_analysis.modules_run).toContain(
        'steganography_detection'
      );
      expect(response.body.advanced_analysis.modules_run).toContain(
        'manipulation_detection'
      );
    });

    it('should require forensic+ tier for advanced analysis', async () => {
      const response = await request(app)
        .post('/api/extract/advanced?tier=free')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .expect(403);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('Advanced analysis requires');
      expect(response.body).toHaveProperty('required_tier', 'forensic');
    });

    it('should calculate forensic score correctly', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(mockAdvancedResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract/advanced?tier=enterprise')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .expect(200);

      const expectedScore = 100 - 0.15 * 30 - 0.05 * 50 - 0.1 * 20;
      expect(response.body.advanced_analysis.forensic_score).toBe(
        Math.round(expectedScore)
      );
      expect(response.body.advanced_analysis.authenticity_assessment).toBe(
        'authentic'
      );
    });
  });

  describe('GET /api/extract/health - Health Check', () => {
    it('should return healthy status when Python engine is available', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              const healthResponse = {
                extraction_info: {
                  engine_version: '4.0.0',
                },
                file: {},
                summary: {},
                filesystem: {},
                hashes: {},
                exif: {},
                gps: null,
                video: null,
                audio: null,
                pdf: null,
                svg: null,
                image: null,
                makernote: null,
                iptc: null,
                xmp: null,
                forensic: {},
                calculated: {},
                extended_attributes: null,
                locked_fields: [],
              };
              callback(Buffer.from(JSON.stringify(healthResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .get('/api/extract/health')
        .expect(200);

      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('python_engine', 'available');
      expect(response.body).toHaveProperty('engine_version', '4.0.0');
    });

    it('should return unhealthy status when Python engine fails', async () => {
      const mockPythonProcess = {
        stdout: { on: jest.fn() },
        stderr: {
          on: jest.fn().mockImplementation((event, callback) => {
            callback(Buffer.from('Python error'));
          }),
        },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(1);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .get('/api/extract/health')
        .expect(503);

      expect(response.body).toHaveProperty('status', 'unhealthy');
      expect(response.body).toHaveProperty('python_engine', 'unavailable');
    });

    it('should return timeout status when Python engine hangs', async () => {
      const mockPythonProcess = {
        stdout: { on: jest.fn() },
        stderr: { on: jest.fn() },
        on: jest.fn((event, callback) => {
          // Don't trigger any events - let the timeout fire
        }),
        kill: jest.fn(),
        killed: false,
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .get('/api/extract/health')
        .expect(503);

      expect(response.body).toHaveProperty('status', 'timeout');
      expect(response.body).toHaveProperty('python_engine', 'unresponsive');
    }, 2000); // Increase timeout for this specific test to 2 seconds
  });

  describe('Tier-based Field Filtering', () => {
    it('should lock advanced fields for free tier', async () => {
      const mockFreeTierResponse = {
        extraction_info: {
          fields_extracted: 50,
          tier: 'free',
          locked_categories: 8,
        },
        file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
        summary: {},
        filesystem: {},
        hashes: { _locked: true },
        exif: {},
        gps: null,
        video: null,
        audio: null,
        pdf: null,
        svg: null,
        image: null,
        makernote: null,
        iptc: null,
        xmp: null,
        forensic: {},
        calculated: {},
        extended_attributes: null,
        locked_fields: [
          'makernote',
          'iptc',
          'xmp',
          'extended_attributes',
          'video',
          'audio',
          'pdf',
          'advanced_analysis',
        ],
      };

      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            callback(Buffer.from(JSON.stringify(mockFreeTierResponse)));
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/extract?tier=free')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .set('x-test-bypass-credits', '1')
        .expect(200);

      expect(response.body).toHaveProperty('tier', 'free');
      expect(response.body).toHaveProperty('fields_available', 200);
      expect(response.body).toHaveProperty('locked_fields');
      expect(response.body.locked_fields.length).toBeGreaterThan(0);
      expect(response.body.file_integrity).toHaveProperty('_locked', true);
    });

    it('should unlock all fields for enterprise tier', async () => {
      const mockEnterpriseResponse = {
        extraction_info: {
          fields_extracted: 1567,
          tier: 'enterprise',
          locked_categories: 0,
        },
        file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
        summary: {},
        filesystem: {},
        hashes: { md5: 'abc123', sha256: 'def456' },
        exif: { Make: 'Canon', Model: 'EOS R5' },
        gps: { latitude: 37.7749, longitude: -122.4194 },
        video: null,
        audio: null,
        pdf: null,
        svg: null,
        image: { width: 4096, height: 3072 },
        makernote: { CameraSerial: '123456' },
        iptc: { Copyright: '2025' },
        xmp: { Keywords: ['test', 'photo'] },
        forensic: {},
        calculated: {},
        extended_attributes: {},
        locked_fields: [],
      };

      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            callback(Buffer.from(JSON.stringify(mockEnterpriseResponse)));
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as unknown as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image'), 'test.jpg')
        .set('x-test-bypass-credits', '1')
        .expect(200);

      expect(response.body).toHaveProperty('tier', 'enterprise');
      expect(response.body).toHaveProperty('fields_available', 45000);
      expect(response.body.locked_fields).toEqual([]);
      expect(response.body.file_integrity).not.toHaveProperty('_locked');
      expect(response.body.makernote).not.toBeNull();
      expect(response.body.iptc).not.toBeNull();
      expect(response.body.xmp).not.toBeNull();
    });
  });
});
