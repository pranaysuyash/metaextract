/**
 * Authentication System Tests for MetaExtract
 * 
 * Comprehensive tests for the enhanced authentication system
 */

import { describe, it, expect, beforeEach, afterEach, vi, MockedFunction } from 'vitest';
import express, { Request, Response } from 'express';
import request from 'supertest';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { storage } from '../storage';
import {
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
  AUTH_CONFIG,
  validatePasswordStrength,
  hashPassword,
  verifyPassword,
  signAccessToken,
  signRefreshToken,
  verifyAccessToken,
  verifyRefreshToken,
  generateSecureToken,
  AuthRequest
} from '../auth-enhanced';

// Mock the storage module
vi.mock('../storage', () => ({
  storage: {
    getUserByEmail: vi.fn(),
    getUserById: vi.fn(),
    createUser: vi.fn(),
    getOrCreateCreditBalance: vi.fn(),
    resetFailedLoginAttempts: vi.fn(),
    enableTwoFactor: vi.fn(),
    disableTwoFactor: vi.fn(),
    setPasswordResetToken: vi.fn(),
    getUserByResetToken: vi.fn(),
    updateUserPassword: vi.fn(),
    updateUserProfile: vi.fn(),
    recordCreditTransaction: vi.fn(),
  }
}));

