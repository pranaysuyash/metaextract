/**
 * Responsive Design System
 * 
 * Mobile-first responsive utilities, breakpoints, and grid system.
 * Supports viewport sizes from 320px to 2560px.
 * 
 * @module responsive
 * @validates Requirements 1.5 - Responsive design compliance
 */

import { breakpoints } from './design-tokens';

// ============================================================================
// Breakpoint Utilities
// ============================================================================

/** Breakpoint values in pixels (numeric) */
export const breakpointValues = {
  xs: 320,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export type BreakpointKey = keyof typeof breakpointValues;

/** Media query strings for each breakpoint (mobile-first: min-width) */
export const mediaQueries = {
  xs: `(min-width: ${breakpoints.xs})`,
  sm: `(min-width: ${breakpoints.sm})`,
  md: `(min-width: ${breakpoints.md})`,
  lg: `(min-width: ${breakpoints.lg})`,
  xl: `(min-width: ${breakpoints.xl})`,
  '2xl': `(min-width: ${breakpoints['2xl']})`,
} as const;

/** Max-width media queries for targeting specific ranges */
export const maxMediaQueries = {
  xs: `(max-width: ${breakpointValues.sm - 1}px)`,
  sm: `(max-width: ${breakpointValues.md - 1}px)`,
  md: `(max-width: ${breakpointValues.lg - 1}px)`,
  lg: `(max-width: ${breakpointValues.xl - 1}px)`,
  xl: `(max-width: ${breakpointValues['2xl'] - 1}px)`,
} as const;

/** Range media queries for targeting specific breakpoint ranges */
export const rangeMediaQueries = {
  'xs-only': `(min-width: ${breakpoints.xs}) and (max-width: ${breakpointValues.sm - 1}px)`,
  'sm-only': `(min-width: ${breakpoints.sm}) and (max-width: ${breakpointValues.md - 1}px)`,
  'md-only': `(min-width: ${breakpoints.md}) and (max-width: ${breakpointValues.lg - 1}px)`,
  'lg-only': `(min-width: ${breakpoints.lg}) and (max-width: ${breakpointValues.xl - 1}px)`,
  'xl-only': `(min-width: ${breakpoints.xl}) and (max-width: ${breakpointValues['2xl'] - 1}px)`,
  'mobile': `(max-width: ${breakpointValues.md - 1}px)`,
  'tablet': `(min-width: ${breakpoints.md}) and (max-width: ${breakpointValues.lg - 1}px)`,
  'desktop': `(min-width: ${breakpoints.lg})`,
} as const;

// ============================================================================
// Grid System
// ============================================================================

/** Grid column counts for different breakpoints */
export const gridColumns = {
  xs: 4,
  sm: 8,
  md: 8,
  lg: 12,
  xl: 12,
  '2xl': 12,
} as const;

/** Container max-widths for each breakpoint */
export const containerMaxWidths = {
  xs: '100%',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

/** Grid gap sizes */
export const gridGaps = {
  none: '0',
  xs: '0.5rem',   // 8px
  sm: '1rem',     // 16px
  md: '1.5rem',   // 24px
  lg: '2rem',     // 32px
  xl: '3rem',     // 48px
} as const;

// ============================================================================
// Responsive CSS Classes
// ============================================================================

/** Container classes with responsive padding */
export const containerClasses = {
  base: 'w-full mx-auto px-4 sm:px-6 lg:px-8',
  narrow: 'w-full mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl',
  wide: 'w-full mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl',
  full: 'w-full px-4 sm:px-6 lg:px-8',
} as const;

/** Grid layout classes */
export const gridClasses = {
  // Basic grids
  cols1: 'grid grid-cols-1',
  cols2: 'grid grid-cols-1 sm:grid-cols-2',
  cols3: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  cols4: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  cols6: 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6',
  cols12: 'grid grid-cols-4 sm:grid-cols-8 lg:grid-cols-12',
  
  // Auto-fit grids
  autoFitSm: 'grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))]',
  autoFitMd: 'grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))]',
  autoFitLg: 'grid grid-cols-[repeat(auto-fit,minmax(320px,1fr))]',
  
  // Gap utilities
  gapNone: 'gap-0',
  gapXs: 'gap-2',
  gapSm: 'gap-4',
  gapMd: 'gap-6',
  gapLg: 'gap-8',
  gapXl: 'gap-12',
} as const;

/** Flex layout classes */
export const flexClasses = {
  row: 'flex flex-row',
  col: 'flex flex-col',
  rowReverse: 'flex flex-row-reverse',
  colReverse: 'flex flex-col-reverse',
  wrap: 'flex flex-wrap',
  nowrap: 'flex flex-nowrap',
  center: 'flex items-center justify-center',
  between: 'flex items-center justify-between',
  start: 'flex items-start justify-start',
  end: 'flex items-end justify-end',
  
  // Responsive direction changes
  colToRow: 'flex flex-col sm:flex-row',
  colToRowMd: 'flex flex-col md:flex-row',
  colToRowLg: 'flex flex-col lg:flex-row',
} as const;

/** Spacing classes for responsive margins/padding */
export const spacingClasses = {
  // Responsive padding
  pResponsive: 'p-4 sm:p-6 lg:p-8',
  pxResponsive: 'px-4 sm:px-6 lg:px-8',
  pyResponsive: 'py-4 sm:py-6 lg:py-8',
  
  // Responsive margins
  mResponsive: 'm-4 sm:m-6 lg:m-8',
  mxResponsive: 'mx-4 sm:mx-6 lg:mx-8',
  myResponsive: 'my-4 sm:my-6 lg:my-8',
  
  // Section spacing
  sectionY: 'py-12 sm:py-16 lg:py-24',
  sectionYSm: 'py-8 sm:py-12 lg:py-16',
} as const;

/** Typography responsive classes */
export const typographyClasses = {
  // Headings
  h1: 'text-3xl sm:text-4xl lg:text-5xl font-bold',
  h2: 'text-2xl sm:text-3xl lg:text-4xl font-bold',
  h3: 'text-xl sm:text-2xl lg:text-3xl font-semibold',
  h4: 'text-lg sm:text-xl lg:text-2xl font-semibold',
  h5: 'text-base sm:text-lg lg:text-xl font-medium',
  h6: 'text-sm sm:text-base lg:text-lg font-medium',
  
  // Body text
  bodyLg: 'text-base sm:text-lg',
  body: 'text-sm sm:text-base',
  bodySm: 'text-xs sm:text-sm',
  
  // Display text
  display: 'text-4xl sm:text-5xl lg:text-6xl font-bold',
  displayLg: 'text-5xl sm:text-6xl lg:text-7xl font-bold',
} as const;

/** Visibility classes */
export const visibilityClasses = {
  hiddenMobile: 'hidden sm:block',
  hiddenTablet: 'hidden md:block',
  hiddenDesktop: 'lg:hidden',
  showMobileOnly: 'block sm:hidden',
  showTabletOnly: 'hidden sm:block lg:hidden',
  showDesktopOnly: 'hidden lg:block',
} as const;

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Check if current viewport matches a breakpoint
 */
export function matchesBreakpoint(breakpoint: BreakpointKey): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia(mediaQueries[breakpoint]).matches;
}

/**
 * Get current breakpoint based on window width
 */
export function getCurrentBreakpoint(): BreakpointKey {
  if (typeof window === 'undefined') return 'xs';
  
  const width = window.innerWidth;
  
  if (width >= breakpointValues['2xl']) return '2xl';
  if (width >= breakpointValues.xl) return 'xl';
  if (width >= breakpointValues.lg) return 'lg';
  if (width >= breakpointValues.md) return 'md';
  if (width >= breakpointValues.sm) return 'sm';
  return 'xs';
}

/**
 * Check if viewport is mobile (< md breakpoint)
 */
export function isMobile(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth < breakpointValues.md;
}

/**
 * Check if viewport is tablet (md to lg)
 */
export function isTablet(): boolean {
  if (typeof window === 'undefined') return false;
  const width = window.innerWidth;
  return width >= breakpointValues.md && width < breakpointValues.lg;
}

/**
 * Check if viewport is desktop (>= lg)
 */
export function isDesktop(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth >= breakpointValues.lg;
}

/**
 * Generate responsive value based on breakpoint
 */
export function responsiveValue<T>(values: Partial<Record<BreakpointKey, T>>, defaultValue: T): T {
  const breakpoint = getCurrentBreakpoint();
  const orderedBreakpoints: BreakpointKey[] = ['2xl', 'xl', 'lg', 'md', 'sm', 'xs'];
  
  // Find the first matching breakpoint value
  const breakpointIndex = orderedBreakpoints.indexOf(breakpoint);
  for (let i = breakpointIndex; i < orderedBreakpoints.length; i++) {
    const bp = orderedBreakpoints[i];
    if (values[bp] !== undefined) {
      return values[bp] as T;
    }
  }
  
  return defaultValue;
}

/**
 * Clamp a value between min and max based on viewport
 */
export function clampToViewport(value: number, minVw: number = 320, maxVw: number = 2560): number {
  if (typeof window === 'undefined') return value;
  const viewportWidth = Math.max(minVw, Math.min(maxVw, window.innerWidth));
  return Math.round((value / 1920) * viewportWidth);
}

// ============================================================================
// CSS Generation Utilities
// ============================================================================

/**
 * Generate CSS custom properties for responsive values
 */
export function generateResponsiveCSS(): string {
  return `
    :root {
      --container-padding: 1rem;
      --grid-columns: ${gridColumns.xs};
      --grid-gap: ${gridGaps.sm};
    }
    
    @media ${mediaQueries.sm} {
      :root {
        --container-padding: 1.5rem;
        --grid-columns: ${gridColumns.sm};
      }
    }
    
    @media ${mediaQueries.md} {
      :root {
        --grid-columns: ${gridColumns.md};
        --grid-gap: ${gridGaps.md};
      }
    }
    
    @media ${mediaQueries.lg} {
      :root {
        --container-padding: 2rem;
        --grid-columns: ${gridColumns.lg};
      }
    }
    
    @media ${mediaQueries.xl} {
      :root {
        --grid-columns: ${gridColumns.xl};
        --grid-gap: ${gridGaps.lg};
      }
    }
    
    @media ${mediaQueries['2xl']} {
      :root {
        --grid-columns: ${gridColumns['2xl']};
      }
    }
  `;
}

// ============================================================================
// Export All
// ============================================================================

export const responsive = {
  breakpointValues,
  mediaQueries,
  maxMediaQueries,
  rangeMediaQueries,
  gridColumns,
  containerMaxWidths,
  gridGaps,
  containerClasses,
  gridClasses,
  flexClasses,
  spacingClasses,
  typographyClasses,
  visibilityClasses,
  matchesBreakpoint,
  getCurrentBreakpoint,
  isMobile,
  isTablet,
  isDesktop,
  responsiveValue,
  clampToViewport,
  generateResponsiveCSS,
} as const;

export default responsive;
