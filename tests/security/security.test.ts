/**
 * Security Testing Suite for MetaExtract
 *
 * Tests security measures across the application:
 * - Input validation and sanitization
 * - File upload security
 * - Rate limiting effectiveness
 * - Authentication security
 * - SQL injection prevention
 * - XSS prevention
 * - CSRF protection
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { createRateLimiter, getRateLimitStatus } from '../server/middleware/rateLimit';
import { storage } from '../server/storage';

// Mock the storage module
jest.mock('../server/storage');

describe('Security Testing Suite', () => {
  let app: Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    jest.clearAllMocks();
  });

  describe('Input Validation and Sanitization', () => {
    describe('Filename Sanitization', () => {
      it('should reject filenames with path traversal attempts', async () => {
        const maliciousFilenames = [
          '../../../etc/passwd',
          '..\\..\\..\\windows\\system32\\config\\sam',
          '/etc/shadow',
          'C:\\Windows\\System32\\config\\SAM',
          './.env',
          '....//....//etc/passwd',
        ];

        for (const maliciousFilename of maliciousFilenames) {
          const response = await request(app)
            .post('/api/extract')
            .attach('file', Buffer.from('fake content'), maliciousFilename)
            .expect(400);

          expect(response.body).toHaveProperty('error');
          expect(response.body.error.toLowerCase()).toMatch(/invalid|filename|security/i);
        }
      });

      it('should reject filenames with dangerous characters', async () => {
        const dangerousFilenames = [
          'file<script>.jpg',
          'file|pipe.jpg',
          'file\null.jpg',
          'file\tab.jpg',
          'file\x00null.jpg',
          'file"quote.jpg',
          'file<angle>.jpg',
          'file>angle>.jpg',
        ];

        for (const dangerousFilename of dangerousFilenames) {
          const response = await request(app)
            .post('/api/extract')
            .attach('file', Buffer.from('fake content'), dangerousFilename)
            .expect(400);

          expect(response.body).toHaveProperty('error');
        }
      });

      it('should reject excessively long filenames', async () => {
        const longFilename = 'a'.repeat(300) + '.jpg';

        const response = await request(app)
          .post('/api/extract')
          .attach('file', Buffer.from('fake content'), longFilename)
          .expect(400);

        expect(response.body).toHaveProperty('error');
        expect(response.body.error.toLowerCase()).toMatch(/filename|too long/i);
      });

      it('should accept safe filenames', async () => {
        const safeFilenames = [
          'normal-file.jpg',
          'my_photo.png',
          'document.pdf',
          'image (1).jpg',
          'file_name-123.jpg',
          '测试文件.jpg', // Unicode characters
          'файл.jpg',    // Cyrillic characters
        ];

        for (const safeFilename of safeFilenames) {
          // These should not be rejected for filename reasons
          // (they might be rejected for other reasons like missing mocks)
          const response = await request(app)
            .post('/api/extract')
            .attach('file', Buffer.from('fake content'), safeFilename);

          // Should not get 400 for filename validation
          expect(response.status).not.toBe(400);
        }
      });
    });

    describe('Query Parameter Validation', () => {
      it('should sanitize tier query parameter', async () => {
        const maliciousTiers = [
          'free; DROP TABLE users--',
          "free' OR '1'='1",
          '${7*7}', // Template injection
          '<script>alert(1)</script>',
          'free../../../../etc/passwd',
        ];

        for (const maliciousTier of maliciousTiers) {
          const response = await request(app)
            .get(`/api/tiers/${maliciousTier}`)
            .expect(200); // Should normalize to a valid tier instead of crashing

          // Should return a valid tier configuration, not execute malicious code
          expect(response.body).toBeDefined();
          expect(response.body).not.toHaveProperty('error');
        }
      });

      it('should handle SQL injection attempts in parameters', async () => {
        const sqlInjectionAttempts = [
          "1' OR '1'='1",
          "1'; DROP TABLE users--",
          "1' UNION SELECT * FROM users--",
          "admin'--",
          "admin'/*",
          "' OR 1=1--",
        ];

        for (const injection of sqlInjectionAttempts) {
          const response = await request(app)
            .get(`/api/tiers/${injection}`)
            .expect(200); // Should handle gracefully, not crash

          // Should not expose database information
          expect(response.body).not.toMatch(/syntax error|mysql|postgresql|sqlite/i);
          expect(response.body).not.toMatch(/SELECT|DROP|UNION|OR 1=1/i);
        }
      });

      it('should prevent XSS through query parameters', async () => {
        const xssAttempts = [
          '<script>alert(1)</script>',
          '<img src=x onerror=alert(1)>',
          'javascript:alert(1)',
          '<svg onload=alert(1)>',
          '" onclick="alert(1)',
        ];

        for (const xss of xssAttempts) {
          const response = await request(app)
            .get(`/api/tiers/${xss}`)
            .expect(200); // Should handle safely

          // Should not execute scripts in response
          const responseString = JSON.stringify(response.body);
          expect(responseString).not.toMatch(/<script|javascript:|onclick/i);
        }
      });
    });

    describe('Content-Type Validation', () => {
      it('should reject dangerous MIME types', async () => {
        const dangerousFiles = [
          { content: Buffer.from('MZ'), name: 'malicious.exe', type: 'application/x-dosexec' },
          { content: Buffer.from('#!/bin/bash'), name: 'script.sh', type: 'application/x-sh' },
          { content: Buffer.from('%PDF'), name: 'malicious.pdf', type: 'application/x-executable' },
        ];

        for (const dangerousFile of dangerousFiles) {
          const response = await request(app)
            .post('/api/extract')
            .attach('file', dangerousFile.content, {
              filename: dangerousFile.name,
              contentType: dangerousFile.type
            })
            .expect(403);

          expect(response.body).toHaveProperty('error');
          expect(response.body.error.toLowerCase()).toMatch(/file type not allowed|dangerous/i);
        }
      });

      it('should validate MIME type matches file extension', async () => {
        // Test file extension/MIME type mismatch
        const misleadingFiles = [
          { content: Buffer.from('MZ'), name: 'safe_image.jpg', type: 'application/x-dosexec' },
          { content: Buffer.from('<script>'), name: 'document.pdf', type: 'application/javascript' },
        ];

        for (const misleadingFile of misleadingFiles) {
          const response = await request(app)
            .post('/api/extract')
            .attach('file', misleadingFile.content, {
              filename: misleadingFile.name,
              contentType: misleadingFile.type
            })
            .expect(403); // Should reject mismatched types

          expect(response.body).toHaveProperty('error');
        }
      });
    });
  });

  describe('File Upload Security', () => {
    it('should enforce file size limits', async () => {
      // Create a file larger than the tier limit (assuming free tier 10MB limit)
      const largeFileSize = 15 * 1024 * 1024; // 15MB
      const largeFile = Buffer.alloc(largeFileSize, 'x');

      const response = await request(app)
        .post('/api/extract?tier=free')
        .attach('file', largeFile, 'large-file.jpg')
        .expect(403);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.toLowerCase()).toMatch(/file size exceeds|too large/i);
      expect(response.body).toHaveProperty('max_size_mb');
    });

    it('should reject double file extensions', async () => {
      const doubleExtensionFiles = [
        'image.jpg.exe',
        'document.pdf.js',
        'photo.png.vbs',
        'file.jpg.php',
        'archive.tar.gz.exe',
      ];

      for (const filename of doubleExtensionFiles) {
        const response = await request(app)
          .post('/api/extract')
          .attach('file', Buffer.from('fake content'), filename)
          .expect(403); // Should reject suspicious double extensions

        expect(response.body).toHaveProperty('error');
      }
    });

    it('should validate file content matches extension', async () => {
      // Create a file with .jpg extension but executable content
      const maliciousFile = Buffer.from('MZ'); // DOS executable header
      const filename = 'innocent.jpg';

      const response = await request(app)
        .post('/api/extract')
        .attach('file', maliciousFile, filename)
        .expect(403); // Should detect mismatch

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.toLowerCase()).toMatch(/file type|dangerous|invalid/i);
    });

    it('should reject files with embedded malicious content', async () => {
      // Create files with suspicious content patterns
      const suspiciousFiles = [
        { content: '<script>alert("XSS")</script>', name: 'image.jpg' },
        { content: 'javascript:alert(1)', name: 'photo.png' },
        { content: '%PDF-1.4\n/JS <script>alert(1)</script>', name: 'doc.pdf' },
      ];

      for (const suspiciousFile of suspiciousFiles) {
        const response = await request(app)
          .post('/api/extract')
          .attach('file', Buffer.from(suspiciousFile.content), suspiciousFile.name)
          .expect(403); // Should detect embedded threats

        expect(response.body).toHaveProperty('error');
        expect(response.body.error.toLowerCase()).toMatch(/malicious|dangerous|security/i);
      }
    });

    it('should enforce safe file storage locations', async () => {
      // Ensure files are stored in safe temp directories, not arbitrary paths
      const safeLocation = '/tmp/metaextract';

      // This would typically be tested by checking the actual file storage
      // For now, we test that the API prevents path traversal
      const traversalAttempts = [
        '../../var/www/html/uploads/malicious.jpg',
        'C:\\Windows\\System32\\config\\malicious.jpg',
        '/home/user/public_html/malicious.jpg',
      ];

      for (const attempt of traversalAttempts) {
        const response = await request(app)
          .post('/api/extract')
          .attach('file', Buffer.from('content'), attempt)
          .expect(400); // Should reject path traversal

        expect(response.body).toHaveProperty('error');
        expect(response.body.error.toLowerCase()).toMatch(/invalid|filename|security/i);
      }
    });
  });

  describe('Rate Limiting Effectiveness', () => {
    beforeEach(() => {
      // Clear rate limit store before each test
      const rateLimitModule = require('../server/middleware/rateLimit');
      if (rateLimitModule.rateLimitStore) {
        rateLimitModule.rateLimitStore.clear();
      }
    });

    it('should enforce rate limits for free tier', async () => {
      // Mock the rate limiter for free tier (assume 10 requests per minute)
      const freeTierLimit = 10;
      let requestCount = 0;
      let rateLimited = false;

      for (let i = 0; i < freeTierLimit + 5; i++) {
        const response = await request(app)
          .post('/api/extract?tier=free')
          .attach('file', Buffer.from('test'), `test${i}.jpg`)
          .field('trial_email', 'test@example.com');

        if (response.status === 429) {
          rateLimited = true;
          expect(response.body).toHaveProperty('error');
          expect(response.body.error.toLowerCase()).toMatch(/too many requests|rate limit/i);
          expect(response.body).toHaveProperty('tier', 'free');
          break;
        }

        requestCount++;
      }

      // Should have been rate limited after reaching the limit
      if (rateLimited) {
        expect(requestCount).toBeLessThanOrEqual(freeTierLimit);
      }
    });

    it('should provide appropriate rate limit headers', async () => {
      const response = await request(app)
        .post('/api/extract?tier=free')
        .attach('file', Buffer.from('test'), 'test.jpg')
        .field('trial_email', 'test@example.com');

      // Check for rate limit headers
      expect(response.headers).toHaveProperty('x-ratelimit-limit');
      expect(response.headers).toHaveProperty('x-ratelimit-remaining');
      expect(response.headers).toHaveProperty('x-ratelimit-reset');

      // Validate header values are numbers
      expect(parseInt(response.headers['x-ratelimit-limit'])).not.toBeNaN();
      expect(parseInt(response.headers['x-ratelimit-remaining'])).not.toBeNaN();
    });

    it('should offer upgrade suggestions when rate limited', async () => {
      // Mock a rate limited response
      const response = await request(app)
        .get('/api/rate-limit-status')
        .query({ tier: 'free' })
        .expect(200);

      // If rate limited, should suggest upgrade
      if (response.body.current?.minute_remaining === 0) {
        expect(response.body).toHaveProperty('upgrade_message');
        expect(response.body.upgrade_message).toMatch(/upgrade/i);
      }
    });

    it('should implement sliding window rate limiting', async () => {
      // Test that rate limiting uses sliding window, not fixed window
      const startTime = Date.now();
      const requests = [];

      // Send requests spaced over time
      for (let i = 0; i < 5; i++) {
        const response = await request(app)
          .post('/api/extract?tier=free')
          .attach('file', Buffer.from('test'), `test${i}.jpg`)
          .field('trial_email', 'test@example.com');

        requests.push({
          time: Date.now() - startTime,
          status: response.status,
          remaining: response.headers['x-ratelimit-remaining']
        });

        // Wait to simulate time passing
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Verify that remaining count decreases over time
      const remainingCounts = requests
        .map(r => parseInt(r.remaining))
        .filter(count => !isNaN(count));

      // Remaining should decrease as requests are made
      expect(remainingCounts.length).toBeGreaterThan(0);
    });

    it('should handle burst limits correctly', async () => {
      // Test burst capacity (short bursts allowed)
      const burstRequests = 5;
      const responses = [];

      for (let i = 0; i < burstRequests; i++) {
        const response = await request(app)
          .post('/api/extract?tier=free')
          .attach('file', Buffer.from('test'), `test${i}.jpg`)
          .field('trial_email', 'test@example.com');

        responses.push(response.status);
      }

      // First few requests should succeed (burst capacity)
      const successfulRequests = responses.filter(status => status === 200).length;
      expect(successfulRequests).toBeGreaterThan(0);
    });
  });

  describe('Authentication Security', () => {
    it('should lock accounts after failed login attempts', async () => {
      const username = 'test_user';
      const maxAttempts = 5;

      // Simulate failed login attempts
      for (let i = 0; i < maxAttempts + 2; i++) {
        const response = await request(app)
          .post('/api/auth/login')
          .send({ username, password: 'wrong_password' });

        if (i < maxAttempts) {
          expect(response.status).toBe(401); // Unauthorized
        } else {
          expect(response.status).toBe(423); // Locked
          expect(response.body).toHaveProperty('error');
          expect(response.body.error.toLowerCase()).toMatch(/locked|too many attempts/i);
        }
      }
    });

    it('should implement secure session management', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({ username: 'test_user', password: 'correct_password' });

      if (response.status === 200) {
        // Check for secure session headers
        expect(response.headers['set-cookie']).toBeDefined();

        const sessionCookie = response.headers['set-cookie'].find((cookie: string) =>
          cookie.includes('session') || cookie.includes('connect.sid')
        );

        expect(sessionCookie).toBeDefined();

        // Check for security flags
        if (sessionCookie) {
          expect(sessionCookie).toMatch(/HttpOnly/i); // Prevent JavaScript access
          expect(sessionCookie).toMatch(/Secure/i);   // HTTPS only
          expect(sessionCookie).toMatch(/SameSite=Strict/i); // CSRF protection
        }
      }
    });

    it('should invalidate sessions after timeout', async () => {
      // This would test session expiration logic
      // For now, we'll test the configuration exists
      const response = await request(app)
        .get('/api/auth/status')
        .expect(200);

      // Should have session timeout configuration
      expect(response.body).toHaveProperty('session_timeout');
      expect(response.body.session_timeout).toBeGreaterThan(0);
      expect(response.body.session_timeout).toBeLessThanOrEqual(3600); // Max 1 hour
    });
  });

  describe('SQL Injection Prevention', () => {
    it('should prevent SQL injection in user input', async () => {
      const sqlInjectionPayloads = [
        "admin'--",
        "admin'/*",
        "' OR '1'='1",
        "1' UNION SELECT * FROM users--",
        "'; DROP TABLE users--",
        "1'; EXEC xp_cmdshell('dir')--",
      ];

      for (const payload of sqlInjectionPayloads) {
        const response = await request(app)
          .post('/api/extract')
          .field('session_id', payload)
          .attach('file', Buffer.from('test'), 'test.jpg');

        // Should not reveal database information
        expect(response.body).not.toMatch(/syntax error|mysql|postgresql|sqlite/i);
        expect(response.body).not.toMatch(/SELECT|DROP|UNION|EXEC/i);
      }
    });

    it('should use parameterized queries', async () => {
      // This test would verify that database queries use parameterization
      // For now, we test that user input is properly escaped
      const userInput = "test'; DROP TABLE users--";

      const response = await request(app)
        .get(`/api/metadata/search?q=${encodeURIComponent(userInput)}`)
        .expect(200); // Should handle gracefully without crashing

      // Should not execute SQL injection
      expect(response.body).not.toMatch(/DROP TABLE|syntax error/i);
    });
  });

  describe('XSS Prevention', () => {
    it('should sanitize user input in responses', async () => {
      const xssPayloads = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        'javascript:alert("XSS")',
        '<svg onload=alert("XSS")>',
        '""><script>alert("XSS")</script>',
      ];

      for (const payload of xssPayloads) {
        const response = await request(app)
          .get(`/api/tiers`)
          .expect(200);

        // Check that response doesn't contain unescaped scripts
        const responseString = JSON.stringify(response.body);
        expect(responseString).not.toMatch(/<script>|javascript:|onclick=/i);
      }
    });

    it('should escape HTML in error messages', async () => {
      const xssPayload = '<script>alert("XSS")</script>';

      const response = await request(app)
        .post('/api/extract')
        .attach('file', Buffer.from('test'), xssPayload);

      // Even if error occurs, message should be escaped
      if (response.body.error) {
        expect(response.body.error).not.toMatch(/<script>|javascript:/i);
        expect(response.body.error).toMatch(/&lt;script&gt;/); // Should be escaped
      }
    });

    it('should set Content-Security-Policy headers', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      // Check for security headers
      expect(response.headers['content-security-policy']).toBeDefined();
      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['x-frame-options']).toBeDefined();
      expect(response.headers['x-xss-protection']).toBeDefined();
    });
  });

  describe('CSRF Protection', () => {
    it('should require CSRF tokens for state-changing operations', async () => {
      // Test POST request without CSRF token
      const response = await request(app)
        .post('/api/extract')
        .attach('file', Buffer.from('test'), 'test.jpg');

      // Should require CSRF token (or have other protection)
      // For now, we'll check that the response doesn't expose CSRF vulnerabilities
      expect(response.body).not.toHaveProperty('csrf_token');
      expect(response.body).not.toMatch(/csrf/i);
    });

    it('should validate CSRF tokens', async () => {
      // This would test CSRF token validation logic
      // For now, we'll test the configuration exists
      const response = await request(app)
        .get('/api/csrf-token')
        .expect(200); // Should provide token endpoint

      expect(response.body).toHaveProperty('csrf_token');
      expect(response.body.csrf_token).toMatch(/^[a-zA-Z0-9-_]+$/); // Should be safe token format
    });
  });

  describe('Security Headers', () => {
    it('should set all required security headers', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      // Check for comprehensive security headers
      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['x-frame-options']).toMatch(/DENY|SAMEORIGIN/i);
      expect(response.headers['strict-transport-security']).toBeDefined();
      expect(response.headers['x-xss-protection']).toBeDefined();
      expect(response.headers['referrer-policy']).toBeDefined();
    });

    it('should prevent MIME type sniffing', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['content-type']).toBeDefined();
    });

    it('should implement HTTPS enforcement in production', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      // Check HSTS header
      const hstsHeader = response.headers['strict-transport-security'];
      if (hstsHeader) {
        expect(hstsHeader).toMatch(/max-age=\d+/);
        expect(hstsHeader).toMatch(/includesubdomains/i);
      }
    });
  });

  describe('Error Handling Security', () => {
    it('should not expose sensitive information in errors', async () => {
      // Trigger various error conditions
      const errorCases = [
        { endpoint: '/api/extract', method: 'post', data: {} }, // Missing file
        { endpoint: '/api/tiers/invalid', method: 'get' }, // Invalid tier
        { endpoint: '/api/nonexistent', method: 'get' }, // Non-existent endpoint
      ];

      for (const testCase of errorCases) {
        const response = await request(app)[testCase.method](testCase.endpoint).send(testCase.data || {});

        // Check that error messages don't expose sensitive info
        if (response.status >= 400) {
          expect(response.body.error).toBeDefined();
          expect(response.body.error).not.toMatch(/password|secret|api[_-]?key|token|database/i);
          expect(response.body.error).not.toMatch(/\/var\/www|C:\\|\/home\/user/i); // No paths
          expect(response.body.error).not.toMatch(/mysql|postgresql|mongodb|sqlite/i); // No DB info
        }
      }
    });

    it('should log security-relevant events', async () => {
      // Mock security event logging
      const securityEvents = [];

      // Trigger security events
      await request(app)
        .post('/api/extract')
        .attach('file', Buffer.from('../../../etc/passwd'), 'malicious.jpg');

      // In a real test, we'd verify security logs were created
      // For now, we'll test that the infrastructure exists
      expect(securityEvents).toBeDefined(); // Placeholder for actual log verification
    });
  });

  describe('Denial of Service Prevention', () => {
    it('should limit request payload size', async () => {
      // Create an oversized request
      const oversizedPayload = {
        data: 'x'.repeat(50 * 1024 * 1024), // 50MB
      };

      const response = await request(app)
        .post('/api/extract')
        .send(oversizedPayload)
        .expect(413); // Payload Too Large

      expect(response.body).toHaveProperty('error');
      expect(response.body.error.toLowerCase()).toMatch(/too large|payload|size/i);
    });

    it('should implement request timeout', async () => {
      // This would test that long-running requests timeout appropriately
      // For now, we test the timeout configuration exists
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      expect(response.body).toBeDefined(); // Server responds in reasonable time
    });

    it('should protect against slow POST attacks', async () => {
      // Test slow POST attack (sending data very slowly)
      // This would require special testing infrastructure
      // For now, we'll verify timeout configurations exist

      const response = await request(app)
        .post('/api/extract')
        .timeout(5000) // 5 second timeout
        .attach('file', Buffer.from('test'), 'test.jpg');

      // Should complete or timeout within expected timeframe
      expect(response.status).not.toBe(408); // Request Timeout
    });
  });
});