/**
 * Theme Provider
 * 
 * Provides centralized theme context and CSS variable injection for the design system.
 * All components should access theme values through this provider.
 * 
 * @module theme-provider
 * @validates Requirements 1.1 - Consistent design system with unified colors, typography, and spacing
 */

import React, { createContext, useContext, useEffect, useState, useMemo, useCallback } from 'react';
import { designTokens, colors, typography, spacing, borderRadius, shadows, transitions } from './design-tokens';
import { customAnimationCSS } from './interactive-feedback';

// ============================================================================
// Types
// ============================================================================

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeContextValue {
  /** Current theme mode */
  mode: ThemeMode;
  /** Resolved theme (light or dark) based on mode and system preference */
  resolvedTheme: 'light' | 'dark';
  /** Set the theme mode */
  setMode: (mode: ThemeMode) => void;
  /** Toggle between light and dark modes */
  toggleTheme: () => void;
  /** Access to design tokens */
  tokens: typeof designTokens;
  /** Get a CSS variable value */
  getCssVar: (name: string) => string;
  /** Check if using design tokens (for testing) */
  isUsingDesignTokens: boolean;
}

// ============================================================================
// Context
// ============================================================================

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

// ============================================================================
// CSS Variable Generation
// ============================================================================

/**
 * Generates CSS custom properties from design tokens
 */
function generateCssVariables(): Record<string, string> {
  const vars: Record<string, string> = {};
  
  // Color variables
  Object.entries(colors).forEach(([category, values]) => {
    if (typeof values === 'string') {
      vars[`--color-${category}`] = values;
    } else if (typeof values === 'object') {
      Object.entries(values).forEach(([shade, value]) => {
        if (shade === 'DEFAULT') {
          vars[`--color-${category}`] = value as string;
        } else {
          vars[`--color-${category}-${shade}`] = value as string;
        }
      });
    }
  });
  
  // Typography variables
  Object.entries(typography.fontSize).forEach(([size, value]) => {
    vars[`--font-size-${size}`] = value;
  });
  
  Object.entries(typography.fontWeight).forEach(([weight, value]) => {
    vars[`--font-weight-${weight}`] = value;
  });
  
  Object.entries(typography.lineHeight).forEach(([height, value]) => {
    vars[`--line-height-${height}`] = value;
  });
  
  Object.entries(typography.fontFamily).forEach(([family, value]) => {
    vars[`--font-family-${family}`] = value;
  });
  
  // Spacing variables
  Object.entries(spacing).forEach(([size, value]) => {
    vars[`--spacing-${size}`] = value;
  });
  
  // Border radius variables
  Object.entries(borderRadius).forEach(([size, value]) => {
    if (size === 'DEFAULT') {
      vars['--radius'] = value;
    } else {
      vars[`--radius-${size}`] = value;
    }
  });
  
  // Shadow variables
  Object.entries(shadows).forEach(([size, value]) => {
    if (size === 'DEFAULT') {
      vars['--shadow'] = value;
    } else {
      vars[`--shadow-${size}`] = value;
    }
  });
  
  // Transition variables
  Object.entries(transitions.duration).forEach(([speed, value]) => {
    vars[`--transition-${speed}`] = value;
  });
  
  return vars;
}

/**
 * Injects CSS variables into the document root
 */
function injectCssVariables(vars: Record<string, string>): void {
  const root = document.documentElement;
  Object.entries(vars).forEach(([name, value]) => {
    root.style.setProperty(name, value);
  });
}

// ============================================================================
// Provider Component
// ============================================================================

export interface ThemeProviderProps {
  children: React.ReactNode;
  /** Default theme mode */
  defaultMode?: ThemeMode;
  /** Storage key for persisting theme preference */
  storageKey?: string;
  /** Whether to inject CSS variables on mount */
  injectCssVars?: boolean;
}

