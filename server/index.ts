// Load environment variables FIRST
import { config } from 'dotenv';
config({ path: './.env' });

import express, { type Request, Response, NextFunction } from 'express';
import cookieParser from 'cookie-parser';
import { registerRoutes } from './routes';
import { registerAuthRoutes, authMiddleware } from './auth';
import {
  registerMockAuthRoutes,
  authMiddleware as mockAuthMiddleware,
} from './auth-mock';
import { serveStatic } from './static';
import { createServer } from 'http';
import { db } from './db';
import expressWs from 'express-ws';
import crypto from 'crypto';
import {
  applySecurityHeaders,
  getClientIP,
  sanitizeErrorMessage,
} from './security-utils';
import { pythonExecutable } from './utils/extraction-helpers';
import { cleanupOrphanedTempFiles, startPeriodicCleanup, cleanupOnExit } from './startup-cleanup';
import { registerHealthRoutes } from './routes/health';
import { registerMonitoringRoutes } from './routes/monitoring';
import { securityAlertManager } from './monitoring/security-alerts';
import { securityEventLogger } from './monitoring/security-events';
import { applyUploadRateLimiting } from './middleware/upload-rate-limit';

const app = express();
const httpServer = createServer(app);

// Add WebSocket support to Express
const expressWsInstance = expressWs(app, httpServer);
const wsApp = expressWsInstance.app;

declare module 'http' {
  interface IncomingMessage {
    rawBody: unknown;
    requestId?: string;
  }
}

// Cookie parser (must be before other middleware)
app.use(cookieParser());

app.use(
  express.json({
    limit: '10kb', // Limit body size to prevent DoS
    verify: (req, _res, buf) => {
      req.rawBody = buf;
    },
  })
);

app.use(express.urlencoded({ extended: false, limit: '10kb' }));

// Debug middleware to track request flow
app.use((req: Request, res: Response, next: NextFunction) => {
  console.log(`[DEBUG] ${req.method} ${req.path} - Request received`);
  next();
});

// Apply security headers to all responses
app.use((req: Request, res: Response, next: NextFunction) => {
  try {
    applySecurityHeaders(res, req);
    next();
  } catch (error) {
    console.error('Security headers middleware error:', error);
    next(error);
  }
});

// Generate request ID for audit trail
app.use((req: Request, res: Response, next: NextFunction) => {
  try {
    req.requestId =
      (req.headers['x-request-id'] as string) || crypto.randomUUID();
    res.setHeader('X-Request-ID', req.requestId);
    next();
  } catch (error) {
    console.error('Request ID middleware error:', error);
    next(error);
  }
});

// Auth middleware - attaches user to request if authenticated
// Use mock auth if database is not available
const isDatabaseAvailable = !!process.env.DATABASE_URL;
if (isDatabaseAvailable) {
  app.use(authMiddleware);
  log('Using database authentication system');
} else {
  app.use(mockAuthMiddleware);
  console.log(
    '\x1b[33m%s\x1b[0m',
    '----------------------------------------------------------------'
  );
  console.log('\x1b[33m%s\x1b[0m', '⚠️  WARNING: DATABASE_URL not configured!');
  console.log('\x1b[33m%s\x1b[0m', '   - Using mock authentication system');
  console.log(
    '\x1b[33m%s\x1b[0m',
    '   - Using in-memory storage (DATA WILL BE LOST ON RESTART)'
  );
  console.log(
    '\x1b[33m%s\x1b[0m',
    '----------------------------------------------------------------'
  );
}

export function log(message: string, source = 'express') {
  const formattedTime = new Date().toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });

  console.log(`${formattedTime} [${source}] ${message}`);
}

log(`Python executable: ${pythonExecutable}`, 'startup');

app.use((req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on('finish', () => {
    const duration = Date.now() - start;
    if (path.startsWith('/api')) {
      const logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      log(logLine);
    }
  });

  next();
});

