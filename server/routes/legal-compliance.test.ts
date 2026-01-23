/**
 * Tests for Legal Compliance Routes
 *
 * Tests GDPR requests, privacy policy, and terms of service endpoints
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { registerLegalComplianceRoutes } from './legal-compliance';

// Mock storage module
const mockGetGdprRequest = jest.fn();
const mockCreateGdprRequest = jest.fn();
const mockUpdateGdprRequest = jest.fn();
const mockGetUserByEmail = jest.fn();

jest.mock('../storage', () => ({
  storage: {
    getGdprRequest: (...args: any[]) => mockGetGdprRequest(...args),
    createGdprRequest: (...args: any[]) => mockCreateGdprRequest(...args),
    updateGdprRequest: (...args: any[]) => mockUpdateGdprRequest(...args),
    getUserByEmail: (...args: any[]) => mockGetUserByEmail(...args),
  },
}));

// Mock auth - routes use authenticateToken middleware
jest.mock('../auth', () => ({
  authenticateToken: (req: any, _res: any, next: any) => {
    req.user = { id: 'test-user-123' };
    next();
  },
  requireAuth: (req: any, _res: any, next: any) => {
    req.user = { id: 'test-user-123' };
    next();
  },
}));

// Mock rateLimitAPI - it returns a middleware when called with no args
jest.mock('../rateLimitMiddleware', () => ({
  rateLimitAPI: jest.fn(() => (_req: any, _res: any, next: any) => next()),
}));

describe('Legal Compliance Routes', () => {
  let app: Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    registerLegalComplianceRoutes(app);
    jest.clearAllMocks();
  });

  describe('GET /api/legal/privacy', () => {
    it('should return privacy policy', async () => {
      const response = await request(app).get('/api/legal/privacy').expect(200);

      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('lastUpdated');
      expect(response.body).toHaveProperty('content');
      expect(response.body.version).toBe('1.0.0');
    });

    it('should return privacy policy with correct structure', async () => {
      const response = await request(app).get('/api/legal/privacy').expect(200);

      expect(response.body.content).toContain('Privacy Policy');
      expect(response.body.content).toContain('Information We Collect');
    });
  });

  describe('GET /api/legal/terms', () => {
    it('should return terms of service', async () => {
      const response = await request(app).get('/api/legal/terms').expect(200);

      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('lastUpdated');
      expect(response.body).toHaveProperty('content');
    });

    it('should return terms with correct structure', async () => {
      const response = await request(app).get('/api/legal/terms').expect(200);

      expect(response.body.content).toContain('Terms of Service');
      expect(response.body.content).toContain('Acceptance of Terms');
    });
  });

  describe('POST /api/legal/gdpr', () => {
    it('should accept valid GDPR request', async () => {
      mockCreateGdprRequest.mockResolvedValue({ id: 'req-123' });

      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'access',
          reason: 'I want to know what data you have about me',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('requestType', 'access');
    });

    it('should reject invalid request type', async () => {
      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'invalid',
          reason: 'Test reason',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
        })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject short reason', async () => {
      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'access',
          reason: 'Short',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
        })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject invalid email', async () => {
      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'access',
          reason: 'I want to exercise my data rights',
          verification: {
            email: 'not-an-email',
            confirmationCode: 'ABC123',
          },
        })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject invalid confirmation code', async () => {
      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'access',
          reason: 'I want to exercise my data rights',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC',
          },
        })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should handle access request type', async () => {
      mockCreateGdprRequest.mockResolvedValue({ id: 'req-123' });

      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'access',
          reason: 'I want to exercise my data rights',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
    });

    it('should handle rectification request type', async () => {
      mockCreateGdprRequest.mockResolvedValue({ id: 'req-123' });

      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'rectification',
          reason: 'I want to correct my data',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
          updates: { name: 'New Name' },
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
    });

    it('should handle erasure request type', async () => {
      mockCreateGdprRequest.mockResolvedValue({ id: 'req-123' });

      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'erasure',
          reason: 'I want to delete my data',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
    });

    it('should handle portability request type', async () => {
      mockCreateGdprRequest.mockResolvedValue({ id: 'req-123' });

      const response = await request(app)
        .post('/api/legal/gdpr')
        .send({
          requestType: 'portability',
          reason: 'I want to export my data',
          verification: {
            email: 'user@example.com',
            confirmationCode: 'ABC123',
          },
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
    });
  });

  describe('GET /api/legal/dpa', () => {
    it('should return data processing agreement', async () => {
      const response = await request(app).get('/api/legal/dpa').expect(200);

      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('lastUpdated');
      expect(response.body).toHaveProperty('content');
      expect(response.body.content).toContain('Data Processing Agreement');
    });
  });

  describe('GET /api/legal/cookies', () => {
    it('should return cookie policy', async () => {
      const response = await request(app).get('/api/legal/cookies').expect(200);

      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('lastUpdated');
      expect(response.body).toHaveProperty('content');
      expect(response.body.content).toContain('Cookie Policy');
    });
  });
});
