/**
 * Mock Authentication System for Development
 * 
 * Provides full authentication functionality without requiring a database.
 * Used when DATABASE_URL is not configured.
 */

import type { Express, Request, Response, NextFunction } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { z } from "zod";

// ============================================================================
// Configuration
// ============================================================================

const JWT_SECRET = process.env.SESSION_SECRET || "metaextract-dev-secret-change-in-production";
const JWT_EXPIRES_IN = "7d";
const SALT_ROUNDS = 12;

// ============================================================================
// In-Memory Storage
// ============================================================================

interface MockUser {
  id: string;
  email: string;
  username: string;
  password: string;
  tier: string;
  subscriptionStatus: string;
  subscriptionId: string | null;
  createdAt: Date;
}

const mockUsers: Map<string, MockUser> = new Map();
const mockUsersByEmail: Map<string, MockUser> = new Map();
const mockUsersByUsername: Map<string, MockUser> = new Map();

// Pre-populate with test users
const testUsers = [
  {
    id: "test-user-1",
    email: "test@metaextract.com",
    username: "testuser",
    password: "testpassword123",
    tier: "professional",
    subscriptionStatus: "active"
  },
  {
    id: "test-user-2", 
    email: "admin@metaextract.com",
    username: "admin",
    password: "adminpassword123",
    tier: "enterprise",
    subscriptionStatus: "active"
  },
  {
    id: "test-user-3",
    email: "forensic@metaextract.com", 
    username: "forensic",
    password: "forensicpassword123",
    tier: "forensic",
    subscriptionStatus: "active"
  }
];

// Initialize test users
async function initializeTestUsers() {
  for (const user of testUsers) {
    const hashedPassword = await bcrypt.hash(user.password, SALT_ROUNDS);
    const mockUser: MockUser = {
      ...user,
      password: hashedPassword,
      subscriptionId: null,
      createdAt: new Date()
    };
    
    mockUsers.set(user.id, mockUser);
    mockUsersByEmail.set(user.email, mockUser);
    mockUsersByUsername.set(user.username, mockUser);
  }
}

// Initialize on module load
initializeTestUsers();

// ============================================================================
// Types (same as main auth system)
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
  email: z.string().email("Invalid email address"),
  username: z.string().min(3, "Username must be at least 3 characters").max(50),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
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

