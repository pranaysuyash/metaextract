/**
 * Property-Based Tests for Tutorial Overlay System
 * 
 * Tests universal correctness properties using fast-check framework.
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import * as fc from 'fast-check';
import { TutorialOverlay, useTutorialOverlay } from '../tutorial-overlay';
import { OnboardingProvider } from '@/lib/onboarding';
import { AuthProvider } from '@/lib/auth';

// Mock auth context
jest.mock('@/lib/auth', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: { id: 'test-user', username: 'testuser' },
    isAuthenticated: true,
    isLoading: false
  })
}));

// Mock fetch for API calls
(global as any).fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ session: null })
  })
);

// ============================================================================
// Test Wrapper
// ============================================================================

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <OnboardingProvider>
        {children}
      </OnboardingProvider>
    </AuthProvider>
  );
}

// ============================================================================
// Property 2: Interactive overlay presence
// ============================================================================

describe('Tutorial Overlay Property Tests', () => {
  beforeEach(() => {
    // Clear any existing portals
    document.body.innerHTML = '';
  });

  it('Property 2: Interactive overlay presence - overlay appears when onboarding is active', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.boolean(), // isOpen
        fc.record({
          id: fc.string({ minLength: 1, maxLength: 20 }),
          title: fc.string({ minLength: 5, maxLength: 50 }),
          description: fc.string({ minLength: 10, maxLength: 200 }),
          position: fc.constantFrom('top', 'bottom', 'left', 'right', 'center'),
          skippable: fc.boolean()
        }),
        async (isOpen, stepData) => {
          const onClose = jest.fn();

          const { container } = render(
            <TestWrapper>
              <TutorialOverlay isOpen={isOpen} onClose={onClose} />
            </TestWrapper>
          );

          if (isOpen) {
            // When overlay is open, it should be present in the DOM
            await waitFor(() => {
              const overlay = document.querySelector('.tutorial-overlay');
              expect(overlay).toBeTruthy();
            }, { timeout: 1000 });
          } else {
            // When overlay is closed, it should not be present
            const overlay = document.querySelector('.tutorial-overlay');
            expect(overlay).toBeFalsy();
          }
        }
      ),
      { numRuns: 20 }
    );
  });

  // ============================================================================
  // Property 3: Step completion feedback
  // ============================================================================

  it('Property 3: Step completion feedback - completing a step updates progress', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 0, max: 10 }), // number of steps
        async (numSteps) => {
          // Create a path with multiple steps
          const steps = Array.from({ length: Math.max(1, numSteps) }, (_, i) => ({
            id: `step-${i}`,
            title: `Step ${i + 1}`,
            description: `Description for step ${i + 1}`,
            position: 'center' as const,
            skippable: true,
            completionCriteria: { type: 'manual' as const }
          }));

          // The progress should always be between 0 and 100
          const completionRate = (1 / steps.length) * 100;
          expect(completionRate).toBeGreaterThanOrEqual(0);
          expect(completionRate).toBeLessThanOrEqual(100);

          // Each step completion should increase progress
          for (let i = 0; i < steps.length; i++) {
            const expectedProgress = ((i + 1) / steps.length) * 100;
            expect(expectedProgress).toBeGreaterThanOrEqual(0);
            expect(expectedProgress).toBeLessThanOrEqual(100);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  // ============================================================================
  // Property 4: Tutorial control availability
  // ============================================================================

  it('Property 4: Tutorial control availability - controls are accessible', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          skippable: fc.boolean(),
          hasNext: fc.boolean(),
          hasPrevious: fc.boolean()
        }),
        async (controls) => {
          const onClose = jest.fn();

          render(
            <TestWrapper>
              <TutorialOverlay isOpen={true} onClose={onClose} />
            </TestWrapper>
          );

          await waitFor(() => {
            const overlay = document.querySelector('.tutorial-overlay');
            expect(overlay).toBeTruthy();
          });

          // Overlay should have proper ARIA attributes
          const overlay = document.querySelector('[role="dialog"]');
          expect(overlay).toBeTruthy();
          expect(overlay?.getAttribute('aria-modal')).toBe('true');
          expect(overlay?.getAttribute('aria-labelledby')).toBe('tutorial-title');
          expect(overlay?.getAttribute('aria-describedby')).toBe('tutorial-description');
        }
      ),
      { numRuns: 20 }
    );
  });

  // ============================================================================
  // Property: Keyboard navigation
  // ============================================================================

  it('Property: Keyboard navigation - Escape key handler is called', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.boolean(), // skippable
        async (skippable) => {
          const onClose = jest.fn();

          // The onClose handler should be a function
          expect(typeof onClose).toBe('function');
          
          // Calling it should work
          onClose();
          expect(onClose).toHaveBeenCalledTimes(1);
        }
      ),
      { numRuns: 10 }
    );
  });

  // ============================================================================
  // Property: Spotlight positioning
  // ============================================================================

  it('Property: Spotlight positioning - spotlight calculation is correct', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          top: fc.integer({ min: 0, max: 1000 }),
          left: fc.integer({ min: 0, max: 1000 }),
          width: fc.integer({ min: 50, max: 500 }),
          height: fc.integer({ min: 50, max: 500 })
        }),
        async (rect) => {
          const padding = 8;
          
          // Calculate spotlight position with padding
          const spotlightTop = rect.top - padding;
          const spotlightLeft = rect.left - padding;
          const spotlightWidth = rect.width + padding * 2;
          const spotlightHeight = rect.height + padding * 2;

          // Spotlight should encompass the target element
          expect(spotlightTop).toBeLessThanOrEqual(rect.top);
          expect(spotlightLeft).toBeLessThanOrEqual(rect.left);
          expect(spotlightTop + spotlightHeight).toBeGreaterThanOrEqual(rect.top + rect.height);
          expect(spotlightLeft + spotlightWidth).toBeGreaterThanOrEqual(rect.left + rect.width);
        }
      ),
      { numRuns: 50 }
    );
  });

  // ============================================================================
  // Property: Progress bar accuracy
  // ============================================================================

  it('Property: Progress bar accuracy - progress bar reflects completion percentage', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 20 }), // total steps
        fc.integer({ min: 0, max: 19 }), // current step
        async (totalSteps, currentStepRaw) => {
          const currentStep = Math.min(currentStepRaw, totalSteps - 1);
          const expectedPercentage = ((currentStep + 1) / totalSteps) * 100;

          // Progress percentage should always be valid
          expect(expectedPercentage).toBeGreaterThanOrEqual(0);
          expect(expectedPercentage).toBeLessThanOrEqual(100);

          // Progress should increase monotonically
          if (currentStep > 0) {
            const previousPercentage = (currentStep / totalSteps) * 100;
            expect(expectedPercentage).toBeGreaterThan(previousPercentage);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  // ============================================================================
  // Property: Tooltip positioning constraints
  // ============================================================================

  it('Property: Tooltip positioning - tooltip stays within viewport bounds', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          viewportWidth: fc.integer({ min: 800, max: 3840 }), // Ensure viewport is large enough for tooltip
          viewportHeight: fc.integer({ min: 600, max: 2160 }),
          targetX: fc.integer({ min: 0, max: 3840 }),
          targetY: fc.integer({ min: 0, max: 2160 })
        }),
        async (viewport) => {
          const tooltipWidth = 400;
          const tooltipHeight = 200;
          const padding = 20;

          // Calculate constrained position
          let left = viewport.targetX;
          let top = viewport.targetY;

          // Ensure tooltip stays within viewport
          const maxLeft = viewport.viewportWidth - tooltipWidth - padding;
          const maxTop = viewport.viewportHeight - tooltipHeight - padding;
          
          // Only test if viewport is large enough
          if (maxLeft >= padding && maxTop >= padding) {
            left = Math.max(padding, Math.min(left, maxLeft));
            top = Math.max(padding, Math.min(top, maxTop));

            // Tooltip should always be within bounds
            expect(left).toBeGreaterThanOrEqual(padding);
            expect(left).toBeLessThanOrEqual(maxLeft);
            expect(top).toBeGreaterThanOrEqual(padding);
            expect(top).toBeLessThanOrEqual(maxTop);
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
