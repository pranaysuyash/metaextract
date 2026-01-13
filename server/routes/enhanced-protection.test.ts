import express from 'express';
import request from 'supertest';
import { describe, it, expect, jest } from '@jest/globals';

jest.mock('../middleware/enhanced-protection', () => {
  return {
    enhancedProtectionMiddleware: (_req: any, _res: any, next: any) => next(),
    verifyEnhancedChallengeResponse: (_req: any, _res: any, next: any) => next(),
    getEnhancedProtectionStats: jest.fn(async () => ({ ok: true })),
    ENHANCED_PROTECTION_CONFIG: {
      THREAT_INTELLIGENCE: true,
      BEHAVIORAL_ANALYSIS: true,
      ADVANCED_ML: true,
      REAL_TIME_UPDATES: true,
      CRITICAL_RISK_THRESHOLD: 90,
      HIGH_RISK_THRESHOLD: 75,
      MEDIUM_RISK_THRESHOLD: 50,
      LOW_RISK_THRESHOLD: 25,
      WEIGHTS: { ip: 1 },
      CHALLENGES: { CAPTCHA: 'captcha' },
      ACTIONS: { ALLOW: 'allow' },
    },
  };
});

import enhancedProtectionRouter from './enhanced-protection';

describe('Enhanced Protection Routes (contract)', () => {
  it('GET /api/enhanced-protection/config returns safe config shape', async () => {
    const app = express();
    app.use('/api/enhanced-protection', enhancedProtectionRouter);

    const response = await request(app)
      .get('/api/enhanced-protection/config')
      .expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.config).toHaveProperty('features');
    expect(response.body.config).toHaveProperty('thresholds');
    expect(response.body.config).toHaveProperty('weights');
    expect(response.body.config).toHaveProperty('challenges');
  });

  it('GET /api/enhanced-protection/stats returns stats payload', async () => {
    const app = express();
    app.use('/api/enhanced-protection', enhancedProtectionRouter);

    const response = await request(app)
      .get('/api/enhanced-protection/stats')
      .expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body).toHaveProperty('stats');
  });
});

