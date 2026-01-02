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
import { db } from './db';
import { users, subscriptions } from '@shared/schema';
import { eq } from 'drizzle-orm';
import { normalizeTier } from '@shared/tierConfig';

// ============================================================================
// Configuration
// ============================================================================

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error('JWT_SECRET environment variable is required for security');
}
const JWT_EXPIRES_IN = '7d'; // 7 days
const SALT_ROUNDS = 12;

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
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
  tier: z.string().optional(),
});

// ============================================================================
// Helper Functions
// ============================================================================

function generateToken(user: AuthUser): string {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
      username: user.username,
      tier: user.tier,
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

function verifyToken(token: string): AuthUser | null {
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as AuthUser;
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
  const cookieToken = req.cookies?.auth_token;

  const token = authHeader?.startsWith('Bearer ')
    ? authHeader.slice(7)
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

      // Generate token
      const authUser: AuthUser = {
        id: newUser.id,
        email: newUser.email,
        username: newUser.username,
        tier: newUser.tier,
        subscriptionStatus: newUser.subscriptionStatus,
        subscriptionId: newUser.subscriptionId,
      };

      const token = generateToken(authUser);

      // Set cookie
      res.cookie('auth_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      });

      res.status(201).json({
        success: true,
        user: {
          id: newUser.id,
          email: newUser.email,
          username: newUser.username,
          tier: newUser.tier,
        },
        token,
      });
    } catch (error) {
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
        return res.status(401).json({
          error: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS',
        });
      }

      // Verify password
      const isValid = await bcrypt.compare(password, user.password);
      if (!isValid) {
        return res.status(401).json({
          error: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS',
        });
      }

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

      // Optional tier override for testing - DISABLED IN PRODUCTION
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

      // Generate token
      const authUser: AuthUser = {
        id: user.id,
        email: user.email,
        username: user.username,
        tier: currentTier,
        subscriptionStatus,
        subscriptionId: user.subscriptionId,
      };

      const token = generateToken(authUser);

      // Set cookie
      res.cookie('auth_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      });

      res.json({
        success: true,
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          tier: currentTier,
          subscriptionStatus,
        },
        token,
      });
    } catch (error) {
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
  app.post('/api/auth/logout', (req: Request, res: Response) => {
    res.clearCookie('auth_token');
    res.json({ success: true, message: 'Logged out' });
  });

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
            const authUser: AuthUser = {
              id: freshUser.id,
              email: freshUser.email,
              username: freshUser.username,
              tier: freshUser.tier,
              subscriptionStatus: freshUser.subscriptionStatus,
              subscriptionId: freshUser.subscriptionId,
            };

            const token = generateToken(authUser);

            res.cookie('auth_token', token, {
              httpOnly: true,
              secure: process.env.NODE_ENV === 'production',
              sameSite: 'lax',
              maxAge: 7 * 24 * 60 * 60 * 1000,
            });

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

      res.cookie('auth_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });

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

      if (!userId || !tier) {
        return res.status(400).json({ error: 'userId and tier required' });
      }

      // For now, only allow users to update their own tier
      // In production, this should be restricted to admin/internal calls only
      if (req.user.id !== userId) {
        return res.status(403).json({ error: 'Can only update your own tier' });
      }

      if (!userId || !tier) {
        return res.status(400).json({ error: 'userId and tier required' });
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
}
