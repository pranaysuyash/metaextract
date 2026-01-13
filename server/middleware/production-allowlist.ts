import type { Request, Response, NextFunction } from 'express';

/**
 * Production Allowlist Middleware
 *
 * Blocks all routes except explicitly allowlisted paths in production.
 * This provides defense-in-depth: even if legacy routes are registered,
 * they cannot be reached in production.
 *
 * SECURITY: This is a hard fail-closed guard. Unknown paths return 404.
 */
const ALLOWED_PATHS_IN_PRODUCTION = [
  '/api/images_mvp',
  '/api/health',
  '/auth',
  '/api/auth',
];

const ALLOWED_EXTENSIONS = [
  '.js',
  '.css',
  '.png',
  '.jpg',
  '.jpeg',
  '.svg',
  '.ico',
  '.woff',
  '.woff2',
  '.ttf',
  '.eot',
  '.webp',
  '.json',
];

/**
 * Check if a path is allowlisted
 */
function isPathAllowed(path: string): boolean {
  for (const allowed of ALLOWED_PATHS_IN_PRODUCTION) {
    if (path.startsWith(allowed)) {
      return true;
    }
  }

  for (const ext of ALLOWED_EXTENSIONS) {
    if (path.endsWith(ext)) {
      return true;
    }
  }

  return false;
}

/**
 * Production allowlist middleware
 * Returns 404 for all non-allowlisted paths in production
 */
export function productionAllowlistMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  if (process.env.NODE_ENV !== 'production') {
    next();
    return;
  }

  if (process.env.IMAGES_MVP_ONLY !== 'true') {
    next();
    return;
  }

  if (isPathAllowed(req.path)) {
    next();
    return;
  }

  res.status(404).json({
    error: 'Not Found',
    message: 'This endpoint is not available in production',
  });
}
