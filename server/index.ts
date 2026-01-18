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
import { db, isDatabaseConnected } from './db';
import expressWs from 'express-ws';
import { productionAllowlistMiddleware } from './middleware/production-allowlist';
import {
  cleanupOrphanedTempFiles,
  startPeriodicCleanup,
  startQuoteCleanup,
  startHoldCleanup,
} from './startup-cleanup';
import { storage } from './storage';

const app = express();
const httpServer = createServer(app);

// Add WebSocket support to Express
const expressWsInstance = expressWs(app, httpServer);
const wsApp = expressWsInstance.app;

declare module 'http' {
  interface IncomingMessage {
    rawBody: unknown;
  }
}

// Cookie parser (must be before other middleware)
app.use(cookieParser());

app.use(
  express.json({
    verify: (req, _res, buf) => {
      req.rawBody = buf;
    },
  })
);

app.use(express.urlencoded({ extended: false }));

// Production allowlist middleware - must be before route registration
app.use(productionAllowlistMiddleware);

// Auth middleware - attaches user to request if authenticated
// Use mock auth if database is not available
// IMPORTANT: Do not rely on truthiness of the Proxy export; check real connectivity
const isDatabaseAvailable = isDatabaseConnected();
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

// Configure trust proxy based on deployment topology
// Default: OFF (safe, prevents header spoofing)
// Set TRUST_PROXY_MODE=one for single reverse proxy
// Set TRUST_PROXY_MODE=all only if origin is locked down
const TRUST_PROXY_MODE = process.env.TRUST_PROXY_MODE || 'off';

if (TRUST_PROXY_MODE === 'one') {
  app.set('trust proxy', 1);
  log('Trust proxy enabled: single hop', 'proxy');
} else if (TRUST_PROXY_MODE === 'all') {
  app.set('trust proxy', true);
  log('Trust proxy enabled: all hops (origin must be locked down!)', 'proxy');
} else {
  log('Trust proxy disabled (default, safe)', 'proxy');
}

// Boot-time warning if behind proxy but trust is off
let proxyWarningShown = false;
app.use((req, res, next) => {
  if (
    !proxyWarningShown &&
    TRUST_PROXY_MODE === 'off' &&
    req.headers['x-forwarded-for']
  ) {
    console.warn(
      '\x1b[33m%s\x1b[0m',
      '[proxy] ⚠️  X-Forwarded-For detected but TRUST_PROXY_MODE=off'
    );
    console.warn(
      '\x1b[33m%s\x1b[0m',
      '[proxy]    If behind reverse proxy, set TRUST_PROXY_MODE=one'
    );
    proxyWarningShown = true;
  }
  next();
});

export function log(message: string, source = 'express') {
  const formattedTime = new Date().toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });

  console.log(`${formattedTime} [${source}] ${message}`);
}

app.use((req, res, next) => {
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
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        const truncated = JSON.stringify(capturedJsonResponse).substring(
          0,
          200
        );
        logLine += ` :: ${truncated}${truncated.length >= 200 ? '...' : ''}`;
      }

      log(logLine);
    }
  });

  next();
});

// Setup function for tests - returns configured app without starting server
// In testMode: returns { app, teardown }
// Otherwise: returns app (via IIFE)
export async function setupApp(opts?: { testMode?: boolean }): Promise<any> {
  const isTestMode = opts?.testMode === true;

  // Startup: Clean up orphaned temp files
  try {
    log('Starting temp file cleanup...');
    const cleanupResult = await cleanupOrphanedTempFiles();
    if (cleanupResult.totalFilesRemoved > 0) {
      log(`Removed ${cleanupResult.totalFilesRemoved} orphaned temp files`);
    } else {
      log('No orphaned temp files to clean');
    }
  } catch (error) {
    console.error('Startup cleanup failed:', error);
  }

  // Register auth routes
  const isDatabaseAvailable = isDatabaseConnected();
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

  // CRITICAL FIX: Add API 404 handler for undefined API routes
  app.use('/api/*', (req: Request, res: Response) => {
    res.status(404).json({
      error: 'API endpoint not found',
      message: `The endpoint ${req.originalUrl} does not exist`,
      availableEndpoints: [
        'GET /api/auth/me',
        'POST /api/auth/register',
        'POST /api/auth/login',
        'POST /api/auth/logout',
        'GET /api/extract/health',
        'POST /api/extract',
        'POST /api/extract/batch',
      ],
    });
  });

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || 'Internal Server Error';

    res.status(status).json({ message });
    throw err;
  });

  // Don't setup vite in test mode (causes import.meta errors in Jest)
  if (!isTestMode) {
    if (process.env.NODE_ENV === 'production') {
      serveStatic(app);
    } else {
      const { setupVite } = await import('./vite');
      await setupVite(httpServer, app);
    }
  }

  // Teardown function for tests
  const teardown = async () => {
    // Close database connections if in test mode
    if (isTestMode) {
      try {
        await db.close();
      } catch (e) {
        // Database already closed or not available
      }
    }
  };

  if (isTestMode) {
    return { app, teardown };
  }

  return app as any;
}

// Only run server startup if not in test mode (environment variable)
// Tests call setupApp() directly with testMode: true
const isTestEnvironment =
  process.env.NODE_ENV === 'test' || process.env.JEST_WORKER_ID !== undefined;

if (!isTestEnvironment) {
  (async () => {
    await setupApp();

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

            // Start periodic temp cleanup (every hour in production)
            if (process.env.NODE_ENV === 'production') {
              startPeriodicCleanup(60 * 60 * 1000);
            }

            // Start quote cleanup (every 5 minutes)
            startQuoteCleanup({
              cleanupExpiredQuotes: () => storage.cleanupExpiredQuotes(),
              intervalMs: 5 * 60 * 1000,
            });

            // ✅ RED FLAG #2 FIX: Start hold cleanup (every 5 minutes)
            // Releases expired HELD credits back to user balances
            startHoldCleanup({
              cleanupExpiredHolds: () => storage.cleanupExpiredHolds(),
              intervalMs: 5 * 60 * 1000,
            });
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
}
