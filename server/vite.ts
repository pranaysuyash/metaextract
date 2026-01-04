import { type Express } from 'express';
import { createServer as createViteServer, createLogger } from 'vite';
import { type Server } from 'http';
import viteConfig from '../vite.config';
import fs from 'fs';
import path from 'path';
import { nanoid } from 'nanoid';

// ============================================================================
// Types
// ============================================================================

interface ViteSetupOptions {
  /** Cache client template in memory (production optimization) */
  cacheTemplate?: boolean;
  /** Max age for in-memory cache in milliseconds */
  cacheMaxAge?: number;
}

interface CachedTemplate {
  content: string;
  timestamp: number;
}

// ============================================================================
// Configuration & Constants
// ============================================================================

const viteLogger = createLogger();
const CLIENT_TEMPLATE_PATH = path.resolve(
  import.meta.dirname,
  '..',
  'client',
  'index.html'
);

// Regex pattern for main.tsx script tag injection
// Matches: src="/src/main.tsx" or src='/src/main.tsx' or src=/src/main.tsx
const MAIN_SCRIPT_PATTERN = /src=(['"]?)\/src\/main\.tsx\1/;
const DEFAULT_CACHE_MAX_AGE = 60000; // 1 minute

// ============================================================================
// State
// ============================================================================

let cachedTemplate: CachedTemplate | null = null;
let shouldCacheTemplate = false;
let cacheMaxAge = DEFAULT_CACHE_MAX_AGE;

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Read client template from disk
 * Respects in-memory cache if enabled
 */
async function getTemplate(): Promise<string> {
  const now = Date.now();

  // Check if cache is valid
  if (
    shouldCacheTemplate &&
    cachedTemplate &&
    now - cachedTemplate.timestamp < cacheMaxAge
  ) {
    return cachedTemplate.content;
  }

  // Read from disk
  const template = await fs.promises.readFile(CLIENT_TEMPLATE_PATH, 'utf-8');

  // Update cache if enabled
  if (shouldCacheTemplate) {
    cachedTemplate = { content: template, timestamp: now };
  }

  return template;
}

/**
 * Inject version token into main.tsx script tag
 * Uses regex for flexibility in whitespace and quote style
 */
function injectVersionToken(template: string): string {
  const versionToken = nanoid();
  return template.replace(
    MAIN_SCRIPT_PATTERN,
    `src="/src/main.tsx?v=${versionToken}"`
  );
}

/**
 * Clear in-memory template cache
 */
export function clearTemplateCache(): void {
  cachedTemplate = null;
}

// ============================================================================
// Vite Setup
// ============================================================================

export async function setupVite(
  server: Server,
  app: Express,
  options?: ViteSetupOptions
) {
  // Configure caching based on options
  shouldCacheTemplate = options?.cacheTemplate ?? false;
  if (options?.cacheMaxAge) {
    cacheMaxAge = options.cacheMaxAge;
  }

  const serverOptions = {
    middlewareMode: true,
    hmr: { server, path: '/vite-hmr' },
    allowedHosts: true as const,
  };

  const vite = await createViteServer({
    ...viteConfig,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg, options) => {
        viteLogger.error(msg, options);
        process.exit(1);
      },
    },
    server: serverOptions,
    appType: 'custom',
  });

  app.use(vite.middlewares);

  app.use('*', async (req, res, next) => {
    // CRITICAL FIX: Skip API routes to prevent HTML from being served for API requests
    if (req.originalUrl.startsWith('/api/')) {
      return next();
    }
    
    const url = req.originalUrl;

    try {
      // Read template (from cache or disk)
      const rawTemplate = await getTemplate();

      // Inject version token for cache busting
      const template = injectVersionToken(rawTemplate);

      // Transform HTML with Vite
      const page = await vite.transformIndexHtml(url, template);

      // Send response
      res.status(200).set({ 'Content-Type': 'text/html' }).end(page);
    } catch (error) {
      const err = error as Error;
      viteLogger.error(`Failed to serve index.html: ${err.message}`);
      vite.ssrFixStacktrace(err);
      next(err);
    }
  });
}
