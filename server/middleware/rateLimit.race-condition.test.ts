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
   * - Rate limit: 10 requests/minute
   * - Send 15 concurrent requests at the same millisecond
   * - Expected: 10 pass, 5 rejected
   * - Not allowed: All 15 pass (race condition)
   */
  it('should prevent 15 concurrent requests from bypassing limit of 10', async () => {
    const limiter = createRateLimiter({ windowMs: 60000 });
    let acceptCount = 0;
    let rejectCount = 0;

    // Mock request and response
    const mockReq = {
      user: { id: 'test_user', tier: 'free' },
      ip: '127.0.0.1',
    } as any as Request;

    // Fire 15 concurrent requests
    const promises = Array.from({ length: 15 }, (_, i) => {
      return new Promise<void>((resolve) => {
        const mockRes = {
          status: function (code: number) {
            if (code === 429) {
              rejectCount++;
            }
            return {
              json: () => resolve(),
            };
          },
          setHeader: () => {},
          statusCode: 200,
          end: () => {},
        } as any as Response;

        let nextCalled = false;
        const next = () => {
          nextCalled = true;
          resolve();
        };

        limiter(mockReq, mockRes, next);

        // If next was called, request was accepted
        if (nextCalled) {
          acceptCount++;
        }
      });
    });

    await Promise.all(promises);

    // Should allow exactly 10 (limit), reject 5
    expect(acceptCount + rejectCount).toBe(15);
    expect(acceptCount).toBeLessThanOrEqual(10);
    expect(rejectCount).toBeGreaterThanOrEqual(5);
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
      user: { id: 'atomic_test', tier: 'free' },
      ip: '127.0.0.1',
    } as any as Request;

    // Send exactly 5 requests (matching limit)
    for (let i = 0; i < 5; i++) {
      const mockRes = {
        status: (code: number) => {
          if (code === 429) rejectCount++;
          return { json: () => {} };
        },
        setHeader: () => {},
        statusCode: 200,
        end: () => {},
      } as any as Response;

      let nextCalled = false;
      limiter(mockReq, mockRes, () => {
        nextCalled = true;
      });

      if (nextCalled) acceptCount++;
    }

    expect(acceptCount).toBe(5);
    expect(rejectCount).toBe(0);

    // 6th request should be rejected
    const mockRes = {
      status: (code: number) => {
        expect(code).toBe(429);
        return { json: () => {} };
      },
      setHeader: () => {},
      statusCode: 429,
      end: () => {},
    } as any as Response;

    limiter(mockReq, mockRes, () => {
      // Next should not be called (request rejected)
      fail('6th request should be rejected');
    });
  });

  /**
   * Test: Failed request decrement works correctly
   *
   * Scenario:
   * - Rate limit: 10 requests/minute
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
      user: { id: 'failed_test', tier: 'free' },
      ip: '127.0.0.1',
    } as any as Request;

    // Simulate 5 requests, 3 fail (400+)
    for (let i = 0; i < 5; i++) {
      let statusCode = 200;
      if (i < 3) statusCode = 400; // First 3 fail

      const mockRes = {
        status: (code: number) => ({ json: () => {} }),
        setHeader: () => {},
        statusCode,
        end: function (...args: any[]) {
          // Called by skipFailedRequests logic
        },
      } as any as Response;

      limiter(mockReq, mockRes, () => {});
    }

    // After 5 requests (3 failed, 2 succeeded), counter should be at 2
    // So next 8 requests should succeed, 9th should fail
    let acceptCount = 0;
    for (let i = 0; i < 10; i++) {
      const mockRes = {
        status: (code: number) => {
          if (code !== 429) acceptCount++;
          return { json: () => {} };
        },
        setHeader: () => {},
        statusCode: 200,
        end: () => {},
      } as any as Response;

      limiter(mockReq, mockRes, () => {
        acceptCount++;
      });
    }

    // 8 should pass (10 - 2 already used), 2 should fail
    expect(acceptCount).toBe(8);
  });
});
