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

const app = express();
const httpServer = createServer(app);

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

// Auth middleware - attaches user to request if authenticated
// Use mock auth if database is not available
const isDatabaseAvailable = !!db;
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

(async () => {
  // Register auth routes - use mock auth if database is not available
  const isDatabaseAvailable = !!db;
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
        'POST /api/extract/batch'
      ]
    });
  });

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || 'Internal Server Error';

    res.status(status).json({ message });
    throw err;
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
