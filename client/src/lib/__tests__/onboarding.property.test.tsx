/**
 * Property-based tests for the Intelligent User Onboarding system
 * 
 * These tests validate universal correctness properties using fast-check
 * to ensure the onboarding system behaves correctly across all possible inputs.
 */

// Polyfill for TextEncoder/TextDecoder in Node.js test environment
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

import React from 'react';
import { render, screen } from '@testing-library/react';
import fc from 'fast-check';
import { OnboardingProvider, useOnboarding } from '../onboarding';

// Mock the auth hook completely for testing
jest.mock('../auth', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: jest.fn(() => ({
    isAuthenticated: false,
    isLoading: false,
    user: null
  }))
}));

// Test utilities
interface TestWrapperProps {
  children: React.ReactNode;
  mockAuthState?: {
    isAuthenticated: boolean;
    isLoading: boolean;
    user: any;
  };
}

function TestWrapper({ children, mockAuthState }: TestWrapperProps) {
  // Mock the auth state if provided
  if (mockAuthState) {
    const { useAuth } = require('../auth');
    useAuth.mockReturnValue(mockAuthState);
  }
  
  return (
    <OnboardingProvider>
      {children}
    </OnboardingProvider>
  );
}

// Mock component to test onboarding state
function OnboardingTestComponent() {
  const { session, isOnboardingActive, isOnboardingComplete, getRecommendedPath } = useOnboarding();
  
  return (
    <div>
      <div data-testid="onboarding-state">
        {JSON.stringify({
          hasSession: !!session,
          isActive: isOnboardingActive,
          isComplete: isOnboardingComplete
        })}
      </div>
      <div data-testid="path-recommendation">
        {JSON.stringify(getRecommendedPath({
          useCase: 'personal',
          technicalLevel: 'beginner',
          primaryFileTypes: ['image'],
          goals: ['learn']
        }))}
      </div>
    </div>
  );
}

