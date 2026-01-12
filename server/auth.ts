/**
 * MetaExtract Authentication System
 *
 * Provides:
 * - User registration with email/password
 * - Login with JWT session tokens
 * - Session validation middleware
 * - Tier enforcement based on subscription status
 */

import type { Express, Request, Response, NextFunction } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import crypto from 'crypto';
import { db } from './db';
import { users, subscriptions, creditBalances } from '@shared/schema';
import { eq, sql } from 'drizzle-orm';
import { normalizeTier } from '@shared/tierConfig';
import {
  isLockedOut,
  recordFailedAttempt,
  clearFailedAttempts,
  generateUserCSRFToken,
  validateUserCSRFToken,
} from './security-utils';
import {
  handleEmailVerification,
  handleResendVerification,
} from './utils/email-verification';
import {
  handleLogoutWithRevocation,
  handleRevokeAllSessions,
} from './utils/session-revocation';

// ============================================================================
// CSRF Protection Middleware
// ============================================================================

/**
 * Simple CSRF protection middleware for auth routes
 * Validates CSRF token from header against user-specific token
 */
function csrfProtection(req: Request, res: Response, next: NextFunction): void {
  // Skip CSRF for GET, HEAD, OPTIONS requests
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    next();
    return;
  }

  // Check for CSRF token in header
  const csrfToken = req.headers['x-csrf-token'] as string;
  if (!csrfToken) {
    res.status(403).json({
      error: 'CSRF token required',
      message: 'Please include X-CSRF-Token header',
    });
    return;
  }

  // Get user ID from authenticated request
  const userId = (req as AuthRequest).user?.id;
  if (!userId) {
    res.status(401).json({
      error: 'Authentication required',
      message: 'Please authenticate before performing this action',
    });
    return;
  }

  // Validate CSRF token
  if (!validateUserCSRFToken(csrfToken, userId)) {
    res.status(403).json({
      error: 'Invalid CSRF token',
      message: 'Please refresh the page and try again',
    });
    return;
  }

  next();
}

// ============================================================================
// Route Registration
// ============================================================================

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error(
    'CRITICAL: JWT_SECRET environment variable is required for security. ' +
      'Please set this in your .env file before starting the server. ' +
      'Generate a strong random secret: openssl rand -hex 32'
  );
}

// Token and session configuration
const JWT_EXPIRES_IN = '7d'; // 7 days
const TOKEN_EXPIRY_MS = 7 * 24 * 60 * 60 * 1000; // Must match JWT_EXPIRES_IN
const SALT_ROUNDS = 12;

// Cookie configuration - enhanced security
const COOKIE_NAME = 'auth_token';
const COOKIE_OPTIONS = {
  httpOnly: true,
  // Lax is required so login persists across Dodo checkout redirects.
  sameSite: 'lax' as const,
  secure: process.env.NODE_ENV === 'production',
  maxAge: TOKEN_EXPIRY_MS,
};

// Token parsing
const BEARER_PREFIX = 'Bearer ';

// ============================================================================
// Types
// ============================================================================

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  tier: string;
  subscriptionStatus: string | null;
  subscriptionId: string | null;
}

export interface AuthRequest extends Request {
  user?: AuthUser;
  isAuthenticated?: boolean;
}

// ============================================================================
// Validation Schemas
// ============================================================================

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters').max(50),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(
      /[^A-Za-z0-9]/,
      'Password must contain at least one special character'
    ),
});

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
  tier: z.string().optional(),
});

const passwordResetRequestSchema = z.object({
  email: z.string().email('Invalid email address'),
});

const passwordResetConfirmSchema = z.object({
  token: z.string().min(10, 'Invalid token'),
  password: registerSchema.shape.password,
});

type ResetTokenRecord = {
  userId: string;
  tokenHash: string;
  expiresAt: number;
};
const inMemoryResetTokens = new Map<string, ResetTokenRecord>();

function hashResetToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Create an AuthUser object from database user data
 */
function createAuthUser(user: {
  id: string;
  email: string;
  username: string;
  tier: string;
  subscriptionStatus: string | null;
  subscriptionId: string | null;
}): AuthUser {
  return {
    id: user.id,
    email: user.email,
    username: user.username,
    tier: user.tier,
    subscriptionStatus: user.subscriptionStatus,
    subscriptionId: user.subscriptionId,
  };
}

