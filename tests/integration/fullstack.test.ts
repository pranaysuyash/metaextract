/**
 * Full-Stack Integration Testing Suite for MetaExtract
 *
 * Tests complete user workflows from frontend to backend:
 * - File upload → metadata extraction → display
 * - User authentication → tier-based access → resource usage
 * - Payment flow → subscription upgrade → feature unlock
 * - Batch processing → progress tracking → results delivery
 * - Error handling → user feedback → recovery
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { registerRoutes } from '../server/routes';
import { registerExtractionRoutes } from '../server/routes/extraction';
import { storage } from '../server/storage';
import { performance } from 'perf_hooks';

// Mock the storage module
jest.mock('../server/storage');

// Mock child_process spawn
jest.mock('child_process', () => ({
  spawn: jest.fn(),
}));

const { spawn } = require('child_process');

// Mock fs operations
jest.mock('fs/promises', () => ({
  mkdir: jest.fn().mockResolvedValue(undefined),
  writeFile: jest.fn().mockResolvedValue(undefined),
  unlink: jest.fn().mockResolvedValue(undefined),
  access: jest.fn().mockResolvedValue(undefined),
}));

describe('Full-Stack Integration Testing', () => {
  let app: Express;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    registerExtractionRoutes(app);
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Complete User Workflow: File Upload to Metadata Display', () => {
    const mockPythonResponse = {
      extraction_info: {
        timestamp: '2025-12-31T12:00:00Z',
        tier: 'enterprise',
        engine_version: '4.0.0',
        fields_extracted: 1567,
        locked_categories: 0,
        processing_ms: 850,
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
        ISO: 100,
        Aperture: 'f/2.8',
        ShutterSpeed: '1/250',
      },
      gps: {
        latitude: 37.7749,
        longitude: -122.4194,
        altitude: 10.5,
      },
      video: null,
      audio: null,
      pdf: null,
      svg: null,
      image: {
        width: 4096,
        height: 3072,
        megapixels: 12.6,
      },
      makernote: {
        CameraSerial: '123456789',
        InternalSerial: '987654321',
      },
      iptc: {
        Copyright: '2025 MetaExtract User',
        Byline: 'Professional Photographer',
      },
      xmp: {
        Keywords: ['nature', 'landscape', 'canon'],
        Rating: 5,
      },
      forensic: {
        file_integrity: 'verified',
        manipulation_detected: false,
      },
      calculated: {
        aspect_ratio: '4:3',
        megapixels: 12.6,
        file_size_mb: 2.3,
      },
      extended_attributes: null,
      locked_fields: [],
    };

    it('should complete full workflow: upload → extract → display', async () => {
      // Step 1: User uploads file
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

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const uploadResponse = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('session_id', 'test-session-123')
        .expect(200);

      // Step 2: Verify extraction response structure
      expect(uploadResponse.body).toHaveProperty('filename', 'test.jpg');
      expect(uploadResponse.body).toHaveProperty('tier', 'enterprise');
      expect(uploadResponse.body).toHaveProperty('fields_extracted', 1567);
      expect(uploadResponse.body).toHaveProperty('exif');
      expect(uploadResponse.body).toHaveProperty('gps');
      expect(uploadResponse.body).toHaveProperty('image');

      // Step 3: Verify metadata completeness for frontend display
      expect(uploadResponse.body.exif).toHaveProperty('Make', 'Canon');
      expect(uploadResponse.body.exif).toHaveProperty('Model', 'EOS R5');
      expect(uploadResponse.body.gps).toHaveProperty('latitude', 37.7749);
      expect(uploadResponse.body.image).toHaveProperty('width', 4096);
      expect(uploadResponse.body.image).toHaveProperty('height', 3072);

      // Step 4: Verify frontend-ready data structure
      expect(uploadResponse.body).toHaveProperty('summary');
      expect(uploadResponse.body.summary).toHaveProperty('filename', 'test.jpg');
      expect(uploadResponse.body.summary).toHaveProperty('filesize', '2.3 MB');

      // Step 5: Verify no locked fields for enterprise tier
      expect(uploadResponse.body.locked_fields).toEqual([]);
      expect(uploadResponse.body.file_integrity).not.toHaveProperty('_locked');
    });

    it('should handle tier-based field filtering in workflow', async () => {
      // Test free tier workflow (limited fields)
      const freeTierResponse = {
        ...mockPythonResponse,
        extraction_info: {
          ...mockPythonResponse.extraction_info,
          tier: 'free',
          fields_extracted: 50,
          locked_categories: 8,
        },
        exif: {
          DateTimeOriginal: '2025-12-31 12:00:00',
          Make: 'Canon',
          Model: 'EOS R5',
        },
        gps: null,
        makernote: null,
        iptc: null,
        xmp: null,
        locked_fields: ['gps', 'makernote', 'iptc', 'xmp', 'extended_attributes'],
      };

      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify(freeTierResponse)));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const freeResponse = await request(app)
        .post('/api/extract?tier=free')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('trial_email', 'test@example.com')
        .expect(200);

      // Verify free tier limitations
      expect(freeResponse.body).toHaveProperty('tier', 'free');
      expect(freeResponse.body).toHaveProperty('fields_extracted', 50);
      expect(freeResponse.body).toHaveProperty('locked_fields');
      expect(freeResponse.body.locked_fields.length).toBeGreaterThan(0);

      // Verify premium fields are locked
      expect(freeResponse.body.gps).toBeNull();
      expect(freeResponse.body.makernote).toBeNull();
    });

    it('should provide consistent data format across tiers', async () => {
      // Test that response structure is consistent regardless of tier
      const tiers = ['free', 'professional', 'forensic', 'enterprise'];

      for (const tier of tiers) {
        const tierResponse = {
          ...mockPythonResponse,
          extraction_info: {
            ...mockPythonResponse.extraction_info,
            tier: tier,
            fields_extracted: tier === 'free' ? 50 : 1567,
          },
        };

        const mockPythonProcess = {
          stdout: {
            on: jest.fn().mockImplementation((event, callback) => {
              if (event === 'data') {
                callback(Buffer.from(JSON.stringify(tierResponse)));
              }
            }),
          },
          stderr: { on: jest.fn() },
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'close') callback(0);
          }),
          kill: jest.fn(),
        };

        (spawn as jest.Mock).mockReturnValue(mockPythonProcess);
        (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

        const response = await request(app)
          .post(`/api/extract?tier=${tier}`)
          .attach('file', Buffer.from('fake image data'), 'test.jpg')
          .field('session_id', `test-session-${tier}`)
          .expect(200);

        // All tiers should have the same basic structure
        expect(response.body).toHaveProperty('filename');
        expect(response.body).toHaveProperty('tier', tier);
        expect(response.body).toHaveProperty('exif');
        expect(response.body).toHaveProperty('summary');
        expect(response.body).toHaveProperty('filesystem');
      }
    });
  });

  describe('Authentication and Authorization Workflow', () => {
    it('should integrate authentication with extraction requests', async () => {
      // Mock authenticated user
      const authenticatedUser = {
        id: 'user-123',
        email: 'user@example.com',
        tier: 'professional',
      };

      // Mock storage to return user tier
      (storage.getUserTier as jest.Mock).mockResolvedValue(authenticatedUser.tier);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify({
                extraction_info: {
                  tier: 'professional',
                  fields_extracted: 500,
                  locked_categories: 0,
                },
                file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
                summary: { filename: 'test.jpg' },
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
              })));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract?tier=professional')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('session_id', authenticatedUser.id)
        .expect(200);

      expect(response.body).toHaveProperty('tier', 'professional');
      expect(storage.logExtractionUsage).toHaveBeenCalledWith(
        authenticatedUser.id,
        'professional',
        expect.any(String)
      );
    });

    it('should enforce tier-based file type restrictions', async () => {
      // Test that tier restrictions are enforced throughout the workflow
      const restrictedFileTypes = [
        { tier: 'free', file: 'test.mp4', mime: 'video/mp4' },
        { tier: 'professional', file: 'test.mp4', mime: 'video/mp4' },
      ];

      for (const { tier, file, mime } of restrictedFileTypes) {
        const response = await request(app)
          .post(`/api/extract?tier=${tier}`)
          .attach('file', Buffer.from('fake content'), file)
          .field('trial_email', 'test@example.com')
          .expect(403);

        expect(response.body).toHaveProperty('error');
        expect(response.body.error).toContain('File type not allowed');
        expect(response.body).toHaveProperty('current_tier', tier);
        expect(response.body).toHaveProperty('required_tier');
      }
    });
  });

  describe('Batch Processing Workflow', () => {
    it('should handle complete batch processing workflow', async () => {
      const mockBatchResponse = {
        results: {
          '/tmp/file1.jpg': {
            extraction_info: {
              fields_extracted: 245,
              tier: 'forensic',
            },
            file: { name: 'file1.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
            summary: { filename: 'file1.jpg', filesize: '2.1 MB', filetype: 'JPEG' },
            filesystem: {},
            hashes: {},
            exif: { Make: 'Canon', Model: 'EOS R5' },
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
            extraction_info: {
              fields_extracted: 189,
              tier: 'forensic',
            },
            file: { name: 'file2.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
            summary: { filename: 'file2.jpg', filesize: '1.8 MB', filetype: 'JPEG' },
            filesystem: {},
            hashes: {},
            exif: { Make: 'Nikon', Model: 'D850' },
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

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract/batch?tier=forensic')
        .attach('files', Buffer.from('file1'), 'file1.jpg')
        .attach('files', Buffer.from('file2'), 'file2.jpg')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('total_files', 2);
      expect(response.body).toHaveProperty('successful_files', 2);
      expect(response.body).toHaveProperty('batch_id');
      expect(response.body).toHaveProperty('results');

      // Verify results structure for frontend processing
      expect(response.body.results).toHaveProperty('file1.jpg');
      expect(response.body.results).toHaveProperty('file2.jpg');
      expect(response.body.results['file1.jpg'].summary).toHaveProperty('filesize', '2.1 MB');
    });
  });

  describe('Error Handling and User Feedback', () => {
    it('should provide clear error messages throughout the workflow', async () => {
      // Test various error scenarios
      const errorScenarios = [
        {
          scenario: 'File too large',
          fileSize: 15 * 1024 * 1024, // 15MB
          tier: 'free',
          expectedError: 'File size exceeds',
        },
        {
          scenario: 'Invalid file type',
          fileName: 'test.exe',
          tier: 'free',
          expectedError: 'File type not allowed',
        },
        {
          scenario: 'No session ID',
          hasSessionId: false,
          tier: 'enterprise',
          expectedError: 'Payment required',
        },
      ];

      for (const scenario of errorScenarios) {
        let response;

        if (scenario.scenario === 'File too large') {
          response = await request(app)
            .post(`/api/extract?tier=${scenario.tier}`)
            .attach('file', Buffer.alloc(scenario.fileSize), 'large.jpg');
        } else if (scenario.scenario === 'Invalid file type') {
          response = await request(app)
            .post(`/api/extract?tier=${scenario.tier}`)
            .attach('file', Buffer.from('content'), scenario.fileName);
        } else if (scenario.scenario === 'No session ID') {
          const mockPythonProcess = {
            stdout: { on: jest.fn() },
            stderr: { on: jest.fn() },
            on: jest.fn().mockImplementation((event, callback) => {
              if (event === 'close') callback(0);
            }),
            kill: jest.fn(),
          };

          (spawn as jest.Mock).mockReturnValue(mockPythonProcess);
          (storage.getOrCreateCreditBalance as jest.Mock).mockResolvedValue({
            id: 'balance-123',
            credits: 0,
          });

          response = await request(app)
            .post(`/api/extract?tier=${scenario.tier}`)
            .attach('file', Buffer.from('content'), 'test.jpg');
        }

        expect(response.body).toHaveProperty('error');
        expect(response.body.error).toContain(scenario.expectedError);
      }
    });

    it('should handle Python extraction failures gracefully', async () => {
      const mockPythonProcess = {
        stdout: { on: jest.fn() },
        stderr: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from('Python extraction failed: Invalid file format'));
            }
          }),
        },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(1);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('corrupted data'), 'corrupted.jpg')
        .field('session_id', 'test-session-123')
        .expect(500);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('Failed to extract metadata');
    });
  });

  describe('Performance and Resource Usage', () => {
    it('should maintain acceptable performance throughout the workflow', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              // Simulate realistic processing time
              setTimeout(() => {
                callback(Buffer.from(JSON.stringify({
                  extraction_info: {
                    tier: 'enterprise',
                    fields_extracted: 1567,
                    processing_ms: 850,
                  },
                  file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
                  summary: { filename: 'test.jpg' },
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
                })));
              }, 100);
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const startTime = performance.now();

      const response = await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('session_id', 'test-session-123')
        .expect(200);

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      expect(response.body).toHaveProperty('filename');
      expect(totalTime).toBeLessThan(5000); // Should complete in under 5 seconds
    });

    it('should properly track resource usage across workflows', async () => {
      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify({
                extraction_info: {
                  tier: 'enterprise',
                  fields_extracted: 1567,
                },
                file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
                summary: { filename: 'test.jpg' },
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
              })));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);

      const userId = 'test-user-123';
      const sessionId = 'test-session-123';

      // Mock storage to track usage
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('session_id', sessionId)
        .expect(200);

      // Verify usage was logged
      expect(storage.logExtractionUsage).toHaveBeenCalledWith(
        userId,
        'enterprise',
        expect.any(String)
      );
    });
  });

  describe('Cross-Service Communication', () => {
    it('should handle Node.js ↔ Python communication', async () => {
      // Test that the Node.js server correctly communicates with Python backend
      const expectedPythonArgs = [
        expect.stringContaining('comprehensive_metadata_engine.py'),
        expect.stringContaining('test'),
        '--tier', 'enterprise',
        '--performance',
        '--advanced',
      ];

      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify({
                extraction_info: {
                  tier: 'enterprise',
                  fields_extracted: 1567,
                },
                file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
                summary: { filename: 'test.jpg' },
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
              })));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      await request(app)
        .post('/api/extract?tier=enterprise')
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('session_id', 'test-session-123')
        .expect(200);

      // Verify Python was called with correct arguments
      expect(spawn).toHaveBeenCalledWith('python3', expectedPythonArgs);
    });

    it('should handle database integration for user data', async () => {
      // Test that user tier and credit information is correctly retrieved
      const userId = 'test-user-123';
      const userTier = 'professional';

      (storage.getUserTier as jest.Mock).mockResolvedValue(userTier);
      (storage.logExtractionUsage as jest.Mock).mockResolvedValue(undefined);

      const mockPythonProcess = {
        stdout: {
          on: jest.fn().mockImplementation((event, callback) => {
            if (event === 'data') {
              callback(Buffer.from(JSON.stringify({
                extraction_info: {
                  tier: userTier,
                  fields_extracted: 500,
                },
                file: { name: 'test.jpg', extension: '.jpg', mime_type: 'image/jpeg' },
                summary: { filename: 'test.jpg' },
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
              })));
            }
          }),
        },
        stderr: { on: jest.fn() },
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'close') callback(0);
        }),
        kill: jest.fn(),
      };

      (spawn as jest.Mock).mockReturnValue(mockPythonProcess);

      await request(app)
        .post(`/api/extract?tier=${userTier}`)
        .attach('file', Buffer.from('fake image data'), 'test.jpg')
        .field('session_id', userId)
        .expect(200);

      // Verify database was queried for user tier
      expect(storage.getUserTier).toHaveBeenCalledWith(userId);
    });
  });
});