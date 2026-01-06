/**
 * Enhanced Authentication System for MetaExtract API
 * 
 * Implements security best practices including:
 * - Secure token handling with httpOnly cookies
 * - Rate limiting
 * - Password policies
 * - 2FA support
 * - Session management
 */

import express, { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import crypto from 'crypto';
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';
import rateLimit from 'express-rate-limit';
import validator from 'validator';
import { storage } from './storage';
import type { User } from './storage/types';

// ============================================================================
// Configuration
// ============================================================================

interface AuthConfig {
  jwtSecret: string;
  jwtRefreshSecret: string;
  jwtExpiration: string;
  refreshTokenExpiration: string;
  bcryptRounds: number;
  maxLoginAttempts: number;
  lockoutDuration: number;
  passwordMinLength: number;
  requireUppercase: boolean;
  requireLowercase: boolean;
  requireNumbers: boolean;
  requireSymbols: boolean;
}

export const AUTH_CONFIG: AuthConfig = {
  jwtSecret: process.env.JWT_SECRET || 'fallback_jwt_secret_for_development',
  jwtRefreshSecret: process.env.JWT_REFRESH_SECRET || 'fallback_refresh_secret_for_development',
  jwtExpiration: process.env.JWT_EXPIRATION || '15m', // 15 minutes
  refreshTokenExpiration: process.env.JWT_REFRESH_EXPIRATION || '7d', // 7 days
  bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '12', 10),
  maxLoginAttempts: parseInt(process.env.MAX_LOGIN_ATTEMPTS || '5', 10),
  lockoutDuration: parseInt(process.env.LOCKOUT_DURATION || '900000', 10), // 15 minutes in ms
  passwordMinLength: parseInt(process.env.PASSWORD_MIN_LENGTH || '8', 10),
  requireUppercase: process.env.PASSWORD_REQUIRE_UPPERCASE === 'true',
  requireLowercase: process.env.PASSWORD_REQUIRE_LOWERCASE === 'true',
  requireNumbers: process.env.PASSWORD_REQUIRE_NUMBERS === 'true',
  requireSymbols: process.env.PASSWORD_REQUIRE_SYMBOLS === 'true',
};

// ============================================================================
// Types
// ============================================================================

export interface AuthRequest extends Request {
  user?: User;
}

export interface TokenPayload {
  userId: string;
  email: string;
  iat: number;
  exp: number;
}

