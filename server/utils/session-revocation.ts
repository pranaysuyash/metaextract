/**
 * Session and Token Revocation System
 * Handles token blacklisting and session management
 */

import { Request, Response } from 'express';
import crypto from 'crypto';
import { db } from '../db';
import { userSessions } from '@shared/schema';
import { eq, sql } from 'drizzle-orm';

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error('JWT_SECRET environment variable is required');
}

// In-memory token blacklist (use Redis in production)
const tokenBlacklist = new Set<string>();

// Session token storage for revocation
const sessionTokens = new Map<
  string,
  { token: string; userId: string; expiresAt: number }
>();

const REVOCATION_CONFIG = {
  BLACKLIST_CLEANUP_INTERVAL: 60 * 60 * 1000, // 1 hour
  MAX_BLACKLIST_SIZE: 10000,
};

/**
 * Add token to blacklist
 */
export function addToBlacklist(token: string): void {
  if (token && token.length > 20) {
    // Basic validation
    tokenBlacklist.add(token);

    // Clean up old tokens if blacklist gets too large
    if (tokenBlacklist.size > REVOCATION_CONFIG.MAX_BLACKLIST_SIZE) {
      cleanupBlacklist();
    }
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
  // Remove oldest tokens (simple FIFO approach)
  const tokensToRemove = Array.from(tokenBlacklist).slice(0, 1000);
  for (const token of tokensToRemove) {
    tokenBlacklist.delete(token);
  }
}

/**
 * Revoke all sessions for a user
 */
export async function revokeAllUserSessions(userId: string): Promise<void> {
  try {
    // Delete all sessions from database
    await db.delete(userSessions).where(eq(userSessions.userId, userId));

    // Remove from in-memory storage
    for (const [sessionId, session] of sessionTokens.entries()) {
      if (session.userId === userId) {
        sessionTokens.delete(sessionId);
      }
    }

    console.log(`Revoked all sessions for user: ${userId}`);
  } catch (error) {
    console.error('Error revoking user sessions:', error);
  }
}

/**
 * Revoke specific session
 */
export async function revokeSession(sessionId: string): Promise<void> {
  try {
    // Delete from database
    await db.delete(userSessions).where(eq(userSessions.sessionId, sessionId));

    // Remove from in-memory storage
    sessionTokens.delete(sessionId);

    console.log(`Revoked session: ${sessionId}`);
  } catch (error) {
    console.error('Error revoking session:', error);
  }
}

/**
 * Store session token for potential revocation
 */
export function storeSessionToken(
  sessionId: string,
  token: string,
  userId: string,
  expiresAt: Date
): void {
  sessionTokens.set(sessionId, {
    token,
    userId,
    expiresAt: expiresAt.getTime(),
  });
}

/**
 * Cleanup expired sessions
 */
export async function cleanupExpiredSessions(): Promise<void> {
  try {
    const now = new Date();

    // Clean up database
    await db
      .delete(userSessions)
      .where(sql`${userSessions.expiresAt} < ${now}`);

    // Clean up in-memory storage
    for (const [sessionId, session] of sessionTokens.entries()) {
      if (new Date() > new Date(session.expiresAt)) {
        sessionTokens.delete(sessionId);
      }
    }

    // Clean up blacklist periodically
    setTimeout(
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