/**
 * Set authentication cookie on response
 */
function setAuthCookie(res: Response, token: string): void {
  res.cookie(COOKIE_NAME, token, {
    ...COOKIE_OPTIONS,
    secure: process.env.NODE_ENV === 'production',
    maxAge: TOKEN_EXPIRY_MS,
  });
}

function generateToken(user: AuthUser): string {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
      username: user.username,
      tier: user.tier,
    },
    JWT_SECRET!,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

export function verifyToken(token: string): AuthUser | null {
  try {
    const decoded = jwt.verify(token, JWT_SECRET!) as AuthUser;
    return decoded;
  } catch {
    return null;
  }
}

function isDatabaseConnectionError(error: unknown): boolean {
  if (!error || typeof error !== 'object') {
    return false;
  }
  const code = (error as { code?: string }).code;
  return (
    code === 'ECONNREFUSED' ||
    code === 'ECONNRESET' ||
    code === 'ETIMEDOUT' ||
    code === 'ENOTFOUND' ||
    code === '57P01' ||
    code === '3D000'
  );
}

// ============================================================================
// Middleware
// ============================================================================

/**
 * Authentication middleware - validates JWT and attaches user to request
 * Does NOT block unauthenticated requests - use requireAuth for that
 */
export function authMiddleware(
  req: AuthRequest,
  res: Response,
  next: NextFunction
) {
  const authHeader = req.headers.authorization;
  const cookieToken = req.cookies?.[COOKIE_NAME];

  const token = authHeader?.startsWith(BEARER_PREFIX)
    ? authHeader.slice(BEARER_PREFIX.length)
    : cookieToken;

  if (token) {
    const user = verifyToken(token);
    if (user) {
      req.user = user;
      req.isAuthenticated = true;
    }
  }

  req.isAuthenticated = req.isAuthenticated || false;
  next();
}

/**
 * Require authentication - returns 401 if not authenticated
 */
export function requireAuth(
  req: AuthRequest,
  res: Response,
  next: NextFunction
) {
  if (!req.isAuthenticated || !req.user) {
    return res.status(401).json({
      error: 'Authentication required',
      code: 'AUTH_REQUIRED',
    });
  }
  next();
}

/**
 * Require specific tier - returns 403 if user's tier is insufficient
 */
export function requireTier(...allowedTiers: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        code: 'AUTH_REQUIRED',
      });
    }

    if (!allowedTiers.includes(req.user.tier)) {
      return res.status(403).json({
        error: 'Upgrade required',
        code: 'TIER_UPGRADE_REQUIRED',
        current_tier: req.user.tier,
        required_tiers: allowedTiers,
      });
    }

    next();
  };
}

/**
 * Get effective tier for a request
 * - Authenticated users: use their subscription tier
 * - Unauthenticated users: "enterprise" tier (full access)
 */
export function getEffectiveTier(req: AuthRequest): string {
  if (req.user && req.user.subscriptionStatus === 'active') {
    return req.user.tier;
  }
  return 'enterprise';
}

// ============================================================================
// Route Handlers
// ============================================================================

