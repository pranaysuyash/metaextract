import type { Request, Response } from 'express';
import crypto from 'crypto';

const COOKIE_NAME = 'metaextract_session_id';

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function readCookieHeader(req: Request, name: string): string | null {
  const header = req.headers?.cookie;
  if (!isNonEmptyString(header)) return null;
  // Very small parser: "a=b; c=d"
  const parts = header.split(';');
  for (const part of parts) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    const eqIndex = trimmed.indexOf('=');
    if (eqIndex <= 0) continue;
    const key = trimmed.slice(0, eqIndex).trim();
    if (key !== name) continue;
    const value = trimmed.slice(eqIndex + 1).trim();
    return value ? decodeURIComponent(value) : null;
  }
  return null;
}

export function getOrSetSessionId(
  req: Request,
  res: Response,
  preferredSessionId?: string | null
): string {
  // If an explicit session id was provided via query or header, prefer it (do not set cookie)
  const querySession = (req as any).query?.sessionId ?? (req as any).query?.session_id;
  if (isNonEmptyString(querySession)) return querySession.trim();

  const bodySession = (req as any).body?.sessionId ?? (req as any).body?.session_id;
  if (isNonEmptyString(bodySession)) return bodySession.trim();

  const headerSession = req.headers?.['x-session-id'] as string | undefined;
  if (isNonEmptyString(headerSession)) return headerSession.trim();

  const cookieValue =
    (req as any).cookies?.[COOKIE_NAME] ?? readCookieHeader(req, COOKIE_NAME);
  if (isNonEmptyString(cookieValue)) return cookieValue;

  const sessionId = isNonEmptyString(preferredSessionId)
    ? preferredSessionId.trim()
    : crypto.randomUUID();

  res.cookie(COOKIE_NAME, sessionId, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 365 * 24 * 60 * 60 * 1000, // 1 year
    path: '/',
  });

  return sessionId;
}
