/**
 * Fingerprint Integration Test
 * 
 * Simple integration test to verify the browser fingerprinting system works
 */

import { generateFingerprint } from '../../monitoring/browser-fingerprint';
import { mlAnomalyDetector } from '../../monitoring/ml-anomaly-detection';

describe('Fingerprint Integration', () => {
  it('should generate a fingerprint from request data', async () => {
    const mockReq = {
      ip: '192.168.1.100',
      connection: { remoteAddress: '192.168.1.100' },
      headers: {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'accept-language': 'en-US,en;q=0.9'
      },
      cookies: {}
    } as any;

    const fingerprint = await generateFingerprint(mockReq);

    expect(fingerprint).toBeDefined();
    expect(fingerprint.fingerprintHash).toBeDefined();
    expect(fingerprint.deviceId).toBeDefined();
    expect(fingerprint.sessionId).toBeDefined();
    expect(fingerprint.userAgent).toBe(mockReq.headers['user-agent']);
    expect(fingerprint.ipAddress).toBe(mockReq.ip);
  });

  it('should detect anomalies in suspicious fingerprints', async () => {
    const suspiciousReq = {
      ip: '192.168.1.100',
      connection: { remoteAddress: '192.168.1.100' },
      headers: {
        'user-agent': 'HeadlessChrome/91.0.4472.124',
        'accept-language': 'en-US,en;q=0.9'
      },
      cookies: {}
    } as any;

    const fingerprint = await generateFingerprint(suspiciousReq);
    
    expect(fingerprint.anomalies).toBeDefined();
    expect(fingerprint.anomalies.length).toBeGreaterThan(0);
    expect(fingerprint.anomalies).toContain('Headless browser detected');
  });

  it('should run ML anomaly detection', async () => {
    const mockReq = {
      ip: '192.168.1.100',
      connection: { remoteAddress: '192.168.1.100' },
      headers: {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      body: {},
      path: '/api/upload',
      method: 'POST'
    } as any;

    const result = await mlAnomalyDetector.detectUploadAnomaly(mockReq);

    expect(result).toBeDefined();
    expect(result.isAnomalous).toBeDefined();
    expect(result.confidence).toBeDefined();
    expect(result.riskScore).toBeDefined();
    expect(result.riskLevel).toBeDefined();
  });

  it('should provide model statistics', () => {
    const stats = mlAnomalyDetector.getModelStats();
    
    expect(stats).toBeDefined();
    expect(stats.modelVersion).toBeDefined();
    expect(stats.totalPredictions).toBeDefined();
  });

  it('should handle high-risk detection', async () => {
    const suspiciousReq = {
      ip: '192.168.1.100',
      connection: { remoteAddress: '192.168.1.100' },
      headers: {
        'user-agent': 'HeadlessChrome/91.0.4472.124'
      },
      body: {},
      path: '/api/upload',
      method: 'POST'
    } as any;

    const fingerprint = await generateFingerprint(suspiciousReq);
    const result = await mlAnomalyDetector.detectUploadAnomaly(suspiciousReq, fingerprint);

    expect(result.isAnomalous).toBe(true);
    expect(result.riskScore).toBeGreaterThan(50);
    expect(result.contributingFactors.length).toBeGreaterThan(0);
  });
});