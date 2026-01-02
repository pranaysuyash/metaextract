/**
 * Design System Tokens
 * 
 * Centralized design tokens for colors, typography, spacing, and other design values.
 * All UI components should use these tokens instead of hardcoded values.
 * 
 * @module design-tokens
 * @validates Requirements 1.1 - Consistent design system with unified colors, typography, and spacing
 */

// ============================================================================
// Color Tokens
// ============================================================================

export const colors = {
  // Primary brand colors
  primary: {
    DEFAULT: 'hsl(230, 85%, 60%)',
    foreground: 'hsl(0, 0%, 100%)',
    50: 'hsl(230, 85%, 95%)',
    100: 'hsl(230, 85%, 90%)',
    200: 'hsl(230, 85%, 80%)',
    300: 'hsl(230, 85%, 70%)',
    400: 'hsl(230, 85%, 65%)',
    500: 'hsl(230, 85%, 60%)',
    600: 'hsl(230, 85%, 50%)',
    700: 'hsl(230, 85%, 40%)',
    800: 'hsl(230, 85%, 30%)',
    900: 'hsl(230, 85%, 20%)',
  },
  
  // Secondary colors (Cyber Purple)
  secondary: {
    DEFAULT: 'hsl(270, 80%, 60%)',
    foreground: 'hsl(0, 0%, 100%)',
    50: 'hsl(270, 80%, 95%)',
    100: 'hsl(270, 80%, 90%)',
    200: 'hsl(270, 80%, 80%)',
    300: 'hsl(270, 80%, 70%)',
    400: 'hsl(270, 80%, 65%)',
    500: 'hsl(270, 80%, 60%)',
    600: 'hsl(270, 80%, 50%)',
    700: 'hsl(270, 80%, 40%)',
    800: 'hsl(270, 80%, 30%)',
    900: 'hsl(270, 80%, 20%)',
  },
  
  // Accent colors (Neon Green for success/data)
  accent: {
    DEFAULT: 'hsl(150, 100%, 50%)',
    foreground: 'hsl(220, 20%, 4%)',
    success: 'hsl(150, 100%, 50%)',
    warning: 'hsl(45, 100%, 50%)',
    info: 'hsl(200, 100%, 50%)',
  },
  
  // Destructive/Error colors
  destructive: {
    DEFAULT: 'hsl(0, 85%, 60%)',
    foreground: 'hsl(210, 40%, 98%)',
  },
  
  // Background colors
  background: {
    DEFAULT: 'hsl(220, 20%, 4%)',
    card: 'hsl(220, 20%, 8%)',
    popover: 'hsl(220, 20%, 8%)',
    muted: 'hsl(220, 20%, 15%)',
    input: 'hsl(220, 20%, 12%)',
  },
  
  // Foreground/Text colors
  foreground: {
    DEFAULT: 'hsl(220, 20%, 97%)',
    muted: 'hsl(220, 20%, 75%)',
    card: 'hsl(220, 20%, 97%)',
    popover: 'hsl(220, 20%, 97%)',
  },
  
  // Border colors
  border: {
    DEFAULT: 'hsl(220, 20%, 15%)',
    ring: 'hsl(230, 85%, 60%)',
  },
} as const;

// ============================================================================
// Typography Tokens
// ============================================================================

export const typography = {
  // Font families
  fontFamily: {
    sans: "'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', monospace",
  },
  
  // Font sizes (in rem, based on 16px base)
  fontSize: {
    xs: '0.75rem',     // 12px
    sm: '0.875rem',    // 14px
    base: '1rem',      // 16px
    lg: '1.125rem',    // 18px
    xl: '1.5rem',      // 24px
    '2xl': '2rem',     // 32px
    '3xl': '2.5rem',   // 40px
    '4xl': '3rem',     // 48px
  },
  
  // Font weights
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
  
  // Line heights
  lineHeight: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  },
  
  // Letter spacing
  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
  },
} as const;

// ============================================================================
// Spacing Tokens (4px base unit)
// ============================================================================

export const spacing = {
  0: '0',
  0.5: '0.125rem',   // 2px
  1: '0.25rem',      // 4px (base unit)
  1.5: '0.375rem',   // 6px
  2: '0.5rem',       // 8px
  2.5: '0.625rem',   // 10px
  3: '0.75rem',      // 12px
  3.5: '0.875rem',   // 14px
  4: '1rem',         // 16px
  5: '1.25rem',      // 20px
  6: '1.5rem',       // 24px
  7: '1.75rem',      // 28px
  8: '2rem',         // 32px
  9: '2.25rem',      // 36px
  10: '2.5rem',      // 40px
  11: '2.75rem',     // 44px
  12: '3rem',        // 48px
  14: '3.5rem',      // 56px
  16: '4rem',        // 64px
  20: '5rem',        // 80px
  24: '6rem',        // 96px
  28: '7rem',        // 112px
  32: '8rem',        // 128px
} as const;

// ============================================================================
// Border Radius Tokens
// ============================================================================

export const borderRadius = {
  none: '0',
  sm: '0.25rem',     // 4px
  DEFAULT: '0.5rem', // 8px
  md: '0.5rem',      // 8px
  lg: '0.75rem',     // 12px
  xl: '1rem',        // 16px
  '2xl': '1.5rem',   // 24px
  full: '9999px',
} as const;

// ============================================================================
// Shadow Tokens
// ============================================================================

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  glow: '0 0 20px rgba(99, 102, 241, 0.3)',
  'glow-lg': '0 0 40px rgba(99, 102, 241, 0.4)',
} as const;

// ============================================================================
// Transition Tokens
// ============================================================================

export const transitions = {
  duration: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
    slower: '500ms',
  },
  timing: {
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    linear: 'linear',
  },
} as const;

// ============================================================================
// Breakpoint Tokens
// ============================================================================

export const breakpoints = {
  xs: '320px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ============================================================================
// Z-Index Tokens
// ============================================================================

export const zIndex = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
} as const;

// ============================================================================
// Animation Tokens
// ============================================================================

export const animations = {
  spin: 'spin 1s linear infinite',
  ping: 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite',
  pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  bounce: 'bounce 1s infinite',
  fadeIn: 'fadeIn 0.2s ease-out',
  fadeOut: 'fadeOut 0.2s ease-in',
  slideIn: 'slideIn 0.3s ease-out',
  slideOut: 'slideOut 0.3s ease-in',
  scaleIn: 'scaleIn 0.2s ease-out',
  scaleOut: 'scaleOut 0.2s ease-in',
} as const;

// ============================================================================
// Complete Design Tokens Export
// ============================================================================

export const designTokens = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  breakpoints,
  zIndex,
  animations,
} as const;

// Type exports for TypeScript support
export type Colors = typeof colors;
export type Typography = typeof typography;
export type Spacing = typeof spacing;
export type BorderRadius = typeof borderRadius;
export type Shadows = typeof shadows;
export type Transitions = typeof transitions;
export type Breakpoints = typeof breakpoints;
export type ZIndex = typeof zIndex;
export type Animations = typeof animations;
export type DesignTokens = typeof designTokens;

export default designTokens;
