/**
 * Email Verification System
 * Handles email verification for new user registrations
 */

import { Request, Response } from 'express';
import crypto from 'crypto';
import { db } from '../db';
import { users, emailVerificationTokens } from '@shared/schema';
import { eq, sql } from 'drizzle-orm';
import { addHours } from 'date-fns';

const VERIFICATION_CONFIG = {
  TOKEN_EXPIRY_HOURS: 24,
  TOKEN_LENGTH: 32,
  MAX_ATTEMPTS: 3,
};

/**
 * Generate email verification token
 */
export function generateEmailVerificationToken(): string {
  return crypto.randomBytes(VERIFICATION_CONFIG.TOKEN_LENGTH).toString('hex');
}

/**
 * Create email verification token for user
 */
export async function createEmailVerificationToken(
  userId: string
): Promise<string> {
  const token = generateEmailVerificationToken();
  const expiresAt = addHours(
    new Date(),
    VERIFICATION_CONFIG.TOKEN_EXPIRY_HOURS
  );

  // Delete any existing tokens for this user
  await db
    .delete(emailVerificationTokens)
    .where(eq(emailVerificationTokens.userId, userId));

  // Create new token
  await db.insert(emailVerificationTokens).values({
    userId,
    token,
    expiresAt,
    createdAt: new Date(),
  });

  return token;
}

/**
 * Verify email verification token
 */
export async function verifyEmailToken(
  token: string
): Promise<{ success: boolean; userId?: string; message: string }> {
  try {
    if (!token || token.length !== VERIFICATION_CONFIG.TOKEN_LENGTH * 2) {
      return { success: false, message: 'Invalid verification token' };
    }

    // Find token in database
    const [verification] = await db
      .select()
      .from(emailVerificationTokens)
      .where(eq(emailVerificationTokens.token, token))
      .limit(1);

    if (!verification) {
      return { success: false, message: 'Verification token not found' };
    }

    // Check if token is expired
    if (new Date() > verification.expiresAt) {
      // Clean up expired token
      await db
        .delete(emailVerificationTokens)
        .where(eq(emailVerificationTokens.token, token));
      return { success: false, message: 'Verification token has expired' };
    }

    // Check if token has been used
    if (verification.usedAt) {
      return {
        success: false,
        message: 'Verification token has already been used',
      };
    }

    // Mark token as used
    await db
      .update(emailVerificationTokens)
      .set({ usedAt: new Date() })
      .where(eq(emailVerificationTokens.token, token));

    // Update user email verification status
    await db
      .update(users)
      .set({ emailVerified: true, updatedAt: new Date() })
      .where(eq(users.id, verification.userId));

    return {
      success: true,
      userId: verification.userId,
      message: 'Email verified successfully',
    };
  } catch (error) {
    console.error('Email verification error:', error);
    return { success: false, message: 'Email verification failed' };
  }
}

/**
 * Resend email verification token
 */
export async function resendEmailVerificationToken(
  userId: string
): Promise<{ success: boolean; message: string; token?: string }> {
  try {
    // Check if user exists and email is not already verified
    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.id, userId))
      .limit(1);

    if (!user) {
      return { success: false, message: 'User not found' };
    }

    if (user.emailVerified) {
      return { success: false, message: 'Email already verified' };
    }

    // Delete any existing tokens
    await db
      .delete(emailVerificationTokens)
      .where(eq(emailVerificationTokens.userId, userId));

    // Create new token
    const token = await createEmailVerificationToken(userId);

    // In production, this would send an email
    // For now, return the token for development/testing
    return { success: true, message: 'Verification email sent', token };
  } catch (error) {
    console.error('Resend verification error:', error);
    return { success: false, message: 'Failed to resend verification email' };
  }
}

/**
 * Check if user email is verified
 */
export async function isEmailVerified(userId: string): Promise<boolean> {
  try {
    const [user] = await db
      .select({ emailVerified: users.emailVerified })
      .from(users)
      .where(eq(users.id, userId))
      .limit(1);

    return user?.emailVerified || false;
  } catch (error) {
    console.error('Email verification check error:', error);
    return false;
  }
}

/**
 * Clean up expired email verification tokens
 */
export async function cleanupEmailVerificationTokens(): Promise<void> {
  try {
    const now = new Date();
    await db
      .delete(emailVerificationTokens)
      .where(sql`${emailVerificationTokens.expiresAt} < ${now}`);
  } catch (error) {
    console.error('Cleanup email verification tokens error:', error);
  }
}

/**
 * Email verification endpoint handler
 */
export async function handleEmailVerification(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { token } = req.body;

    if (!token) {
      res.status(400).json({ error: 'Verification token is required' });
      return;
    }

    const result = await verifyEmailToken(token);

    if (result.success) {
      res.json({
        success: true,
        message: result.message,
        userId: result.userId,
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.message,
      });
    }
  } catch (error) {
    console.error('Email verification handler error:', error);
    res.status(500).json({
      error: 'Email verification failed',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

/**
 * Resend verification email endpoint handler
 */
export async function handleResendVerification(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const userId = (req as any).user?.id;

    if (!userId) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    const result = await resendEmailVerificationToken(userId);

    if (result.success) {
      res.json({
        success: true,
        message: 'Verification email sent',
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.message,
      });
    }
  } catch (error) {
    console.error('Resend verification handler error:', error);
    res.status(500).json({
      error: 'Failed to resend verification email',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
