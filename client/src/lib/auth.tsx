/**
 * MetaExtract Auth Context
 *
 * Provides authentication state and methods throughout the app.
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from 'react';

export interface User {
  id: string;
  email: string;
  username: string;
  tier: string;
  subscriptionStatus: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  register: (
    email: string,
    username: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

const parseJsonSafe = async (response: Response) => {
  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    return null;
  }
  try {
    return await response.json();
  } catch {
    return null;
  }
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check auth status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include',
      });
      const data = await parseJsonSafe(response);

      if (data && (data as any).authenticated && (data as any).user) {
        setUser((data as any).user);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const tierOverride = localStorage.getItem('metaextract_tier_override');
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          ...(tierOverride ? { tier: tierOverride } : {}),
        }),
      });

      const data = await parseJsonSafe(response);

      if (!response.ok) {
        return {
          success: false,
          error: (data && (data as any).error) || 'Login failed',
        };
      }

      if (data && (data as any).user) {
        setUser((data as any).user);
      }

      // Store token in localStorage for API calls
      if (data && (data as any).token) {
        localStorage.setItem('auth_token', (data as any).token);
      }

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: 'Network error. Please try again.',
      };
    }
  };

  const register = async (
    email: string,
    username: string,
    password: string
  ) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, username, password }),
      });

      const data = await parseJsonSafe(response);

      if (!response.ok) {
        // Handle validation errors
        if (data && (data as any).details) {
          const firstError = Object.values((data as any).details).flat()[0];
          return {
            success: false,
            error: (firstError as string) || (data as any).error,
          };
        }
        return {
          success: false,
          error: (data && (data as any).error) || 'Registration failed',
        };
      }

      if (data && (data as any).user) {
        setUser((data as any).user);
      }

      if (data && (data as any).token) {
        localStorage.setItem('auth_token', (data as any).token);
      }

      return { success: true };
    } catch (error) {
      console.error('Register error:', error);
      return {
        success: false,
        error: 'Network error. Please try again.',
      };
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('auth_token');
    }
  };

  const refreshUser = useCallback(async () => {
    await checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Get the user's effective tier for feature gating
 */
export function useEffectiveTier(): string {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return 'free';
  }

  // Only count subscription as active if status is "active"
  if (user.subscriptionStatus === 'active') {
    return user.tier;
  }

  return 'enterprise';
}

/**
 * Check if user can access a specific tier's features
 */
export function useCanAccessTier(requiredTier: string): boolean {
  const effectiveTier = useEffectiveTier();

  const tierOrder = ['free', 'professional', 'forensic', 'enterprise'];
  const currentIndex = tierOrder.indexOf(effectiveTier);
  const requiredIndex = tierOrder.indexOf(requiredTier);

  return currentIndex >= requiredIndex;
}
