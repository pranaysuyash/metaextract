import { getRateLimitKey } from '../../middleware/upload-rate-limit';
import { securityEventLogger } from '../security-events';

// Mock storage module to isolate tests and avoid DB interactions
jest.mock('../../storage', () => ({
  storage: {
    logSecurityEvent: jest.fn().mockResolvedValue(undefined),
  },
}));

import { storage } from '../../storage';

describe('getRateLimitKey and SecurityEventLogger integration', () => {
  beforeEach(() => {
    // Prevent actual storage interactions during this unit test
    jest.spyOn(storage, 'logSecurityEvent').mockResolvedValue(undefined as any);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('getRateLimitKey returns user key when user.id is present', () => {
    const key = getRateLimitKey({ user: { id: 'user123' } } as any);
    expect(key).toBe('user:user123');
  });

  test('getRateLimitKey returns session key when session cookie is present', () => {
    const key = getRateLimitKey({ cookies: { metaextract_session_id: 'sess_123' } } as any);
    expect(key).toBe('session:sess_123');
  });

  test('getRateLimitKey falls back to ip key when no user/session provided', () => {
    const key = getRateLimitKey({ ip: '1.2.3.4', headers: {} } as any);
    expect(key.startsWith('ip:')).toBe(true);
  });

  test('securityEventLogger.logRateLimitViolation uses session id and does not throw', async () => {
    const req = {
      cookies: { metaextract_session_id: 'sess_abc' },
      headers: { 'user-agent': 'jest' },
      ip: '1.2.3.4',
    } as any;

    await expect(
      securityEventLogger.logRateLimitViolation(req, 'rate', 50, '15 minutes')
    ).resolves.not.toThrow();

    // Force flush of the buffer to ensure storage is called in this test
    await (securityEventLogger as any).flushBuffer();

    expect(storage.logSecurityEvent).toHaveBeenCalled();
    const calledArg = (storage.logSecurityEvent as jest.Mock).mock.calls[0][0];
    expect(calledArg.details.sessionId).toBe('sess_abc');
  });
});
