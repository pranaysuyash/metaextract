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
import { storage } from '../storage';

// ============================================================================
// Route Registration
// ============================================================================

export function registerAdminRoutes(app: Express): void {
  // Health check
  app.get('/api/health', (req, res) => {
    res.json({
      status: 'ok',
      service: 'MetaExtract API',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
    });
  });

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
        __dirname,
        '..',
        'extractor',
        'utils',
        'cache.py'
      );
      const cacheStats = await new Promise<any>((resolve) => {
        const python = spawn('python3', [
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
        python.stdout.on('data', (data) => (stdout += data.toString()));
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
      const pattern = req.body.pattern || 'metadata:*';

      const pythonScript = path.join(
        __dirname,
        '..',
        'extractor',
        'utils',
        'cache.py'
      );
      const result = await new Promise<number>((resolve) => {
        const python = spawn('python3', [
          '-c',
          `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from cache import clear_cache_pattern
print(clear_cache_pattern('${pattern}'))
          `,
        ]);

        let stdout = '';
        python.stdout.on('data', (data) => (stdout += data.toString()));
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
}