describe('Authentication System', () => {
  let app: express.Application;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    
    // Mock console to suppress logs during tests
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Password Validation', () => {
    it('should validate strong passwords', () => {
      const result = validatePasswordStrength('ValidPass123!');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject weak passwords', () => {
      const result = validatePasswordStrength('weak');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters long');
    });

    it('should enforce uppercase requirement', () => {
      const result = validatePasswordStrength('lowercase123!');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one uppercase letter');
    });
  });

  describe('Password Hashing', () => {
    it('should hash passwords correctly', async () => {
      const password = 'testPassword123!';
      const hashed = await hashPassword(password);
      
      expect(hashed).toBeDefined();
      expect(hashed).not.toBe(password);
      expect(await verifyPassword(password, hashed)).toBe(true);
    });

    it('should verify passwords correctly', async () => {
      const password = 'testPassword123!';
      const wrongPassword = 'wrongPassword';
      const hashed = await hashPassword(password);
      
      expect(await verifyPassword(password, hashed)).toBe(true);
      expect(await verifyPassword(wrongPassword, hashed)).toBe(false);
    });
  });

  describe('JWT Token Functions', () => {
    it('should sign and verify access tokens', () => {
      const payload = { userId: '123', email: 'test@example.com' };
      const token = signAccessToken(payload);
      const decoded = verifyAccessToken(token);
      
      expect(decoded).toBeDefined();
      expect(decoded!.userId).toBe(payload.userId);
      expect(decoded!.email).toBe(payload.email);
    });

    it('should sign and verify refresh tokens', () => {
      const payload = { tokenId: 'abc123', userId: '123' };
      const token = signRefreshToken(payload);
      const decoded = verifyRefreshToken(token);
      
      expect(decoded).toBeDefined();
      expect(decoded!.tokenId).toBe(payload.tokenId);
      expect(decoded!.userId).toBe(payload.userId);
    });

    it('should return null for invalid tokens', () => {
      const invalidToken = 'invalid.token.here';
      const decoded = verifyAccessToken(invalidToken);
      const decodedRefresh = verifyRefreshToken(invalidToken);
      
      expect(decoded).toBeNull();
      expect(decodedRefresh).toBeNull();
    });
  });

  describe('Registration', () => {
    it('should register a new user successfully', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        password: 'hashedPassword',
        firstName: 'Test',
        lastName: 'User',
        emailVerified: false,
        twoFactorEnabled: false,
        twoFactorSecret: null,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserByEmail).mockResolvedValue(null);
      vi.mocked(storage.createUser).mockResolvedValue(mockUser);
      vi.mocked(storage.getOrCreateCreditBalance).mockResolvedValue({ id: 'balance123', userId: '123', credits: 0 });

      const response = await request(app)
        .post('/register')
        .send({
          email: 'test@example.com',
          password: 'ValidPass123!',
          firstName: 'Test',
          lastName: 'User'
        })
        .expect(201);

      expect(response.body.message).toBe('User registered successfully');
      expect(response.body.user.email).toBe('test@example.com');
      expect(response.body.accessToken).toBeDefined();
    });

    it('should reject registration with existing email', async () => {
      const existingUser = { id: '123', email: 'test@example.com', password: 'hashed' };
      vi.mocked(storage.getUserByEmail).mockResolvedValue(existingUser);

      const response = await request(app)
        .post('/register')
        .send({
          email: 'test@example.com',
          password: 'ValidPass123!'
        })
        .expect(409);

      expect(response.body.error).toBe('User with this email already exists');
    });

    it('should reject registration with weak password', async () => {
      const response = await request(app)
        .post('/register')
        .send({
          email: 'test@example.com',
          password: 'weak'
        })
        .expect(400);

      expect(response.body.error).toBe('Password validation failed');
    });
  });

  describe('Login', () => {
    it('should login user with valid credentials', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        password: await hashPassword('ValidPass123!'),
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        twoFactorSecret: null,
        failedLoginAttempts: 0,
        lastFailedLoginAttempt: null,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserByEmail).mockResolvedValue(mockUser);

      const response = await request(app)
        .post('/login')
        .send({
          email: 'test@example.com',
          password: 'ValidPass123!'
        })
        .expect(200);

      expect(response.body.message).toBe('Login successful');
      expect(response.body.user.email).toBe('test@example.com');
      expect(response.body.accessToken).toBeDefined();
    });

    it('should reject login with invalid credentials', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        password: await hashPassword('ValidPass123!'),
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        twoFactorSecret: null,
        failedLoginAttempts: 0,
        lastFailedLoginAttempt: null,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserByEmail).mockResolvedValue(mockUser);

      const response = await request(app)
        .post('/login')
        .send({
          email: 'test@example.com',
          password: 'WrongPassword!'
        })
        .expect(401);

      expect(response.body.error).toBe('Invalid credentials');
    });

    it('should require 2FA if enabled', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        password: await hashPassword('ValidPass123!'),
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: true,
        twoFactorSecret: 'someSecret',
        failedLoginAttempts: 0,
        lastFailedLoginAttempt: null,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserByEmail).mockResolvedValue(mockUser);

      const response = await request(app)
        .post('/login')
        .send({
          email: 'test@example.com',
          password: 'ValidPass123!'
        })
        .expect(401);

      expect(response.body.error).toBe('Two-factor authentication required');
      expect(response.body.twoFactorRequired).toBe(true);
    });
  });

  describe('Password Reset', () => {
    it('should request password reset successfully', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        password: 'hashed',
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        twoFactorSecret: null,
        resetToken: null,
        resetTokenExpiry: null,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserByEmail).mockResolvedValue(mockUser);
      vi.mocked(storage.setPasswordResetToken).mockResolvedValue(undefined);

      const response = await request(app)
        .post('/password/reset/request')
        .send({ email: 'test@example.com' })
        .expect(200);

      expect(response.body.message).toBe('If an account exists with this email, a reset link has been sent');
    });

    it('should reset password with valid token', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        password: 'oldHashedPassword',
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        twoFactorSecret: null,
        resetToken: 'validToken',
        resetTokenExpiry: new Date(Date.now() + 10000), // Not expired
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserByResetToken).mockResolvedValue(mockUser);
      vi.mocked(storage.updateUserPassword).mockResolvedValue(undefined);

      const response = await request(app)
        .post('/password/reset')
        .send({
          token: 'validToken',
          newPassword: 'NewValidPass123!'
        })
        .expect(200);

      expect(response.body.message).toBe('Password reset successfully');
    });

    it('should reject reset with invalid token', async () => {
      vi.mocked(storage.getUserByResetToken).mockResolvedValue(null);

      const response = await request(app)
        .post('/password/reset')
        .send({
          token: 'invalidToken',
          newPassword: 'NewValidPass123!'
        })
        .expect(400);

      expect(response.body.error).toBe('Invalid or expired reset token');
    });
  });

  describe('Profile Management', () => {
    it('should get user profile', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      // Create a mock request with user attached
      const mockReq = {
        user: mockUser
      } as AuthRequest;

      const mockRes = {
        json: vi.fn(),
        status: vi.fn().mockReturnThis()
      } as unknown as Response;

      await getProfile(mockReq, mockRes);

      expect(mockRes.json).toHaveBeenCalledWith({
        id: mockUser.id,
        email: mockUser.email,
        firstName: mockUser.firstName,
        lastName: mockUser.lastName,
        emailVerified: mockUser.emailVerified,
        twoFactorEnabled: mockUser.twoFactorEnabled,
        createdAt: mockUser.createdAt,
        updatedAt: mockUser.updatedAt,
      });
    });

    it('should update user profile', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const updatedUser = {
        ...mockUser,
        firstName: 'Updated',
        lastName: 'Name',
      };

      vi.mocked(storage.updateUserProfile).mockResolvedValue(updatedUser);

      const mockReq = {
        user: mockUser,
        body: {
          firstName: 'Updated',
          lastName: 'Name'
        }
      } as AuthRequest;

      const mockRes = {
        json: vi.fn(),
        status: vi.fn().mockReturnThis()
      } as unknown as Response;

      await updateProfile(mockReq, mockRes);

      expect(mockRes.json).toHaveBeenCalledWith({
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
    });
  });

  describe('Utility Functions', () => {
    it('should generate secure tokens', () => {
      const token1 = generateSecureToken(16);
      const token2 = generateSecureToken(16);

      expect(token1).toBeDefined();
      expect(token2).toBeDefined();
      expect(token1).not.toBe(token2);
      expect(token1.length).toBe(32); // 16 bytes = 32 hex chars
    });
  });
});

