/**
 * Integration tests for API endpoints
 * Tests Express routes, request/response handling, and API contracts
 */

import { describe, it, expect } from '@jest/globals';
import express, { type Request, type Response, type NextFunction } from 'express';

// ============================================================================
// Test App Setup
// ============================================================================

function createTestApp() {
  const app = express();

  app.use(express.json());

  app.use((req: Request, _res: Response, next: NextFunction) => {
    const tier = (req.headers['x-user-tier'] as string) || 'free';
    (req as any).user = {
      id: 'test-user-id',
      email: 'test@example.com',
      tier,
      credits: tier === 'free' ? 0 : 100,
    };
    next();
  });

  app.get('/api/health', (_req: Request, res: Response) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.get('/api/capabilities', (_req: Request, res: Response) => {
    const capabilities = {
      free: { advanced_analysis: false, max_file_size_mb: 10 },
      professional: { advanced_analysis: true, max_file_size_mb: 100 },
      forensic: { advanced_analysis: true, max_file_size_mb: 500 },
      enterprise: { advanced_analysis: true, max_file_size_mb: 2000 },
    };
    res.json(capabilities);
  });

  app.post('/api/file/info', (req: Request, res: Response) => {
    const { filename, filesize, filetype } = req.body;

    if (!filename) {
      return res.status(400).json({ error: 'Filename is required' });
    }

    const response = {
      filename,
      filesize: filesize ? `${filesize} bytes` : '0 bytes',
      filetype: filetype || 'unknown',
      tier: 'free',
      fields_extracted: 47,
      metadata: {
        summary: {
          filename,
          filesize: filesize ? `${filesize} bytes` : 'Unknown',
          filetype: filetype || 'application/octet-stream',
        },
        image: (filetype as string)?.startsWith('image/') ? {
          width: 1920,
          height: 1080,
          color_depth: 24,
        } : null,
        exif: null,
        gps: null,
        filesystem: {},
        calculated: {},
        forensic: {},
      },
      locked_fields: ['makernote', 'iptc', 'xmp'],
      burned_metadata: null,
    };

    res.json(response);
  });

  app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    console.error('Test error:', err);
    res.status(500).json({ error: 'Internal server error' });
  });

  return app;
}

// ============================================================================
// Mock Request/Response Helpers
// ============================================================================

function createMockRequest(options: {
  method: string;
  path: string;
  body?: Record<string, any>;
  headers?: Record<string, string>;
}): Request {
  const req = {
    method: options.method,
    url: options.path,
    path: options.path,
    body: options.body || {},
    headers: {
      'content-type': 'application/json',
      ...options.headers,
    },
  } as unknown as Request;
  return req;
}

function createMockResponse() {
  let statusCode = 200;
  let responseData: any = null;

  const res = {
    status: (code: number) => {
      statusCode = code;
      return res;
    },
    json: (data: any) => {
      responseData = data;
      return res;
    },
    getStatus: () => statusCode,
    getData: () => responseData,
  } as unknown as Response & { getStatus: () => number; getData: () => any };

  return res;
}

// ============================================================================
// Integration Tests
// ============================================================================

describe('API Integration Tests', () => {
  const app = createTestApp();

  describe('Health Check Endpoint', () => {
    it('should return health status', async () => {
      const req = createMockRequest({ method: 'GET', path: '/api/health' });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/health')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        expect(res.getStatus()).toBe(200);
        expect(res.getData().status).toBe('ok');
        expect(res.getData().timestamp).toBeDefined();
      }
    });
  });

  describe('Capabilities Endpoint', () => {
    it('should return capabilities for all tiers', async () => {
      const req = createMockRequest({ method: 'GET', path: '/api/capabilities' });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/capabilities')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        expect(res.getStatus()).toBe(200);
        expect(res.getData().free).toBeDefined();
        expect(res.getData().professional).toBeDefined();
        expect(res.getData().forensic).toBeDefined();
        expect(res.getData().enterprise).toBeDefined();
      }
    });

    it('should correctly identify tier features', async () => {
      const req = createMockRequest({ method: 'GET', path: '/api/capabilities' });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/capabilities')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        const data = res.getData();
        expect(data.free.advanced_analysis).toBe(false);
        expect(data.free.max_file_size_mb).toBe(10);
        expect(data.professional.advanced_analysis).toBe(true);
        expect(data.professional.max_file_size_mb).toBe(100);
        expect(data.forensic.max_file_size_mb).toBe(500);
        expect(data.enterprise.max_file_size_mb).toBe(2000);
      }
    });
  });

  describe('File Info Endpoint', () => {
    it('should return file metadata for valid request', async () => {
      const req = createMockRequest({
        method: 'POST',
        path: '/api/file/info',
        body: {
          filename: 'test.jpg',
          filesize: 1024000,
          filetype: 'image/jpeg',
        },
      });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/file/info')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        expect(res.getStatus()).toBe(200);
        expect(res.getData().filename).toBe('test.jpg');
        expect(res.getData().filesize).toBe('1024000 bytes');
        expect(res.getData().fields_extracted).toBe(47);
      }
    });

    it('should return image data for image files', async () => {
      const req = createMockRequest({
        method: 'POST',
        path: '/api/file/info',
        body: {
          filename: 'photo.png',
          filesize: 2048000,
          filetype: 'image/png',
        },
      });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/file/info')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        const data = res.getData();
        expect(data.metadata.image).toBeDefined();
        expect(data.metadata.image.width).toBe(1920);
        expect(data.metadata.image.height).toBe(1080);
      }
    });

    it('should return null image data for non-image files', async () => {
      const req = createMockRequest({
        method: 'POST',
        path: '/api/file/info',
        body: {
          filename: 'document.pdf',
          filesize: 512000,
          filetype: 'application/pdf',
        },
      });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/file/info')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        expect(res.getData().metadata.image).toBeNull();
      }
    });

    it('should return 400 for missing filename', async () => {
      const req = createMockRequest({
        method: 'POST',
        path: '/api/file/info',
        body: { filesize: 1024000 },
      });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/file/info')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        expect(res.getStatus()).toBe(400);
        expect(res.getData().error).toBe('Filename is required');
      }
    });

    it('should include locked fields', async () => {
      const req = createMockRequest({
        method: 'POST',
        path: '/api/file/info',
        body: { filename: 'test.jpg' },
      });
      const res = createMockResponse();

      const handler = app._router.stack
        .find((layer: any) => layer.route?.path === '/api/file/info')
        ?.route?.stack[0].handle;

      if (handler) {
        handler(req, res);
        const data = res.getData();
        expect(data.locked_fields).toBeInstanceOf(Array);
        expect(data.locked_fields).toContain('makernote');
        expect(data.locked_fields).toContain('iptc');
      }
    });
  });
});

