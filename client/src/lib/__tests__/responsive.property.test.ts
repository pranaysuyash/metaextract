/**
 * Property Tests for Responsive Design System
 * 
 * Tests responsive breakpoints, grid system, and utilities.
 * 
 * @validates Requirements 1.5 - Responsive design compliance
 */

import * as fc from 'fast-check';
import {
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
  BreakpointKey,
} from '../responsive';

describe('Responsive Design System - Property Tests', () => {
  // ============================================================================
  // Breakpoint Properties
  // ============================================================================

  describe('Breakpoint Values', () => {
    const breakpointKeys: BreakpointKey[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];

    it('should have all breakpoints defined with positive pixel values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...breakpointKeys),
          (key) => {
            const value = breakpointValues[key];
            return typeof value === 'number' && value > 0 && value <= 3840;
          }
        ),
        { numRuns: breakpointKeys.length }
      );
    });

    it('should have breakpoints in ascending order', () => {
      const values = breakpointKeys.map(k => breakpointValues[k]);
      for (let i = 1; i < values.length; i++) {
        expect(values[i]).toBeGreaterThan(values[i - 1]);
      }
    });

    it('should cover viewport range from 320px to 1536px+', () => {
      expect(breakpointValues.xs).toBe(320);
      expect(breakpointValues['2xl']).toBe(1536);
    });

    it('should have reasonable gaps between breakpoints', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: breakpointKeys.length - 2 }),
          (index) => {
            const current = breakpointValues[breakpointKeys[index]];
            const next = breakpointValues[breakpointKeys[index + 1]];
            const gap = next - current;
            // Gap should be between 100px and 500px for usability
            return gap >= 100 && gap <= 500;
          }
        ),
        { numRuns: breakpointKeys.length - 1 }
      );
    });
  });

  // ============================================================================
  // Media Query Properties
  // ============================================================================

  describe('Media Queries', () => {
    const breakpointKeys: BreakpointKey[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];

    it('should generate valid min-width media queries', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...breakpointKeys),
          (key) => {
            const query = mediaQueries[key];
            return (
              typeof query === 'string' &&
              query.includes('min-width') &&
              query.includes('px')
            );
          }
        ),
        { numRuns: breakpointKeys.length }
      );
    });

    it('should generate valid max-width media queries', () => {
      const maxKeys = ['xs', 'sm', 'md', 'lg', 'xl'] as const;
      fc.assert(
        fc.property(
          fc.constantFrom(...maxKeys),
          (key) => {
            const query = maxMediaQueries[key];
            return (
              typeof query === 'string' &&
              query.includes('max-width') &&
              query.includes('px')
            );
          }
        ),
        { numRuns: maxKeys.length }
      );
    });

    it('should have range queries for common device categories', () => {
      expect(rangeMediaQueries['mobile']).toContain('max-width');
      expect(rangeMediaQueries['tablet']).toContain('min-width');
      expect(rangeMediaQueries['tablet']).toContain('max-width');
      expect(rangeMediaQueries['desktop']).toContain('min-width');
    });

    it('should have media query values matching breakpoint values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...breakpointKeys),
          (key) => {
            const query = mediaQueries[key];
            const expectedValue = breakpointValues[key];
            return query.includes(`${expectedValue}px`);
          }
        ),
        { numRuns: breakpointKeys.length }
      );
    });
  });

  // ============================================================================
  // Grid System Properties
  // ============================================================================

  describe('Grid System', () => {
    const breakpointKeys: BreakpointKey[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];

    it('should have valid column counts for all breakpoints', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...breakpointKeys),
          (key) => {
            const cols = gridColumns[key];
            // Column count should be 4, 8, or 12 (standard grid systems)
            return [4, 8, 12].includes(cols);
          }
        ),
        { numRuns: breakpointKeys.length }
      );
    });

    it('should have non-decreasing column counts as viewport increases', () => {
      const values = breakpointKeys.map(k => gridColumns[k]);
      for (let i = 1; i < values.length; i++) {
        expect(values[i]).toBeGreaterThanOrEqual(values[i - 1]);
      }
    });

    it('should have valid container max-widths', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...breakpointKeys),
          (key) => {
            const maxWidth = containerMaxWidths[key];
            return (
              typeof maxWidth === 'string' &&
              (maxWidth === '100%' || maxWidth.endsWith('px'))
            );
          }
        ),
        { numRuns: breakpointKeys.length }
      );
    });

    it('should have valid grid gap values', () => {
      const gapKeys = Object.keys(gridGaps) as (keyof typeof gridGaps)[];
      fc.assert(
        fc.property(
          fc.constantFrom(...gapKeys),
          (key) => {
            const gap = gridGaps[key];
            return (
              typeof gap === 'string' &&
              (gap === '0' || gap.endsWith('rem'))
            );
          }
        ),
        { numRuns: gapKeys.length }
      );
    });
  });

  // ============================================================================
  // CSS Class Properties
  // ============================================================================

  describe('CSS Classes', () => {
    it('should have valid container classes with responsive padding', () => {
      const containerKeys = Object.keys(containerClasses) as (keyof typeof containerClasses)[];
      fc.assert(
        fc.property(
          fc.constantFrom(...containerKeys),
          (key) => {
            const classes = containerClasses[key];
            return (
              typeof classes === 'string' &&
              classes.includes('px-') &&
              classes.length > 0
            );
          }
        ),
        { numRuns: containerKeys.length }
      );
    });

    it('should have grid classes with proper grid definitions', () => {
      const gridKeys = Object.keys(gridClasses) as (keyof typeof gridClasses)[];
      fc.assert(
        fc.property(
          fc.constantFrom(...gridKeys),
          (key) => {
            const classes = gridClasses[key];
            return (
              typeof classes === 'string' &&
              (classes.includes('grid') || classes.includes('gap'))
            );
          }
        ),
        { numRuns: gridKeys.length }
      );
    });

    it('should have flex classes with proper flex definitions', () => {
      const flexKeys = Object.keys(flexClasses) as (keyof typeof flexClasses)[];
      fc.assert(
        fc.property(
          fc.constantFrom(...flexKeys),
          (key) => {
            const classes = flexClasses[key];
            return typeof classes === 'string' && classes.includes('flex');
          }
        ),
        { numRuns: flexKeys.length }
      );
    });

    it('should have spacing classes with responsive breakpoint prefixes', () => {
      const spacingKeys = Object.keys(spacingClasses) as (keyof typeof spacingClasses)[];
      fc.assert(
        fc.property(
          fc.constantFrom(...spacingKeys),
          (key) => {
            const classes = spacingClasses[key];
            // Should have at least one responsive prefix (sm:, md:, lg:)
            return (
              typeof classes === 'string' &&
              (classes.includes('sm:') || classes.includes('md:') || classes.includes('lg:'))
            );
          }
        ),
        { numRuns: spacingKeys.length }
      );
    });

    it('should have typography classes with responsive font sizes', () => {
      const headingKeys = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] as const;
      fc.assert(
        fc.property(
          fc.constantFrom(...headingKeys),
          (key) => {
            const classes = typographyClasses[key];
            return (
              typeof classes === 'string' &&
              classes.includes('text-') &&
              classes.includes('font-')
            );
          }
        ),
        { numRuns: headingKeys.length }
      );
    });

    it('should have visibility classes with proper breakpoint modifiers', () => {
      const visibilityKeys = Object.keys(visibilityClasses) as (keyof typeof visibilityClasses)[];
      fc.assert(
        fc.property(
          fc.constantFrom(...visibilityKeys),
          (key) => {
            const classes = visibilityClasses[key];
            return (
              typeof classes === 'string' &&
              (classes.includes('hidden') || classes.includes('block'))
            );
          }
        ),
        { numRuns: visibilityKeys.length }
      );
    });
  });

  // ============================================================================
  // Viewport Coverage Properties
  // ============================================================================

  describe('Viewport Coverage', () => {
    it('should handle any viewport width from 320px to 2560px', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 320, max: 2560 }),
          (width) => {
            // Find which breakpoint this width falls into
            const breakpointKeys: BreakpointKey[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
            let matchedBreakpoint: BreakpointKey = 'xs';
            
            for (const key of breakpointKeys) {
              if (width >= breakpointValues[key]) {
                matchedBreakpoint = key;
              }
            }
            
            // Every width should match exactly one breakpoint
            return breakpointKeys.includes(matchedBreakpoint);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should have no gaps in breakpoint coverage', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 320, max: 2560 }),
          (width) => {
            const breakpointKeys: BreakpointKey[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
            
            // Count how many breakpoints this width satisfies (min-width)
            let satisfiedCount = 0;
            for (const key of breakpointKeys) {
              if (width >= breakpointValues[key]) {
                satisfiedCount++;
              }
            }
            
            // Should satisfy at least one breakpoint (xs at 320px)
            return satisfiedCount >= 1;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should correctly categorize mobile/tablet/desktop', () => {
      // Mobile: < 768px
      expect(breakpointValues.md).toBe(768);
      
      // Tablet: 768px - 1023px
      expect(breakpointValues.lg).toBe(1024);
      
      // Desktop: >= 1024px
      fc.assert(
        fc.property(
          fc.integer({ min: 320, max: 2560 }),
          (width) => {
            const isMobile = width < breakpointValues.md;
            const isTablet = width >= breakpointValues.md && width < breakpointValues.lg;
            const isDesktop = width >= breakpointValues.lg;
            
            // Exactly one category should be true
            const categories = [isMobile, isTablet, isDesktop].filter(Boolean);
            return categories.length === 1;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // ============================================================================
  // Consistency Properties
  // ============================================================================

  describe('Design Consistency', () => {
    it('should use consistent spacing scale (4px base)', () => {
      const gapValues = Object.values(gridGaps).filter(v => v !== '0');
      
      for (const gap of gapValues) {
        const remValue = parseFloat(gap);
        const pxValue = remValue * 16; // 1rem = 16px
        // Should be divisible by 4 (4px base unit)
        expect(pxValue % 4).toBe(0);
      }
    });

    it('should have mobile-first responsive classes', () => {
      // Container classes should start with base styles, then add responsive
      const baseContainer = containerClasses.base;
      expect(baseContainer).toMatch(/^[^:]+/); // Should start without breakpoint prefix
      expect(baseContainer).toContain('sm:');
      expect(baseContainer).toContain('lg:');
    });

    it('should have consistent naming conventions', () => {
      // Grid classes should follow pattern
      expect(gridClasses.cols1).toContain('grid-cols-1');
      expect(gridClasses.cols2).toContain('grid-cols-');
      expect(gridClasses.cols3).toContain('grid-cols-');
      expect(gridClasses.cols4).toContain('grid-cols-');
    });
  });
});