// Additional tests for middleware functions
describe('Authentication Middleware', () => {
  let app: express.Application;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    
    // Mock console to suppress logs during tests
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('authenticateToken', () => {
    it('should authenticate with valid token', async () => {
      const validToken = jwt.sign(
        { userId: '123', email: 'test@example.com' },
        AUTH_CONFIG.jwtSecret,
        { expiresIn: AUTH_CONFIG.jwtExpiration }
      );

      const mockUser = {
        id: '123',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        emailVerified: true,
        twoFactorEnabled: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(storage.getUserById).mockResolvedValue(mockUser);

      const mockReq = {
        headers: { authorization: `Bearer ${validToken}` },
      } as Request;

      const mockRes = {
        json: vi.fn(),
        status: vi.fn().mockReturnThis()
      } as unknown as Response;

      const next = vi.fn();

      await authenticateToken(mockReq as AuthRequest, mockRes, next);

      expect(next).toHaveBeenCalled();
      expect((mockReq as AuthRequest).user).toEqual(mockUser);
    });

    it('should reject with invalid token', async () => {
      const mockReq = {
        headers: { authorization: 'Bearer invalidToken' },
      } as Request;

      const mockRes = {
        json: vi.fn(),
        status: vi.fn().mockReturnThis()
      } as unknown as Response;

      const next = vi.fn();

      await authenticateToken(mockReq as AuthRequest, mockRes, next);

      expect(mockRes.status).toHaveBeenCalledWith(403);
      expect(mockRes.json).toHaveBeenCalledWith({ error: 'Invalid or expired access token' });
      expect(next).not.toHaveBeenCalled();
    });

    it('should reject with missing token', async () => {
      const mockReq = {
        headers: {},
      } as Request;

      const mockRes = {
        json: vi.fn(),
        status: vi.fn().mockReturnThis()
      } as unknown as Response;

      const next = vi.fn();

      await authenticateToken(mockReq as AuthRequest, mockRes, next);

      expect(mockRes.status).toHaveBeenCalledWith(401);
      expect(mockRes.json).toHaveBeenCalledWith({ error: 'Access token required' });
      expect(next).not.toHaveBeenCalled();
    });
  });
});