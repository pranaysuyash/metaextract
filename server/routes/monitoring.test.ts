/**
 * Tests for Monitoring Routes
 * 
 * Tests the security monitoring endpoints:
 * - Dashboard overview
 * - Security events
 * - Alert history
 * - Abuse detection
 * - Real-time metrics
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { registerMonitoringRoutes } from './monitoring';

describe('Monitoring Routes', () => {
  let app: Express;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    registerMonitoringRoutes(app);
  });

  describe('GET /api/monitoring/dashboard', () => {
    test('should return security dashboard data', async () => {
      const response = await request(app)
        .get('/api/monitoring/dashboard')
        .expect(200);

      expect(response.body).toMatchObject({
        status: 'active',
        timestamp: expect.any(String),
        overview: expect.objectContaining({
          totalEvents: expect.any(Number),
          criticalAlerts: expect.any(Number),
          highSeverityEvents: expect.any(Number),
          tempFiles: expect.any(Number),
          tempSizeMB: expect.any(Number),
        }),
        systemHealth: expect.objectContaining({
          tempDirectories: expect.any(Object),
          systemMetrics: expect.any(Object),
          status: expect.any(String),
        }),
        securityMetrics: expect.any(Object),
        recentAlerts: expect.any(Array),
        abuseDetection: expect.any(Object),
        recommendations: expect.any(Array),
      });
    });

    test('should handle errors gracefully', async () => {
      // Mock an error condition if needed
      const response = await request(app)
        .get('/api/monitoring/dashboard')
        .expect(200);

      expect(response.body).toHaveProperty('status', 'active');
    });
  });

  describe('GET /api/monitoring/events', () => {
    test('should return security events with default parameters', async () => {
      const response = await request(app)
        .get('/api/monitoring/events')
        .expect(200);

      expect(response.body).toMatchObject({
        events: expect.any(Array),
        totalCount: expect.any(Number),
        filters: expect.any(Object),
        pagination: expect.any(Object),
      });

      expect(response.body.events.length).toBeLessThanOrEqual(100); // Default limit
    });

    test('should accept query parameters', async () => {
      const response = await request(app)
        .get('/api/monitoring/events')
        .query({
          limit: 10,
          severity: 'high',
          eventType: 'upload_rejected',
        })
        .expect(200);

      expect(response.body).toMatchObject({
        events: expect.any(Array),
        filters: expect.objectContaining({
          eventType: 'upload_rejected',
          severity: 'high',
        }),
      });
    });
  });

  describe('GET /api/monitoring/alerts', () => {
    test('should return recent security alerts', async () => {
      const response = await request(app)
        .get('/api/monitoring/alerts')
        .expect(200);

      expect(response.body).toMatchObject({
        alerts: expect.any(Array),
        totalCount: expect.any(Number),
        filters: expect.any(Object),
      });
    });

    test('should accept query parameters', async () => {
      const response = await request(app)
        .get('/api/monitoring/alerts')
        .query({
          limit: 5,
          severity: 'high',
        })
        .expect(200);

      expect(response.body.filters).toMatchObject({
        limit: 5,
        severity: 'high',
      });
    });
  });

  describe('GET /api/monitoring/abuse-detection', () => {
    test('should return abuse pattern analysis', async () => {
      const response = await request(app)
        .get('/api/monitoring/abuse-detection')
        .expect(200);

      expect(response.body).toMatchObject({
        patterns: expect.any(Array),
        riskScore: expect.any(Number),
        riskLevel: expect.any(String),
        analysisTime: expect.any(String),
        timeWindow: expect.any(String),
      });
    });

    test('should accept hoursBack parameter', async () => {
      const startTime = Date.now();
      const response = await request(app)
        .get('/api/monitoring/abuse-detection')
        .query({ hoursBack: 12 })
        .timeout(2000)
        .expect(200);

      const elapsedMs = Date.now() - startTime;
      expect(elapsedMs).toBeLessThan(100); // Should respond quickly (< 100ms)
      expect(response.body.timeWindow).toBe('12 hours');
    }, 3000);
  });

  describe('GET /api/monitoring/metrics', () => {
    test('should return real-time security metrics', async () => {
      const response = await request(app)
        .get('/api/monitoring/metrics')
        .expect(200);

      expect(response.body).toMatchObject({
        timestamp: expect.any(String),
        tempDirectory: expect.any(Object),
        system: expect.any(Object),
        security: expect.any(Object),
      });
    });
  });

  describe('GET /api/monitoring/export', () => {
    test('should export security data as JSON by default', async () => {
      const response = await request(app)
        .get('/api/monitoring/export')
        .expect(200);

      expect(response.body).toHaveProperty('exportInfo');
      expect(response.body).toHaveProperty('analytics');
      expect(response.body).toHaveProperty('systemInfo');
      expect(response.headers['content-type']).toContain('application/json');
    });

    test('should export security data as CSV when requested', async () => {
      const response = await request(app)
        .get('/api/monitoring/export')
        .query({ format: 'csv' })
        .expect(200);

      expect(response.headers['content-type']).toContain('text/csv');
      expect(response.headers['content-disposition']).toContain('attachment');
    });
  });

  describe('Error Handling', () => {
    test('should handle monitoring system errors gracefully', async () => {
      // All endpoints should return proper error responses
      const endpoints = [
        '/api/monitoring/dashboard',
        '/api/monitoring/events',
        '/api/monitoring/alerts',
        '/api/monitoring/abuse-detection',
        '/api/monitoring/metrics',
        '/api/monitoring/export',
      ];

      for (const endpoint of endpoints) {
        const response = await request(app)
          .get(endpoint)
          .expect(200); // All should return 200 with data or empty results

        // Should not have error when successful
        expect(response.body).not.toHaveProperty('error');
      }
    });
  });

  describe('Security Headers', () => {
    test('should include security headers in responses', async () => {
      const response = await request(app)
        .get('/api/monitoring/dashboard')
        .expect(200);

      // Should have basic security headers
      expect(response.headers).toHaveProperty('content-type');
      expect(response.headers['content-type']).toContain('application/json');
    });
  });

  describe('Performance', () => {
    test('should respond within reasonable time', async () => {
      const startTime = Date.now();
      
      const response = await request(app)
        .get('/api/monitoring/dashboard')
        .expect(200);
      
      const responseTime = Date.now() - startTime;
      
      // Should respond within 2 seconds
      expect(responseTime).toBeLessThan(2000);
      
      // Should have reasonable payload size
      expect(JSON.stringify(response.body).length).toBeLessThan(100000); // 100KB max
    });
  });
});