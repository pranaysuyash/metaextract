/**
 * Responsive React Hooks
 * 
 * Custom hooks for responsive behavior in React components.
 * 
 * @module use-responsive
 * @validates Requirements 1.5 - Responsive design compliance
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  breakpointValues, 
  BreakpointKey, 
  getCurrentBreakpoint,
  isMobile,
  isTablet,
  isDesktop,
  mediaQueries
} from './responsive';

// ============================================================================
// useBreakpoint Hook
// ============================================================================

export interface BreakpointState {
  breakpoint: BreakpointKey;
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isXs: boolean;
  isSm: boolean;
  isMd: boolean;
  isLg: boolean;
  isXl: boolean;
  is2xl: boolean;
}

/**
 * Hook to track current breakpoint and viewport dimensions
 */
export function useBreakpoint(): BreakpointState {
  const [state, setState] = useState<BreakpointState>(() => {
    if (typeof window === 'undefined') {
      return {
        breakpoint: 'xs',
        width: 320,
        height: 568,
        isMobile: true,
        isTablet: false,
        isDesktop: false,
        isXs: true,
        isSm: false,
        isMd: false,
        isLg: false,
        isXl: false,
        is2xl: false,
      };
    }
    
    const width = window.innerWidth;
    const breakpoint = getCurrentBreakpoint();
    
    return {
      breakpoint,
      width,
      height: window.innerHeight,
      isMobile: isMobile(),
      isTablet: isTablet(),
      isDesktop: isDesktop(),
      isXs: width < breakpointValues.sm,
      isSm: width >= breakpointValues.sm && width < breakpointValues.md,
      isMd: width >= breakpointValues.md && width < breakpointValues.lg,
      isLg: width >= breakpointValues.lg && width < breakpointValues.xl,
      isXl: width >= breakpointValues.xl && width < breakpointValues['2xl'],
      is2xl: width >= breakpointValues['2xl'],
    };
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    let rafId: number;
    
    const handleResize = () => {
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        const width = window.innerWidth;
        const breakpoint = getCurrentBreakpoint();
        
        setState({
          breakpoint,
          width,
          height: window.innerHeight,
          isMobile: isMobile(),
          isTablet: isTablet(),
          isDesktop: isDesktop(),
          isXs: width < breakpointValues.sm,
          isSm: width >= breakpointValues.sm && width < breakpointValues.md,
          isMd: width >= breakpointValues.md && width < breakpointValues.lg,
          isLg: width >= breakpointValues.lg && width < breakpointValues.xl,
          isXl: width >= breakpointValues.xl && width < breakpointValues['2xl'],
          is2xl: width >= breakpointValues['2xl'],
        });
      });
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return state;
}

// ============================================================================
// useMediaQuery Hook
// ============================================================================

/**
 * Hook to check if a media query matches
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

/**
 * Hook to check if viewport is at or above a breakpoint
 */
export function useMinBreakpoint(breakpoint: BreakpointKey): boolean {
  return useMediaQuery(mediaQueries[breakpoint]);
}

// ============================================================================
// useResponsiveValue Hook
// ============================================================================

/**
 * Hook to get a value based on current breakpoint
 */
export function useResponsiveValue<T>(
  values: Partial<Record<BreakpointKey, T>>,
  defaultValue: T
): T {
  const { breakpoint } = useBreakpoint();
  
  return useMemo(() => {
    const orderedBreakpoints: BreakpointKey[] = ['2xl', 'xl', 'lg', 'md', 'sm', 'xs'];
    const breakpointIndex = orderedBreakpoints.indexOf(breakpoint);
    
    for (let i = breakpointIndex; i < orderedBreakpoints.length; i++) {
      const bp = orderedBreakpoints[i];
      if (values[bp] !== undefined) {
        return values[bp] as T;
      }
    }
    
    return defaultValue;
  }, [breakpoint, values, defaultValue]);
}

// ============================================================================
// useContainerQuery Hook (simulated)
// ============================================================================

export interface ContainerSize {
  width: number;
  height: number;
  breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

/**
 * Hook to track container size (simulated container queries)
 */
export function useContainerQuery(ref: React.RefObject<HTMLElement>): ContainerSize {
  const [size, setSize] = useState<ContainerSize>({
    width: 0,
    height: 0,
    breakpoint: 'xs',
  });

  useEffect(() => {
    if (!ref.current) return;

    const getBreakpoint = (width: number): ContainerSize['breakpoint'] => {
      if (width >= 1024) return 'xl';
      if (width >= 768) return 'lg';
      if (width >= 480) return 'md';
      if (width >= 320) return 'sm';
      return 'xs';
    };

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setSize({
          width,
          height,
          breakpoint: getBreakpoint(width),
        });
      }
    });

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return size;
}

// ============================================================================
// useOrientation Hook
// ============================================================================

export type Orientation = 'portrait' | 'landscape';

/**
 * Hook to track device orientation
 */
export function useOrientation(): Orientation {
  const [orientation, setOrientation] = useState<Orientation>(() => {
    if (typeof window === 'undefined') return 'portrait';
    return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleResize = () => {
      setOrientation(
        window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
      );
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return orientation;
}

// ============================================================================
// useScrollDirection Hook
// ============================================================================

export type ScrollDirection = 'up' | 'down' | null;

/**
 * Hook to track scroll direction (useful for hiding/showing headers)
 */
export function useScrollDirection(threshold: number = 10): ScrollDirection {
  const [scrollDirection, setScrollDirection] = useState<ScrollDirection>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    const updateScrollDirection = () => {
      const scrollY = window.scrollY;
      const diff = scrollY - lastScrollY;

      if (Math.abs(diff) > threshold) {
        setScrollDirection(diff > 0 ? 'down' : 'up');
        lastScrollY = scrollY;
      }
      
      ticking = false;
    };

    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(updateScrollDirection);
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [threshold]);

  return scrollDirection;
}

// ============================================================================
// useTouchDevice Hook
// ============================================================================

/**
 * Hook to detect touch device
 */
export function useTouchDevice(): boolean {
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    setIsTouch(
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0
    );
  }, []);

  return isTouch;
}

// ============================================================================
// Export All
// ============================================================================

export const responsiveHooks = {
  useBreakpoint,
  useMediaQuery,
  useMinBreakpoint,
  useResponsiveValue,
  useContainerQuery,
  useOrientation,
  useScrollDirection,
  useTouchDevice,
} as const;

export default responsiveHooks;