(async () => {
  // Register auth routes - use mock auth if database is not available
  const isDatabaseAvailable = !!process.env.DATABASE_URL;
  if (isDatabaseAvailable) {
    registerAuthRoutes(app);
    log('Registered database authentication routes');
  } else {
    registerMockAuthRoutes(app);
    log('⚠️  Registered mock authentication routes (development mode)');
    log('📋 Test credentials available at /api/auth/dev/users');
  }

  // Register main API routes
  await registerRoutes(httpServer, app);

  // Register health check routes
  registerHealthRoutes(app);
  log('Registered health check routes');

  // Register monitoring routes
  registerMonitoringRoutes(app);
  log('Registered monitoring routes');

  // Apply upload rate limiting (skip in test environment)
  if (process.env.NODE_ENV !== 'test') {
    applyUploadRateLimiting(app);
    log('Applied upload rate limiting');
  } else {
    log('Skipping rate limiting in test environment');
  }

  // Initialize temp file cleanup system (skip in test environment)
  if (process.env.NODE_ENV !== 'test') {
    log('Initializing temp file cleanup system...');
    try {
      // Run cleanup on startup
      const startupResult = await cleanupOrphanedTempFiles();
      log(`Startup cleanup completed: removed ${startupResult.totalFilesRemoved} files, freed ${Math.round(startupResult.totalSpaceFreed / (1024 * 1024))}MB`);
      
      // Start periodic cleanup (hourly)
      const cleanupInterval = startPeriodicCleanup(60 * 60 * 1000);
      log('Periodic cleanup scheduled every hour');
      
      // Initialize security monitoring
      log('Initializing security monitoring system...');
      try {
        // Start periodic security monitoring (every 5 minutes)
        const monitoringInterval = securityAlertManager.startPeriodicMonitoring(5 * 60 * 1000);
        log('Security monitoring active - checking every 5 minutes');
        
        // Cleanup monitoring on exit
        process.on('exit', () => {
          securityAlertManager.stopPeriodicMonitoring(monitoringInterval);
          // Stop periodic security event flush if running
          try {
            // securityEventLogger is a singleton that may have a running timer
            (securityEventLogger as any)?.stopPeriodicFlush?.();
          } catch (e) {
            // ignore
          }
        });
        
        process.on('SIGINT', async () => {
          securityAlertManager.stopPeriodicMonitoring(monitoringInterval);
          try {
            (securityEventLogger as any)?.stopPeriodicFlush?.();
          } catch (e) {
            // ignore
          }
        });
        
        process.on('SIGTERM', async () => {
          securityAlertManager.stopPeriodicMonitoring(monitoringInterval);
          try {
            (securityEventLogger as any)?.stopPeriodicFlush?.();
          } catch (e) {
            // ignore
          }
        });
        
      } catch (error) {
        log(`Warning: Security monitoring initialization failed: ${error}`, 'startup');
      }
      
      // Cleanup on process exit
      process.on('exit', async () => {
        clearInterval(cleanupInterval);
        await cleanupOnExit();
      });
      
      // Handle graceful shutdown
      process.on('SIGINT', async () => {
        log('Received SIGINT, cleaning up...');
        clearInterval(cleanupInterval);
        await cleanupOnExit();
        process.exit(0);
      });
      
      process.on('SIGTERM', async () => {
        log('Received SIGTERM, cleaning up...');
        clearInterval(cleanupInterval);
        await cleanupOnExit();
        process.exit(0);
      });
      
    } catch (error) {
      log(`Warning: Temp cleanup system initialization failed: ${error}`, 'startup');
      // Continue startup even if cleanup fails
    }
  } else {
    log('Skipping temp cleanup system initialization in test environment');
  }

  // CRITICAL FIX: Add API 404 handler for undefined API routes
  app.use('/api/*', (req: Request, res: Response) => {
    res.status(404).json({
      error: 'API endpoint not found',
      message: `The endpoint ${req.originalUrl} does not exist`,
      requestId: req.requestId,
    });
  });

  // Enhanced error handler with sanitization
  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const context =
      process.env.NODE_ENV === 'production' ? 'production' : 'development';

    try {
      const message = sanitizeErrorMessage(err.message, context);
      const requestId = (_req as any).requestId || 'unknown';

      // Log full error with request ID for debugging (without sensitive data)
      console.error(`[${requestId}] Error:`, {
        status,
        message: sanitizeErrorMessage(err.message, context),
        stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
      });

      res.status(status).json({
        error: status >= 500 ? 'Internal Server Error' : message,
        requestId,
      });
    } catch (handlerError) {
      // If the error handler itself fails, log and return a safe response
      console.error('Error handler failed:', handlerError);
      console.error('Original error:', err);
      res.status(500).json({
        error: 'Internal Server Error',
        requestId: 'unknown',
      });
    }
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (process.env.NODE_ENV === 'production') {
    serveStatic(app);
  } else {
    const { setupVite } = await import('./vite');
    await setupVite(httpServer, app);
  }

  // ALWAYS serve the app on the port specified in the environment variable PORT
  // Other ports are firewalled. Default to 3000 if not specified.
  // this serves both the API and the client.
  // It is the only port that is not firewalled.
  const port = parseInt(process.env.PORT || '3000', 10);
  const host = process.env.HOST || '0.0.0.0';

  const startServer = (portToUse: number) => {
    httpServer
      .listen(
        {
          port: portToUse,
          host,
        },
        () => {
          log(`serving on ${host}:${portToUse}`);
        }
      )
      .on('error', (err: any) => {
        if (err.code === 'EADDRINUSE') {
          log(`Port ${portToUse} is in use, retrying on ${portToUse + 1}...`);
          startServer(portToUse + 1);
        } else {
          console.error('Server failed to start:', err);
        }
      });
  };

  startServer(port);
})();