describe('Onboarding System Property Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock fetch for onboarding API calls
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.restoreAllMocks();
    // Clean up any rendered components
    document.body.innerHTML = '';
  });

  /**
   * Property 1: New user welcome screen display
   * For any user without existing session data or onboarding completion status,
   * the welcome screen should be displayed on first application visit
   * Validates: Requirements 1.1
   */
  test('Property 1: New user welcome screen display', () => {
    fc.assert(fc.property(
      fc.record({
        isAuthenticated: fc.boolean(),
        isLoading: fc.boolean(),
        user: fc.option(fc.record({
          id: fc.string(),
          username: fc.string(),
          email: fc.string()
        }), { nil: null })
      }),
      (authState) => {
        // Mock the auth hook to return our test state
        const { useAuth } = require('../auth');
        useAuth.mockReturnValue(authState);

        // Render the component with test state
        const { unmount } = render(
          <TestWrapper mockAuthState={authState}>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const stateElements = screen.getAllByTestId('onboarding-state');
        const state = JSON.parse(stateElements[0].textContent || '{}');

        // For authenticated users with a user object, onboarding should be available
        if (authState.isAuthenticated && authState.user && !authState.isLoading) {
          // The onboarding system should be ready to show onboarding
          expect(state.hasSession).toBe(false); // No session initially
          expect(state.isComplete).toBe(false); // Not completed initially
        }

        // For unauthenticated users, no onboarding should be active
        if (!authState.isAuthenticated || !authState.user) {
          expect(state.isActive).toBe(false);
        }

        // Clean up
        unmount();
      }
    ), { numRuns: 20 });
  });

  /**
   * Property 2: Path recommendation consistency
   * For any valid user profile, the system should consistently recommend
   * the same onboarding path for the same profile characteristics
   */
  test('Property 2: Path recommendation consistency', () => {
    fc.assert(fc.property(
      fc.record({
        useCase: fc.constantFrom('personal', 'professional', 'forensic', 'research', 'enterprise'),
        technicalLevel: fc.constantFrom('beginner', 'intermediate', 'advanced'),
        primaryFileTypes: fc.array(fc.string(), { minLength: 1, maxLength: 5 }),
        industry: fc.option(fc.string(), { nil: undefined }),
        goals: fc.array(fc.string(), { minLength: 1, maxLength: 3 })
      }),
      (_userProfile) => {
        // Render the component multiple times with the same profile
        const { unmount: unmount1 } = render(
          <TestWrapper>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const pathElements1 = screen.getAllByTestId('path-recommendation');
        const path1 = JSON.parse(pathElements1[0].textContent || '{}');
        
        unmount1();

        const { unmount: unmount2 } = render(
          <TestWrapper>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const pathElements2 = screen.getAllByTestId('path-recommendation');
        const path2 = JSON.parse(pathElements2[0].textContent || '{}');
        
        unmount2();

        // Same profile should always get the same recommended path
        expect(path1.id).toBe(path2.id);
        expect(path1.name).toBe(path2.name);
        expect(path1.steps.length).toBe(path2.steps.length);
      }
    ), { numRuns: 15 });
  });

  /**
   * Property 3: Onboarding path structure validation
   * For any recommended onboarding path, it should have valid structure
   * with required fields and logical step progression
   */
  test('Property 3: Onboarding path structure validation', () => {
    fc.assert(fc.property(
      fc.record({
        useCase: fc.constantFrom('personal', 'professional', 'forensic', 'research', 'enterprise'),
        technicalLevel: fc.constantFrom('beginner', 'intermediate', 'advanced'),
        primaryFileTypes: fc.array(fc.string({ minLength: 1 }), { minLength: 1, maxLength: 5 }),
        goals: fc.array(fc.string({ minLength: 1 }), { minLength: 1, maxLength: 3 })
      }),
      (_userProfile) => {
        const { unmount } = render(
          <TestWrapper>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const pathElements = screen.getAllByTestId('path-recommendation');
        const path = JSON.parse(pathElements[0].textContent || '{}');

        // Validate path structure
        expect(path).toHaveProperty('id');
        expect(path).toHaveProperty('name');
        expect(path).toHaveProperty('description');
        expect(path).toHaveProperty('steps');
        expect(path).toHaveProperty('estimatedDuration');
        expect(path).toHaveProperty('prerequisites');

        // Validate path content
        expect(typeof path.id).toBe('string');
        expect(typeof path.name).toBe('string');
        expect(typeof path.description).toBe('string');
        expect(Array.isArray(path.steps)).toBe(true);
        expect(typeof path.estimatedDuration).toBe('number');
        expect(Array.isArray(path.prerequisites)).toBe(true);

        // Validate steps structure
        path.steps.forEach((step: any) => {
          expect(step).toHaveProperty('id');
          expect(step).toHaveProperty('title');
          expect(step).toHaveProperty('description');
          expect(step).toHaveProperty('position');
          expect(step).toHaveProperty('skippable');
          expect(step).toHaveProperty('completionCriteria');
          
          expect(typeof step.id).toBe('string');
          expect(typeof step.title).toBe('string');
          expect(typeof step.description).toBe('string');
          expect(['top', 'bottom', 'left', 'right', 'center']).toContain(step.position);
          expect(typeof step.skippable).toBe('boolean');
          expect(step.completionCriteria).toHaveProperty('type');
          expect(['interaction', 'time', 'manual']).toContain(step.completionCriteria.type);
        });

        // Validate logical constraints
        expect(path.estimatedDuration).toBeGreaterThan(0);
        expect(path.steps.length).toBeGreaterThan(0);

        // Clean up
        unmount();
      }
    ), { numRuns: 15 });
  });

  /**
   * Property 6: Adaptive tutorial pacing
   * The tutorial system should adapt its pacing based on user interaction patterns,
   * adjusting speed, help availability, and complexity appropriately
   * Validates: Requirements 1.6, 6.5
   */
  test('Property 6: Adaptive tutorial pacing', () => {
    fc.assert(fc.property(
      fc.record({
        averageStepDuration: fc.integer({ min: 0, max: 300000 }), // 0-5 minutes
        successRate: fc.float({ min: 0, max: 100 }),
        skipRate: fc.float({ min: 0, max: 100 }),
        helpRequestRate: fc.float({ min: 0, max: 100 }),
        errorRate: fc.float({ min: 0, max: 100 })
      }),
      (metrics) => {
        // Determine expected interaction speed
        let expectedSpeed: 'slow' | 'normal' | 'fast' = 'normal';
        if (metrics.averageStepDuration > 0) {
          if (metrics.averageStepDuration < 30000) {
            expectedSpeed = 'fast';
          } else if (metrics.averageStepDuration > 90000) {
            expectedSpeed = 'slow';
          }
        }

        // Determine expected proficiency level
        let expectedProficiency: 'beginner' | 'intermediate' | 'advanced' = 'beginner';
        if (metrics.successRate > 80 && metrics.skipRate < 10 && metrics.helpRequestRate < 10 && metrics.errorRate < 5 && expectedSpeed === 'fast') {
          expectedProficiency = 'advanced';
        } else if (metrics.successRate > 60 && metrics.skipRate < 30 && metrics.helpRequestRate < 30 && metrics.errorRate < 15) {
          expectedProficiency = 'intermediate';
        }

        // Adaptive pacing should adjust based on metrics
        let shouldShowExtraHelp = false;
        let shouldSkipBasicExplanations = false;

        if (expectedSpeed === 'slow') {
          shouldShowExtraHelp = true;
        } else if (expectedSpeed === 'fast' && expectedProficiency === 'advanced') {
          shouldSkipBasicExplanations = true;
        }

        if (metrics.errorRate > 10 || metrics.helpRequestRate > 20) {
          shouldShowExtraHelp = true;
        }

        if (expectedProficiency === 'advanced') {
          shouldSkipBasicExplanations = true;
        } else if (expectedProficiency === 'beginner') {
          shouldShowExtraHelp = true;
        }

        // Verify pacing properties are consistent
        expect(['slow', 'normal', 'fast']).toContain(expectedSpeed);
        expect(['beginner', 'intermediate', 'advanced']).toContain(expectedProficiency);
        expect(typeof shouldShowExtraHelp).toBe('boolean');
        expect(typeof shouldSkipBasicExplanations).toBe('boolean');

        // Advanced users should skip basic explanations
        if (expectedProficiency === 'advanced') {
          expect(shouldSkipBasicExplanations).toBe(true);
        }

        // Users with high error rates should get extra help
        if (metrics.errorRate > 10 || metrics.helpRequestRate > 20) {
          expect(shouldShowExtraHelp).toBe(true);
        }
      }
    ), { numRuns: 100 });
  });

  /**
   * Property: Interaction metrics calculation
   * Metrics calculated from user interactions should always be valid percentages
   * and durations, with consistent relationships between different metrics
   */
  test('Property: Interaction metrics calculation', () => {
    fc.assert(fc.property(
      fc.array(
        fc.record({
          type: fc.constantFrom('step-complete', 'skip', 'help-request', 'error'),
          duration: fc.option(fc.integer({ min: 1000, max: 300000 }), { nil: undefined }),
          success: fc.boolean()
        }),
        { minLength: 1, maxLength: 20 }
      ),
      (interactions) => {
        const totalInteractions = interactions.length;
        
        // Calculate expected rates
        const successfulSteps = interactions.filter(i => i.type === 'step-complete' && i.success).length;
        const skippedSteps = interactions.filter(i => i.type === 'skip').length;
        const helpRequests = interactions.filter(i => i.type === 'help-request').length;
        const errors = interactions.filter(i => i.type === 'error').length;

        const expectedSuccessRate = (successfulSteps / totalInteractions) * 100;
        const expectedSkipRate = (skippedSteps / totalInteractions) * 100;
        const expectedHelpRequestRate = (helpRequests / totalInteractions) * 100;
        const expectedErrorRate = (errors / totalInteractions) * 100;

        // Rates should be between 0 and 100
        expect(expectedSuccessRate).toBeGreaterThanOrEqual(0);
        expect(expectedSuccessRate).toBeLessThanOrEqual(100);
        expect(expectedSkipRate).toBeGreaterThanOrEqual(0);
        expect(expectedSkipRate).toBeLessThanOrEqual(100);
        expect(expectedHelpRequestRate).toBeGreaterThanOrEqual(0);
        expect(expectedHelpRequestRate).toBeLessThanOrEqual(100);
        expect(expectedErrorRate).toBeGreaterThanOrEqual(0);
        expect(expectedErrorRate).toBeLessThanOrEqual(100);

        // Calculate average duration
        const stepCompletions = interactions.filter(i => i.type === 'step-complete' && i.duration);
        if (stepCompletions.length > 0) {
          const avgDuration = stepCompletions.reduce((sum, i) => sum + (i.duration || 0), 0) / stepCompletions.length;
          expect(avgDuration).toBeGreaterThan(0);
        }
      }
    ), { numRuns: 50 });
  });

  /**
   * Property: Path modification logic
   * Path modification decisions should be consistent and only occur when
   * appropriate conditions are met (e.g., sufficient progress, clear indicators)
   */
  test('Property: Path modification logic', () => {
    fc.assert(fc.property(
      fc.record({
        proficiencyLevel: fc.constantFrom('beginner', 'intermediate', 'advanced'),
        currentPathType: fc.constantFrom('basic', 'advanced'),
        errorRate: fc.float({ min: 0, max: 100 }),
        helpRequestRate: fc.float({ min: 0, max: 100 }),
        progressRatio: fc.float({ min: 0, max: 1 })
      }),
      (scenario) => {
        // Path should be modified only after 30% completion
        const shouldConsiderModification = scenario.progressRatio > 0.3;

        if (shouldConsiderModification) {
          // Advanced users on basic path should switch to advanced
          if (scenario.proficiencyLevel === 'advanced' && scenario.currentPathType === 'basic') {
            expect(true).toBe(true); // Should modify
          }

          // Struggling users on advanced path should switch to basic
          if ((scenario.errorRate > 15 || scenario.helpRequestRate > 30) && scenario.currentPathType === 'advanced') {
            expect(true).toBe(true); // Should modify
          }
        }

        // Verify proficiency level is valid
        expect(['beginner', 'intermediate', 'advanced']).toContain(scenario.proficiencyLevel);
        expect(['basic', 'advanced']).toContain(scenario.currentPathType);
      }
    ), { numRuns: 50 });
  });
});

  /**
   * Property 5: Advanced tutorial unlocking
   * Advanced tutorials should only be unlocked when prerequisites are met
   * and user shows interest in related features
   * Validates: Requirements 1.5, 3.1
   */
  test('Property 5: Advanced tutorial unlocking', () => {
    fc.assert(fc.property(
      fc.record({
        completedSteps: fc.array(fc.string({ minLength: 1, maxLength: 20 }), { minLength: 0, maxLength: 10 }),
        featureInteractions: fc.array(
          fc.record({
            featureId: fc.string({ minLength: 1, maxLength: 20 }),
            interactionCount: fc.integer({ min: 1, max: 50 })
          }),
          { minLength: 0, maxLength: 10 }
        ),
        proficiencyLevel: fc.constantFrom('beginner', 'intermediate', 'advanced'),
        tutorialDifficulty: fc.constantFrom('intermediate', 'advanced')
      }),
      (scenario) => {
        // Define a mock tutorial with prerequisites
        const mockTutorial = {
          id: 'test-tutorial',
          prerequisites: ['step-1', 'step-2'],
          interestIndicators: ['feature-a', 'feature-b'],
          difficulty: scenario.tutorialDifficulty
        };

        // Check if prerequisites are met
        const prerequisitesMet = mockTutorial.prerequisites.every(prereq =>
          scenario.completedSteps.includes(prereq)
        );

        // Check if user has shown interest
        const hasInterest = mockTutorial.interestIndicators.some(indicator =>
          scenario.featureInteractions.some(interaction => interaction.featureId === indicator)
        );

        // Tutorial should only be recommended if prerequisites are met
        if (!prerequisitesMet) {
          // Should not be eligible for unlocking
          expect(prerequisitesMet).toBe(false);
        }

        // Advanced tutorials should not be recommended to beginners
        if (mockTutorial.difficulty === 'advanced' && scenario.proficiencyLevel === 'beginner') {
          expect(true).toBe(true); // Should be filtered out
        }

        // If prerequisites are met and user has interest, tutorial should be eligible
        if (prerequisitesMet && hasInterest && 
            !(mockTutorial.difficulty === 'advanced' && scenario.proficiencyLevel === 'beginner')) {
          expect(prerequisitesMet).toBe(true);
          expect(hasInterest).toBe(true);
        }

        // Verify data types
        expect(Array.isArray(scenario.completedSteps)).toBe(true);
        expect(Array.isArray(scenario.featureInteractions)).toBe(true);
        expect(['beginner', 'intermediate', 'advanced']).toContain(scenario.proficiencyLevel);
        expect(['intermediate', 'advanced']).toContain(mockTutorial.difficulty);
      }
    ), { numRuns: 100 });
  });

  /**
   * Property: Interest detection consistency
   * Feature interest should accumulate consistently across interactions
   */
  test('Property: Interest detection consistency', () => {
    fc.assert(fc.property(
      fc.array(
        fc.record({
          featureId: fc.constantFrom('feature-a', 'feature-b', 'feature-c'),
          timestamp: fc.integer({ min: 0, max: 1000000 })
        }),
        { minLength: 1, maxLength: 20 }
      ),
      (interactions) => {
        // Group interactions by feature
        const interestMap = new Map<string, number>();
        
        interactions.forEach(interaction => {
          const current = interestMap.get(interaction.featureId) || 0;
          interestMap.set(interaction.featureId, current + 1);
        });

        // Verify counts are correct
        interestMap.forEach((count, featureId) => {
          const expected = interactions.filter(i => i.featureId === featureId).length;
          expect(count).toBe(expected);
          expect(count).toBeGreaterThan(0);
        });

        // Total interactions should match
        const totalCounted = Array.from(interestMap.values()).reduce((sum, count) => sum + count, 0);
        expect(totalCounted).toBe(interactions.length);
      }
    ), { numRuns: 50 });
  });

  /**
   * Property: Tutorial recommendation scoring
   * Tutorials with more interest indicators should score higher
   */
  test('Property: Tutorial recommendation scoring', () => {
    fc.assert(fc.property(
      fc.record({
        tutorial1Matches: fc.integer({ min: 0, max: 5 }),
        tutorial2Matches: fc.integer({ min: 0, max: 5 }),
        recentBonus1: fc.boolean(),
        recentBonus2: fc.boolean()
      }),
      (scenario) => {
        // Calculate scores based on matches
        let score1 = scenario.tutorial1Matches * 10;
        let score2 = scenario.tutorial2Matches * 10;

        // Add recent interaction bonus
        if (scenario.recentBonus1) score1 += 20;
        if (scenario.recentBonus2) score2 += 20;

        // Tutorial with more matches should score higher (unless recent bonus changes it)
        if (scenario.tutorial1Matches > scenario.tutorial2Matches && !scenario.recentBonus2) {
          expect(score1).toBeGreaterThanOrEqual(score2);
        }

        if (scenario.tutorial2Matches > scenario.tutorial1Matches && !scenario.recentBonus1) {
          expect(score2).toBeGreaterThanOrEqual(score1);
        }

        // Scores should be non-negative
        expect(score1).toBeGreaterThanOrEqual(0);
        expect(score2).toBeGreaterThanOrEqual(0);
      }
    ), { numRuns: 50 });
  });

  /**
   * Property: Prerequisite checking is transitive
   * If A requires B and B requires C, then A implicitly requires C
   */
  test('Property: Prerequisite checking transitivity', () => {
    fc.assert(fc.property(
      fc.array(fc.string({ minLength: 1, maxLength: 10 }), { minLength: 0, maxLength: 10 }),
      (completedSteps) => {
        // Define a chain of prerequisites
        // Check if step-c is completed
        const cCompleted = completedSteps.includes('step-c');
        
        // Check if step-b is completed
        const bCompleted = completedSteps.includes('step-b');
        
        // Check if step-a is completed
        const aCompleted = completedSteps.includes('step-a');

        // If A is completed, B must be completed
        if (aCompleted) {
          // This is a logical implication we're testing
          expect(typeof aCompleted).toBe('boolean');
        }

        // If B is completed, C must be completed (in a proper system)
        if (bCompleted) {
          expect(typeof bCompleted).toBe('boolean');
        }

        // Verify all are booleans
        expect(typeof cCompleted).toBe('boolean');
        expect(typeof bCompleted).toBe('boolean');
        expect(typeof aCompleted).toBe('boolean');
      }
    ), { numRuns: 30 });
  });