export interface RefreshTokenPayload {
  tokenId: string;
  userId: string;
  iat: number;
  exp: number;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Validates password strength based on configuration
 */
export function validatePasswordStrength(password: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (password.length < AUTH_CONFIG.passwordMinLength) {
    errors.push(`Password must be at least ${AUTH_CONFIG.passwordMinLength} characters long`);
  }

  if (AUTH_CONFIG.requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (AUTH_CONFIG.requireLowercase && !/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (AUTH_CONFIG.requireNumbers && !/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  if (AUTH_CONFIG.requireSymbols && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Generates a secure random token
 */
export function generateSecureToken(length: number = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

/**
 * Hashes a password using bcrypt
 */
export async function hashPassword(password: string): Promise<string> {
  return await bcrypt.hash(password, AUTH_CONFIG.bcryptRounds);
}

/**
 * Verifies a password against a hash
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(password, hash);
}

/**
 * Signs a JWT access token
 */
export function signAccessToken(payload: Partial<TokenPayload>): string {
  return jwt.sign(payload, AUTH_CONFIG.jwtSecret, { expiresIn: AUTH_CONFIG.jwtExpiration });
}

/**
 * Signs a JWT refresh token
 */
export function signRefreshToken(payload: Partial<RefreshTokenPayload>): string {
  return jwt.sign(payload, AUTH_CONFIG.jwtRefreshSecret, { expiresIn: AUTH_CONFIG.refreshTokenExpiration });
}

/**
 * Verifies a JWT access token
 */
export function verifyAccessToken(token: string): TokenPayload | null {
  try {
    return jwt.verify(token, AUTH_CONFIG.jwtSecret) as TokenPayload;
  } catch (error) {
    console.error('Access token verification failed:', error);
    return null;
  }
}

/**
 * Verifies a JWT refresh token
 */
export function verifyRefreshToken(token: string): RefreshTokenPayload | null {
  try {
    return jwt.verify(token, AUTH_CONFIG.jwtRefreshSecret) as RefreshTokenPayload;
  } catch (error) {
    console.error('Refresh token verification failed:', error);
    return null;
  }
}

// ============================================================================
// Rate Limiting
// ============================================================================

/**
 * Login rate limiter to prevent brute force attacks
 */
export const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  message: {
    error: 'Too many login attempts, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * General API rate limiter
 */
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// ============================================================================
// Authentication Middleware
// ============================================================================

/**
 * Middleware to authenticate requests using JWT
 */
export async function authenticateToken(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    res.status(401).json({ error: 'Access token required' });
    return;
  }

  const decoded = verifyAccessToken(token);
  if (!decoded) {
    res.status(403).json({ error: 'Invalid or expired access token' });
    return;
  }

  try {
    // Verify user still exists in database
    const user = await storage.getUserById(decoded.userId);
    if (!user) {
      res.status(403).json({ error: 'User no longer exists' });
      return;
    }

    req.user = user;
    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(500).json({ error: 'Authentication error' });
  }
}

/**
 * Middleware to authenticate requests using refresh token
 */
export async function authenticateRefreshToken(req: Request, res: Response, next: NextFunction): Promise<void> {
  const token = req.cookies?.refreshToken || req.body.refreshToken;

  if (!token) {
    res.status(401).json({ error: 'Refresh token required' });
    return;
  }

  const decoded = verifyRefreshToken(token);
  if (!decoded) {
    res.status(403).json({ error: 'Invalid or expired refresh token' });
    return;
  }

  // In a real implementation, you'd verify the refresh token exists in the database
  // and hasn't been revoked. For now, we'll just pass through.
  (req as AuthRequest).user = { id: decoded.userId } as User; // Minimal user object
  next();
}

// ============================================================================
// Authentication Controllers
// ============================================================================

/**
 * Register a new user
 */
export async function register(req: Request, res: Response): Promise<void> {
  try {
    const { email, password, firstName, lastName } = req.body;

    // Validate input
    if (!email || !password) {
      res.status(400).json({ error: 'Email and password are required' });
      return;
    }

    if (!validator.isEmail(email)) {
      res.status(400).json({ error: 'Invalid email format' });
      return;
    }

    // Check if user already exists
    const existingUser = await storage.getUserByEmail(email);
    if (existingUser) {
      res.status(409).json({ error: 'User with this email already exists' });
      return;
    }

    // Validate password strength
    const passwordValidation = validatePasswordStrength(password);
    if (!passwordValidation.isValid) {
      res.status(400).json({ error: 'Password validation failed', details: passwordValidation.errors });
      return;
    }

    // Hash password
    const hashedPassword = await hashPassword(password);

    // Create user
    const newUser = await storage.createUser({
      email,
      password: hashedPassword,
      firstName: firstName || '',
      lastName: lastName || '',
      emailVerified: false,
      twoFactorEnabled: false,
      twoFactorSecret: null,
    });

    // Create initial credit balance (account-bound)
    await storage.getOrCreateCreditBalance(
      `credits:core:user:${newUser.id}`,
      newUser.id
    );

    // In a real implementation, you'd send a verification email here
    console.log(`Verification email would be sent to: ${email}`);

    // Generate tokens
    const accessToken = signAccessToken({ 
      userId: newUser.id, 
      email: newUser.email 
    });
    
    const refreshToken = signRefreshToken({ 
      tokenId: generateSecureToken(16), // In real implementation, store this in DB
      userId: newUser.id 
    });

    // Set refresh token as httpOnly cookie
    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production', // Use HTTPS in production
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      // Lax is required so refresh persists across external checkout redirects.
      sameSite: 'lax',
    });

    res.status(201).json({
      message: 'User registered successfully',
      user: {
        id: newUser.id,
        email: newUser.email,
        firstName: newUser.firstName,
        lastName: newUser.lastName,
        emailVerified: newUser.emailVerified,
      },
      accessToken, // Send access token in response body
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
}

/**
 * Login user
 */
export async function login(req: Request, res: Response): Promise<void> {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Email and password are required' });
      return;
    }

    // Get user from database
    const user = await storage.getUserByEmail(email);
    if (!user) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }

    // Verify password
    const isValidPassword = await verifyPassword(password, user.password);
    if (!isValidPassword) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }

    // Check if account is locked
    if (user.failedLoginAttempts >= AUTH_CONFIG.maxLoginAttempts) {
      const lockoutTime = new Date(user.lastFailedLoginAttempt!).getTime() + AUTH_CONFIG.lockoutDuration;
      if (Date.now() < lockoutTime) {
        const remainingTime = Math.ceil((lockoutTime - Date.now()) / 1000 / 60);
        res.status(423).json({ 
          error: 'Account temporarily locked due to multiple failed login attempts', 
          remainingMinutes: remainingTime 
        });
        return;
      } else {
        // Reset failed attempts after lockout period
        await storage.resetFailedLoginAttempts(user.id);
      }
    }

    // If user has 2FA enabled, verify the code
    if (user.twoFactorEnabled) {
      const twoFactorCode = req.body.twoFactorCode;
      if (!twoFactorCode) {
        res.status(401).json({ 
          error: 'Two-factor authentication required',
          twoFactorRequired: true 
        });
        return;
      }

      const verified = speakeasy.totp.verify({
        secret: user.twoFactorSecret!,
        encoding: 'base32',
        token: twoFactorCode,
        window: 2, // Allow 2 steps before or after
      });

      if (!verified) {
        res.status(401).json({ error: 'Invalid two-factor authentication code' });
        return;
      }
    }

    // Reset failed login attempts
    await storage.resetFailedLoginAttempts(user.id);

    // Generate tokens
    const accessToken = signAccessToken({ 
      userId: user.id, 
      email: user.email 
    });
    
    const refreshToken = signRefreshToken({ 
      tokenId: generateSecureToken(16), // In real implementation, store this in DB
      userId: user.id 
    });

    // Set refresh token as httpOnly cookie
    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production', // Use HTTPS in production
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      sameSite: 'lax',
    });

    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        emailVerified: user.emailVerified,
        twoFactorEnabled: user.twoFactorEnabled,
      },
      accessToken,
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
}

/**
 * Logout user
 */
export async function logout(req: AuthRequest, res: Response): Promise<void> {
  try {
    // In a real implementation, you'd invalidate the refresh token in the database
    // For now, we'll just clear the cookie
    res.clearCookie('refreshToken');
    
    res.json({ message: 'Logout successful' });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ error: 'Logout failed' });
  }
}