export function ThemeProvider({
  children,
  defaultMode = 'dark',
  storageKey = 'metaextract-theme',
  injectCssVars = true,
}: ThemeProviderProps) {
  // Initialize mode from storage or default
  const [mode, setModeState] = useState<ThemeMode>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(storageKey);
      if (stored && ['light', 'dark', 'system'].includes(stored)) {
        return stored as ThemeMode;
      }
    }
    return defaultMode;
  });
  
  // Track system preference
  const [systemPreference, setSystemPreference] = useState<'light' | 'dark'>(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'dark';
  });
  
  // Resolve the actual theme based on mode
  const resolvedTheme = useMemo(() => {
    if (mode === 'system') {
      return systemPreference;
    }
    return mode;
  }, [mode, systemPreference]);
  
  // Listen for system preference changes
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      setSystemPreference(e.matches ? 'dark' : 'light');
    };
    
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  // Inject CSS variables on mount
  useEffect(() => {
    if (injectCssVars && typeof window !== 'undefined') {
      const vars = generateCssVariables();
      injectCssVariables(vars);

      // Inject custom animation CSS
      const styleId = 'metaextract-animations';
      if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = customAnimationCSS;
        document.head.appendChild(style);
      }

      // Add theme transition styles
      const transitionStyleId = 'theme-transitions';
      if (!document.getElementById(transitionStyleId)) {
        const transitionStyle = document.createElement('style');
        transitionStyle.id = transitionStyleId;
        transitionStyle.textContent = `
          :root {
            color-scheme: light dark;
            transition: background-color ${transitions.duration.slow} ${transitions.timing.ease}, color ${transitions.duration.slow} ${transitions.timing.ease}, border-color ${transitions.duration.slow} ${transitions.timing.ease};
          }

          * {
            transition: background-color ${transitions.duration.slow} ${transitions.timing.ease}, color ${transitions.duration.slow} ${transitions.timing.ease}, border-color ${transitions.duration.slow} ${transitions.timing.ease}, fill ${transitions.duration.slow} ${transitions.timing.ease}, stroke ${transitions.duration.slow} ${transitions.timing.ease};
          }

          /* Optimize performance for transitions */
          * {
            will-change: background-color, color, border-color;
          }

          /* Smooth transitions for theme changes */
          html,
          body,
          .light,
          .dark {
            transition: background-color ${transitions.duration.slow} ${transitions.timing.ease}, color ${transitions.duration.slow} ${transitions.timing.ease}, border-color ${transitions.duration.slow} ${transitions.timing.ease};
          }
        `;
        document.head.appendChild(transitionStyle);
      }
    }
  }, [injectCssVars]);
  
  // Update document class for theme
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(resolvedTheme);
  }, [resolvedTheme]);
  
  // Persist mode to storage
  const setMode = useCallback((newMode: ThemeMode) => {
    setModeState(newMode);
    if (typeof window !== 'undefined') {
      localStorage.setItem(storageKey, newMode);
    }
  }, [storageKey]);
  
  // Toggle between light and dark
  const toggleTheme = useCallback(() => {
    setMode(resolvedTheme === 'dark' ? 'light' : 'dark');
  }, [resolvedTheme, setMode]);
  
  // Get CSS variable value
  const getCssVar = useCallback((name: string): string => {
    if (typeof window === 'undefined') return '';
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }, []);
  
  const value = useMemo<ThemeContextValue>(() => ({
    mode,
    resolvedTheme,
    setMode,
    toggleTheme,
    tokens: designTokens,
    getCssVar,
    isUsingDesignTokens: true,
  }), [mode, resolvedTheme, setMode, toggleTheme, getCssVar]);
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access theme context
 * @throws Error if used outside ThemeProvider
 */
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Hook to access design tokens directly
 */
export function useDesignTokens() {
  const { tokens } = useTheme();
  return tokens;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get a CSS variable reference string
 */
export function cssVar(name: string): string {
  return `var(--${name})`;
}

/**
 * Get a color token as CSS variable
 */
export function colorVar(color: string, shade?: string | number): string {
  if (shade !== undefined) {
    return `var(--color-${color}-${shade})`;
  }
  return `var(--color-${color})`;
}

/**
 * Get a spacing token as CSS variable
 */
export function spacingVar(size: keyof typeof spacing): string {
  return `var(--spacing-${size})`;
}

/**
 * Get a font size token as CSS variable
 */
export function fontSizeVar(size: keyof typeof typography.fontSize): string {
  return `var(--font-size-${size})`;
}

/**
 * Get a border radius token as CSS variable
 */
export function radiusVar(size?: keyof typeof borderRadius): string {
  if (size && size !== 'DEFAULT') {
    return `var(--radius-${size})`;
  }
  return 'var(--radius)';
}

/**
 * Get a shadow token as CSS variable
 */
export function shadowVar(size?: keyof typeof shadows): string {
  if (size && size !== 'DEFAULT') {
    return `var(--shadow-${size})`;
  }
  return 'var(--shadow)';
}

// Export CSS variable generation for testing
export { generateCssVariables };

export default ThemeProvider;
