/**
 * Health Check Routes
 * 
 * Provides health monitoring endpoints for:
 * - Temp directory usage
 * - Memory usage
 * - Disk space
 * - Security metrics
 */

import type { Express, Request, Response } from 'express';
import { checkTempHealth, cleanupOrphanedTempFiles } from '../startup-cleanup';
import os from 'os';
import fs from 'fs/promises';
import path from 'path';

/**
 * Register health check routes
 */
export function registerHealthRoutes(app: Express): void {
  // Basic health check
  app.get('/api/health', async (req: Request, res: Response) => {
    try {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        pid: process.pid,
        node: process.version,
        platform: os.platform(),
        arch: os.arch(),
      });
    } catch (error) {
      res.status(500).json({
        status: 'unhealthy',
        error: 'Health check failed',
        timestamp: new Date().toISOString(),
      });
    }
  });

  // Temp directory health check
  app.get('/api/health/disk', async (req: Request, res: Response) => {
    try {
      const tempHealth = await checkTempHealth();
      
      // Get disk space info
      const diskInfo = {
        total: os.totalmem(),
        free: os.freemem(),
        used: os.totalmem() - os.freemem(),
        usage_percent: Math.round(((os.totalmem() - os.freemem()) / os.totalmem()) * 100),
      };

      const response = {
        status: tempHealth.healthy ? 'healthy' : 'warning',
        timestamp: new Date().toISOString(),
        temp_directories: {
          healthy: tempHealth.healthy,
          total_size: tempHealth.totalSize,
          file_count: tempHealth.fileCount,
          warnings: tempHealth.warnings,
          limits: {
            max_size_bytes: 10 * 1024 * 1024 * 1024, // 10GB
            max_file_count: 1000,
            max_file_age_ms: 60 * 60 * 1000, // 1 hour
          },
        },
        memory: diskInfo,
      };

      if (tempHealth.healthy) {
        res.json(response);
      } else {
        res.status(503).json(response);
      }
    } catch (error) {
      res.status(500).json({
        status: 'error',
        error: 'Disk health check failed',
        timestamp: new Date().toISOString(),
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // Trigger temp cleanup manually
  app.post('/api/health/cleanup', async (req: Request, res: Response) => {
    try {
      // Optional: Add authentication for this endpoint in production
      if (process.env.NODE_ENV === 'production' && !req.headers['x-admin-token']) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Admin token required for cleanup',
        });
      }

      const result = await cleanupOrphanedTempFiles();
      
      res.json({
        status: 'success',
        timestamp: new Date().toISOString(),
        cleanup: {
          files_removed: result.totalFilesRemoved,
          space_freed_bytes: result.totalSpaceFreed,
          space_freed_mb: Math.round(result.totalSpaceFreed / (1024 * 1024)),
          duration_ms: result.totalDuration,
          directories: result.directories.map(d => ({
            path: d.directory,
            files_removed: d.filesRemoved,
            space_freed_bytes: d.spaceFreed,
            errors: d.errors.length,
          })),
          warnings: result.warnings,
          errors: result.errors,
        },
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        error: 'Cleanup failed',
        timestamp: new Date().toISOString(),
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // Security metrics endpoint
  app.get('/api/health/security', async (req: Request, res: Response) => {
    try {
      // Get basic security metrics
      const tempHealth = await checkTempHealth();
      
      // Get process security info
      const securityInfo = {
        uid: process.getuid?.() || null,
        gid: process.getgid?.() || null,
        groups: process.getgroups?.() || null,
        cwd: process.cwd(),
        execPath: process.execPath,
        version: process.version,
        argv: process.argv,
      };

      // Get environment security info (redacted)
      const envSecurity = {
        node_env: process.env.NODE_ENV,
        has_database_url: !!process.env.DATABASE_URL,
        has_redis_url: !!process.env.REDIS_URL,
        has_jwt_secret: !!process.env.JWT_SECRET,
        has_token_secret: !!process.env.TOKEN_SECRET,
        app_version: process.env.APP_VERSION,
        has_dodo_api_key: !!process.env.DODO_PAYMENTS_API_KEY,
      };

      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        security: {
          temp_directories: {
            healthy: tempHealth.healthy,
            file_count: tempHealth.fileCount,
            total_size: tempHealth.totalSize,
            warnings: tempHealth.warnings.length,
          },
          process: securityInfo,
          environment: envSecurity,
          memory: {
            usage: process.memoryUsage(),
            system: {
              total: os.totalmem(),
              free: os.freemem(),
              usage_percent: Math.round(((os.totalmem() - os.freemem()) / os.totalmem()) * 100),
            },
          },
        },
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        error: 'Security health check failed',
        timestamp: new Date().toISOString(),
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // Detailed system info (for debugging)
  app.get('/api/health/system', async (req: Request, res: Response) => {
    try {
      const uptime = process.uptime();
      const loadAvg = os.loadavg();
      const cpuCount = os.cpus().length;
      const networkInterfaces = os.networkInterfaces();
      
      // Get disk space for temp directories
      const tempDirs = ['/tmp', '/tmp/metaextract', '/tmp/metaextract-uploads'];
      const diskInfo: Record<string, any> = {};
      
      for (const dir of tempDirs) {
        try {
          const stats = await fs.stat(dir);
          diskInfo[dir] = {
            exists: true,
            size: stats.size,
            mode: stats.mode.toString(8),
            uid: stats.uid,
            gid: stats.gid,
            atime: stats.atime,
            mtime: stats.mtime,
            ctime: stats.ctime,
          };
        } catch (error) {
          diskInfo[dir] = {
            exists: false,
            error: (error as Error).message,
          };
        }
      }

      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        system: {
          hostname: os.hostname(),
          platform: os.platform(),
          arch: os.arch(),
          release: os.release(),
          uptime: os.uptime(),
          loadavg: loadAvg,
          cpu_count: cpuCount,
          memory: {
            total: os.totalmem(),
            free: os.freemem(),
            used: os.totalmem() - os.freemem(),
            usage_percent: Math.round(((os.totalmem() - os.freemem()) / os.totalmem()) * 100),
          },
          process: {
            pid: process.pid,
            ppid: process.ppid,
            uptime: uptime,
            version: process.version,
            versions: process.versions,
            arch: process.arch,
            platform: process.platform,
            argv: process.argv,
            execPath: process.execPath,
            cwd: process.cwd(),
            memory: process.memoryUsage(),
          },
          network: {
            interfaces: Object.keys(networkInterfaces),
          },
          disk: diskInfo,
        },
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        error: 'System health check failed',
        timestamp: new Date().toISOString(),
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });
}