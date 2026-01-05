/**
 * Admin Routes Module
 *
 * Handles admin and monitoring endpoints:
 * - Analytics
 * - Performance monitoring
 * - Cache management
 * - Health checks
 */

import type { Express, Response } from 'express';
import path from 'path';
import { spawn } from 'child_process';
import { pythonExecutable } from '../utils/extraction-helpers';

// Get the routes directory - compatible with both ESM and CommonJS
const projectRoot = process.cwd();
const currentDirPath = path.join(projectRoot, 'server', 'routes');
import { storage } from '../storage/index';
import { getRateLimitMetrics, resetRateLimit } from '../rateLimitMiddleware';
import {
  adminAuthMiddleware,
  adminRateLimitMiddleware,
  healthCheckAuth,
} from '../middleware/admin-auth';
import { sanitizeFilename } from '../security-utils';

// Allowed patterns for cache clearing (whitelist)
const ALLOWED_CACHE_PATTERNS = [
  /^metadata:\*$/,
  /^metadata:[\w-]+$/,
  /^quota:[\w-]+$/,
  /^activity:[\w-]+$/,
];

// ============================================================================
// Route Registration
// ============================================================================

export function registerAdminRoutes(app: Express): void {
  // Health check - no auth required
  app.get('/api/health', healthCheckAuth, (req, res) => {
    res.json({
      status: 'ok',
      service: 'MetaExtract API',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
    });
  });

  // Admin-only endpoints require authentication and rate limiting
  app.use('/api/admin', adminAuthMiddleware);
  app.use('/api/admin', adminRateLimitMiddleware);

  // Analytics summary
  app.get('/api/admin/analytics', async (req, res) => {
    try {
      const summary = await storage.getAnalyticsSummary();
      res.json(summary);
    } catch (error) {
      console.error('Analytics error:', error);
      res.status(500).json({ error: 'Failed to fetch analytics' });
    }
  });

  // Recent extractions
  app.get('/api/admin/extractions', async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 50;
      const extractions = await storage.getRecentExtractions(limit);
      res.json(extractions);
    } catch (error) {
      console.error('Extractions history error:', error);
      res.status(500).json({ error: 'Failed to fetch extractions' });
    }
  });

  // Performance stats
  app.get('/api/performance/stats', async (req, res) => {
    try {
      // Get cache statistics if Redis is available
      const pythonScript = path.join(
        currentDirPath,
        '..',
        'extractor',
        'utils',
        'cache.py'
      );
      const cacheStats = await new Promise<any>(resolve => {
        const python = spawn(pythonExecutable, [
          '-c',
          `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from cache import get_cache_stats
import json
print(json.dumps(get_cache_stats()))
          `,
        ]);

        let stdout = '';
        python.stdout.on('data', data => (stdout += data.toString()));
        python.on('close', () => {
          try {
            resolve(JSON.parse(stdout));
          } catch {
            resolve({ available: false });
          }
        });

        setTimeout(() => {
          python.kill();
          resolve({ available: false, error: 'timeout' });
        }, 5000);
      });

      res.json({
        cache: cacheStats,
        server: {
          uptime_seconds: process.uptime(),
          memory_usage: process.memoryUsage(),
          node_version: process.version,
          platform: process.platform,
        },
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to get performance stats' });
    }
  });

  // Cache management (admin only)
  app.post('/api/performance/cache/clear', async (req, res) => {
    try {
      let pattern = req.body.pattern || 'metadata:*';

      // Validate pattern against whitelist
      const isValidPattern = ALLOWED_CACHE_PATTERNS.some(regex =>
        regex.test(pattern)
      );
      if (!isValidPattern) {
        return res.status(400).json({
          error: 'Invalid pattern',
          message: 'Pattern must match one of the allowed patterns',
          allowed_patterns: [
            'metadata:*',
            'metadata:<id>',
            'quota:<id>',
            'activity:<id>',
          ],
        });
      }

      // Sanitize the pattern
      pattern = sanitizeFilename(pattern);

      const pythonScript = path.join(
        currentDirPath,
        '..',
        'extractor',
        'utils',
        'cache.py'
      );
      const result = await new Promise<number>(resolve => {
        const python = spawn(pythonExecutable, [
          '-c',
          `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from cache import clear_cache_pattern
print(clear_cache_pattern('${pattern}'))
          `,
        ]);

        let stdout = '';
        python.stdout.on('data', data => {
          stdout += data.toString();
        });
        python.on('close', () => {
          resolve(parseInt(stdout.trim()) || 0);
        });

        setTimeout(() => {
          python.kill();
          resolve(0);
        }, 10000);
      });

      res.json({
        success: true,
        cleared_entries: result,
        pattern,
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to clear cache' });
    }
  });

  // Rate limiting for admin endpoints
  app.get('/api/admin/rate-limit/metrics', async (req, res) => {
    try {
      await getRateLimitMetrics(req, res);
    } catch (error) {
      res.status(500).json({
        error: 'Failed to retrieve rate limit metrics',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  app.post('/api/admin/rate-limit/reset/:identifier', async (req, res) => {
    try {
      await resetRateLimit(req, res);
    } catch (error) {
      res.status(500).json({
        error: 'Failed to reset rate limit',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // Monitoring and health endpoints
  app.get('/api/monitoring/status', async (req, res) => {
    try {
      // Call the Python monitoring module
      const { spawn } = require('child_process');
      const path = require('path');
      const currentDir = path.dirname(
        require.main ? require.main.filename : __filename
      );

      const pythonScript = path.join(
        currentDir,
        '..',
        'extractor',
        'monitoring.py'
      );
      const result = await new Promise<any>((resolve, reject) => {
        const python = spawn(pythonExecutable, [
          '-c',
          `
import sys
import os
sys.path.append(os.path.join(os.path.dirname('${pythonScript}')))
from monitoring import get_monitoring_data
import json
print(json.dumps(get_monitoring_data()))
          `,
        ]);

        let stdout = '';
        let stderr = '';

        python.stdout.on('data', (data: Buffer) => {
          stdout += data.toString();
        });

        python.stderr.on('data', (data: Buffer) => {
          stderr += data.toString();
        });

        python.on('close', (code: number | null) => {
          if (code !== 0) {
            console.error('Monitoring data error:', stderr);
            reject(new Error('Failed to get monitoring data'));
            return;
          }
          try {
            resolve(JSON.parse(stdout));
          } catch (e) {
            reject(new Error('Failed to parse monitoring data'));
          }
        });

        setTimeout(() => {
          python.kill();
          reject(new Error('Monitoring data request timed out'));
        }, 10000);
      });

      res.json(result);
    } catch (error) {
      console.error('Monitoring status error:', error);
      res.status(500).json({
        error: 'Failed to get monitoring status',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  app.get('/api/monitoring/performance', async (req, res) => {
    try {
      // Call the Python monitoring module
      const { spawn } = require('child_process');
      const path = require('path');
      const currentDir = path.dirname(
        require.main ? require.main.filename : __filename
      );

      const pythonScript = path.join(
        currentDir,
        '..',
        'extractor',
        'monitoring.py'
      );
      const result = await new Promise<any>((resolve, reject) => {
        const python = spawn(pythonExecutable, [
          '-c',
          `
import sys
import os
sys.path.append(os.path.join(os.path.dirname('${pythonScript}')))
from monitoring import get_performance_summary
import json
print(json.dumps(get_performance_summary()))
          `,
        ]);

        let stdout = '';
        let stderr = '';

        python.stdout.on('data', (data: Buffer) => {
          stdout += data.toString();
        });

        python.stderr.on('data', (data: Buffer) => {
          stderr += data.toString();
        });

        python.on('close', (code: number | null) => {
          if (code !== 0) {
            console.error('Performance data error:', stderr);
            reject(new Error('Failed to get performance data'));
            return;
          }
          try {
            resolve(JSON.parse(stdout));
          } catch (e) {
            reject(new Error('Failed to parse performance data'));
          }
        });

        setTimeout(() => {
          python.kill();
          reject(new Error('Performance data request timed out'));
        }, 10000);
      });

      res.json(result);
    } catch (error) {
      console.error('Performance monitoring error:', error);
      res.status(500).json({
        error: 'Failed to get performance data',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  app.get('/api/monitoring/errors', async (req, res) => {
    try {
      // Call the Python monitoring module
      const { spawn } = require('child_process');
      const path = require('path');
      const currentDir = path.dirname(
        require.main ? require.main.filename : __filename
      );

      const pythonScript = path.join(
        currentDir,
        '..',
        'extractor',
        'monitoring.py'
      );
      const result = await new Promise<any>((resolve, reject) => {
        const python = spawn(pythonExecutable, [
          '-c',
          `
import sys
import os
sys.path.append(os.path.join(os.path.dirname('${pythonScript}')))
from monitoring import get_error_summary
import json
print(json.dumps(get_error_summary()))
          `,
        ]);

        let stdout = '';
        let stderr = '';

        python.stdout.on('data', (data: Buffer) => {
          stdout += data.toString();
        });

        python.stderr.on('data', (data: Buffer) => {
          stderr += data.toString();
        });

        python.on('close', (code: number | null) => {
          if (code !== 0) {
            console.error('Error data error:', stderr);
            reject(new Error('Failed to get error data'));
            return;
          }
          try {
            resolve(JSON.parse(stdout));
          } catch (e) {
            reject(new Error('Failed to parse error data'));
          }
        });

        setTimeout(() => {
          python.kill();
          reject(new Error('Error data request timed out'));
        }, 10000);
      });

      res.json(result);
    } catch (error) {
      console.error('Error monitoring error:', error);
      res.status(500).json({
        error: 'Failed to get error data',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });
}
