/**
 * Tests for Admin Routes
 *
 * Tests admin and monitoring endpoints:
 * - Health checks
 * - Analytics endpoints
 * - Admin dashboard
 * - Cache management
 * - Rate limiting
 */

import request from 'supertest';
import express, { Express } from 'express';
import { registerAdminRoutes } from '../routes/admin';

// Mock storage
jest.mock('../storage', () => ({
  storage: {
    getAnalyticsSummary: jest.fn(),
    getRecentExtractions: jest.fn(),
    getFileLevelAnalytics: jest.fn(),
    getAdminDashboardStats: jest.fn(),
    getAnalyticsByDateRange: jest.fn(),
    getCreditGrantByPaymentId: jest.fn(),
  },
}));

// Mock rate limit middleware
jest.mock('../rateLimitMiddleware', () => ({
  getRateLimitMetrics: jest.fn(),
  resetRateLimit: jest.fn(),
}));

// Mock security utilities
jest.mock('../utils/enhanced-quota-handler', () => ({
  getRecentSecurityEvents: jest.fn(),
  getSecurityStats: jest.fn(),
}));

// Mock admin auth middleware
jest.mock('../middleware/admin-auth', () => ({
  adminAuthMiddleware: (req: any, res: any, next: any) => {
    if (req.headers['x-admin-token'] !== 'admin-secret') {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    req.user = { id: 'admin-123', role: 'admin' };
    next();
  },
  adminRateLimitMiddleware: (req: any, res: any, next: any) => {
    next();
  },
  healthCheckAuth: (req: any, res: any, next: any) => {
    next();
  },
}));

// Mock security utilities
jest.mock('../security-utils', () => ({
  sanitizeFilename: jest.fn(input => input),
}));

describe('Admin Routes', () => {
  let app: Express;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    registerAdminRoutes(app);
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Health Check', () => {
    it('should return health status', async () => {
      const response = await request(app).get('/api/health');

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('ok');
      expect(response.body.service).toBe('MetaExtract API');
      expect(response.body.version).toBe('2.0.0');
      expect(response.body.timestamp).toBeDefined();
    });
  });

  describe('Analytics Endpoints', () => {
    it('should return analytics summary with admin auth', async () => {
      const mockSummary = {
        totalExtractions: 1000,
        activeUsers: 500,
        storageUsed: 1024000,
      };

      const { storage } = require('../storage');
      storage.getAnalyticsSummary.mockResolvedValue(mockSummary);

      const response = await request(app)
        .get('/api/admin/analytics')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockSummary);
    });

    it('should reject analytics without admin auth', async () => {
      const response = await request(app).get('/api/admin/analytics');

      expect(response.status).toBe(401);
    });

    it('should return recent extractions', async () => {
      const mockExtractions = [
        { id: '1', filename: 'test.jpg', status: 'success' },
        { id: '2', filename: 'test2.png', status: 'error' },
      ];

      const { storage } = require('../storage');
      storage.getRecentExtractions.mockResolvedValue(mockExtractions);

      const response = await request(app)
        .get('/api/admin/extractions?limit=50')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockExtractions);
    });

    it('should return file level analytics', async () => {
      const mockAnalytics = [
        { fileType: 'JPEG', count: 500, avgSize: 1024 },
        { fileType: 'PNG', count: 300, avgSize: 2048 },
      ];

      const { storage } = require('../storage');
      storage.getFileLevelAnalytics.mockResolvedValue(mockAnalytics);

      const response = await request(app)
        .get('/api/admin/analytics/files?limit=100')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.files).toEqual(mockAnalytics);
    });

    it('should return analytics by date range (first handler returns file analytics)', async () => {
      const mockAnalytics = {
        totalExtractions: 100,
        byProduct: { images: 80, documents: 20 },
      };

      const { storage } = require('../storage');
      storage.getFileLevelAnalytics.mockResolvedValue([
        { fileType: 'JPEG', count: 100 },
      ]);

      const response = await request(app)
        .get('/api/admin/analytics/range?start=2024-01-01&end=2024-01-31')
        .set('x-admin-token', 'admin-secret');

      // First route handler returns file analytics without date validation
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });
  });

  describe('Admin Dashboard', () => {
    it('should return dashboard stats', async () => {
      const mockDashboardStats = {
        totalUsers: 1000,
        totalExtractions: 5000,
        storageUsed: 10240000,
      };

      const mockSecurityStats = {
        criticalEvents: 2,
        highRiskEvents: 5,
      };

      const mockSecurityEvents = [
        { id: '1', severity: 'medium', message: 'Test event' },
      ];

      const mockExtractions = [
        { id: '1', filename: 'test.jpg', status: 'success' },
      ];

      const { storage } = require('../storage');
      const {
        getSecurityStats,
        getRecentSecurityEvents,
      } = require('../utils/enhanced-quota-handler');

      storage.getAdminDashboardStats.mockResolvedValue(mockDashboardStats);
      getSecurityStats.mockResolvedValue(mockSecurityStats);
      getRecentSecurityEvents.mockResolvedValue(mockSecurityEvents);
      storage.getRecentExtractions.mockResolvedValue(mockExtractions);

      const response = await request(app)
        .get('/api/admin/dashboard')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.dashboard).toBeDefined();
      expect(response.body.dashboard.stats).toEqual(mockDashboardStats);
      expect(response.body.dashboard.security).toBeDefined();
      expect(response.body.dashboard.extractions).toBeDefined();
      expect(response.body.timestamp).toBeDefined();
    });

    it('should calculate threat level correctly', async () => {
      const mockDashboardStats = { totalUsers: 100 };
      const mockSecurityStats = { criticalEvents: 10, highRiskEvents: 5 };
      const mockSecurityEvents = [
        { id: '1', severity: 'critical', message: 'Critical event' },
      ];
      const mockExtractions: any[] = [];

      const { storage } = require('../storage');
      const {
        getSecurityStats,
        getRecentSecurityEvents,
      } = require('../utils/enhanced-quota-handler');

      storage.getAdminDashboardStats.mockResolvedValue(mockDashboardStats);
      getSecurityStats.mockResolvedValue(mockSecurityStats);
      getRecentSecurityEvents.mockResolvedValue(mockSecurityEvents);
      storage.getRecentExtractions.mockResolvedValue(mockExtractions);

      const response = await request(app)
        .get('/api/admin/dashboard')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body.dashboard.security.threatLevel).toBe('high');
    });
  });

  describe('Rate Limit Endpoints', () => {
    it('should return rate limit metrics', async () => {
      const { getRateLimitMetrics } = require('../rateLimitMiddleware');
      const mockMetrics = { totalRequests: 1000, blockedRequests: 5 };
      getRateLimitMetrics.mockImplementation((req: any, res: any) => {
        res.json(mockMetrics);
      });

      const response = await request(app)
        .get('/api/admin/rate-limit/metrics')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockMetrics);
    });

    it('should reset rate limit for identifier', async () => {
      const { resetRateLimit } = require('../rateLimitMiddleware');
      resetRateLimit.mockImplementation((req: any, res: any) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .post('/api/admin/rate-limit/reset/user-123')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });
  });

  describe('Credit Refund Eligibility', () => {
    it('should return refund eligibility for valid payment', async () => {
      const { storage } = require('../storage');
      const mockGrant = {
        amount: 100,
        remaining: 100,
        createdAt: new Date(),
      };
      storage.getCreditGrantByPaymentId.mockResolvedValue(mockGrant);

      const response = await request(app)
        .get('/api/admin/credits/refund-eligibility?paymentId=pay_123')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body.eligible).toBe(true);
      expect(response.body.policy).toEqual({
        window_days: 7,
        unused_only: true,
      });
    });

    it('should return not eligible for used credits', async () => {
      const { storage } = require('../storage');
      const mockGrant = {
        amount: 100,
        remaining: 50, // Some credits used
        createdAt: new Date(),
      };
      storage.getCreditGrantByPaymentId.mockResolvedValue(mockGrant);

      const response = await request(app)
        .get('/api/admin/credits/refund-eligibility?paymentId=pay_123')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(200);
      expect(response.body.eligible).toBe(false);
      expect(response.body.details.unused).toBe(false);
    });

    it('should return 404 for non-existent payment', async () => {
      const { storage } = require('../storage');
      storage.getCreditGrantByPaymentId.mockResolvedValue(null);

      const response = await request(app)
        .get('/api/admin/credits/refund-eligibility?paymentId=non-existent')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(404);
      expect(response.body.error).toBe('Purchase not found');
    });

    it('should require paymentId parameter', async () => {
      const response = await request(app)
        .get('/api/admin/credits/refund-eligibility')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(400);
      expect(response.body.error).toBe('paymentId is required');
    });
  });

  describe('Cache Management', () => {
    it('should clear cache with valid pattern', async () => {
      const { sanitizeFilename } = require('../security-utils');

      const response = await request(app)
        .post('/api/performance/cache/clear')
        .set('x-admin-token', 'admin-secret')
        .send({ pattern: 'metadata:test-123' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(sanitizeFilename).toHaveBeenCalledWith('metadata:test-123');
    });

    it('should reject invalid cache pattern', async () => {
      const response = await request(app)
        .post('/api/performance/cache/clear')
        .set('x-admin-token', 'admin-secret')
        .send({ pattern: 'invalid:pattern:*' });

      expect(response.status).toBe(400);
      expect(response.body.error).toBe('Invalid pattern');
    });

    it('should use default pattern if not provided', async () => {
      const response = await request(app)
        .post('/api/performance/cache/clear')
        .set('x-admin-token', 'admin-secret')
        .send({});

      expect(response.status).toBe(200);
      expect(response.body.pattern).toBe('metadata:*');
    });
  });

  describe('Error Handling', () => {
    it('should handle analytics errors gracefully', async () => {
      const { storage } = require('../storage');
      storage.getAnalyticsSummary.mockRejectedValue(
        new Error('Database error')
      );

      const response = await request(app)
        .get('/api/admin/analytics')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(500);
      expect(response.body.error).toBe('Failed to fetch analytics');
    });

    it('should handle dashboard errors gracefully', async () => {
      const { storage } = require('../storage');
      const {
        getSecurityStats,
        getRecentSecurityEvents,
      } = require('../utils/enhanced-quota-handler');

      storage.getAdminDashboardStats.mockRejectedValue(new Error('DB error'));
      getSecurityStats.mockResolvedValue({});
      getRecentSecurityEvents.mockResolvedValue([]);
      storage.getRecentExtractions.mockResolvedValue([]);

      const response = await request(app)
        .get('/api/admin/dashboard')
        .set('x-admin-token', 'admin-secret');

      expect(response.status).toBe(500);
      expect(response.body.error).toBe('Failed to get dashboard data');
    });
  });
});