/**
 * Refresh access token using refresh token
 */
export async function refreshAccessToken(req: Request, res: Response): Promise<void> {
  try {
    const refreshToken = req.cookies?.refreshToken || req.body.refreshToken;

    if (!refreshToken) {
      res.status(401).json({ error: 'Refresh token required' });
      return;
    }

    const decoded = verifyRefreshToken(refreshToken);
    if (!decoded) {
      res.status(403).json({ error: 'Invalid or expired refresh token' });
      return;
    }

    // In a real implementation, you'd check if the refresh token exists in the database
    // and hasn't been revoked. For now, we'll proceed.

    // Get user to ensure they still exist
    const user = await storage.getUserById(decoded.userId);
    if (!user) {
      res.status(403).json({ error: 'User no longer exists' });
      return;
    }

    // Generate new access token
    const newAccessToken = signAccessToken({ 
      userId: user.id, 
      email: user.email 
    });

    res.json({
      accessToken: newAccessToken,
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({ error: 'Token refresh failed' });
  }
}

/**
 * Enable 2FA for user
 */
export async function enableTwoFactor(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    // Generate a new secret for 2FA
    const secret = speakeasy.generateSecret({
      name: `MetaExtract (${req.user.email})`,
      issuer: 'MetaExtract',
    });

    // In a real implementation, you'd temporarily store the secret in the database
    // and not finalize until the user verifies the code
    // For now, we'll just return the QR code data

    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url!);

    res.json({
      secret: secret.base32,
      qrCodeUrl,
      manualEntryKey: secret.ascii,
    });
  } catch (error) {
    console.error('Enable 2FA error:', error);
    res.status(500).json({ error: 'Failed to enable 2FA' });
  }
}

/**
 * Verify 2FA setup
 */
export async function verifyTwoFactorSetup(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    const { token, secret } = req.body;

    if (!token || !secret) {
      res.status(400).json({ error: 'Token and secret are required' });
      return;
    }

    // Verify the token against the secret
    const verified = speakeasy.totp.verify({
      secret: secret,
      encoding: 'base32',
      token: token,
      window: 2,
    });

    if (!verified) {
      res.status(400).json({ error: 'Invalid token' });
      return;
    }

    // Update user to enable 2FA
    await storage.enableTwoFactor(req.user.id, secret);

    res.json({
      message: 'Two-factor authentication enabled successfully',
      twoFactorEnabled: true,
    });
  } catch (error) {
    console.error('Verify 2FA setup error:', error);
    res.status(500).json({ error: 'Failed to verify 2FA setup' });
  }
}

/**
 * Disable 2FA for user
 */
export async function disableTwoFactor(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    await storage.disableTwoFactor(req.user.id);

    res.json({
      message: 'Two-factor authentication disabled successfully',
      twoFactorEnabled: false,
    });
  } catch (error) {
    console.error('Disable 2FA error:', error);
    res.status(500).json({ error: 'Failed to disable 2FA' });
  }
}

/**
 * Request password reset
 */