export function registerAuthRoutes(app: Express) {
  // -------------------------------------------------------------------------
  // Password Reset (dev-friendly)
  // -------------------------------------------------------------------------
  // This does not send email yet; in development we return the token so you can test.
  app.post(
    '/api/auth/password-reset/request',
    async (req: Request, res: Response) => {
      try {
        const validation = passwordResetRequestSchema.safeParse(req.body);
        if (!validation.success) {
          return res.status(400).json({
            error: 'Validation failed',
            details: validation.error.flatten().fieldErrors,
          });
        }

        if (!db) {
          return res.status(503).json({
            error: 'Database not available',
            message: 'Please configure DATABASE_URL',
          });
        }

        const email = validation.data.email;
        const [user] = await db
          .select()
          .from(users)
          .where(eq(users.email, email))
          .limit(1);

        // Always return a generic message to avoid email enumeration.
        if (!user) {
          return res.json({
            message:
              'If an account exists with this email, a reset link has been sent.',
          });
        }

        const token = crypto.randomBytes(24).toString('hex');
        const tokenHash = hashResetToken(token);
        const expiresAt = Date.now() + 15 * 60 * 1000; // 15 minutes

        // Persist token if table exists; otherwise fall back to in-memory (dev/test).
        try {
          await db.execute(sql`
          insert into password_reset_tokens
            (user_id, token_hash, expires_at, used_at, created_at)
          values
            (${user.id}, ${tokenHash}, to_timestamp(${expiresAt} / 1000.0), null, now())
        `);
        } catch (e: any) {
          // 42P01: undefined_table
          if (e?.code === '42P01') {
            inMemoryResetTokens.set(tokenHash, {
              userId: user.id,
              tokenHash,
              expiresAt,
            });
          } else {
            throw e;
          }
        }

        const response: any = {
          message:
            'If an account exists with this email, a reset link has been sent.',
        };
        if (process.env.NODE_ENV === 'development') {
          response.token = token;
        }
        return res.json(response);
      } catch (error: unknown) {
        console.error('Password reset request error:', error);
        return res.status(500).json({ error: 'Password reset request failed' });
      }
    }
  );

  app.post(
    '/api/auth/password-reset/confirm',
    csrfProtection, // Add CSRF protection for password reset
    async (req: Request, res: Response) => {
      try {
        const validation = passwordResetConfirmSchema.safeParse(req.body);
        if (!validation.success) {
          return res.status(400).json({
            error: 'Validation failed',
            details: validation.error.flatten().fieldErrors,
          });
        }

        if (!db) {
          return res.status(503).json({
            error: 'Database not available',
            message: 'Please configure DATABASE_URL',
          });
        }

        const { token, password } = validation.data;
        const tokenHash = hashResetToken(token);

        // Prefer DB-backed tokens, fall back to in-memory if table missing.
        let userId: string | null = null;
        let expiresAtMs: number | null = null;
        let tokenRowId: string | null = null;

        // Security: Ensure token is a string and not empty
        if (!token || typeof token !== 'string' || token.length < 10) {
          return res
            .status(400)
            .json({ error: 'Invalid or expired reset token' });
        }

        try {
          const result = await db.execute(sql`
          select
            id,
            user_id as "userId",
            extract(epoch from expires_at) * 1000 as "expiresAtMs",
            used_at as "usedAt"
          from password_reset_tokens
          where token_hash = ${tokenHash}
          limit 1
        `);

          const row: any = (result as any).rows?.[0] ?? null;
          if (row && !row.usedAt) {
            userId = row.userId;
            expiresAtMs = Number(row.expiresAtMs);
            tokenRowId = row.id;
          }
        } catch (e: any) {
          if (e?.code === '42P01') {
            const rec = inMemoryResetTokens.get(tokenHash);
            if (rec) {
              userId = rec.userId;
              expiresAtMs = rec.expiresAt;
            }
          } else {
            throw e;
          }
        }

        if (!userId || !expiresAtMs || Date.now() > expiresAtMs) {
          return res
            .status(400)
            .json({ error: 'Invalid or expired reset token' });
        }

        const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
        await db
          .update(users)
          .set({ password: hashedPassword, updatedAt: new Date() })
          .where(eq(users.id, userId));

        if (tokenRowId) {
          try {
            await db.execute(sql`
            update password_reset_tokens set used_at = now() where id = ${tokenRowId}
          `);
          } catch {
            // ignore
          }
        } else {
          inMemoryResetTokens.delete(tokenHash);
        }

        return res.json({ success: true });
      } catch (error: unknown) {
        console.error('Password reset confirm error:', error);
        return res.status(500).json({ error: 'Password reset failed' });
      }
    }
  );

  // -------------------------------------------------------------------------
  // Register
  // -------------------------------------------------------------------------
  app.post('/api/auth/register', async (req: Request, res: Response) => {
    try {
      // Validate input
      const validation = registerSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({
          error: 'Validation failed',
          details: validation.error.flatten().fieldErrors,
        });
      }

      const { email, username, password } = validation.data;

      // Check if db is available
      if (!db) {
        return res.status(503).json({
          error: 'Database not available',
          message: 'Please configure DATABASE_URL for user registration',
        });
      }

      // Check if email already exists
      const existingEmail = await db
        .select()
        .from(users)
        .where(eq(users.email, email))
        .limit(1);
      if (existingEmail.length > 0) {
        return res.status(409).json({
          error: 'Email already registered',
          code: 'EMAIL_EXISTS',
        });
      }

      // Check if username already exists
      const existingUsername = await db
        .select()
        .from(users)
        .where(eq(users.username, username))
        .limit(1);
      if (existingUsername.length > 0) {
        return res.status(409).json({
          error: 'Username already taken',
          code: 'USERNAME_EXISTS',
        });
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

      // Create user
      const [newUser] = await db
        .insert(users)
        .values({
          email,
          username,
          password: hashedPassword,
          tier: 'enterprise',
          subscriptionStatus: 'none',
        })
        .returning();

      // ✅ Use helper to create AuthUser
      const authUser = createAuthUser(newUser);
      const token = generateToken(authUser);

      // ✅ Use helper to set cookie
      setAuthCookie(res, token);

      // Create initial credit balance for new user
      try {
        await db.insert(creditBalances).values({
          userId: newUser.id,
          sessionId: `credits:core:user:${newUser.id}`,
          credits: 0, // New users start with 0 credits
        });
      } catch (creditError) {
        console.error(
          'Could not create initial credit balance for user:',
          creditError
        );
        // Continue registration even if credit balance creation fails
      }

      res.status(201).json({
        success: true,
        user: {
          id: newUser.id,
          email: newUser.email,
          username: newUser.username,
          tier: newUser.tier,
          credits: 0, // New users start with 0 credits
        },
        token,
      });
    } catch (error: unknown) {
      console.error('Registration error:', error);
      const status = isDatabaseConnectionError(error) ? 503 : 500;
      res.status(status).json({
        error: 'Registration failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // -------------------------------------------------------------------------
  // Login
  // -------------------------------------------------------------------------
  app.post('/api/auth/login', async (req: Request, res: Response) => {
    try {
      // Check for brute force - use email as identifier
      const loginIdentifier =
        (req.body?.email as string) || req.ip || 'unknown';
      const lockStatus = isLockedOut(
        `login:${loginIdentifier}`,
        5,
        15 * 60 * 1000
      );

      if (lockStatus.locked) {
        res.setHeader(
          'Retry-After',
          Math.ceil((lockStatus.resetTime - Date.now()) / 1000)
        );
        return res.status(429).json({
          error: 'Too many login attempts',
          message: 'Please wait 15 minutes before trying again',
          retryAfter: Math.ceil((lockStatus.resetTime - Date.now()) / 1000),
        });
      }

      // Validate input
      const validation = loginSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({
          error: 'Validation failed',
          details: validation.error.flatten().fieldErrors,
        });
      }

      const { email, password, tier } = validation.data;

      // Check if db is available
      if (!db) {
        return res.status(503).json({
          error: 'Database not available',
          message: 'Please configure DATABASE_URL',
        });
      }

      // Find user
      const [user] = await db
        .select()
        .from(users)
        .where(eq(users.email, email))
        .limit(1);

      if (!user) {
        // Record failed attempt even for non-existent users (prevent username enumeration)
        recordFailedAttempt(`login:${loginIdentifier}`, 5, 15 * 60 * 1000);
        return res.status(401).json({
          error: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS',
        });
      }

      // Verify password
      const isValid = await bcrypt.compare(password, user.password);
      if (!isValid) {
        recordFailedAttempt(`login:${loginIdentifier}`, 5, 15 * 60 * 1000);
        return res.status(401).json({
          error: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS',
        });
      }

      // Clear failed attempts on successful login
      clearFailedAttempts(`login:${loginIdentifier}`);

      // Check subscription status (refresh from DB)
      let currentTier = user.tier;
      let subscriptionStatus = user.subscriptionStatus;

      if (user.subscriptionId) {
        const [sub] = await db
          .select()
          .from(subscriptions)
          .where(eq(subscriptions.dodoSubscriptionId, user.subscriptionId))
          .limit(1);

        if (sub) {
          currentTier = sub.tier;
          subscriptionStatus = sub.status;
        }
      }

      // Tier override is DISABLED by default and requires explicit environment variable
      // This should NEVER be enabled in production
      const allowTierOverride =
        process.env.ALLOW_TIER_OVERRIDE === 'true' &&
        process.env.NODE_ENV === 'development';

      if (allowTierOverride && tier) {
        const overrideTier = normalizeTier(tier);
        currentTier = overrideTier;
        subscriptionStatus = 'active';
        await db
          .update(users)
          .set({ tier: overrideTier, subscriptionStatus: 'active' })
          .where(eq(users.id, user.id));
      }

      // ✅ Create AuthUser with subscription-aware tier
      const authUser: AuthUser = {
        id: user.id,
        email: user.email,
        username: user.username,
        tier: currentTier,
        subscriptionStatus,
        subscriptionId: user.subscriptionId,
      };

      const token = generateToken(authUser);

      // ✅ Use helper to set cookie
      setAuthCookie(res, token);

      // Get user's credit balance
      let creditBalance = 0;
      try {
        const [balance] = await db
          .select({ credits: creditBalances.credits })
          .from(creditBalances)
          .where(eq(creditBalances.userId, user.id))
          .limit(1);

        if (balance) {
          creditBalance = balance.credits;
        }
      } catch (creditError) {
        console.warn('Could not fetch credit balance for user:', creditError);
        // Continue without credit info if there's an error
      }

      res.json({
        success: true,
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          tier: currentTier,
          subscriptionStatus,
          credits: creditBalance, // Include credit balance in user response
        },
        token,
      });
    } catch (error: unknown) {
      console.error('Login error:', error);
      const status = isDatabaseConnectionError(error) ? 503 : 500;
      res.status(status).json({
        error: 'Login failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // -------------------------------------------------------------------------
  // Logout
  // -------------------------------------------------------------------------
  app.post('/api/auth/logout', async (req: Request, res: Response) => {
    await handleLogoutWithRevocation(req, res);
  });

  // -------------------------------------------------------------------------
  // CSRF Token Generation
  // -------------------------------------------------------------------------
  app.get(
    '/api/auth/csrf-token',
    authMiddleware,
    async (req: AuthRequest, res: Response) => {
      try {
        if (!req.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        const token = generateUserCSRFToken(req.user.id);

        // Set CSRF token in cookie for client-side access
        res.cookie('csrf_token', token, {
          httpOnly: false, // Allow client-side JavaScript to read for AJAX requests
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'strict',
          maxAge: 60 * 60 * 1000, // 1 hour
        });

        res.json({
          token,
          expiresAt: Date.now() + 60 * 60 * 1000,
        });
      } catch (error) {
        console.error('CSRF token generation error:', error);
        res.status(500).json({
          error: 'Failed to generate CSRF token',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );

  // -------------------------------------------------------------------------
  // CSRF Token Generation
  // -------------------------------------------------------------------------
  app.get(
    '/api/auth/csrf-token',
    authMiddleware,
    async (req: AuthRequest, res: Response) => {
      try {
        if (!req.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        // Generate user-specific CSRF token
        const token = generateUserCSRFToken(req.user.id);

        // Set CSRF token in cookie for client-side access
        res.cookie('csrf_token', token, {
          httpOnly: false, // Allow client-side JavaScript to read for AJAX requests
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'strict',
          maxAge: 60 * 60 * 1000, // 1 hour
        });

        res.json({
          token,
          expiresAt: Date.now() + 60 * 60 * 1000,
        });
      } catch (error) {
        console.error('CSRF token generation error:', error);
        res.status(500).json({
          error: 'Failed to generate CSRF token',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );

  // -------------------------------------------------------------------------
  // Get Current User (Session Validation)
  // -------------------------------------------------------------------------
  app.get(
    '/api/auth/me',
    authMiddleware,
    async (req: AuthRequest, res: Response) => {
      try {
        if (!req.isAuthenticated || !req.user) {
          return res.json({
            authenticated: false,
            user: null,
          });
        }

        // Refresh user data from DB if available
        if (db) {
          try {
            const [freshUser] = await db
              .select()
              .from(users)
              .where(eq(users.id, req.user.id))
              .limit(1);

            if (freshUser) {
              return res.json({
                authenticated: true,
                user: {
                  id: freshUser.id,
                  email: freshUser.email,
                  username: freshUser.username,
                  tier: freshUser.tier,
                  subscriptionStatus: freshUser.subscriptionStatus,
                },
              });
            }
          } catch {
            // Fall back to token data
          }
        }

        res.json({
          authenticated: true,
          user: {
            id: req.user.id,
            email: req.user.email,
            username: req.user.username,
            tier: req.user.tier,
            subscriptionStatus: req.user.subscriptionStatus,
          },
        });
      } catch (error) {
        console.error('Auth session check error:', error);
        res.status(200).json({
          authenticated: false,
          user: null,
          error: 'Session check failed',
        });
      }
    }
  );

  // -------------------------------------------------------------------------
  // Refresh Token
  // -------------------------------------------------------------------------
  app.post(
    '/api/auth/refresh',
    authMiddleware,
    async (req: AuthRequest, res: Response) => {
      if (!req.isAuthenticated || !req.user) {
        return res.status(401).json({
          error: 'Not authenticated',
          code: 'NOT_AUTHENTICATED',
        });
      }

      // Refresh user data from DB
      if (db) {
        try {
          const [freshUser] = await db
            .select()
            .from(users)
            .where(eq(users.id, req.user.id))
            .limit(1);

          if (freshUser) {
            // ✅ Use helper to create AuthUser
            const authUser = createAuthUser(freshUser);
            const token = generateToken(authUser);

            // ✅ Use helper to set cookie
            setAuthCookie(res, token);

            return res.json({
              success: true,
              user: {
                id: freshUser.id,
                email: freshUser.email,
                username: freshUser.username,
                tier: freshUser.tier,
                subscriptionStatus: freshUser.subscriptionStatus,
              },
              token,
            });
          }
        } catch {
          // Fall through
        }
      }

      // Re-issue token with existing data
      const token = generateToken(req.user);

      // ✅ Use helper to set cookie
      setAuthCookie(res, token);

      res.json({
        success: true,
        user: req.user,
        token,
      });
    }
  );

  // -------------------------------------------------------------------------
  // Update User Tier (Called by webhook handlers)
  // -------------------------------------------------------------------------
  app.post(
    '/api/auth/update-tier',
    authMiddleware,
    async (req: AuthRequest, res: Response) => {
      // This should only be called internally by webhook handlers
      // Now requires authentication - only authenticated users can call this

      if (!req.user) {
        return res.status(401).json({ error: 'Authentication required' });
      }

      // Only allow admin users or the user themselves to update tiers
      const { userId, tier, subscriptionId, subscriptionStatus } = req.body;

      // ✅ Validate required fields (single check, not duplicate)
      if (!userId || !tier) {
        return res.status(400).json({ error: 'userId and tier required' });
      }

      // For now, only allow users to update their own tier
      // In production, this should be restricted to admin/internal calls only
      if (req.user.id !== userId) {
        return res.status(403).json({ error: 'Can only update your own tier' });
      }

      if (!db) {
        return res.status(503).json({ error: 'Database not available' });
      }

      try {
        await db
          .update(users)
          .set({
            tier,
            subscriptionId: subscriptionId || null,
            subscriptionStatus: subscriptionStatus || 'active',
          })
          .where(eq(users.id, userId));

        res.json({ success: true });
      } catch (error) {
        console.error('Update tier error:', error);
        res.status(500).json({ error: 'Failed to update tier' });
      }
    }
  );

  // -------------------------------------------------------------------------
  // Email Verification
  // -------------------------------------------------------------------------
  app.post('/api/auth/verify-email', async (req: Request, res: Response) => {
    await handleEmailVerification(req, res);
  });

  app.post(
    '/api/auth/resend-verification',
    requireAuth,
    async (req: AuthRequest, res: Response) => {
      await handleResendVerification(req, res);
    }
  );

  // -------------------------------------------------------------------------
  // Session Revocation
  // -------------------------------------------------------------------------
  app.post(
    '/api/auth/logout-all',
    requireAuth,
    async (req: AuthRequest, res: Response) => {
      await handleRevokeAllSessions(req, res);
    }
  );

  app.post('/api/auth/logout', async (req: Request, res: Response) => {
    await handleLogoutWithRevocation(req, res);
  });
}

// Backwards-compatible re-exports from auth-enhanced
export { authenticateToken, authenticateRefreshToken, loginLimiter, apiLimiter } from './auth-enhanced';