function generateId(): string {
  return `mock-user-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

// ============================================================================
// Middleware (same as main auth system)
// ============================================================================

export function authMiddleware(req: AuthRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  const cookieToken = req.cookies?.auth_token;
  
  const token = authHeader?.startsWith("Bearer ") 
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

export function requireAuth(req: AuthRequest, res: Response, next: NextFunction) {
  if (!req.isAuthenticated || !req.user) {
    return res.status(401).json({ 
      error: "Authentication required",
      code: "AUTH_REQUIRED"
    });
  }
  next();
}

export function requireTier(...allowedTiers: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ 
        error: "Authentication required",
        code: "AUTH_REQUIRED"
      });
    }
    
    if (!allowedTiers.includes(req.user.tier)) {
      return res.status(403).json({
        error: "Upgrade required",
        code: "TIER_UPGRADE_REQUIRED",
        current_tier: req.user.tier,
        required_tiers: allowedTiers,
      });
    }
    
    next();
  };
}

export function getEffectiveTier(req: AuthRequest): string {
  if (req.user && req.user.subscriptionStatus === "active") {
    return req.user.tier;
  }
  return "enterprise";
}

// ============================================================================
// Route Handlers
// ============================================================================

export function registerMockAuthRoutes(app: Express) {
  
  // -------------------------------------------------------------------------
  // Register
  // -------------------------------------------------------------------------
  app.post("/api/auth/register", async (req: Request, res: Response) => {
    try {
      // Validate input
      const validation = registerSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({
          error: "Validation failed",
          details: validation.error.flatten().fieldErrors,
        });
      }
      
      const { email, username, password } = validation.data;
      
      // Check if email already exists
      if (mockUsersByEmail.has(email)) {
        return res.status(409).json({
          error: "Email already registered",
          code: "EMAIL_EXISTS"
        });
      }
      
      // Check if username already exists
      if (mockUsersByUsername.has(username)) {
        return res.status(409).json({
          error: "Username already taken",
          code: "USERNAME_EXISTS"
        });
      }
      
      // Hash password
      const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
      
      // Create user
      const newUser: MockUser = {
        id: generateId(),
        email,
        username,
        password: hashedPassword,
        tier: "professional", // Default tier for new users
        subscriptionStatus: "active",
        subscriptionId: null,
        createdAt: new Date()
      };
      
      // Store user
      mockUsers.set(newUser.id, newUser);
      mockUsersByEmail.set(email, newUser);
      mockUsersByUsername.set(username, newUser);
      
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
      res.cookie("auth_token", token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
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
      console.error("Mock registration error:", error);
      res.status(500).json({
        error: "Registration failed",
        message: error instanceof Error ? error.message : "Unknown error"
      });
    }
  });
  
  // -------------------------------------------------------------------------
  // Login
  // -------------------------------------------------------------------------
  app.post("/api/auth/login", async (req: Request, res: Response) => {
    try {
      // Validate input
      const validation = loginSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({
          error: "Validation failed",
          details: validation.error.flatten().fieldErrors,
        });
      }
      
      const { email, password } = validation.data;
      
      // Find user
      const user = mockUsersByEmail.get(email);
      
      if (!user) {
        return res.status(401).json({
          error: "Invalid credentials",
          code: "INVALID_CREDENTIALS"
        });
      }
      
      // Verify password
      const isValid = await bcrypt.compare(password, user.password);
      if (!isValid) {
        return res.status(401).json({
          error: "Invalid credentials",
          code: "INVALID_CREDENTIALS"
        });
      }
      
      // Generate token
      const authUser: AuthUser = {
        id: user.id,
        email: user.email,
        username: user.username,
        tier: user.tier,
        subscriptionStatus: user.subscriptionStatus,
        subscriptionId: user.subscriptionId,
      };
      
      const token = generateToken(authUser);
      
      // Set cookie
      res.cookie("auth_token", token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      });
      
      res.json({
        success: true,
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          tier: user.tier,
          subscriptionStatus: user.subscriptionStatus,
        },
        token,
      });
      
    } catch (error) {
      console.error("Mock login error:", error);
      res.status(500).json({
        error: "Login failed",
        message: error instanceof Error ? error.message : "Unknown error"
      });
    }
  });
  
  // -------------------------------------------------------------------------
  // Logout
  // -------------------------------------------------------------------------
  app.post("/api/auth/logout", (req: Request, res: Response) => {
    res.clearCookie("auth_token");
    res.json({ success: true, message: "Logged out" });
  });
  
  // -------------------------------------------------------------------------
  // Get Current User
  // -------------------------------------------------------------------------
  app.get("/api/auth/me", authMiddleware, async (req: AuthRequest, res: Response) => {
    if (!req.isAuthenticated || !req.user) {
      return res.json({ 
        authenticated: false,
        user: null 
      });
    }
    
    // Get fresh user data
    const user = mockUsers.get(req.user.id);
    if (!user) {
      return res.json({ 
        authenticated: false,
        user: null 
      });
    }
    
    res.json({
      authenticated: true,
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        tier: user.tier,
        subscriptionStatus: user.subscriptionStatus,
      }
    });
  });
  
  // -------------------------------------------------------------------------
  // Refresh Token
  // -------------------------------------------------------------------------
  app.post("/api/auth/refresh", authMiddleware, async (req: AuthRequest, res: Response) => {
    if (!req.isAuthenticated || !req.user) {
      return res.status(401).json({
        error: "Not authenticated",
        code: "NOT_AUTHENTICATED"
      });
    }
    
    // Get fresh user data
    const user = mockUsers.get(req.user.id);
    if (!user) {
      return res.status(401).json({
        error: "User not found",
        code: "USER_NOT_FOUND"
      });
    }
    
    const authUser: AuthUser = {
      id: user.id,
      email: user.email,
      username: user.username,
      tier: user.tier,
      subscriptionStatus: user.subscriptionStatus,
      subscriptionId: user.subscriptionId,
    };
    
    const token = generateToken(authUser);
    
    res.cookie("auth_token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });
    
    res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        tier: user.tier,
        subscriptionStatus: user.subscriptionStatus,
      },
      token,
    });
  });
  
  // -------------------------------------------------------------------------
  // Update User Tier (Mock)
  // -------------------------------------------------------------------------
  app.post("/api/auth/update-tier", async (req: Request, res: Response) => {
    const { userId, tier, subscriptionId, subscriptionStatus } = req.body;
    
    if (!userId || !tier) {
      return res.status(400).json({ error: "userId and tier required" });
    }
    
    const user = mockUsers.get(userId);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    
    // Update user
    user.tier = tier;
    user.subscriptionId = subscriptionId || null;
    user.subscriptionStatus = subscriptionStatus || "active";
    
    res.json({ success: true });
  });
  
  // -------------------------------------------------------------------------
  // Development Helper: List All Users
  // -------------------------------------------------------------------------
  app.get("/api/auth/dev/users", (req: Request, res: Response) => {
    if (process.env.NODE_ENV === "production") {
      return res.status(404).json({ error: "Not found" });
    }
    
    const users = Array.from(mockUsers.values()).map(user => ({
      id: user.id,
      email: user.email,
      username: user.username,
      tier: user.tier,
      subscriptionStatus: user.subscriptionStatus,
      createdAt: user.createdAt
    }));
    
    res.json({ users });
  });
}

// ============================================================================
// Export Test Credentials
// ============================================================================

export const TEST_CREDENTIALS = {
  professional: {
    email: "test@metaextract.com",
    password: "testpassword123",
    tier: "professional"
  },
  enterprise: {
    email: "admin@metaextract.com", 
    password: "adminpassword123",
    tier: "enterprise"
  },
  forensic: {
    email: "forensic@metaextract.com",
    password: "forensicpassword123", 
    tier: "forensic"
  }
};