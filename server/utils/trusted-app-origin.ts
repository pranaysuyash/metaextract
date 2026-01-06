import type { Request } from 'express';

const DEV_APP_ORIGINS = new Set([
  'http://localhost:3000',
  'http://127.0.0.1:3000',
  'http://localhost:5173',
  'http://127.0.0.1:5173',
  'http://localhost:5174',
  'http://127.0.0.1:5174',
  'http://localhost:5175',
  'http://127.0.0.1:5175',
]);

function safeOriginFromUrl(value: string): string | null {
  try {
    const url = new URL(value);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') return null;
    return url.origin;
  } catch {
    return null;
  }
}

function getCandidateOrigin(req: Request): string | null {
  const originHeader = req.headers.origin;
  if (typeof originHeader === 'string') {
    const origin = safeOriginFromUrl(originHeader);
    if (origin) return origin;
  }

  const refererHeader = req.headers.referer;
  if (typeof refererHeader === 'string') {
    const origin = safeOriginFromUrl(refererHeader);
    if (origin) return origin;
  }

  return null;
}

function getEnvAppOrigins(): string[] {
  const candidates = [
    process.env.PUBLIC_APP_URL,
    process.env.BASE_URL,
    process.env.REPLIT_DEV_DOMAIN ? `https://${process.env.REPLIT_DEV_DOMAIN}` : null,
    process.env.RAILWAY_PUBLIC_DOMAIN
      ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}`
      : null,
  ].filter(Boolean) as string[];

  const origins: string[] = [];
  for (const value of candidates) {
    const origin = safeOriginFromUrl(value);
    if (origin) origins.push(origin);
  }
  return origins;
}

export function getTrustedAppOrigin(req: Request): string | null {
  const candidate = getCandidateOrigin(req);
  if (!candidate) return null;

  if (DEV_APP_ORIGINS.has(candidate)) return candidate;

  const envOrigins = getEnvAppOrigins();
  if (envOrigins.includes(candidate)) return candidate;

  return null;
}