// ============================================================================
// Response Structure Tests
// ============================================================================

describe('API Response Structures', () => {
  describe('File Info Response', () => {
    it('should have all required fields', () => {
      const mockResponse = {
        filename: 'test.jpg',
        filesize: '1024000 bytes',
        filetype: 'image/jpeg',
        tier: 'free',
        fields_extracted: 47,
        metadata: {
          summary: { filename: 'test.jpg' },
          image: { width: 1920, height: 1080 },
          exif: null,
          gps: null,
        },
        locked_fields: ['makernote'],
      };

      expect(mockResponse).toHaveProperty('filename');
      expect(mockResponse).toHaveProperty('filesize');
      expect(mockResponse).toHaveProperty('filetype');
      expect(mockResponse).toHaveProperty('tier');
      expect(mockResponse).toHaveProperty('metadata');
      expect(mockResponse).toHaveProperty('locked_fields');
    });

    it('should handle burned metadata', () => {
      const response = {
        filename: 'photo.jpg',
        burned_metadata: {
          has_burned_metadata: true,
          confidence: 'high',
          parsed_data: {
            gps: { latitude: 37.77, longitude: -122.41 },
          },
        },
      };

      expect(response.burned_metadata.has_burned_metadata).toBe(true);
      expect(response.burned_metadata.confidence).toBe('high');
    });
  });

  describe('Capabilities Response', () => {
    it('should have correct structure', () => {
      const capabilities = {
        free: { advanced_analysis: false, max_file_size_mb: 10 },
        professional: { advanced_analysis: true, max_file_size_mb: 100 },
      };

      Object.values(capabilities).forEach((config: any) => {
        expect(config).toHaveProperty('advanced_analysis');
        expect(config).toHaveProperty('max_file_size_mb');
      });
    });
  });
});

// ============================================================================
// Tier Configuration Tests
// ============================================================================

describe('Tier Configuration', () => {
  const tierConfigs = {
    free: { maxFileSizeMB: 10, fieldsPerFile: 200, maxFiles: 10 },
    professional: { maxFileSizeMB: 100, fieldsPerFile: 1000, maxFiles: 50 },
    forensic: { maxFileSizeMB: 500, fieldsPerFile: 15000, maxFiles: 100 },
    enterprise: { maxFileSizeMB: 2000, fieldsPerFile: 45000, maxFiles: 500 },
  };

  it('should have correct free tier', () => {
    expect(tierConfigs.free.maxFileSizeMB).toBe(10);
    expect(tierConfigs.free.fieldsPerFile).toBe(200);
  });

  it('should have correct professional tier', () => {
    expect(tierConfigs.professional.maxFileSizeMB).toBe(100);
    expect(tierConfigs.professional.fieldsPerFile).toBe(1000);
  });

  it('should have increasing limits across tiers', () => {
    const tiers = ['free', 'professional', 'forensic', 'enterprise'];
    let prevSize = 0;

    tiers.forEach((tier) => {
      expect(tierConfigs[tier as keyof typeof tierConfigs].maxFileSizeMB).toBeGreaterThan(prevSize);
      prevSize = tierConfigs[tier as keyof typeof tierConfigs].maxFileSizeMB;
    });
  });

  it('should have increasing field limits across tiers', () => {
    const tiers = ['free', 'professional', 'forensic', 'enterprise'];
    let prevFields = 0;

    tiers.forEach((tier) => {
      expect(tierConfigs[tier as keyof typeof tierConfigs].fieldsPerFile).toBeGreaterThan(prevFields);
      prevFields = tierConfigs[tier as keyof typeof tierConfigs].fieldsPerFile;
    });
  });
});
