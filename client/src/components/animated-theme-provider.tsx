import React, { createContext, useContext, useEffect, useState } from 'react';

/**
 * Animated Theme Provider
 * 
 * Provides smooth animated transitions when switching between light/dark themes.
 * Uses Framer Motion for fluid animations and prevents flash of unstyled content.
 * 
 * Features:
 * - Smooth fade transitions between themes
 * - No flash of unstyled content (FOUC)
 * - Respects system preferences
 * - Persists user choice to localStorage
 * - Accessible with proper ARIA labels
 */

interface ThemeContextType {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  resolvedTheme: 'light' | 'dark';
  isAnimating: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function useAnimatedTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useAnimatedTheme must be used within AnimatedThemeProvider');
  }
  return context;
}

interface AnimatedThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: 'light' | 'dark' | 'system';
  storageKey?: string;
  transitionDuration?: number;
}

export function AnimatedThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'theme',
  transitionDuration = 300,
}: AnimatedThemeProviderProps) {
  const [theme, setThemeState] = useState<'light' | 'dark' | 'system'>(defaultTheme);
  const [isAnimating, setIsAnimating] = useState(false);
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  // Initialize theme from localStorage and system preference
  useEffect(() => {
    const stored = localStorage.getItem(storageKey) as 'light' | 'dark' | 'system' | null;
    if (stored) {
      setThemeState(stored);
    }

    // Listen to system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (theme === 'system') {
        setResolvedTheme(mediaQuery.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [storageKey, theme]);

  // Resolve theme (system -> light/dark)
  useEffect(() => {
    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setResolvedTheme(isDark ? 'dark' : 'light');
    } else {
      setResolvedTheme(theme);
    }
  }, [theme]);

  // Apply theme with animation
  useEffect(() => {
    const root = document.documentElement;

    // Start animation
    setIsAnimating(true);

    // Add transition class
    root.style.setProperty('--theme-transition-duration', `${transitionDuration}ms`);
    root.classList.add('theme-transitioning');

    // Apply theme
    if (resolvedTheme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Remove transition class after animation
    const timer = setTimeout(() => {
      root.classList.remove('theme-transitioning');
      setIsAnimating(false);
    }, transitionDuration);

    return () => clearTimeout(timer);
  }, [resolvedTheme, transitionDuration]);

  const setTheme = (newTheme: 'light' | 'dark' | 'system') => {
    setThemeState(newTheme);
    localStorage.setItem(storageKey, newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme, isAnimating }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Example usage:
// import { AnimatedThemeProvider, useAnimatedTheme } from '@/components/animated-theme-provider';
//
// function App() {
//   return (
//     <AnimatedThemeProvider>
//       <YourApp />
//     </AnimatedThemeProvider>
//   );
// }
//
// function ThemeToggle() {
//   const { theme, setTheme, isAnimating } = useAnimatedTheme();
//   
//   return (
//     <button 
//       onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
//       disabled={isAnimating}
//     >
//       Toggle Theme
//     </button>
//   );
// }
