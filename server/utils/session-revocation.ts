/**
 * Session and Token Revocation System
 * Handles token blacklisting and session management
 */

import { Request, Response } from 'express';
import { db } from '../db';
import { userSessions } from '@shared/schema';
import { eq, sql } from 'drizzle-orm';

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error('JWT_SECRET environment variable is required');
}

const REVOCATION_CONFIG = {
  BLACKLIST_CLEANUP_INTERVAL: 60 * 60 * 1000, // 1 hour
  MAX_BLACKLIST_SIZE: 10000,
  BLACKLIST_TTL_DAYS: 7,
};

let cleanupTimer: NodeJS.Timeout | null = null;

type BlacklistedToken = { token: string; expiresAt: number };
const tokenBlacklist = new Map<string, BlacklistedToken>();

/**
 * Validate JWT format
 */
function isValidJWTFormat(token: string): boolean {
  const parts = token.split('.');
  return parts.length === 3 && parts.every(part => part.length > 0);
}

/**
 * Add token to blacklist
 */
export function addToBlacklist(token: string, expiresAt?: Date): void {
  if (!token || token.length <= 20 || token.length > 5000) {
    return;
  }

  if (!isValidJWTFormat(token)) {
    return;
  }

  const expiry =
    expiresAt?.getTime() ||
    Date.now() + REVOCATION_CONFIG.BLACKLIST_TTL_DAYS * 24 * 60 * 60 * 1000;
  tokenBlacklist.set(token, { token, expiresAt: expiry });

  if (tokenBlacklist.size > REVOCATION_CONFIG.MAX_BLACKLIST_SIZE) {
    cleanupBlacklist();
  }
}

/**
 * Check if token is blacklisted
 */
export function isTokenBlacklisted(token: string): boolean {
  return tokenBlacklist.has(token);
}

/**
 * Cleanup old tokens from blacklist
 */
function cleanupBlacklist(): void {
  const now = Date.now();

  for (const [token, data] of tokenBlacklist.entries()) {
    if (data.expiresAt < now) {
      tokenBlacklist.delete(token);
    }
  }

  if (tokenBlacklist.size > REVOCATION_CONFIG.MAX_BLACKLIST_SIZE) {
    const tokensToRemove = Array.from(tokenBlacklist.entries()).slice(0, 1000);
    for (const [token, _] of tokensToRemove) {
      tokenBlacklist.delete(token);
    }
  }
}

/**
 * Revoke all sessions for a user
 */
export async function revokeAllUserSessions(userId: string): Promise<void> {
  try {
    await db.transaction(async (tx: any) => {
      await tx.delete(userSessions).where(eq(userSessions.userId, userId));
    });

    console.log(`Revoked all sessions for user: ${userId}`);
  } catch (error) {
    console.error('Error revoking user sessions:', error);
    throw error;
  }
}

/**
 * Revoke specific session
 */
export async function revokeSession(sessionId: string): Promise<void> {
  try {
    await db.delete(userSessions).where(eq(userSessions.sessionId, sessionId));
    console.log(`Revoked session: ${sessionId}`);
  } catch (error) {
    console.error('Error revoking session:', error);
  }
}

/**
 * Cleanup expired sessions
 */
export async function cleanupExpiredSessions(): Promise<void> {
  try {
    const now = new Date();

    await db.transaction(async (tx: any) => {
      await tx
        .delete(userSessions)
        .where(sql`${userSessions.expiresAt} < ${now}`);
    });

    cleanupTimer = setTimeout(
      () => cleanupBlacklist(),
      REVOCATION_CONFIG.BLACKLIST_CLEANUP_INTERVAL
    );

    console.log('Cleaned up expired sessions');
  } catch (error) {
    console.error('Error cleaning up expired sessions:', error);
  }
}

/**
 * Handle logout with token revocation
 */
export async function handleLogoutWithRevocation(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader?.startsWith('Bearer ')
      ? authHeader.substring(7)
      : null;
    const userId = (req as any).user?.id;

    if (token) {
      // Add current token to blacklist
      addToBlacklist(token);
    }

    if (userId) {
      // Revoke all sessions for this user
      await revokeAllUserSessions(userId);
    }

    // Clear auth cookie
    res.clearCookie('auth_token');

    res.json({
      success: true,
      message: 'Logged out successfully. All sessions have been revoked.',
    });
  } catch (error) {
    console.error('Logout with revocation error:', error);
    res.status(500).json({
      error: 'Logout failed',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

/**
 * Handle revoke all sessions
 */
export async function handleRevokeAllSessions(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const userId = (req as any).user?.id;

    if (!userId) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    await revokeAllUserSessions(userId);

    // Add current token to blacklist
    const authHeader = req.headers.authorization;
    const token = authHeader?.startsWith('Bearer ')
      ? authHeader.substring(7)
      : null;
    if (token) {
      addToBlacklist(token);
    }

    res.json({
      success: true,
      message: 'All sessions have been revoked',
    });
  } catch (error) {
    console.error('Revoke all sessions error:', error);
    res.status(500).json({
      error: 'Failed to revoke sessions',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

process.on('SIGTERM', () => {
  if (cleanupTimer) {
    clearTimeout(cleanupTimer);
    cleanupTimer = null;
  }
});

process.on('SIGINT', () => {
  if (cleanupTimer) {
    clearTimeout(cleanupTimer);
    cleanupTimer = null;
  }
});

cleanupExpiredSessions();
