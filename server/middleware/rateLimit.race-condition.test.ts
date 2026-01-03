/**
 * Race Condition Test for Rate Limiting
 *
 * This test verifies that concurrent requests properly respect rate limits
 * through atomic increment-and-check pattern.
 */

import { createRateLimiter } from './rateLimit';
import type { Request, Response } from 'express';

describe('Rate Limiting - Race Condition Prevention', () => {
  /**
   * Test: Concurrent requests should not bypass rate limit
   *
   * Scenario:
   * - Rate limit: 3 requests/minute for free tier
   * - Send 10 concurrent requests at the same millisecond
   * - Expected: 3 pass, 7 rejected
   * - Not allowed: All 10 pass (race condition)
   */
  it('should prevent 10 concurrent requests from bypassing limit of 3', async () => {
    const limiter = createRateLimiter({ windowMs: 60000 });
    let acceptCount = 0;
    let rejectCount = 0;

    // Mock request and response
    const mockReq = {
      user: { id: 'test_user_' + Date.now(), tier: 'free' },
      ip: '127.0.0.1',
    } as any as Request;

    // Fire 10 concurrent requests
    const promises = Array.from({ length: 10 }, (_, i) => {
      return new Promise<void>((resolve) => {
        let wasRejected = false;
        const mockRes = {
          status: function (code: number) {
            if (code === 429) {
              rejectCount++;
              wasRejected = true;
            }
            return {
              json: () => resolve(),
            };
          },
          setHeader: () => {},
          statusCode: 200,
          end: () => {},
        } as any as Response;

        const next = () => {
          if (!wasRejected) {
            acceptCount++;
          }
          resolve();
        };

        limiter(mockReq, mockRes, next);
      });
    });

    await Promise.all(promises);

    // Should allow exactly 3 (limit), reject 7
    expect(acceptCount + rejectCount).toBe(10);
    expect(acceptCount).toBe(3);
    expect(rejectCount).toBe(7);
  });

  /**
   * Test: Atomic increment ensures no double-counting
   *
   * Scenario:
   * - Rate limit: 5 requests/minute
   * - Send 5 concurrent requests
   * - All 5 should pass
   * - 6th request should be rejected
   */
  it('should atomically allow exactly N concurrent requests matching limit', async () => {
    const limiter = createRateLimiter({ windowMs: 60000 });
    let acceptCount = 0;
    let rejectCount = 0;

    const mockReq = {
      user: { id: 'atomic_test_' + Date.now(), tier: 'free' },
      ip: '127.0.0.1',
    } as any as Request;

    // Free tier has 3 requests/minute
    // Send exactly 3 requests (matching limit)
    for (let i = 0; i < 3; i++) {
      let wasRejected = false;
      const mockRes = {
        status: (code: number) => {
          if (code === 429) {
            rejectCount++;
            wasRejected = true;
          }
          return { json: () => {} };
        },
        setHeader: () => {},
        statusCode: 200,
        end: () => {},
      } as any as Response;

      limiter(mockReq, mockRes, () => {
        if (!wasRejected) {
          acceptCount++;
        }
      });
    }

    expect(acceptCount).toBe(3);
    expect(rejectCount).toBe(0);

    // 4th request should be rejected
    let rejected = false;
    const mockRes = {
      status: (code: number) => {
        if (code === 429) rejected = true;
        return { json: () => {} };
      },
      setHeader: () => {},
      statusCode: 429,
      end: () => {},
    } as any as Response;

    limiter(mockReq, mockRes, () => {
      // Next should not be called (request rejected)
      fail('4th request should be rejected');
    });

    expect(rejected).toBe(true);
  });

  /**
   * Test: Failed request decrement works correctly
   *
   * Scenario:
   * - Rate limit: 3 requests/minute for free tier
   * - With skipFailedRequests: true
   * - Send 5 requests, 3 fail
   * - Expected: Only 2 count against limit
   */
  it('should decrement count for failed requests when configured', async () => {
    const limiter = createRateLimiter({
      windowMs: 60000,
      skipFailedRequests: true,
    });

    const mockReq = {
      user: { id: 'failed_test_' + Date.now(), tier: 'free' },
      ip: '127.0.0.1',
    } as any as Request;

    // Simulate 5 requests, 3 fail (400+)
    for (let i = 0; i < 5; i++) {
      const isFailed = i < 3;
      const statusCode = isFailed ? 400 : 200;

      const mockRes = {
        status: (code: number) => ({ json: () => {} }),
        setHeader: () => {},
        statusCode,
        end: function (...args: any[]) {
          // Simulating response end to trigger skipFailedRequests logic
          // The middleware wraps res.end and decrements count if status >= 400
        },
      } as any as Response;

      limiter(mockReq, mockRes, () => {
        // Simulate end being called (which happens after next() in real Express)
        if (isFailed) {
          (mockRes.end as any)();
        }
      });
    }

    // After 5 requests (3 failed, 2 succeeded), counter should be at 2
    // Limit is 3, so next 1 request should succeed, 2nd should fail
    let acceptCount = 0;
    let rejectCount = 0;
    for (let i = 0; i < 3; i++) {
      let wasRejected = false;
      const mockRes = {
        status: (code: number) => {
          if (code === 429) {
            rejectCount++;
            wasRejected = true;
          }
          return { json: () => {} };
        },
        setHeader: () => {},
        statusCode: 200,
        end: () => {},
      } as any as Response;

      limiter(mockReq, mockRes, () => {
        if (!wasRejected) {
          acceptCount++;
        }
      });
    }

    // 1 should pass (3 - 2 already used), 2 should fail
    expect(acceptCount).toBe(1);
    expect(rejectCount).toBe(2);
  });
});