export async function requestPasswordReset(req: Request, res: Response): Promise<void> {
  try {
    const { email } = req.body;

    if (!email) {
      res.status(400).json({ error: 'Email is required' });
      return;
    }

    if (!validator.isEmail(email)) {
      res.status(400).json({ error: 'Invalid email format' });
      return;
    }

    // Get user from database
    const user = await storage.getUserByEmail(email);
    if (!user) {
      // Don't reveal if email exists to prevent enumeration
      res.json({ message: 'If an account exists with this email, a reset link has been sent' });
      return;
    }

    // Generate password reset token
    const resetToken = generateSecureToken(32);
    const resetTokenExpiry = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

    // Store reset token in database
    await storage.setPasswordResetToken(user.id, resetToken, resetTokenExpiry);

    // In a real implementation, you'd send an email with the reset link
    console.log(`Password reset email would be sent to: ${email} with token: ${resetToken}`);

    res.json({ message: 'If an account exists with this email, a reset link has been sent' });
  } catch (error) {
    console.error('Password reset request error:', error);
    res.status(500).json({ error: 'Password reset request failed' });
  }
}

/**
 * Reset password
 */
export async function resetPassword(req: Request, res: Response): Promise<void> {
  try {
    const { token, newPassword } = req.body;

    if (!token || !newPassword) {
      res.status(400).json({ error: 'Token and new password are required' });
      return;
    }

    // Validate password strength
    const passwordValidation = validatePasswordStrength(newPassword);
    if (!passwordValidation.isValid) {
      res.status(400).json({ error: 'Password validation failed', details: passwordValidation.errors });
      return;
    }

    // Get user by reset token
    const user = await storage.getUserByResetToken(token);
    if (!user) {
      res.status(400).json({ error: 'Invalid or expired reset token' });
      return;
    }

    // Check if token is expired
    if (user.resetTokenExpiry && user.resetTokenExpiry < new Date()) {
      res.status(400).json({ error: 'Reset token has expired' });
      return;
    }

    // Hash new password
    const hashedPassword = await hashPassword(newPassword);

    // Update user password and clear reset token
    await storage.updateUserPassword(user.id, hashedPassword);

    // In a real implementation, you'd invalidate all sessions for this user
    // For now, we'll just log that this would happen

    res.json({ message: 'Password reset successfully' });
  } catch (error) {
    console.error('Password reset error:', error);
    res.status(500).json({ error: 'Password reset failed' });
  }
}

/**
 * Change user password
 */
export async function changePassword(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      res.status(400).json({ error: 'Current password and new password are required' });
      return;
    }

    // Validate new password strength
    const passwordValidation = validatePasswordStrength(newPassword);
    if (!passwordValidation.isValid) {
      res.status(400).json({ error: 'New password does not meet requirements', details: passwordValidation.errors });
      return;
    }

    // Get user to verify current password
    const user = await storage.getUserById(req.user.id);
    if (!user) {
      res.status(404).json({ error: 'User not found' });
      return;
    }

    // Verify current password
    const isValidPassword = await verifyPassword(currentPassword, user.password);
    if (!isValidPassword) {
      res.status(401).json({ error: 'Current password is incorrect' });
      return;
    }

    // Hash new password
    const hashedNewPassword = await hashPassword(newPassword);

    // Update password
    await storage.updateUserPassword(user.id, hashedNewPassword);

    res.json({ message: 'Password changed successfully' });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({ error: 'Password change failed' });
  }
}

/**
 * Get current user profile
 */
export async function getProfile(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    // Get user with sensitive data removed
    const user = await storage.getUserById(req.user.id);
    if (!user) {
      res.status(404).json({ error: 'User not found' });
      return;
    }

    res.json({
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      emailVerified: user.emailVerified,
      twoFactorEnabled: user.twoFactorEnabled,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ error: 'Failed to get profile' });
  }
}

/**
 * Update user profile
 */
export async function updateProfile(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    const { firstName, lastName } = req.body;

    // Validate input
    if (firstName !== undefined && typeof firstName !== 'string') {
      res.status(400).json({ error: 'First name must be a string' });
      return;
    }

    if (lastName !== undefined && typeof lastName !== 'string') {
      res.status(400).json({ error: 'Last name must be a string' });
      return;
    }

    // Update user profile
    const updatedUser = await storage.updateUserProfile(req.user.id, {
      firstName: firstName !== undefined ? firstName : undefined,
      lastName: lastName !== undefined ? lastName : undefined,
    });

    res.json({
      message: 'Profile updated successfully',
      user: {
        id: updatedUser.id,
        email: updatedUser.email,
        firstName: updatedUser.firstName,
        lastName: updatedUser.lastName,
        emailVerified: updatedUser.emailVerified,
        twoFactorEnabled: updatedUser.twoFactorEnabled,
      },
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({ error: 'Profile update failed' });
  }
}

// Export the enhanced auth system
export default {
  authenticateToken,
  authenticateRefreshToken,
  register,
  login,
  logout,
  refreshAccessToken,
  enableTwoFactor,
  verifyTwoFactorSetup,
  disableTwoFactor,
  requestPasswordReset,
  resetPassword,
  changePassword,
  getProfile,
  updateProfile,
  loginLimiter,
  apiLimiter,
};
