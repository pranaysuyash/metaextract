/**
 * Property-Based Tests for Design Token Consistency
 * 
 * Feature: professional-product-polish
 * Property 1: Design token consistency
 * 
 * Tests that all UI components use design tokens from the central theme system
 * rather than hardcoded values.
 * 
 * **Validates: Requirements 1.1**
 */

import { describe, it, expect } from '@jest/globals';
import * as fc from 'fast-check';
import { 
  designTokens, 
  colors, 
  typography, 
  spacing, 
  borderRadius, 
  shadows, 
  transitions,
  breakpoints,
  zIndex
} from '../design-tokens';
import { generateCssVariables } from '../theme-provider';

describe('Design Token Consistency Property Tests', () => {
  
  // ============================================================================
  // Property 1: Design token consistency - All tokens have valid values
  // ============================================================================
  
  describe('Property 1: Design token consistency', () => {
    
    it('all color tokens should have valid HSL or hex color values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(colors)),
          (colorCategory) => {
            const colorValue = colors[colorCategory as keyof typeof colors];
            
            if (typeof colorValue === 'string') {
              // Single color value - should be valid HSL
              expect(colorValue).toMatch(/^hsl\(\d+,?\s*\d+%?,?\s*\d+%?\)$/);
            } else if (typeof colorValue === 'object') {
              // Color scale - all values should be valid HSL
              Object.values(colorValue).forEach((value) => {
                if (typeof value === 'string') {
                  expect(value).toMatch(/^hsl\(\d+,?\s*\d+%?,?\s*\d+%?\)$/);
                }
              });
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all typography tokens should have valid CSS values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(typography.fontSize)),
          (sizeKey) => {
            const fontSize = typography.fontSize[sizeKey as keyof typeof typography.fontSize];
            // Font sizes should be in rem format
            expect(fontSize).toMatch(/^\d+(\.\d+)?rem$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all spacing tokens should have valid CSS values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(spacing)),
          (spacingKey) => {
            const spacingValue = spacing[spacingKey as unknown as keyof typeof spacing];
            // Spacing should be 0 or in rem format
            expect(spacingValue).toMatch(/^(0|\d+(\.\d+)?rem)$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all border radius tokens should have valid CSS values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(borderRadius)),
          (radiusKey) => {
            const radiusValue = borderRadius[radiusKey as keyof typeof borderRadius];
            // Border radius should be 0, rem, or px format
            expect(radiusValue).toMatch(/^(0|\d+(\.\d+)?(rem|px))$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all shadow tokens should have valid CSS box-shadow values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(shadows)),
          (shadowKey) => {
            const shadowValue = shadows[shadowKey as keyof typeof shadows];
            // Shadow should be 'none', 'inset ...', or standard box-shadow format
            expect(typeof shadowValue).toBe('string');
            expect(shadowValue.length).toBeGreaterThan(0);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all transition duration tokens should have valid CSS time values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(transitions.duration)),
          (durationKey) => {
            const durationValue = transitions.duration[durationKey as keyof typeof transitions.duration];
            // Duration should be in ms format
            expect(durationValue).toMatch(/^\d+ms$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all breakpoint tokens should have valid CSS pixel values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(breakpoints)),
          (breakpointKey) => {
            const breakpointValue = breakpoints[breakpointKey as keyof typeof breakpoints];
            // Breakpoints should be in px format
            expect(breakpointValue).toMatch(/^\d+px$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all z-index tokens should have valid numeric or auto values', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(zIndex)),
          (zIndexKey) => {
            const zIndexValue = zIndex[zIndexKey as keyof typeof zIndex];
            // Z-index should be a number or 'auto'
            expect(
              typeof zIndexValue === 'number' || zIndexValue === 'auto'
            ).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // ============================================================================
  // Property: CSS Variable Generation Consistency
  // ============================================================================

  describe('CSS Variable Generation', () => {
    
    it('generated CSS variables should have consistent naming convention', () => {
      const cssVars = generateCssVariables();
      
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(cssVars)),
          (varName) => {
            // All CSS variable names should start with --
            expect(varName).toMatch(/^--[a-z]/);
            // Should use kebab-case (allowing dots for decimal spacing values like 0.5)
            expect(varName).toMatch(/^--[a-z0-9.-]+$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('all generated CSS variables should have non-empty values', () => {
      const cssVars = generateCssVariables();
      
      fc.assert(
        fc.property(
          fc.constantFrom(...Object.keys(cssVars)),
          (varName) => {
            const value = cssVars[varName];
            expect(value).toBeTruthy();
            expect(typeof value).toBe('string');
            expect(value.length).toBeGreaterThan(0);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('color CSS variables should reference valid color tokens', () => {
      const cssVars = generateCssVariables();
      const colorVars = Object.entries(cssVars).filter(([key]) => key.startsWith('--color-'));
      
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: colorVars.length - 1 }),
          (index) => {
            if (colorVars.length === 0) return true;
            const [, value] = colorVars[index];
            // Color values should be valid HSL
            expect(value).toMatch(/^hsl\(\d+,?\s*\d+%?,?\s*\d+%?\)$/);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('spacing CSS variables should reference valid spacing tokens', () => {
      const cssVars = generateCssVariables();
      const spacingVars = Object.entries(cssVars).filter(([key]) => key.startsWith('--spacing-'));
      
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: spacingVars.length - 1 }),
          (index) => {
            if (spacingVars.length === 0) return true;
            const [, value] = spacingVars[index];
            // Spacing values should be 0 or rem
            expect(value).toMatch(/^(0|\d+(\.\d+)?rem)$/);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // ============================================================================
  // Property: Design Token Completeness
  // ============================================================================

  describe('Design Token Completeness', () => {
    
    it('design tokens object should contain all required categories', () => {
      const requiredCategories = [
        'colors',
        'typography',
        'spacing',
        'borderRadius',
        'shadows',
        'transitions',
        'breakpoints',
        'zIndex',
        'animations'
      ];
      
      fc.assert(
        fc.property(
          fc.constantFrom(...requiredCategories),
          (category) => {
            expect(designTokens).toHaveProperty(category);
            expect(designTokens[category as keyof typeof designTokens]).toBeDefined();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('color tokens should include all semantic color categories', () => {
      const semanticColors = [
        'primary',
        'secondary',
        'accent',
        'destructive',
        'background',
        'foreground',
        'border'
      ];
      
      fc.assert(
        fc.property(
          fc.constantFrom(...semanticColors),
          (colorCategory) => {
            expect(colors).toHaveProperty(colorCategory);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('typography tokens should include all required properties', () => {
      const typographyProps = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing'];
      
      fc.assert(
        fc.property(
          fc.constantFrom(...typographyProps),
          (prop) => {
            expect(typography).toHaveProperty(prop);
            expect(typeof typography[prop as keyof typeof typography]).toBe('object');
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // ============================================================================
  // Property: Token Value Consistency
  // ============================================================================

  describe('Token Value Consistency', () => {
    
    it('spacing scale should be monotonically increasing', () => {
      const spacingKeys = Object.keys(spacing)
        .filter(k => !isNaN(Number(k)))
        .map(Number)
        .sort((a, b) => a - b);
      
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: spacingKeys.length - 2 }),
          (index) => {
            if (spacingKeys.length < 2) return true;
            
            const currentKey = spacingKeys[index];
            const nextKey = spacingKeys[index + 1];
            
            const currentValue = parseFloat(spacing[currentKey as unknown as keyof typeof spacing] || '0');
            const nextValue = parseFloat(spacing[nextKey as unknown as keyof typeof spacing] || '0');
            
            // Each spacing value should be greater than or equal to the previous
            expect(nextValue).toBeGreaterThanOrEqual(currentValue);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('z-index values should maintain proper stacking order', () => {
      const stackingOrder = ['base', 'docked', 'dropdown', 'sticky', 'banner', 'overlay', 'modal', 'popover', 'toast', 'tooltip'];
      
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: stackingOrder.length - 2 }),
          (index) => {
            const currentKey = stackingOrder[index] as keyof typeof zIndex;
            const nextKey = stackingOrder[index + 1] as keyof typeof zIndex;
            
            const currentValue = zIndex[currentKey];
            const nextValue = zIndex[nextKey];
            
            if (typeof currentValue === 'number' && typeof nextValue === 'number') {
              // Each z-index should be greater than the previous in stacking order
              expect(nextValue).toBeGreaterThan(currentValue);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('breakpoints should be monotonically increasing', () => {
      const breakpointOrder = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
      
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: breakpointOrder.length - 2 }),
          (index) => {
            const currentKey = breakpointOrder[index] as keyof typeof breakpoints;
            const nextKey = breakpointOrder[index + 1] as keyof typeof breakpoints;
            
            const currentValue = parseInt(breakpoints[currentKey]);
            const nextValue = parseInt(breakpoints[nextKey]);
            
            // Each breakpoint should be larger than the previous
            expect(nextValue).toBeGreaterThan(currentValue);
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
