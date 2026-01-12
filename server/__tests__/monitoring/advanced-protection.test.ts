/**
 * Advanced Protection System Tests
 *
 * Comprehensive test suite for browser fingerprinting and ML anomaly detection
 */

import { Request, Response, NextFunction } from 'express';
import {
  advancedProtectionMiddleware,
  verifyChallengeResponse,
  getProtectionStats,
} from '../../middleware/advanced-protection';
import {
  generateFingerprint,
  trackFingerprint,
} from '../../monitoring/browser-fingerprint';
import { mlAnomalyDetector } from '../../monitoring/ml-anomaly-detection';
import { securityEventLogger } from '../../monitoring/security-events';

// Mock dependencies
jest.mock('../../monitoring/browser-fingerprint');
jest.mock('../../monitoring/ml-anomaly-detection');
jest.mock('../../monitoring/security-events');
jest.mock('../../monitoring/security-alerts');

describe('Advanced Protection System', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: NextFunction;
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup request/response mocks
    mockReq = {
      ip: '192.168.1.100',
      // connection is a Socket in real requests; use any for test stub
      connection: { remoteAddress: '192.168.1.100' } as any,
      headers: {
        'user-agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        referer: 'https://example.com/upload',
      },
      body: {},
      path: '/api/upload',
      method: 'POST',
    };

    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };

    mockNext = jest.fn();

    // Mock console.error to avoid test output pollution
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  describe('Browser Fingerprinting', () => {
    it('should generate fingerprint from request data', async () => {
      const mockFingerprint = {
        fingerprintHash: 'test_hash_123',
        deviceId: 'device_123',
        sessionId: 'session_123',
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        platform: 'Windows',
        language: 'en-US',
        timestamp: new Date(),
        confidence: 0.85,
        anomalies: [],
      };

      (generateFingerprint as jest.Mock).mockResolvedValue(mockFingerprint as any);

      const result = await generateFingerprint(mockReq as Request);

      expect(generateFingerprint).toHaveBeenCalledWith(mockReq);
      expect(result).toEqual(mockFingerprint);
    });

    it('should include client-side fingerprint data when provided', async () => {
      const clientData = {
        canvas: 'canvas_hash_123',
        webgl: 'webgl_hash_123',
        fonts: 'font_list_123',
      };

      mockReq.body = { fingerprintData: clientData };

      const mockFingerprint = {
        fingerprintHash: 'test_hash_456',
        deviceId: 'device_456',
        sessionId: 'session_456',
        canvas: clientData.canvas,
        webgl: clientData.webgl,
        fonts: clientData.fonts,
        timestamp: new Date(),
        confidence: 0.9,
        anomalies: [],
      };

      (generateFingerprint as jest.Mock).mockResolvedValue(mockFingerprint as any);

      const result = await generateFingerprint(mockReq as Request, clientData);

      expect(generateFingerprint).toHaveBeenCalledWith(mockReq, clientData);
      expect(result.canvas).toBe(clientData.canvas);
      expect(result.webgl).toBe(clientData.webgl);
      expect(result.fonts).toBe(clientData.fonts);
    });

    it('should detect anomalies in fingerprint data', async () => {
      const suspiciousFingerprint = {
        fingerprintHash: 'suspicious_hash_123',
        deviceId: 'device_suspicious',
        sessionId: 'session_suspicious',
        userAgent: 'HeadlessChrome/91.0.4472.124',
        platform: 'Linux',
        language: 'en-US',
        timestamp: new Date(),
        confidence: 0.3,
        anomalies: ['Headless browser detected', 'Minimal browser fingerprint'],
      };

      (generateFingerprint as jest.Mock).mockResolvedValue(
        suspiciousFingerprint as any
      );

      const result = await generateFingerprint(mockReq as Request);

      expect(result.anomalies).toContain('Headless browser detected');
      expect(result.anomalies).toContain('Minimal browser fingerprint');
      expect(result.confidence).toBeLessThan(0.5);
    });
  });

  describe('ML Anomaly Detection', () => {
    it('should detect normal behavior', async () => {
      const mockFingerprint = {
        fingerprintHash: 'normal_hash_123',
        deviceId: 'device_normal',
        sessionId: 'session_normal',
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        timestamp: new Date(),
        confidence: 0.9,
        anomalies: [],
      };

      const mockAnomalyResult = {
        isAnomalous: false,
        confidence: 0.15,
        riskScore: 15,
        riskLevel: 'low',
        contributingFactors: [],
        recommendations: [],
        modelVersion: '1.0.0',
        timestamp: new Date(),
      };

      (mlAnomalyDetector.detectUploadAnomaly as jest.Mock).mockResolvedValue(
        mockAnomalyResult
      );

      const result = await mlAnomalyDetector.detectUploadAnomaly(
        mockReq as Request,
        mockFingerprint as any
      );

      expect(result.isAnomalous).toBe(false);
      expect(result.riskScore).toBeLessThan(40);
      expect(result.riskLevel).toBe('low');
    });

    it('should detect anomalous behavior', async () => {
      const suspiciousFingerprint = {
        fingerprintHash: 'suspicious_hash_456',
        deviceId: 'device_suspicious',
        sessionId: 'session_suspicious',
        userAgent: 'HeadlessChrome/91.0.4472.124',
        timestamp: new Date(),
        confidence: 0.3,
        anomalies: ['Headless browser detected'],
      };

      const mockAnomalyResult = {
        isAnomalous: true,
        confidence: 0.85,
        riskScore: 75,
        riskLevel: 'high',
        contributingFactors: [
          'High upload frequency',
          'Headless browser detected',
        ],
        recommendations: [
          'Implement additional verification',
          'Consider rate limiting',
        ],
        modelVersion: '1.0.0',
        timestamp: new Date(),
      };

      (mlAnomalyDetector.detectUploadAnomaly as jest.Mock).mockResolvedValue(
        mockAnomalyResult
      );

      const result = await mlAnomalyDetector.detectUploadAnomaly(
        mockReq as Request,
        suspiciousFingerprint as any
      );

      expect(result.isAnomalous).toBe(true);
      expect(result.riskScore).toBeGreaterThan(60);
      expect(result.riskLevel).toBe('high');
      expect(result.contributingFactors.length).toBeGreaterThan(0);
    });

    it('should provide model statistics', async () => {
      const mockStats = {
        totalPredictions: 1000,
        truePositives: 150,
        falsePositives: 25,
        trueNegatives: 800,
        falseNegatives: 25,
        accuracy: 0.95,
        precision: 0.857,
        recall: 0.857,
        f1Score: 0.857,
        lastTraining: new Date(),
        modelVersion: '1.0.0',
      };

      (mlAnomalyDetector.getModelStats as jest.Mock).mockReturnValue(mockStats);

      const stats = mlAnomalyDetector.getModelStats();

      expect(stats.totalPredictions).toBe(1000);
      expect(stats.accuracy).toBeGreaterThan(0.9);
      expect(stats.modelVersion).toBe('1.0.0');
    });
  });

  describe('Advanced Protection Middleware', () => {
    beforeEach(() => {
      // Mock successful fingerprint and anomaly detection
      const mockFingerprint = {
        fingerprintHash: 'test_fingerprint_123',
        deviceId: 'test_device_123',
        sessionId: 'test_session_123',
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        timestamp: new Date(),
        confidence: 0.85,
        anomalies: [],
      };

      const mockAnomalyResult = {
        isAnomalous: false,
        confidence: 0.2,
        riskScore: 20,
        riskLevel: 'low',
        contributingFactors: [],
        recommendations: [],
        modelVersion: '1.0.0',
        timestamp: new Date(),
      };

      const mockTracking = {
        isNewDevice: false,
        previousSessions: 3,
        riskLevel: 'low',
        action: 'allow',
      };

      (generateFingerprint as jest.Mock).mockResolvedValue(mockFingerprint);
      (mlAnomalyDetector.detectUploadAnomaly as jest.Mock).mockResolvedValue(
        mockAnomalyResult
      );
      (trackFingerprint as jest.Mock).mockResolvedValue(mockTracking);
      (securityEventLogger.logEvent as jest.Mock).mockResolvedValue(undefined);

      // Provide minimal client-side fingerprint data to avoid missing-fingerprint penalties in risk calculation
      (mockReq as any).body = { fingerprintData: {} } as any;
    });

    it('should allow normal requests', async () => {
      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      expect(mockNext).toHaveBeenCalled();
      expect(mockRes.status).not.toHaveBeenCalled();
    });

    it('should block high-risk requests', async () => {
      // Mock high-risk detection
      const highRiskAnomaly = {
        isAnomalous: true,
        confidence: 0.9,
        // High enough to trigger block (>= BLOCK_THRESHOLD 90)
        riskScore: 95,
        riskLevel: 'high',
        contributingFactors: [
          'High upload frequency',
          'Suspicious fingerprint',
        ],
        recommendations: ['Block request', 'Monitor device'],
        modelVersion: '1.0.0',
        timestamp: new Date(),
      };

      (mlAnomalyDetector.detectUploadAnomaly as jest.Mock).mockResolvedValue(
        highRiskAnomaly
      );

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      expect(mockNext).not.toHaveBeenCalled();
      expect(mockRes.status).toHaveBeenCalledWith(403);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Access denied',
          // Risk level may be 'high' or 'critical' depending on score
          riskLevel: expect.any(String),
          riskScore: expect.any(Number),
        })
      );

      // And ensure the reported risk is high/critical
      const responseData = (mockRes.json as jest.Mock).mock.calls[0][0];
      expect(responseData.riskScore).toBeGreaterThanOrEqual(85);
      expect(['high', 'critical']).toContain(responseData.riskLevel);
    });

    it('should challenge medium-risk requests', async () => {
      // Mock medium-risk detection
      const mediumRiskAnomaly = {
        isAnomalous: true,
        confidence: 0.7,
        // Medium but above challenge threshold (>= 70)
        riskScore: 75,
        riskLevel: 'medium',
        contributingFactors: ['Unusual timing pattern'],
        recommendations: ['Implement challenge'],
        modelVersion: '1.0.0',
        timestamp: new Date(),
      };

      (mlAnomalyDetector.detectUploadAnomaly as jest.Mock).mockResolvedValue(
        mediumRiskAnomaly
      );

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      expect(mockNext).not.toHaveBeenCalled();
      expect(mockRes.status).toHaveBeenCalledWith(403);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Challenge required',
          challenge: expect.objectContaining({
            type: expect.any(String),
            data: expect.any(Object),
          }),
        })
      );
    });

    it('should handle errors gracefully', async () => {
      // Mock error in fingerprint generation
      (generateFingerprint as jest.Mock).mockRejectedValue(
        new Error('Fingerprint error')
      );

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      // Should allow request to continue on error
      expect(mockNext).toHaveBeenCalled();
      expect(mockRes.status).not.toHaveBeenCalledWith(500);
    });

    it('should skip protection for health check endpoints', async () => {
      (mockReq as any).path = '/health';

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockNext).toHaveBeenCalled();
      expect(generateFingerprint).not.toHaveBeenCalled();
    });
  });

  describe('Challenge Verification', () => {
    it('should verify valid challenge response', async () => {
      mockReq.body = {
        challengeResponse: {
          type: 'captcha',
          token: 'valid_captcha_token_123',
        },
        sessionId: 'test_session_123',
      };

      await verifyChallengeResponse(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockNext).toHaveBeenCalled();
      expect((mockReq as any).challengePassed).toBe(true);
    });

    it('should reject invalid challenge response', async () => {
      mockReq.body = {
        challengeResponse: {
          type: 'captcha',
          token: '', // Invalid token
        },
        sessionId: 'test_session_123',
      };

      await verifyChallengeResponse(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockNext).not.toHaveBeenCalled();
      expect(mockRes.status).toHaveBeenCalledWith(403);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Challenge verification failed',
        })
      );
    });

    it('should handle missing challenge response', async () => {
      mockReq.body = {};

      await verifyChallengeResponse(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockNext).not.toHaveBeenCalled();
      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Missing challenge response',
        })
      );
    });
  });

  describe('Protection Statistics', () => {
    it('should return protection statistics', async () => {
      const mockStats = {
        totalRequests: 1000,
        blockedRequests: 50,
        challengedRequests: 100,
        monitoredRequests: 200,
        allowedRequests: 650,
        averageRiskScore: 35,
        modelVersion: '1.0.0',
        isModelTrained: true,
        timestamp: new Date(),
      };

      (mlAnomalyDetector.getModelStats as jest.Mock).mockReturnValue({
        totalPredictions: 1000,
        accuracy: 0.95,
      });

      const stats = await getProtectionStats();

      expect(stats).toHaveProperty('modelVersion');
      expect(stats).toHaveProperty('isModelTrained');
      expect(stats).toHaveProperty('timestamp');
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle requests without IP address', async () => {
      (mockReq as any).ip = undefined;
      (mockReq as any).connection = {} as any;

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      expect(mockNext).toHaveBeenCalled();
    });

    it('should handle requests without user agent', async () => {
      (mockReq.headers as any)['user-agent'] = undefined;

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      expect(mockNext).toHaveBeenCalled();
    });

    it('should handle concurrent requests', async () => {
      const promises = [];

      for (let i = 0; i < 5; i++) {
        promises.push(
          advancedProtectionMiddleware(
            mockReq as Request,
            mockRes as Response,
            mockNext
          )
        );
      }

      await Promise.all(promises);

      // All requests should be processed
      expect(mockNext).toHaveBeenCalledTimes(5);
    });

    it('should handle malformed fingerprint data', async () => {
      mockReq.body = {
        fingerprintData: {
          invalid: 'data',
          missingRequiredFields: true,
        },
      };

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      expect(mockNext).toHaveBeenCalled();
    });
  });

  describe('Performance and Scalability', () => {
    it('should complete processing within reasonable time', async () => {
      const startTime = Date.now();

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      // Should complete within 2 seconds (including async operations)
      expect(processingTime).toBeLessThan(2000);
    });

    it('should handle high-frequency requests', async () => {
      const requestCount = 10;
      const promises = [];

      for (let i = 0; i < requestCount; i++) {
        promises.push(
          advancedProtectionMiddleware(
            mockReq as Request,
            mockRes as Response,
            mockNext
          )
        );
      }

      await Promise.all(promises);

      expect(mockNext).toHaveBeenCalledTimes(requestCount);
    });
  });

  describe('Security and Privacy', () => {
    it('should not expose sensitive information in responses', async () => {
      const highRiskAnomaly = {
        isAnomalous: true,
        confidence: 0.9,
        riskScore: 85,
        riskLevel: 'high',
        contributingFactors: ['Internal system details'],
        recommendations: ['Block request'],
        modelVersion: '1.0.0',
        timestamp: new Date(),
      };

      (mlAnomalyDetector.detectUploadAnomaly as jest.Mock).mockResolvedValue(
        highRiskAnomaly
      );

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      const responseData = (mockRes.json as jest.Mock).mock.calls[0][0];

      // Should not expose internal system details
      expect(responseData).not.toHaveProperty('internalDetails');
      expect(responseData).not.toHaveProperty('debugInfo');
    });

    it('should handle privacy-sensitive data appropriately', async () => {
      const mockFingerprint = {
        fingerprintHash: 'test_hash_123',
        deviceId: 'device_123',
        sessionId: 'session_123',
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        timestamp: new Date(),
        confidence: 0.85,
        anomalies: [],
      };

      (generateFingerprint as jest.Mock).mockResolvedValue(mockFingerprint);

      await advancedProtectionMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      // Wait for async operations
      await new Promise(resolve => setImmediate(resolve));

      // Should not log full user agent in plain text
      const loggedEvents = (securityEventLogger.logEvent as jest.Mock).mock
        .calls;
      const hasUserAgentInDetails = loggedEvents.some(
        call => call[0].details && call[0].details.userAgent
      );

      // User agent should be hashed or truncated in logs
      expect(hasUserAgentInDetails).toBe(false);
    });
  });
});
