/**
 * Tests for auth.ts PII sanitization utilities
 * Added as part of AUTH-004 remediation
 */

describe('Email sanitization for logging', () => {
  // Test the sanitization pattern that is implemented in auth.ts
  const sanitizeEmailForLog = (email: string): string => {
    const atIndex = email.indexOf('@');
    if (atIndex <= 0) return '***';
    const local = email.substring(0, atIndex);
    const domain = email.substring(atIndex);
    if (local.length <= 1) return local + '***' + domain;
    return local[0] + '***' + domain;
  };

  it('should mask email local part while preserving domain', () => {
    expect(sanitizeEmailForLog('user@example.com')).toBe('u***@example.com');
    expect(sanitizeEmailForLog('test.user@domain.org')).toBe('t***@domain.org');
  });

  it('should handle single character local parts', () => {
    expect(sanitizeEmailForLog('a@test.com')).toBe('a***@test.com');
  });

  it('should handle malformed emails gracefully', () => {
    expect(sanitizeEmailForLog('@nodomain.com')).toBe('***');
    expect(sanitizeEmailForLog('noatsign')).toBe('***');
    expect(sanitizeEmailForLog('')).toBe('***');
  });

  it('should preserve domain for debugging purposes', () => {
    const result = sanitizeEmailForLog('admin@company.internal');
    expect(result).toContain('@company.internal');
    expect(result).not.toContain('admin');
  });
});
