/**
 * Property Tests for User-Friendly Error Messaging System
 * 
 * Tests universal correctness properties of the error messaging system.
 * 
 * @validates Requirements 1.4, 3.4 - User-friendly error messaging
 */

import * as fc from 'fast-check';
import {
  ERROR_CODES,
  ErrorCode,
  ErrorCategory,
  ErrorSeverity,
  mapHttpStatusToErrorCode,
  detectErrorCode,
  getUserFriendlyError,
  toUserFriendlyError,
  createUserFriendlyError,
  calculateRetryDelay,
  shouldRetry,
  getErrorIcon,
  getErrorColorClass,
  formatErrorForLogging,
  formatErrorForDisplay,
  RetryConfig,
} from '../error-messages';

describe('Error Messages Property Tests', () => {
  // ========================================================================
  // Error Code Coverage
  // ========================================================================
  
  describe('Error Code Coverage', () => {
    const allErrorCodes = Object.values(ERROR_CODES);
    
    it('should have a template for every error code', () => {
      allErrorCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(error).toBeDefined();
        expect(error.code).toBe(code);
      });
    });

    it('should have unique error codes', () => {
      const uniqueCodes = new Set(allErrorCodes);
      expect(uniqueCodes.size).toBe(allErrorCodes.length);
    });

    it('should have error codes following naming convention', () => {
      allErrorCodes.forEach(code => {
        // Format: PREFIX_DESCRIPTION or PREFIX_NUMBER
        expect(code).toMatch(/^[A-Z]+_[A-Z0-9_]+$/);
      });
    });
  });

  // ========================================================================
  // User-Friendly Message Properties
  // ========================================================================
  
  describe('User-Friendly Message Properties', () => {
    const allErrorCodes = Object.values(ERROR_CODES);
    
    it('every error should have a non-empty title', () => {
      allErrorCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(error.title).toBeDefined();
        expect(error.title.length).toBeGreaterThan(0);
        expect(error.title.length).toBeLessThanOrEqual(50); // Titles should be concise
      });
    });

    it('every error should have a non-empty message', () => {
      allErrorCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(error.message).toBeDefined();
        expect(error.message.length).toBeGreaterThan(0);
        expect(error.message.length).toBeLessThanOrEqual(200); // Messages should be readable
      });
    });

    it('every error should have at least one suggestion', () => {
      allErrorCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(error.suggestions).toBeDefined();
        expect(Array.isArray(error.suggestions)).toBe(true);
        expect(error.suggestions.length).toBeGreaterThanOrEqual(1);
      });
    });

    it('suggestions should be actionable (not empty)', () => {
      allErrorCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        error.suggestions.forEach(suggestion => {
          expect(suggestion.length).toBeGreaterThan(0);
          expect(suggestion.length).toBeLessThanOrEqual(150);
        });
      });
    });

    it('error messages should not contain technical jargon', () => {
      const technicalTerms = [
        'exception',
        'stack trace',
        'null pointer',
        'undefined is not',
        ' NaN ',
        'ECONNREFUSED',
        'ETIMEDOUT',
        '500 Internal Server',
        'HTTP/1.1',
        'segfault',
        'core dump',
      ];
      
      allErrorCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        const fullText = `${error.title} ${error.message}`.toLowerCase();
        
        technicalTerms.forEach(term => {
          expect(fullText).not.toContain(term.toLowerCase());
        });
      });
    });
  });

  // ========================================================================
  // Error Category and Severity Properties
  // ========================================================================
  
  describe('Error Category and Severity Properties', () => {
    const validCategories: ErrorCategory[] = [
      'network', 'upload', 'processing', 'authentication',
      'authorization', 'validation', 'server', 'timeout', 'quota', 'unknown'
    ];
    
    const validSeverities: ErrorSeverity[] = ['info', 'warning', 'error', 'critical'];
    
    it('every error should have a valid category', () => {
      Object.values(ERROR_CODES).forEach(code => {
        const error = getUserFriendlyError(code);
        expect(validCategories).toContain(error.category);
      });
    });

    it('every error should have a valid severity', () => {
      Object.values(ERROR_CODES).forEach(code => {
        const error = getUserFriendlyError(code);
        expect(validSeverities).toContain(error.severity);
      });
    });

    it('critical errors should be rare and important', () => {
      const criticalErrors = Object.values(ERROR_CODES).filter(code => {
        const error = getUserFriendlyError(code);
        return error.severity === 'critical';
      });
      
      // Critical should be used sparingly
      expect(criticalErrors.length).toBeLessThanOrEqual(3);
    });

    it('network errors should have network or timeout category', () => {
      const networkCodes = [
        ERROR_CODES.NETWORK_OFFLINE,
        ERROR_CODES.NETWORK_TIMEOUT,
        ERROR_CODES.NETWORK_UNREACHABLE,
      ];
      
      networkCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(['network', 'timeout']).toContain(error.category);
      });
    });
  });

  // ========================================================================
  // HTTP Status Code Mapping Properties
  // ========================================================================
  
  describe('HTTP Status Code Mapping', () => {
    it('should map all 4xx client errors to appropriate codes', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 400, max: 499 }),
          (status) => {
            const code = mapHttpStatusToErrorCode(status);
            expect(code).toBeDefined();
            expect(typeof code).toBe('string');
            
            // Should not map to server errors
            const error = getUserFriendlyError(code);
            expect(error.category).not.toBe('server');
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should map all 5xx server errors to server-related codes', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 500, max: 599 }),
          (status) => {
            const code = mapHttpStatusToErrorCode(status);
            expect(code).toBeDefined();
            
            const error = getUserFriendlyError(code);
            // Server errors should be server, timeout, or unknown category
            expect(['server', 'timeout', 'unknown']).toContain(error.category);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should map specific status codes correctly', () => {
      const mappings: [number, ErrorCode][] = [
        [401, ERROR_CODES.AUTH_SESSION_EXPIRED],
        [403, ERROR_CODES.AUTHZ_FEATURE_LOCKED],
        [413, ERROR_CODES.UPLOAD_FILE_TOO_LARGE],
        [429, ERROR_CODES.AUTHZ_RATE_LIMITED],
        [500, ERROR_CODES.SERVER_INTERNAL],
        [503, ERROR_CODES.SERVER_MAINTENANCE],
      ];
      
      mappings.forEach(([status, expectedCode]) => {
        expect(mapHttpStatusToErrorCode(status)).toBe(expectedCode);
      });
    });
  });

  // ========================================================================
  // Error Detection Properties
  // ========================================================================
  
  describe('Error Detection', () => {
    it('should always return a valid error code', () => {
      fc.assert(
        fc.property(
          fc.anything(),
          (input) => {
            const code = detectErrorCode(input);
            expect(code).toBeDefined();
            expect(Object.values(ERROR_CODES)).toContain(code);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should detect network errors from Error objects', () => {
      const networkError = new Error('Network request failed');
      expect(detectErrorCode(networkError)).toBe(ERROR_CODES.NETWORK_UNREACHABLE);
      
      const fetchError = new Error('fetch failed');
      expect(detectErrorCode(fetchError)).toBe(ERROR_CODES.NETWORK_UNREACHABLE);
    });

    it('should detect timeout errors', () => {
      const timeoutError = new Error('Request timed out');
      expect(detectErrorCode(timeoutError)).toBe(ERROR_CODES.NETWORK_TIMEOUT);
    });

    it('should detect abort/cancel errors', () => {
      const abortError = new Error('Request aborted');
      abortError.name = 'AbortError';
      expect(detectErrorCode(abortError)).toBe(ERROR_CODES.UPLOAD_CANCELLED);
    });

    it('should handle null and undefined gracefully', () => {
      expect(detectErrorCode(null)).toBe(ERROR_CODES.UNKNOWN);
      expect(detectErrorCode(undefined)).toBe(ERROR_CODES.UNKNOWN);
    });
  });

  // ========================================================================
  // Retry Logic Properties
  // ========================================================================
  
  describe('Retry Logic', () => {
    it('should calculate increasing delays with exponential backoff', () => {
      const config: RetryConfig = {
        maxAttempts: 5,
        baseDelay: 1000,
        exponentialBackoff: true,
      };
      
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10 }),
          (attempt) => {
            const delay = calculateRetryDelay(attempt, config);
            const expectedDelay = config.baseDelay * Math.pow(2, attempt - 1);
            expect(delay).toBe(expectedDelay);
          }
        ),
        { numRuns: 10 }
      );
    });

    it('should respect maxDelay cap', () => {
      const config: RetryConfig = {
        maxAttempts: 10,
        baseDelay: 1000,
        exponentialBackoff: true,
        maxDelay: 5000,
      };
      
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 20 }),
          (attempt) => {
            const delay = calculateRetryDelay(attempt, config);
            expect(delay).toBeLessThanOrEqual(config.maxDelay!);
          }
        ),
        { numRuns: 20 }
      );
    });

    it('should return constant delay without exponential backoff', () => {
      const config: RetryConfig = {
        maxAttempts: 5,
        baseDelay: 2000,
        exponentialBackoff: false,
      };
      
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10 }),
          (attempt) => {
            const delay = calculateRetryDelay(attempt, config);
            expect(delay).toBe(config.baseDelay);
          }
        ),
        { numRuns: 10 }
      );
    });

    it('should correctly determine if retry is allowed', () => {
      const recoverableError = getUserFriendlyError(ERROR_CODES.NETWORK_TIMEOUT);
      const nonRecoverableError = getUserFriendlyError(ERROR_CODES.UPLOAD_FILE_TOO_LARGE);
      
      // Recoverable errors should allow retry up to maxAttempts
      expect(shouldRetry(recoverableError, 0)).toBe(true);
      expect(shouldRetry(recoverableError, 1)).toBe(true);
      expect(shouldRetry(recoverableError, recoverableError.retry!.maxAttempts)).toBe(false);
      
      // Non-recoverable errors should never allow retry
      expect(shouldRetry(nonRecoverableError, 0)).toBe(false);
      expect(shouldRetry(nonRecoverableError, 1)).toBe(false);
    });
  });

  // ========================================================================
  // Error Conversion Properties
  // ========================================================================
  
  describe('Error Conversion', () => {
    it('toUserFriendlyError should always return valid UserFriendlyError', () => {
      fc.assert(
        fc.property(
          fc.anything(),
          (input) => {
            const error = toUserFriendlyError(input);
            
            expect(error.code).toBeDefined();
            expect(error.category).toBeDefined();
            expect(error.severity).toBeDefined();
            expect(error.title).toBeDefined();
            expect(error.message).toBeDefined();
            expect(Array.isArray(error.suggestions)).toBe(true);
            expect(typeof error.recoverable).toBe('boolean');
          }
        ),
        { numRuns: 50 }
      );
    });

    it('createUserFriendlyError should create valid errors with custom messages', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 50 }),
          fc.string({ minLength: 1, maxLength: 200 }),
          (title, message) => {
            const error = createUserFriendlyError({ title, message });
            
            expect(error.title).toBe(title);
            expect(error.message).toBe(message);
            expect(error.code).toBeDefined();
            expect(error.category).toBeDefined();
            expect(error.severity).toBeDefined();
          }
        ),
        { numRuns: 20 }
      );
    });
  });

  // ========================================================================
  // Display Utility Properties
  // ========================================================================
  
  describe('Display Utilities', () => {
    const validSeverities: ErrorSeverity[] = ['info', 'warning', 'error', 'critical'];
    
    it('should return valid icon names for all severities', () => {
      validSeverities.forEach(severity => {
        const icon = getErrorIcon(severity);
        expect(icon).toBeDefined();
        expect(typeof icon).toBe('string');
        expect(icon.length).toBeGreaterThan(0);
      });
    });

    it('should return valid color classes for all severities', () => {
      validSeverities.forEach(severity => {
        const colorClass = getErrorColorClass(severity);
        expect(colorClass).toBeDefined();
        expect(typeof colorClass).toBe('string');
        expect(colorClass).toContain('text-');
        expect(colorClass).toContain('bg-');
        expect(colorClass).toContain('border-');
      });
    });

    it('formatErrorForLogging should produce valid JSON', () => {
      Object.values(ERROR_CODES).forEach(code => {
        const error = getUserFriendlyError(code, 'Test technical details');
        const logged = formatErrorForLogging(error);
        
        expect(() => JSON.parse(logged)).not.toThrow();
        
        const parsed = JSON.parse(logged);
        expect(parsed.code).toBe(code);
        expect(parsed.timestamp).toBeDefined();
      });
    });

    it('formatErrorForDisplay should produce readable string', () => {
      Object.values(ERROR_CODES).forEach(code => {
        const error = getUserFriendlyError(code);
        const display = formatErrorForDisplay(error);
        
        expect(display).toContain(error.title);
        expect(display).toContain(error.message);
        expect(display.length).toBeLessThan(300);
      });
    });
  });

  // ========================================================================
  // Recoverability Properties
  // ========================================================================
  
  describe('Recoverability Properties', () => {
    it('recoverable errors should have retry config', () => {
      Object.values(ERROR_CODES).forEach(code => {
        const error = getUserFriendlyError(code);
        
        if (error.recoverable) {
          expect(error.retry).toBeDefined();
          expect(error.retry!.maxAttempts).toBeGreaterThan(0);
          expect(error.retry!.baseDelay).toBeGreaterThan(0);
          expect(typeof error.retry!.exponentialBackoff).toBe('boolean');
        }
      });
    });

    it('non-recoverable errors should not suggest retry', () => {
      Object.values(ERROR_CODES).forEach(code => {
        const error = getUserFriendlyError(code);
        
        if (!error.recoverable) {
          // Suggestions should not include "try again" for non-recoverable errors
          const suggestionsText = error.suggestions.join(' ').toLowerCase();
          // Allow "try again" only if it's about trying something different
          if (suggestionsText.includes('try again')) {
            expect(
              suggestionsText.includes('different') || 
              suggestionsText.includes('later') ||
              suggestionsText.includes('new')
            ).toBe(true);
          }
        }
      });
    });

    it('network errors should generally be recoverable', () => {
      const networkCodes = [
        ERROR_CODES.NETWORK_OFFLINE,
        ERROR_CODES.NETWORK_TIMEOUT,
        ERROR_CODES.NETWORK_UNREACHABLE,
      ];
      
      networkCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(error.recoverable).toBe(true);
      });
    });

    it('validation errors should not be recoverable', () => {
      const validationCodes = [
        ERROR_CODES.VALIDATION_REQUIRED_FIELD,
        ERROR_CODES.VALIDATION_INVALID_FORMAT,
        ERROR_CODES.VALIDATION_OUT_OF_RANGE,
      ];
      
      validationCodes.forEach(code => {
        const error = getUserFriendlyError(code);
        expect(error.recoverable).toBe(false);
      });
    });
  });
});
