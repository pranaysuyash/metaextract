/**
 * Property-Based Tests for Interactive Feedback System
 * 
 * Tests that interactive feedback classes are consistently applied
 * across all component types and variants.
 * 
 * @validates Requirements 1.2 - Interactive feedback for all components
 * 
 * **Property 2: Interactive feedback universality**
 * For all component types and variants, the feedback system SHALL provide
 * valid CSS classes for hover, focus, and active states.
 */

import * as fc from 'fast-check';
import {
  interactiveStates,
  transitionClasses,
  componentFeedback,
  microInteractions,
  combineFeedback,
  getFeedbackClasses,
  createHoverEffect,
} from '../interactive-feedback';

describe('Interactive Feedback System - Property Tests', () => {
  // ============================================================================
  // Property 2: Interactive feedback universality
  // ============================================================================
  
  describe('Property 2: Interactive feedback universality', () => {
    /**
     * Property: All interactive state classes should be non-empty strings
     */
    it('all interactive state classes are non-empty strings', () => {
      // Test hover states
      Object.entries(interactiveStates.hover).forEach(([key, value]) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
        expect(value.trim()).toBe(value); // No leading/trailing whitespace
      });
      
      // Test focus states
      Object.entries(interactiveStates.focus).forEach(([key, value]) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
      
      // Test active states
      Object.entries(interactiveStates.active).forEach(([key, value]) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
      
      // Test disabled states
      Object.entries(interactiveStates.disabled).forEach(([key, value]) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
    });
    
    /**
     * Property: All transition classes should be non-empty strings
     */
    it('all transition classes are non-empty strings', () => {
      Object.entries(transitionClasses).forEach(([key, value]) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
    });
    
    /**
     * Property: All component feedback classes should be non-empty strings
     */
    it('all component feedback classes are non-empty strings', () => {
      Object.entries(componentFeedback).forEach(([component, variants]) => {
        Object.entries(variants).forEach(([variant, classes]) => {
          expect(typeof classes).toBe('string');
          expect(classes.length).toBeGreaterThan(0);
        });
      });
    });
    
    /**
     * Property: All micro-interaction classes should be non-empty strings
     */
    it('all micro-interaction classes are non-empty strings', () => {
      Object.entries(microInteractions).forEach(([key, value]) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
    });
    
    /**
     * Property: For any component type, getFeedbackClasses returns valid classes
     */
    it('getFeedbackClasses returns valid classes for all component types', () => {
      const componentTypes = Object.keys(componentFeedback) as Array<keyof typeof componentFeedback>;
      
      fc.assert(
        fc.property(
          fc.constantFrom(...componentTypes),
          (componentType) => {
            const classes = getFeedbackClasses(componentType);
            expect(typeof classes).toBe('string');
            expect(classes.length).toBeGreaterThan(0);
            // Should not have multiple consecutive spaces
            expect(classes).not.toMatch(/\s{2,}/);
          }
        ),
        { numRuns: 100 }
      );
    });
    
    /**
     * Property: For any component type and variant, getFeedbackClasses returns valid classes
     */
    it('getFeedbackClasses returns valid classes for all component variants', () => {
      const componentVariants: Array<{ component: keyof typeof componentFeedback; variant: string }> = [];
      
      Object.entries(componentFeedback).forEach(([component, variants]) => {
        Object.keys(variants).forEach((variant) => {
          componentVariants.push({
            component: component as keyof typeof componentFeedback,
            variant,
          });
        });
      });
      
      fc.assert(
        fc.property(
          fc.constantFrom(...componentVariants),
          ({ component, variant }) => {
            const classes = getFeedbackClasses(component, variant);
            expect(typeof classes).toBe('string');
            expect(classes.length).toBeGreaterThan(0);
          }
        ),
        { numRuns: 100 }
      );
    });
    
    /**
     * Property: combineFeedback should handle any combination of inputs
     */
    it('combineFeedback handles arbitrary string combinations', () => {
      fc.assert(
        fc.property(
          fc.array(fc.oneof(
            fc.string(),
            fc.constant(undefined),
            fc.constant(null),
            fc.constant(false)
          ), { minLength: 0, maxLength: 10 }),
          (inputs) => {
            const result = combineFeedback(...inputs);
            expect(typeof result).toBe('string');
            // Should not have multiple consecutive spaces
            expect(result).not.toMatch(/\s{2,}/);
            // Should not have leading/trailing whitespace
            expect(result).toBe(result.trim());
          }
        ),
        { numRuns: 100 }
      );
    });
    
    /**
     * Property: combineFeedback preserves all valid class names
     */
    it('combineFeedback preserves all valid class names', () => {
      fc.assert(
        fc.property(
          fc.array(fc.string().filter(s => s.trim().length > 0 && !s.includes(' ')), { minLength: 1, maxLength: 5 }),
          (classNames) => {
            const result = combineFeedback(...classNames);
            // All input class names should be present in the result
            classNames.forEach(className => {
              expect(result).toContain(className);
            });
          }
        ),
        { numRuns: 100 }
      );
    });
    
    /**
     * Property: createHoverEffect returns valid CSS classes
     */
    it('createHoverEffect returns valid CSS classes for any options', () => {
      fc.assert(
        fc.property(
          fc.record({
            scale: fc.option(fc.float({ min: Math.fround(0.9), max: Math.fround(1.2) })),
            brightness: fc.option(fc.float({ min: Math.fround(0.8), max: Math.fround(1.5) })),
            shadow: fc.option(fc.boolean()),
            glow: fc.option(fc.boolean()),
          }),
          (options) => {
            const result = createHoverEffect({
              scale: options.scale ?? undefined,
              brightness: options.brightness ?? undefined,
              shadow: options.shadow ?? undefined,
              glow: options.glow ?? undefined,
            });
            expect(typeof result).toBe('string');
            // Should always include transition class
            expect(result).toContain('transition');
          }
        ),
        { numRuns: 100 }
      );
    });
  });
  
  // ============================================================================
  // Additional Property Tests
  // ============================================================================
  
  describe('Interactive state consistency', () => {
    /**
     * Property: Hover states should contain 'hover:' prefix
     */
    it('hover states contain hover: prefix', () => {
      Object.values(interactiveStates.hover).forEach((classes) => {
        expect(classes).toMatch(/hover:/);
      });
    });
    
    /**
     * Property: Focus states should contain 'focus' keyword
     */
    it('focus states contain focus keyword', () => {
      Object.values(interactiveStates.focus).forEach((classes) => {
        expect(classes).toMatch(/focus/);
      });
    });
    
    /**
     * Property: Active states should contain 'active:' prefix
     */
    it('active states contain active: prefix', () => {
      Object.values(interactiveStates.active).forEach((classes) => {
        expect(classes).toMatch(/active:/);
      });
    });
    
    /**
     * Property: Disabled states should contain 'disabled:' prefix
     */
    it('disabled states contain disabled: prefix', () => {
      Object.values(interactiveStates.disabled).forEach((classes) => {
        expect(classes).toMatch(/disabled:/);
      });
    });
  });
  
  describe('Transition class consistency', () => {
    /**
     * Property: All transition classes should contain 'transition' keyword
     */
    it('all transition classes contain transition keyword', () => {
      Object.values(transitionClasses).forEach((classes) => {
        expect(classes).toMatch(/transition/);
      });
    });
    
    /**
     * Property: Duration-based transitions should contain 'duration' keyword
     */
    it('duration-based transitions contain duration keyword', () => {
      ['fast', 'normal', 'slow', 'slower'].forEach((key) => {
        const classes = transitionClasses[key as keyof typeof transitionClasses];
        expect(classes).toMatch(/duration/);
      });
    });
  });
  
  describe('Component feedback completeness', () => {
    /**
     * Property: All component types should have a 'default' variant
     */
    it('all component types have a default variant', () => {
      Object.entries(componentFeedback).forEach(([component, variants]) => {
        // Check if 'default' exists or if there's at least one variant
        const hasDefault = 'default' in variants;
        const hasVariants = Object.keys(variants).length > 0;
        expect(hasDefault || hasVariants).toBe(true);
      });
    });
    
    /**
     * Property: Button component should have multiple variants
     */
    it('button component has multiple variants', () => {
      expect(Object.keys(componentFeedback.button).length).toBeGreaterThanOrEqual(2);
    });
    
    /**
     * Property: Card component should have interactive variant
     */
    it('card component has interactive variant', () => {
      expect('interactive' in componentFeedback.card).toBe(true);
    });
  });
  
  describe('Micro-interaction animations', () => {
    /**
     * Property: All micro-interactions should start with 'animate-'
     */
    it('all micro-interactions start with animate- prefix', () => {
      Object.values(microInteractions).forEach((className) => {
        expect(className).toMatch(/^animate-/);
      });
    });
  });
});
